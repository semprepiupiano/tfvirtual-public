"""
Production Settings for Heroku
"""
import os
import django_heroku

from tfwvirtual.settings.dev import *

ALLOWED_HOSTS = ['tfwvirtual.herokuapp.com']

# Parse database connection url strings like psql://user:pass@127.0.0.1:8458/db
DATABASES = {
    # read os.environ['DATABASE_URL'] and raises ImproperlyConfigured exception if not found
    'default': os.environ.get('DATABASE_URL'),
}

django_heroku.settings(locals())

SECURE_HSTS_SECONDS = 3600
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True