import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import ChatRoom, Message, TypingStatus
from apps.authentication.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to chat'
        }))
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Set typing status to false
        await self.update_typing_status(False)
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'chat_message':
            await self.handle_chat_message(data)
        elif message_type == 'typing':
            await self.handle_typing(data)
        elif message_type == 'read_receipt':
            await self.handle_read_receipt(data)
    
    async def handle_chat_message(self, data):
        message_text = data['message']
        shared_content_id = data.get('shared_content_id')
        msg_type = data.get('message_type', 'text')
        
        # Save message to database
        message = await self.save_message(
            message_text, 
            msg_type, 
            shared_content_id
        )
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message_broadcast',
                'message_id': str(message.id),
                'message': message_text,
                'message_type': msg_type,
                'shared_content_id': shared_content_id,
                'sender_id': str(self.user.id),
                'sender_username': self.user.username,
                'sender_profile_picture': self.user.profile_picture,
                'timestamp': message.created_at.isoformat()
            }
        )
    
    async def chat_message_broadcast(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message_id': event['message_id'],
            'message': event['message'],
            'message_type': event['message_type'],
            'shared_content_id': event['shared_content_id'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'sender_profile_picture': event['sender_profile_picture'],
            'timestamp': event['timestamp']
        }))
    
    async def handle_typing(self, data):
        is_typing = data.get('is_typing', False)
        
        # Update typing status
        await self.update_typing_status(is_typing)
        
        # Broadcast typing status
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_broadcast',
                'user_id': str(self.user.id),
                'username': self.user.username,
                'is_typing': is_typing
            }
        )
    
    async def typing_broadcast(self, event):
        # Don't send to self
        if event['user_id'] != str(self.user.id):
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_typing': event['is_typing']
            }))
    
    async def handle_read_receipt(self, data):
        message_id = data.get('message_id')
        
        # Mark message as read
        await self.mark_message_read(message_id)
        
        # Send read receipt to sender
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'read_receipt_broadcast',
                'message_id': message_id,
                'reader_id': str(self.user.id)
            }
        )
    
    async def read_receipt_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'message_id': event['message_id'],
            'reader_id': event['reader_id']
        }))
    
    @database_sync_to_async
    def save_message(self, message_text, msg_type, shared_content_id):
        chat_room = ChatRoom.objects.get(id=self.room_id)
        message = Message.objects.create(
            chat_room=chat_room,
            sender=self.user,
            message_text=message_text,
            message_type=msg_type,
            shared_content_id=shared_content_id
        )
        
        # Update chat room
        chat_room.last_message_text = message_text[:100]
        chat_room.last_message_at = timezone.now()
        chat_room.last_message_sender = self.user
        chat_room.save()
        
        return message
    
    @database_sync_to_async
    def update_typing_status(self, is_typing):
        chat_room = ChatRoom.objects.get(id=self.room_id)
        TypingStatus.objects.update_or_create(
            chat_room=chat_room,
            user=self.user,
            defaults={
                'is_typing': is_typing,
                'last_updated': timezone.now()
            }
        )
    
    @database_sync_to_async
    def mark_message_read(self, message_id):
        try:
            message = Message.objects.get(id=message_id)
            if message.sender != self.user:
                message.is_read = True
                message.read_at = timezone.now()
                message.save()
        except Message.DoesNotExist:
            pass
