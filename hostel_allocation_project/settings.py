import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-CHANGE_THIS_TO_SOMETHING_SECRET")

DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"


def _split_csv_env(name, default=""):
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


ALLOWED_HOSTS = _split_csv_env(
    "DJANGO_ALLOWED_HOSTS",
    "127.0.0.1,localhost,.onrender.com",
)

CSRF_TRUSTED_ORIGINS = _split_csv_env(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "http://127.0.0.1:5173,http://127.0.0.1:5174,http://localhost:5173,http://localhost:5174",
)

CORS_ALLOWED_ORIGINS = _split_csv_env("DJANGO_CORS_ALLOWED_ORIGINS", "")
CORS_ALLOW_CREDENTIALS = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',

    'rest_framework',
    'hostel_app',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'frontend' / 'dist'],
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


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hostel_allocation_project.urls'

WSGI_APPLICATION = 'hostel_allocation_project.wsgi.application'

DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/hostel_db",
        ),
        conn_max_age=600,
        ssl_require=not DEBUG,
    )
}

AUTH_USER_MODEL = 'hostel_app.CustomUser'

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'frontend' / 'dist']
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = "None" if not DEBUG else "Lax"
CSRF_COOKIE_SAMESITE = "None" if not DEBUG else "Lax"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
