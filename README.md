SmartQueue
==========

Backend para un **sistema inteligente de turnos y asignación automática**. SmartQueue permite gestionar filas virtuales para servicios como bancos, clínicas, centros de trámites o soporte al cliente, optimizando la asignación de turnos según prioridad, tipo de servicio, carga de trabajo de los agentes y horarios disponibles.

Descripción general del sistema
-------------------------------

SmartQueue ofrece:

- Gestión de usuarios con roles (cliente, agente y administrador).
- Registro de servicios (caja, asesoría, soporte, trámites, etc.) y tiempo estimado por atención.
- Creación y gestión de tickets de turno con prioridad, estado y horario estimado.
- Motor de asignación inteligente que selecciona el mejor agente disponible.
- Endpoints de simulación y confirmación atómica de asignaciones.
- Filtrado avanzado, autenticación JWT y documentación con Swagger/OpenAPI.

Apps principales
----------------

- `users/`: gestión de usuarios, perfiles y roles.
- `services/`: servicios ofrecidos y relación con agentes.
- `queue/`: tickets de turno, prioridades y estados.
- `smartqueue/`: motor de asignación inteligente, simulación y commit.

Base de datos
-------------

SmartQueue usa **MySQL** tanto en desarrollo como en producción.

La configuración de la base de datos se controla mediante variables de entorno (cargadas desde `.env` en local):

- `DJANGO_DB_ENGINE` (por defecto `django.db.backends.mysql`).
- `DJANGO_DB_NAME`: nombre de la base de datos (por ejemplo, `smartqueue`).
- `DJANGO_DB_USER`: usuario de la base de datos.
- `DJANGO_DB_PASSWORD`: contraseña del usuario.
- `DJANGO_DB_HOST`: host del servidor MySQL (por defecto `localhost` en desarrollo).
- `DJANGO_DB_PORT`: puerto del servidor MySQL (por defecto `3306`).
- `DJANGO_DB_CHARSET`: charset usado por la base de datos (por defecto `utf8mb4`).

Entornos:

- **Desarrollo**: usa el módulo de settings `config.settings.dev`, normalmente apuntando a un MySQL local definido en `.env`.
- **Producción**: usa el módulo de settings `config.settings.prod`, apuntando a una instancia MySQL en la nube configurada con las mismas variables de entorno en el proveedor (Railway, Render, RDS, etc.).

Roles y responsabilidades
-------------------------

Cada integrante es propietario principal de una app o área y colabora en integración, pruebas y revisión de código.

- **Hugo (líder técnico)**
  - Propietario: arquitectura, configuración multi‑entorno (`config/settings`), seguridad y despliegue.
  - Responsabilidades principales:
    - Configurar la estructura profesional del proyecto (base/dev/prod) y variables de entorno.
    - Implementar autenticación JWT (SimpleJWT) y el manejador global de excepciones.
    - Implementar el endpoint de salud `/api/health/` con verificación de base de datos.
    - Diseñar el motor de asignación en `smartqueue/` (endpoints `simulate` y `commit` con transacciones atómicas).
    - Diseñar y mantener el pipeline de CI/CD y el despliegue en la nube (PostgreSQL o MySQL).

- **Andrei (users – autenticación y permisos)**
  - Propietario: app `users/`.
  - Responsabilidades principales:
    - Definir el modelo `Profile` (OneToOne con `User`) y los roles (`customer`, `agent`, `admin`).
    - Implementar endpoints de registro y login con JWT, y endpoint de perfil (`/profile/me/`).
    - Crear permisos personalizados (`IsAdmin`, `IsAgent`, `IsOwnerOrReadOnly`).
    - Configurar filtros avanzados de usuarios (por nombre, rol, email).
    - Desarrollar pruebas unitarias de serializers, vistas y permisos de `users`.

- **Anderson (services – servicios y agentes)**
  - Propietario: app `services/`.
  - Responsabilidades principales:
    - Diseñar los modelos `Service` (tipo de servicio, duración estimada) y relación con agentes.
    - Implementar el CRUD de servicios y endpoints personalizados (por ejemplo: `services/<id>/agents/`, `services/popular/`).
    - Incorporar filtros avanzados (nombre, tiempo estimado, categoría).
    - Mantener la documentación de la API relacionada con `services` en Swagger/OpenAPI.

- **Luque (queue – tickets y flujo de turnos)**
  - Propietario: app `queue/`.
  - Responsabilidades principales:
    - Diseñar el modelo `QueueTicket` (usuario, servicio, número de turno, prioridad, estado, hora estimada).
    - Implementar el CRUD y endpoints personalizados (`create-ticket`, `cancel`, `user/history`).
    - Validar reglas de negocio (no duplicar tickets activos, restricciones de cancelación según estado, etc.).
    - Configurar filtros avanzados (por servicio, prioridad, estado, fecha).
    - Desarrollar pruebas unitarias y de integración sobre el flujo de turnos.

Colaboración y trabajo en equipo
--------------------------------

- Cada integrante desarrolla su app en una rama del estilo `feat/<app>-<descripcion>`.
- Todo cambio entra por Pull Request asociado a un issue; nadie hace push directo a `main`.
- Al menos un integrante distinto al autor debe revisar y aprobar cada PR.
- Hugo coordina la integración técnica entre `users`, `services`, `queue` y `smartqueue`, así como el despliegue.

Este README se irá ampliando con la arquitectura detallada, modelos, endpoints principales y guía de despliegue a medida que el proyecto avance.

