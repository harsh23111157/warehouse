"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os
import django
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

try:
    from django.core.management import call_command
    call_command('migrate', interactive=False)
    call_command('ensure_superuser', interactive=False)
except Exception as _e:
    print(f"Startup init note: {_e}")

application = get_wsgi_application()
