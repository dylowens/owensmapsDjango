"""
WSGI config for django_portfolio project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""
from django.core.wsgi import get_wsgi_application
import os
"what is this?"


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoApp.settings')

application = get_wsgi_application()
