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

