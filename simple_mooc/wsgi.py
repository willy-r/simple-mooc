"""
WSGI config for simple_mooc project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os

from django.conf import BASE_DIR
from django.core.wsgi import get_wsgi_application

import dotenv

dotenv.read_dotenv(BASE_DIR, '.env'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simple_mooc.settings')

application = get_wsgi_application()
