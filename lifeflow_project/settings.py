import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-lifeflow-default-development-key-2026')
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')

raw_hosts = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0,testserver')
ALLOWED_HOSTS = [h.strip() for h in raw_hosts.split(',') if h.strip()]
if DEBUG and 'testserver' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('testserver')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # LifeFlow Custom Apps
    'core.apps.CoreConfig',
    'audit.apps.AuditConfig',
    'accounts.apps.AccountsConfig',
    'hospitals.apps.HospitalsConfig',
    'patients.apps.PatientsConfig',
    'donors.apps.DonorsConfig',
    'camps.apps.CampsConfig',
    'appointments.apps.AppointmentsConfig',
    'donations.apps.DonationsConfig',
    'laboratory.apps.LaboratoryConfig',
    'blood_components.apps.BloodComponentsConfig',
    'inventory.apps.InventoryConfig',
    'requests_app.apps.RequestsAppConfig',
    'notifications.apps.NotificationsConfig',
    'reports.apps.ReportsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'audit.middleware.AuditMiddleware',
]

ROOT_URLCONF = 'lifeflow_project.urls'

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
                'core.context_processors.lifeflow_global_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'lifeflow_project.wsgi.application'

# Database Configuration (PostgreSQL-ready with SQLite fallback)
DB_ENGINE = os.getenv('DB_ENGINE', 'sqlite').lower()
if DB_ENGINE == 'postgresql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'lifeflow_db'),
            'USER': os.getenv('DB_USER', 'lifeflow_user'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'lifeflow_password'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            'ATOMIC_REQUESTS': False,
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:dashboard'
LOGOUT_REDIRECT_URL = 'accounts:login'

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# LifeFlow Configurable Defaults
ORGANIZATION_NAME = os.getenv('ORGANIZATION_NAME', 'LIFEFlow National Blood & Hemovigilance System')
ORGANIZATION_CODE = 'LIFEFLOW-HQ'
ENABLE_AUDIT_LOGGING = os.getenv('ENABLE_AUDIT_LOGGING', 'True').lower() in ('true', '1')
