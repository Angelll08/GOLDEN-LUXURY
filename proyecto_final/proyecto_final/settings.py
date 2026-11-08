"""Settings de GOLDEN LUXURY.

Funciona en tu computadora (MySQL de AppServ) y en Render (PostgreSQL).
Los secretos se leen de variables de entorno o del archivo .env, que NO se sube a GitHub.
"""
import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')


def env_bool(nombre, defecto):
    return os.environ.get(nombre, str(defecto)).strip().lower() in ('1', 'true', 'yes', 'si', 'sí')


DEBUG = env_bool('DEBUG', True)
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-solo-para-desarrollo-local')
if not DEBUG and 'SECRET_KEY' not in os.environ:
    raise ImproperlyConfigured('Define la variable de entorno SECRET_KEY cuando DEBUG es False.')

ALLOWED_HOSTS = ['localhost', '127.0.0.1']
CSRF_TRUSTED_ORIGINS = []
RENDER_HOST = os.environ.get('RENDER_EXTERNAL_HOSTNAME')       # Render la define automáticamente
if RENDER_HOST:
    ALLOWED_HOSTS.append(RENDER_HOST)
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_HOST}')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',          # requerido por django-allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'cuentas',
    'tienda',
    'panel',
    'analitica.apps.AnaliticaConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',      # sirve los archivos estáticos en producción
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'cuentas.middleware.SesionObligatoriaMiddleware',   # visitantes: solo ven el inicio
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'proyecto_final.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'tienda.context_processors.carrito',
                'cuentas.context_processors.social',
            ],
        },
    },
]

WSGI_APPLICATION = 'proyecto_final.wsgi.application'

# --- Base de datos ---
# En Render se define DATABASE_URL (PostgreSQL). En tu computadora se usa el MySQL de AppServ.
if os.environ.get('DATABASE_URL'):
    DATABASES = {'default': dj_database_url.config(conn_max_age=600)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('DB_NAME', 'golden_luxury'),
            'USER': os.environ.get('DB_USER', 'root'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
            'PORT': os.environ.get('DB_PORT', '3306'),
            'OPTIONS': {'charset': 'utf8mb4'},
        }
    }

AUTH_USER_MODEL = 'cuentas.Usuario'
SITE_ID = 1

# Permite entrar con usuario O correo, y también con redes sociales (allauth)
AUTHENTICATION_BACKENDS = [
    'cuentas.backends.CorreoOUsuarioBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'inicio'
LOGOUT_REDIRECT_URL = 'inicio'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'          # aquí collectstatic junta todo en producción
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}
if not DEBUG:
    STORAGES['staticfiles'] = {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# OpenStreetMap exige que el navegador envíe el "Referer" al pedir los mapas.
# El valor por defecto de Django (same-origin) lo bloquea y sale "403 Access blocked".
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

if not DEBUG:
    # Render entrega la página por HTTPS a través de un proxy
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'


# ============================================================
# INICIO DE SESIÓN CON REDES SOCIALES (Google y Facebook)
# Instagram NO está disponible: Meta ya no permite usarlo para iniciar sesión
# en sitios externos (recomiendan Facebook Login).
# Las credenciales se guardan en el archivo .env (local) o en las variables de entorno de Render.
# Mientras estén vacías, el botón aparece desactivado.
# ============================================================
ACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID', ''),
            'secret': os.environ.get('GOOGLE_SECRET', ''),
            'key': '',
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    },
    'facebook': {
        'APP': {
            'client_id': os.environ.get('FACEBOOK_APP_ID', ''),
            'secret': os.environ.get('FACEBOOK_SECRET', ''),
            'key': '',
        },
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'FIELDS': ['id', 'email', 'name', 'first_name', 'last_name'],
    },
}
