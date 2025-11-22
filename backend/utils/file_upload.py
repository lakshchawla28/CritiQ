import cloudinary
import cloudinary.uploader
from django.conf import settings
import os
import uuid

def upload_profile_picture(file, user_id):
    """Upload profile picture to Cloudinary or local storage"""
    
    if settings.CLOUDINARY_CONFIG.get('cloud_name'):
        # Use Cloudinary
        try:
            result = cloudinary.uploader.upload(
                file,
                folder=f"popcult/profiles/{user_id}",
                public_id=str(uuid.uuid4()),
                overwrite=True,
                resource_type="image"
            )
            return result['secure_url']
        except Exception as e:
            print(f"Cloudinary upload failed: {e}")
            return None
    else:
        # Use local storage
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'profiles', str(user_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        filename = f"{uuid.uuid4()}{os.path.splitext(file.name)[1]}"
        filepath = os.path.join(upload_dir, filename)
        
        with open(filepath, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        return f"{settings.MEDIA_URL}profiles/{user_id}/{filename}"