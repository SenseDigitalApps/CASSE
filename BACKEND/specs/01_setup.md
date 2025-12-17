## PASO 1: Crear estructura básica del proyecto

Crea un proyecto **Django + Django REST Framework** para una **App de Seguros (backend)** con **PostgreSQL**, **JWT + OTP por correo**, y un **endpoint de health**.  
El proyecto debe funcionar **primero en local** y luego ser **dockerizado**, manteniendo una arquitectura clara y alineada al alcance del contrato.

El contrato posee el siguiente alcance:
**Épica 1 – Gestión de Usuarios y Roles**

Funcionalidades:

- Registro y autenticación de usuarios mediante JWT y doble validación OTP por correo.
- Roles diferenciados (Administrador, Cliente, Interventoría, Supervisor).
- Panel de control con permisos específicos y vistas personalizadas.

Casos de uso:

- Un administrador puede crear, editar, suspender usuarios y asignar permisos.
- El usuario cliente puede registrarse, validar su correo, recuperar contraseña y editar su perfil.

**Épica 2 – Estados de Cuenta y Pagos**

Funcionalidades:

- Visualización del estado de cuenta, saldo y pagos realizados.
- Integración con pasarela de pago (PSE o Wompi).
- Envío automático de comprobantes al correo.
- Actualización en tiempo real del saldo y movimientos.

Casos de uso:

- El usuario consulta su estado de cuenta.
- Realiza un pago directamente desde la app y recibe confirmación inmediata.
- El sistema registra y sincroniza los movimientos en el back-end administrativo.

**Épica 3 – Gestión de Pólizas**

Funcionalidades:

- Consulta en línea de pólizas activas y vencidas.
- Descarga de pólizas en PDF desde el sistema central o APIs externas.
- Integración APIs o webservice para cotización y emisión (SI LO PERMITE, LA API O WEB SERVICE)
- Visualización detallada de coberturas, vigencias y estados.

Casos de uso:

- Un usuario ingresa y visualiza sus pólizas vigentes.
- El sistema sincroniza información del core CASSE y muestra en tiempo real actualizaciones.
- El usuario puede generar una cotización, guardarla y descargarla como PDF.

**Épica 3 – Estados de Cuenta y Pagos**

Funcionalidades:

- Visualización del estado de cuenta, saldo y pagos realizados.
- Integración con pasarela de pago (PSE o Wompi).
- Envío automático de comprobantes al correo.
- Actualización en tiempo real del saldo y movimientos.

Casos de uso:

- El usuario consulta su estado de cuenta.
- Realiza un pago directamente desde la app y recibe confirmación inmediata.
- El sistema registra y sincroniza los movimientos en el back-end administrativo.

**Épica 4 – Notificaciones y Alertas (Opcional)**

Funcionalidades:

- Envío de notificaciones push y por correo.
- Panel administrativo para crear campañas manuales (vía Firebase Cloud Messaging o OneSignal).
- Alertas automáticas configurables (vencimiento de pólizas, nuevos productos, etc.).

Casos de uso:

- El administrador envía un mensaje promocional a un grupo de clientes.
- El sistema notifica automáticamente al cliente cuando su póliza está por vencer.

**Épica 5 – Administración y Reportes**

Funcionalidades:

- Dashboard administrativo con métricas en tiempo real.
- Reportes descargables en CSV/PDF (usuarios activos, pólizas emitidas, cotizaciones).
- Filtros por fechas, estados y aseguradoras.
- Panel de configuración general (API keys, notificaciones, usuarios).

Casos de uso:

- El administrador visualiza cuántas pólizas se emitieron en la última semana.
- Descarga un reporte general de actividad de usuarios.

### Estructura sugerida (domain-first)
insurance_api/
├── backend/
│   ├── manage.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── common/
│   │   │   ├── __init__.py
│   │   │   └── health/
│   │   │       ├── __init__.py
│   │   │       ├── urls.py
│   │   │       └── views.py
│   │   ├── users/
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── permissions.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── tests/
│   │   ├── authn/                 # JWT + OTP (se crea pero NO se implementa aún)
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── services/
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   └── urls.py
│   │   ├── accounts/              # Estados de cuenta (placeholder)
│   │   ├── payments/              # Pagos + webhooks (placeholder)
│   │   ├── policies/              # Pólizas (placeholder)
│   │   ├── quotes/                # Cotizaciones (placeholder)
│   │   ├── integrations/          # CASSE/APIs externas (placeholder)
│   │   ├── notifications/         # Notificaciones (placeholder)
│   │   ├── reports/               # Reportes (placeholder)
│   │   └── audit/                 # Auditoría (placeholder)
│   └── requirements.txt
├── docker/
│   ├── Dockerfile
│   └── entrypoint.sh
├── docker-compose.yml
├── .env.example
└── README.md


## PASO 2: Configurar dependencias

Crea el archivo `backend/requirements.txt` con las dependencias mínimas necesarias para el backend de la **App de Seguros**, utilizando **Django + Django REST Framework**, **PostgreSQL**, **JWT**, **CORS** y configuración por variables de entorno.

### Dependencias requeridas

