"""
Django settings for restaurante project.
"""

from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'django-insecure-@4x!h6lqck-8s1g=sgu!ug!q7sfuajq^l5h=ug5ch2@=wfy)3!'

DEBUG = True
# En desarrollo permitimos todas las IPs para poder entrar desde el celular
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Django REST Framework y Swagger
    'rest_framework',
    'drf_yasg',
    # Aplicaciones personalizadas
    'apps.core',
    'apps.usuarios',
    'apps.menu',
    'apps.mesas',
    'apps.pedidos',
    'apps.caja',
    'apps.inventario',
    'apps.contactos',
    'apps.estadisticas',
    'apps.ajustes',
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

ROOT_URLCONF = 'restaurante.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'restaurante.wsgi.application'


# -------------------------
#   DATABASES
# -------------------------
# default -> SQLite local

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Clave primaria por defecto
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'




AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = 'es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# -------------------------
#   STATIC FILES
# -------------------------
STATIC_URL = 'static/'

# -------------------------
#   AUTH / LOGIN
# -------------------------
# Para que los decoradores login_required sin login_url personalizado
# redirijan correctamente a nuestra vista de login
LOGIN_URL = 'login'

# Opcional: después de iniciar sesión, redirigir al dashboard
LOGIN_REDIRECT_URL = 'dashboard'


# -------------------------
#   REST FRAMEWORK
# -------------------------
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# -------------------------
#   SWAGGER SETTINGS
# -------------------------
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Basic': {
            'type': 'basic'
        },
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': True,
    'LOGIN_URL': 'admin:login',
    'LOGOUT_URL': 'admin:logout',
}

