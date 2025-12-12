#!/usr/bin/env bash
set -e

if [ "${SKIP_MIGRATIONS:-}" = "true" ]; then
    echo "SKIP_MIGRATIONS=false — skipping migrations."
else
    echo "Running Django migrations (prod settings)..."
    python manage.py migrate --noinput --settings=config.settings.prod
fi

echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=config.settings.prod <<'PY'
import os
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ.get('SUPERUSER_USERNAME')
email = os.environ.get('SUPERUSER_EMAIL', '')
password = os.environ.get('SUPERUSER_PASSWORD')
if username and password:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print('Superuser created:', username)
    else:
        print('Superuser already exists:', username)
else:
    print('SUPERUSER_USERNAME or SUPERUSER_PASSWORD not set; skipping superuser creation')
PY

echo "Starting gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
