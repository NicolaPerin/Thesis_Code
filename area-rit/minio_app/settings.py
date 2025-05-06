from pathlib import Path
import os
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

SECRET_KEY = config('DJANGO_SECRET_KEY', default='fallback-secret-key')

DEBUG = config('DJANGO_DEBUG', default=False, cast=bool)

# Allowed Hosts – read directly from environment variable
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '').split(',')
print("ALLOWED_HOSTS:", ALLOWED_HOSTS)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mozilla_django_oidc',
    'storages',
    'file_manager',
]

AUTHENTICATION_BACKENDS = [
    'mozilla_django_oidc.auth.OIDCAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
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

ROOT_URLCONF = 'minio_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

############################### AUTHENTIK / OIDC ###############################
OIDC_RP_CLIENT_ID = config('OIDC_RP_CLIENT_ID')
OIDC_RP_CLIENT_SECRET = config('OIDC_RP_CLIENT_SECRET')
OIDC_RP_SCOPES = config('OIDC_RP_SCOPES', default="openid email profile")
OIDC_RP_SIGN_ALGO = config('OIDC_RP_SIGN_ALGO', default="RS256")
OIDC_VERIFY_SSL = config('OIDC_VERIFY_SSL', default=True, cast=bool)

# Force SSL usage behind a reverse proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True

OIDC_OP_AUTHORIZATION_ENDPOINT = config('OIDC_OP_AUTHORIZATION_ENDPOINT')
OIDC_OP_TOKEN_ENDPOINT = config('OIDC_OP_TOKEN_ENDPOINT')
OIDC_OP_USER_ENDPOINT = config('OIDC_OP_USER_ENDPOINT')
OIDC_OP_JWKS_ENDPOINT = config('OIDC_OP_JWKS_ENDPOINT')

OIDC_REQUESTS_OPTIONS = {
    "verify": os.getenv("REQUESTS_CA_BUNDLE", "/etc/ssl/certs/ca-certificates.crt")
}

LOGIN_URL = config('OIDC_LOGIN_URL', default='/oidc/login/')
LOGIN_REDIRECT_URL = config('OIDC_LOGIN_REDIRECT_URL', default='https://lame-fair.dev.rt.areasciencepark.it/oidc/callback/')

OIDC_OP_LOGOUT_ENDPOINT = config('OIDC_OP_LOGOUT_ENDPOINT')
OIDC_LOGOUT_REDIRECT_URL = config('OIDC_LOGOUT_REDIRECT_URL', default='https://lame-fair.dev.rt.areasciencepark.it')
OIDC_RP_INITIATED_LOGOUT = config('OIDC_RP_INITIATED_LOGOUT', default=True, cast=bool)

LOGOUT_REDIRECT_URL = OIDC_LOGOUT_REDIRECT_URL

################################### MinIO ####################################
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_S3_ENDPOINT_URL = config('MINIO_ENDPOINT_URL')
AWS_ACCESS_KEY_ID = config('MINIO_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = config('MINIO_SECRET_KEY')
AWS_STORAGE_BUCKET_NAME = config('MINIO_BUCKET_NAME')
AWS_S3_USE_SSL = config('AWS_S3_USE_SSL', default=True, cast=bool)
AWS_S3_VERIFY = config('AWS_S3_VERIFY', default=True, cast=bool)
