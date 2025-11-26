import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.shortcuts import get_object_or_404
from .models import MatchingSession
from .utils import calculate_match_results_for_session
from apps.movies.models import Movie


class MatchingSessionConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for real-time matching sessions.
    - Group name: matching_<session_id>
    Events:
      - client -> server: {"action":"swipe","movie_id":"<uuid>","liked": true}
      - server -> clients: {"type":"results_update", "results": [...], "swipe": {...}}
    """

    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.group_name = f"matching_{self.session_id}"

        # verify session exists
        exists = await database_sync_to_async(MatchingSession.objects.filter(id=self.session_id).exists)()
        if not exists:
            await self.close(code=4001)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        except Exception:
            pass

    async def receive_json(self, content, **kwargs):
        action = content.get('action')
        user = self.scope.get('user')

        if action == 'swipe':
            movie_id = content.get('movie_id')
            liked = content.get('liked', True)
            # _handle_swipe performs db work; call and get payload
            payload = await self._handle_swipe(user, movie_id, liked)
            if payload:
                # broadcast to group so all participants get updates
                await self.channel_layer.group_send(self.group_name, {
                    'type': 'results_update',
                    **payload
                })

    @database_sync_to_async
    def _handle_swipe(self, user, movie_id, liked):
        # Reuse REST logic: upsert swipe and recalc results
        session = get_object_or_404(MatchingSession, id=self.session_id)
        if user not in session.participants.all():
            session.participants.add(user)

        from .models import MovieSwipe
        from apps.movies.models import Movie

        movie = get_object_or_404(Movie, id=movie_id)
        swipe, created = MovieSwipe.objects.update_or_create(
            session=session, user=user, movie=movie, defaults={'liked': bool(liked)}
        )

        results = calculate_match_results_for_session(session)

        msg = {
            'results': [
                {
                    'movie_id': str(r.movie.id),
                    'title': getattr(r.movie, 'title', ''),
                    'likes_count': r.likes_count,
                    'match_percentage': r.match_percentage
                } for r in results
            ],
            'swipe': {
                'user_id': str(user.id),
                'movie_id': str(movie.id),
                'liked': bool(liked)
            }
        }
        return msg

    async def results_update(self, event):
        # forward results_update to connected client
        await self.send_json(event)

