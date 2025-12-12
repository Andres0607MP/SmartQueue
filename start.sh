#!/usr/bin/env bash
set -e

# Ejecutar migraciones solo si SKIP_MIGRATIONS no está activado
if [ "${SKIP_MIGRATIONS:-}" = "true" ]; then
    echo "SKIP_MIGRATIONS=true — skipping migrations."
else
    echo "Running Django migrations (prod settings)..."
    python manage.py migrate --noinput --settings=config.settings.prod
fi

# Recoger archivos estáticos
echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=config.settings.prod

# Crear superusuario si no existe — solo si CREATE_SUPERUSER_ON_START=true
if [ "${CREATE_SUPERUSER_ON_START:-}" = "true" ]; then
    echo "Ensuring superuser exists..."
    python manage.py shell --settings=config.settings.prod <<'PY'
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin')

if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print('Created superuser:', username)
else:
        print('Superuser already exists:', username)
PY
else
    echo "Skipping superuser creation (CREATE_SUPERUSER_ON_START not true)"
fi

# Iniciar Gunicorn usando el puerto correcto
echo "Starting gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
