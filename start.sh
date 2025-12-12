#!/usr/bin/env bash
set -e

# Ejecutar migraciones solo si SKIP_MIGRATIONS no está activado
if [ "${SKIP_MIGRATIONS:-}" = "true" ]; then
    echo "SKIP_MIGRATIONS=true — skipping migrations."
else
    echo "Running Django migrations (prod settings)..."
    # Run migrations but do not abort the whole start script if they fail.
    # This prevents deploys from failing hard when the DB is temporarily
    # inaccessible or credentials/permissions are not yet correct.
    if python manage.py migrate --noinput --settings=config.settings.prod; then
        echo "Migrations completed successfully."
    else
        echo "WARNING: migrations failed — continuing startup. Check logs for details." >&2
    fi
fi

# Recoger archivos estáticos
echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=config.settings.prod

# Crear superusuario si no existe — solo si CREATE_SUPERUSER_ON_START=true
# Además: no crear si SKIP_MIGRATIONS=true para evitar fallos cuando la BD no está lista
if [ "${SKIP_MIGRATIONS:-}" != "true" ] && [ "${CREATE_SUPERUSER_ON_START:-}" = "true" ]; then
    echo "Ensuring superuser exists..."
    python manage.py shell --settings=config.settings.prod 

echo "Starting gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