---

**Resumen rápido / Qué hay en este repo**
- `config/` : configuraciones de entorno (`base.py`, `dev.py`, `prod.py`) y URLs globales.
- `apps/` : aplicaciones del dominio (`users`, `services`, `queue_app`, `smartqueue`).
- `.env.example` : ejemplo de variables de entorno (no editar, copiar a `.env` para desarrollo local).
- `requirements.txt` / `requirements-dev.txt` : dependencias.

**Estado importante (antes de ejecutar)**
- El proyecto define `prod` y `dev` de forma separada. `manage.py` por defecto apunta a `config.settings.prod` (seguridad: evita arrancar en `DEBUG=True` si alguien clona y ejecuta por defecto).
- Nunca subas tu `.env` al repositorio. `/.gitignore` ya incluye `.env`.
- Si copias `.env.example` a `.env`, revisa `DJANGO_DEBUG` y pon `False` para producción.

---

**Instalación (desarrollo)**
1. Crear y activar un entorno virtual (recomendado):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instalar dependencias:

```bash
pip install -r requirements-dev.txt
```

3. Crear `.env` a partir del ejemplo y editar valores (BD, SECRET_KEY):

```bash
cp .env.example .env
# editar .env con tu editor y ajustar variables
```

4. Migraciones y superuser (modo desarrollo):

```bash
python manage.py migrate --settings=config.settings.dev
python manage.py createsuperuser --settings=config.settings.dev
```

5. Ejecutar servidor en modo desarrollo (explicitar settings dev):

```bash
python manage.py runserver --settings=config.settings.dev
```

---

**Endpoints principales (rápido)**
- Health check: `GET /api/health/`  — comprueba conexión a BD y devuelve 200/503.
- Swagger/OpenAPI: `GET /swagger/` y `GET /api/schema/`.
- JWT tokens: `POST /api/token/` (obtener access/refresh), `POST /api/token/refresh/`.

Apps y rutas:
- `users`: `/api/users/` (ViewSet), `/api/users/register/` (registro público), `/api/users/me/` (perfil autenticado).
- `services`: `/api/services/` (CRUD + `/popular/`, `/{pk}/agents/`, `/{pk}/assign_agents/`).
- `queue`: `/api/queue/tickets/` (CRUD + `/create-ticket/`, `/{pk}/cancel/`, `/user/history/`).
- `smartqueue`: `/api/smart/simulate_assignment/` (simular) y `/api/smart/commit_assignment/` (persistir con `@transaction.atomic`).

Ejemplos curl rápidos:

1) Registro de usuario
```bash
curl -X POST "http://localhost:8000/api/users/register/" \
  -H "Content-Type: application/json" \
  -d '{"username":"mario","email":"mario@example.com","password":"secret123"}'
```

2) Obtener token (login)
```bash
curl -X POST "http://localhost:8000/api/token/" \
  -H "Content-Type: application/json" \
  -d '{"username":"mario","password":"secret123"}'
```

3) Crear ticket autenticado (usar `Authorization: Bearer <TOKEN>`)
```bash
curl -X POST "http://localhost:8000/api/queue/tickets/create-ticket/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"servicio":"Atención","numero_turno":1,"prioridad":1,"hora_estimada":"2025-12-11T12:00:00Z"}'
```

---

**Pruebas**
- Ejecutar tests (recomendado usar `requirements-dev.txt`):

```bash
pytest --cov=apps --cov-report=term-missing
```

- El proyecto contiene tests en `apps/queue_app/tests.py`, `apps/users/tests.py`, `apps/smartqueue/tests.py`. Asegurate de alcanzar >=50% de coverage según la consigna.

---

**Producción / Despliegue**
- Recomendado: Gunicorn (añadir a `requirements.txt`) o `uvicorn`+`gunicorn` para ASGI. Un ejemplo de `Procfile` (Render / Railway):

```
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

- Variables de entorno obligatorias en producción: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=false`, `DJANGO_DB_*`.
- Asegurate que la base de datos en la nube (PlanetScale, Supabase, Railway, etc.) esté configurada y el host/usuario/clave estén en las variables de entorno.
- La API en producción debe responder `GET /api/health/` correctamente.

---

**Buenas prácticas y seguridad**
- Nunca subir `.env` al repo público. Si lo hiciste, rota las credenciales inmediatamente.
- `manage.py` se ha configurado para arrancar por defecto con `config.settings.prod` para minimizar el riesgo de arrancar accidentalmente en `DEBUG=True`.
- Mantén `DEBUG=False` en producción siempre.

---

**Estructura del proyecto y dónde mirar**
- `config/urls.py` : enrutamiento global y health check.
- `config/settings/` : control de entornos.
- `apps/users/` : modelos `Profile`, serializers, `RegisterView`, permisos personalizados.
- `apps/services/` : `Service` (ManyToMany con usuarios), filtros y endpoints extra.
- `apps/queue_app/` : `QueueTicket` (ForeignKey a `User`), reglas de negocio y endpoints personalizados.
- `apps/smartqueue/` : motor de asignación (`simulate_assignment`, `commit_assignment` con `@transaction.atomic`).

---

Si querés, puedo:
- Añadir ejemplos más detallados (Postman collection o OpenAPI export) — dime si lo querés.
- Añadir instrucciones de despliegue automáticas (Dockerfile + Procfile) y un script CI básico que verifica `DEBUG=False` en `prod`.

Contacto: abre un issue o asigname una tarea si querés que automatice alguno de los pasos.


