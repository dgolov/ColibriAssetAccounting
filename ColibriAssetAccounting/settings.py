from pathlib import Path
from dotenv import load_dotenv

import os


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()


SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG', True)
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'web',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ColibriAssetAccounting.urls'

SETTINGS_PATH = os.path.dirname(os.path.dirname(__file__))

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(SETTINGS_PATH, 'templates')],
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

WSGI_APPLICATION = 'ColibriAssetAccounting.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DB_DATABASE', os.path.join(BASE_DIR, 'db.sqlite3')),
        'USER': os.environ.get('DB_USER', 'user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# User

AUTH_USER_MODEL = 'web.CustomUser'

# Internationalization

LANGUAGE_CODE = 'ru-rus'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(SETTINGS_PATH, 'static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'web/static')
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGOUT_REDIRECT_URL = "/"


# Redis settings

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = int(os.environ.get('REDIS_PORT'))
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')


# Logging settings

if not os.path.exists("./logs/"):
    os.mkdir("./logs/")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': os.environ.get('LOGGING_FORMAT')
        },
        'file': {
            'format': os.environ.get('LOGGING_FORMAT')
        }
    },
    'handlers': {
        'console': {
            'level': os.environ.get('LOGGING_LEVEL'),
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        },
        'file': {
            'level': os.environ.get('LOGGING_LEVEL'),
            'class': 'logging.FileHandler',
            'formatter': 'file',
            'filename': os.environ.get('LOGGING_PATH')
        }
    },
    'loggers': {
        'main': {
            'level': os.environ.get('LOGGING_LEVEL'),
            'handlers': ['console', 'file']
        }
    }
}


# Формат загружаемого excel файда

ASSET_UPLOAD_FORMAT = os.environ.get('UPLOAD_FORMAT', '').split(',')
ASSET_UPLOAD_FIELDS = os.environ.get('UPLOAD_FIELDS', '').split(',')