- **Django** (>=5.0)  
- **Django REST Framework** (>=3.15)  
- **psycopg2-binary** (>=2.9) — Driver PostgreSQL  
- **python-dotenv** (>=1.0) — Variables de entorno  
- **djangorestframework-simplejwt** (>=5.3) — Autenticación JWT  
- **django-cors-headers** (>=4.0) — Manejo de CORS  
- **gunicorn** (>=21.2) — Servidor WSGI para producción / contenedores  

### Ejemplo de `backend/requirements.txt`

```txt
Django>=5.0,<6.0
djangorestframework>=3.15,<4.0
psycopg2-binary>=2.9
python-dotenv>=1.0
djangorestframework-simplejwt>=5.3
django-cors-headers>=4.0
gunicorn>=21.2

## PASO 3: Crear configuración de la aplicación (settings + env)

### 3.1 Crear `.env.example` en la raíz del proyecto

Crea el archivo `.env.example` con las variables mínimas para ejecutar el backend en local y en Docker:

```env
DJANGO_SECRET_KEY=change_me
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=insurance_db
DB_USER=insurance_user
DB_PASSWORD=insurance_pass
DB_HOST=localhost
DB_PORT=5432

JWT_ACCESS_MINUTES=15
JWT_REFRESH_DAYS=7

### 3.2 Configurar `backend/app/settings.py`

En el archivo `backend/app/settings.py` se debe:

- Leer variables de entorno usando:
  - `python-dotenv` únicamente en entorno local.
  - `os.environ` para Docker y producción.
- Configurar la conexión a PostgreSQL usando variables de entorno.
- Instalar y configurar Django REST Framework.
- Instalar y configurar autenticación JWT con SimpleJWT.
- Configurar CORS usando `django-cors-headers`.
- Definir las configuraciones `REST_FRAMEWORK` y `SIMPLE_JWT` usando valores provenientes del entorno.

---

### 3.3 Checklist mínima de `settings.py`

La configuración mínima obligatoria debe incluir:

- **INSTALLED_APPS**:
  - `rest_framework`
  - `corsheaders`
  - `apps.common`
  - `apps.users`
  - `apps.authn` *(aunque aún no se implemente completamente)*

- **DATABASES**:
  - Configuración PostgreSQL obtenida desde:
    - `DB_NAME`
    - `DB_USER`
    - `DB_PASSWORD`
    - `DB_HOST`
    - `DB_PORT`

- **REST_FRAMEWORK**:
  - Autenticación JWT configurada como default.

- **SIMPLE_JWT**:
  - Expiración de tokens configurable vía entorno:
    - `JWT_ACCESS_MINUTES`
    - `JWT_REFRESH_DAYS`


## PASO 4: Crear aplicación Django básica + Health Endpoint

En este paso se implementa únicamente lo mínimo para validar que el backend está operativo:
- Django + DRF funcionando
- Rutas base versionadas (`/api/v1/`)
- Endpoint `GET /api/v1/health/` para verificación de estado del servicio
- (Opcional recomendado) chequeo simple de conectividad a PostgreSQL

> Regla: NO crear otros endpoints aún (users/auth/policies/payments). Solo health + configuración de URLs.

---

### 4.1 Registrar rutas (versionadas) en `backend/app/urls.py`

En `backend/app/urls.py`:

- Crear un prefijo base `/api/v1/`
- Incluir las rutas del módulo `health`
- Mantener `admin/` habilitado para pruebas iniciales

Estructura sugerida:

- `/admin/`
- `/api/v1/health/`

---

### 4.2 Crear módulo Health

Crear el módulo de health en:

- `backend/apps/common/health/views.py`
- `backend/apps/common/health/urls.py`

---

### 4.3 Implementar `GET /api/v1/health/`

En `backend/apps/common/health/views.py`:

- Implementar un endpoint DRF usando `@api_view(["GET"])` o `APIView`
- Retornar un JSON con:
  - `status`: `"ok"`
  - `service`: `"insurance_api"`
  - `version`: `"v1"`
  - `database`: `"ok"` o `"error"` *(recomendado: validar conexión simple)*

Respuesta esperada (ejemplo):

```json
{
  "status": "ok",
  "service": "insurance_api",
  "version": "v1",
  "database": "ok"
}

### 4.4 Validación de base de datos (recomendado)

Para reportar `database` como `"ok"` o `"error"`:

- Realizar una verificación simple de conexión (ej. `SELECT 1`).
- Si falla, capturar la excepción y responder `"error"` sin romper el endpoint.

---

### 4.5 Definir rutas del módulo `health`

En `backend/apps/common/health/urls.py`:

- Mapear la vista a la ruta raíz del módulo:

```python
path("", health_view, name="health"

Luego, en backend/app/urls.py, incluir:

path("api/v1/health/", include("apps.common.health.urls"))


4.6 Checklist de verificación del PASO 4

Al finalizar, debe funcionar:

GET http://localhost:8000/api/v1/health/ → retorna status OK

GET http://localhost:8000/admin/ → carga el panel de Django

El endpoint no debe depender de autenticación (público)

Nota: El endpoint health es público porque se usa para monitoreo (load balancer, uptime checks, etc.).