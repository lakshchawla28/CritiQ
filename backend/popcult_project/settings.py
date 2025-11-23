"""
Django settings for popcult_project
"""

from pathlib import Path
from decouple import config
from datetime import timedelta
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------
# SECURITY
# --------------------------
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1").split(",")

# --------------------------
# INSTALLED APPS
# --------------------------
INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'channels',
    'django_celery_beat',

    # Local apps
    'apps.authentication',
    'apps.users',
    'apps.movies',
    'apps.reviews',
    'apps.social',
    'apps.chat',
    'apps.matching',
    'apps.recommendations',
]

# --------------------------
# MIDDLEWARE
# --------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'popcult_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'popcult_project.wsgi.application'
ASGI_APPLICATION = 'popcult_project.asgi.application'

# --------------------------
# DATABASE (POSTGRESQL)
# --------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config("POSTGRES_DB"),
        'USER': config("POSTGRES_USER"),
        'PASSWORD': config("POSTGRES_PASSWORD"),
        'HOST': config("POSTGRES_HOST", default="localhost"),
        'PORT': config("POSTGRES_PORT", default="5432"),
    }
}

# Custom User Model
AUTH_USER_MODEL = 'authentication.User'

# --------------------------
# PASSWORD VALIDATION
# --------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --------------------------
# REST FRAMEWORK
# --------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# --------------------------
# JWT
# --------------------------
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", default=60, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config("JWT_REFRESH_TOKEN_EXPIRE_DAYS", default=7, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# --------------------------
# CORS
# --------------------------
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True

# --------------------------
# CHANNELS (WEBSOCKETS)
# --------------------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(config("REDIS_HOST", default="localhost"), config("REDIS_PORT", default=6379, cast=int))],
        },
    },
}

# --------------------------
# CELERY
# --------------------------
CELERY_BROKER_URL = f"redis://{config('REDIS_HOST', default='localhost')}:{config('REDIS_PORT', default=6379)}/0"
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = "UTC"

# --------------------------
# TMDB
# --------------------------
TMDB_API_KEY = config('TMDB_API_KEY')
TMDB_BASE_URL = config('TMDB_BASE_URL')

# --------------------------
# CLOUDINARY
# --------------------------
CLOUDINARY_CONFIG = {
    'cloud_name': config('CLOUDINARY_CLOUD_NAME', default=''),
    'api_key': config('CLOUDINARY_API_KEY', default=''),
    'api_secret': config('CLOUDINARY_API_SECRET', default=''),
}

# --------------------------
# MEDIA
# --------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
MAX_UPLOAD_SIZE = 5242880  # 5 MB

# --------------------------
# EMAIL
# --------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")

# --------------------------
# STATIC FILES
# --------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

# --------------------------
# DEFAULTS
# --------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --------------------------
# LOGGING
# --------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}


