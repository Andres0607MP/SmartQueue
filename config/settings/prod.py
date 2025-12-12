from .base import *  # noqaq
import os
import dj_database_url

DEBUG = False

# Allow configuring hosts via env var, fallback to all (change in production)
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '*').split(',')

# If DATABASE_URL is provided (e.g., from Filess), use it
if os.getenv('DATABASE_URL'):
	DATABASES = {
		'default': dj_database_url.parse(os.getenv('DATABASE_URL'), conn_max_age=600)
	}
