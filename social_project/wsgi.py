"""
WSGI config for social_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_project.settings')

application = get_wsgi_application()

# Alias for Vercel serverless Python runtime
app = application

if os.environ.get('VERCEL'):
    try:
        from django.core.management import call_command
        from django.db import connection
        table_names = connection.introspection.table_names()
        if 'auth_user' not in table_names:
            call_command('migrate', interactive=False)
            try:
                call_command('seed_data')
            except Exception:
                pass
    except Exception:
        pass
