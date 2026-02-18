import os
from pathlib import Path
from celery.schedules import crontab

from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-newsportal-placeholder-secret-key'

DEBUG = True

ALLOWED_HOSTS = ['testserver', '127.0.0.1', 'localhost']

INSTALLED_APPS = [
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.yandex',

    'news.apps.NewsConfig',
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'news.middleware.TimezoneMiddleware',
]

ROOT_URLCONF = 'newsportal.urls'

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
                'news.context_processors.all_timezones',
            ],
        },
    },
]

WSGI_APPLICATION = 'newsportal.wsgi.application'
ASGI_APPLICATION = 'newsportal.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'ru'

LANGUAGES = [
    ('en-us', _('English')),
    ('ru', _('Russian')),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale')
]

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# django-allauth basic configuration
SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGIN_METHODS = {'email', 'username'}
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_SIGNUP_FIELDS = ['username*', 'password1*', 'password2*']

# Email configuration (console backend by default). Configure SMTP in production.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'no-reply@example.com'

# Celery / Redis configuration
# Redis is used as the broker and result backend by default. Adjust via env vars in production.
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = False

# Celery Beat schedule: every Monday at 08:00 local time
CELERY_BEAT_SCHEDULE = {
    'send-weekly-digest-every-monday-08-00': {
        'task': 'news.tasks.send_weekly_digest_task',
        'schedule': crontab(minute=0, hour=8, day_of_week='mon'),
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'style': '%',
    'formatters': {
        'console_debug': {
            'format': '%(asctime)s %(levelname)s %(message)s'
        },
        'console_warning': {
            'format': '%(asctime)s %(levelname)s %(message)s %(pathname)s'
        },
        'console_error': {
            'format': '%(asctime)s %(levelname)s %(message)s %(pathname)s %(exc_info)s'
        },
        'general_format': {
            'format': '%(asctime)s %(levelname)s %(module)s %(message)s'
        },
        'errors_format': {
            'format': '%(asctime)s %(levelname)s %(message)s %(pathname)s %(exc_info)s'
        },
        'security_format': {
            'format': '%(asctime)s %(levelname)s %(module)s %(message)s'
        },
        'mail_format': {
            'format': '%(asctime)s %(levelname)s %(message)s %(pathname)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'console_debug'
        },
        'console_warning': {
            'level': 'WARNING',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'console_warning'
        },
        'console_error': {
            'level': 'ERROR',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'console_error'
        },
        'general_file': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'class': 'logging.FileHandler',
            'filename': 'general.log',
            'formatter': 'general_format'
        },
        'errors_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'errors.log',
            'formatter': 'errors_format'
        },
        'security_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'security.log',
            'formatter': 'security_format'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'mail_format'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'console_warning', 'console_error', 'general_file'],
            'level': 'DEBUG',
        },
        'django.request': {
            'handlers': ['errors_file', 'mail_admins'],
            'propagate': True,
        },
        'django.server': {
            'handlers': ['errors_file', 'mail_admins'],
            'propagate': True,
        },
        'django.template': {
            'handlers': ['errors_file'],
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['errors_file'],
            'propagate': True,
        },
        'django.security': {
            'handlers': ['security_file'],
            'propagate': True,
        },
    }
}
