import os
import django
from django.conf import settings

# Configurar Django antes de que pytest importe los tests
def pytest_configure():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cafearoma.settings')
    django.setup()