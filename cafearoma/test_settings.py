from .settings import *

# Configuración específica para pruebas
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # Base de datos en memoria para pruebas rápidas
    }
}

# Desactivar emails en pruebas
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Más rápido para pruebas
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Desactivar debug toolbar y otras herramientas de desarrollo
DEBUG = False
TEMPLATE_DEBUG = False

# Para pruebas más rápidas
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True