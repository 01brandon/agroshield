import os
from pathlib import Path
from datetime import timedelta
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost'])

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist',
    'django_celery_beat',
    'channels',
    'cloudinary',
    'cloudinary_storage',
    'drf_spectacular',
    'django_filters',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.farms',
    'apps.disease',
    'apps.weather',
    'apps.marketplace',
    'apps.seeds',
    'apps.cooperatives',
    'apps.livestock',
    'apps.insurance',
    'apps.soil',
    'apps.satellite',
    'apps.forum',
    'apps.academy',
    'apps.traceability',
    'apps.carbon',
    'apps.drones',
    'apps.finance',
    'apps.ivr',
    'apps.alerts',
    'apps.equipment',
    'apps.campaigns',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    }
}

REDIS_URL = env('REDIS_URL')

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {'hosts': [REDIS_URL]},
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': REDIS_URL,
    }
}

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_TIMEZONE = 'Africa/Nairobi'

AUTH_USER_MODEL = 'accounts.User'
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'optional'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': env('GOOGLE_CLIENT_ID'),
            'secret': env('GOOGLE_CLIENT_SECRET'),
        }
    }
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=env.int('ACCESS_TOKEN_LIFETIME_MINUTES', 60)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=env.int('REFRESH_TOKEN_LIFETIME_DAYS', 7)),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'AgroShield API',
    'DESCRIPTION': 'AI-Powered Food Security & Agricultural Intelligence Platform',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': env('CLOUDINARY_API_KEY'),
    'API_SECRET': env('CLOUDINARY_API_SECRET'),
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# celery beat schedule - defines when each task runs automatically
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'fetch-weather-every-3-hours': {
        'task':     'apps.weather.tasks.fetch_weather_for_all_farms',
        'schedule': crontab(minute=0, hour='*/3'),
    },
    'check-food-security-daily': {
        'task':     'apps.alerts.tasks.check_food_security_risk',
        'schedule': crontab(minute=0, hour=6),
    },
    'send-scheduled-campaigns': {
        'task':     'apps.campaigns.tasks.send_scheduled_campaigns',
        'schedule': crontab(minute='*/30'),
    },
}

# api rate limiting - prevents abuse and brute force
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = [
    'rest_framework.throttling.AnonRateThrottle',
    'rest_framework.throttling.UserRateThrottle',
]
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '60/hour',
    'user': '1000/hour',
}

# security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS              = 'DENY'
SECURE_BROWSER_XSS_FILTER   = True

# cors - only allow known frontends
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:8000',
]
CORS_ALLOW_CREDENTIALS = True

# api rate limiting - prevents abuse and brute force
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = [
    'rest_framework.throttling.AnonRateThrottle',
    'rest_framework.throttling.UserRateThrottle',
]
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '60/hour',
    'user': '1000/hour',
}

# security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS              = 'DENY'
SECURE_BROWSER_XSS_FILTER   = True

# cors - only allow known frontends
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:8000',
]
CORS_ALLOW_CREDENTIALS = True

# third party api keys - loaded from .env
OPENWEATHER_API_KEY = env('OPENWEATHER_API_KEY', default='')

# celery beat schedule - defines when each task runs automatically
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'fetch-weather-every-3-hours': {
        'task':     'apps.weather.tasks.fetch_weather_for_all_farms',
        'schedule': crontab(minute=0, hour='*/3'),
    },
    'check-food-security-daily': {
        'task':     'apps.alerts.tasks.check_food_security_risk',
        'schedule': crontab(minute=0, hour=6),
    },
    'send-scheduled-campaigns': {
        'task':     'apps.campaigns.tasks.send_scheduled_campaigns',
        'schedule': crontab(minute='*/30'),
    },
}

# api rate limiting - prevents abuse and brute force
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = [
    'rest_framework.throttling.AnonRateThrottle',
    'rest_framework.throttling.UserRateThrottle',
]
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '60/hour',
    'user': '1000/hour',
}

# security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS              = 'DENY'
SECURE_BROWSER_XSS_FILTER   = True

# cors - only allow known frontends
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:8000',
]
CORS_ALLOW_CREDENTIALS = True

# twilio sms
TWILIO_ACCOUNT_SID  = env('TWILIO_ACCOUNT_SID',  default='')
TWILIO_AUTH_TOKEN   = env('TWILIO_AUTH_TOKEN',    default='')
TWILIO_PHONE_NUMBER = env('TWILIO_PHONE_NUMBER',  default='')

# mpesa daraja
MPESA_CONSUMER_KEY    = env('MPESA_CONSUMER_KEY',    default='')
MPESA_CONSUMER_SECRET = env('MPESA_CONSUMER_SECRET', default='')
MPESA_SHORTCODE       = env('MPESA_SHORTCODE',       default='174379')
MPESA_PASSKEY         = env('MPESA_PASSKEY',         default='')
MPESA_ENV             = env('MPESA_ENV',             default='sandbox')

# stripe
STRIPE_SECRET_KEY      = env('STRIPE_SECRET_KEY',      default='')
STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY', default='')

# openai
OPENAI_API_KEY = env('OPENAI_API_KEY', default='')

# sentinel hub
SENTINELHUB_CLIENT_ID     = env('SENTINELHUB_CLIENT_ID',     default='')
SENTINELHUB_CLIENT_SECRET = env('SENTINELHUB_CLIENT_SECRET', default='')

# gcp
GCP_PROJECT_ID  = env('GCP_PROJECT_ID',  default='')
GCP_PUBSUB_TOPIC = env('GCP_PUBSUB_TOPIC', default='agroshield-scans')

# google credentials file path
GOOGLE_APPLICATION_CREDENTIALS = str(BASE_DIR / 'service_account.json')

# add satellite task to the schedule
CELERY_BEAT_SCHEDULE['fetch-ndvi-every-5-days'] = {
    'task':     'apps.satellite.tasks.fetch_ndvi_for_all_farms',
    'schedule': crontab(minute=0, hour=0, day_of_week='*/5'),
}
