# Backend Django (DRF) — App Integral de Seguros

## Guía de Implementación Paso a Paso

**Autenticación estándar (Email + Password + JWT)**

---

## 📋 Objetivo

Construir un backend base funcional y seguro que incluya:

- Django 5.x + Django REST Framework
- PostgreSQL
- Autenticación estándar (email + password + JWT)
- Gestión completa de usuarios (CRUD con control por roles)
- Auditoría de acciones sensibles
- Endpoint `/api/v1/health` con validación de DB
- Celery + Redis preparados (sin OTP)
- Dockerización (API + DB + Redis)

### ⚠️ Alcance explícito

**NO se implementa OTP ni verificación por correo en esta fase.**  
El login es tradicional (email + password), con JWT.

---

## 🔧 Paso 0: Pre-requisitos

### Instalar herramientas necesarias

```bash
# Verificar Python 3.12+
python --version

# Instalar Docker y Docker Compose
# macOS: brew install docker docker-compose
# Linux: seguir instrucciones oficiales de Docker

# Verificar instalaciones
docker --version
docker-compose --version
```

**Requisitos:**
- ✅ Python 3.12+
- ✅ Docker + Docker Compose
- ✅ PostgreSQL (si se corre sin Docker)
- ✅ Redis (preparado para futuras tareas async)

---

## 📁 Paso 1: Crear Estructura del Proyecto (Domain-First)

### 1.1 Crear directorio base

```bash
mkdir -p backend
cd backend
```

### 1.2 Crear estructura de directorios

```bash
# Estructura principal
mkdir -p app/settings
mkdir -p apps/{common,audit,users,authn,health}
mkdir -p apps/audit/services
mkdir -p apps/users/{selectors,services}

# Crear archivos __init__.py
touch app/__init__.py
touch app/settings/__init__.py
touch apps/__init__.py
touch apps/common/__init__.py
touch apps/audit/__init__.py
touch apps/users/__init__.py
touch apps/authn/__init__.py
touch apps/health/__init__.py
touch apps/audit/services/__init__.py
touch apps/users/selectors/__init__.py
touch apps/users/services/__init__.py
```

### 1.3 Estructura final esperada

```
backend/
├── app/
│   ├── __init__.py
│   ├── celery.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── local.py
│   │   ├── production.py
│   │   └── logging.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   ├── common/
│   │   ├── __init__.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── pagination.py
│   │   └── utils.py
│   ├── audit/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── admin.py
│   │   └── services/
│   │       ├── __init__.py
│   │       └── audit_log.py
│   ├── users/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── models.py
│   │   ├── permissions.py
│   │   ├── selectors/
│   │   │   ├── __init__.py
│   │   │   └── users.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── users.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── authn/
│   │   ├── __init__.py
│   │   ├── serializers.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── jwt.py
│   │   ├── views.py
│   │   └── urls.py
│   └── health/
│       ├── __init__.py
│       ├── views.py
│       └── urls.py
├── manage.py
├── requirements.txt
├── .env.example
├── Dockerfile
└── docker-compose.yml
```

---

## 📦 Paso 2: Configurar Dependencias

### 2.1 Crear `requirements.txt`

```bash
cat > requirements.txt << 'EOF'
Django>=5.2
djangorestframework>=3.15
djangorestframework-simplejwt>=5.3
psycopg[binary]>=3.2
python-dotenv>=1.0
celery>=5.3
redis>=5.0
django-cors-headers>=4.4
gunicorn>=22.0
drf-spectacular>=0.27
EOF
```

### 2.2 Instalar dependencias

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

---

## ⚙️ Paso 3: Configurar Variables de Entorno

### 3.1 Crear `.env.example`

```bash
cat > .env.example << 'EOF'
DJANGO_SECRET_KEY=change_me
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_URL=postgres://postgres:postgres@localhost:5432/insurance_db
REDIS_URL=redis://localhost:6379/0

JWT_ACCESS_MINUTES=15
JWT_REFRESH_DAYS=7

LOG_LEVEL=INFO
EOF
```

### 3.2 Crear `.env` desde ejemplo

```bash
cp .env.example .env
# Editar .env y cambiar DJANGO_SECRET_KEY
```

---

## 🚀 Paso 4: Inicializar Proyecto Django

### 4.1 Crear proyecto Django

```bash
django-admin startproject app .
```

### 4.2 Verificar estructura

```bash
# Debe existir:
# - app/ (configuración Django)
# - manage.py
```

---

## ⚙️ Paso 5: Configurar Settings

### 5.1 Crear estructura de settings

```bash
# Mover settings.py a settings/base.py
mv app/settings.py app/settings/base.py

# Crear archivos de settings
touch app/settings/local.py
touch app/settings/production.py
touch app/settings/logging.py
```

### 5.2 Configurar `app/settings/base.py`

**Tareas a realizar:**

1. **Importar variables de entorno:**
   ```python
   from dotenv import load_dotenv
   import os
   load_dotenv()
   ```

2. **Configurar INSTALLED_APPS:**
   ```python
   INSTALLED_APPS = [
       'django.contrib.admin',
       'django.contrib.auth',
       'django.contrib.contenttypes',
       'django.contrib.sessions',
       'django.contrib.messages',
       'django.contrib.staticfiles',
       # Third party
       'rest_framework',
       'rest_framework_simplejwt',
       'corsheaders',
       'drf_spectacular',
       # Local apps
       'apps.users',
       'apps.authn',
       'apps.audit',
       'apps.health',
       'apps.common',
   ]
   ```

3. **Configurar AUTH_USER_MODEL:**
   ```python
   AUTH_USER_MODEL = 'users.User'
   ```

4. **Configurar base de datos desde DATABASE_URL**

5. **Configurar DRF:**
   - JWT como autenticación por defecto
   - Paginación obligatoria
   - `IsAuthenticated` como permiso por defecto

6. **Configurar logging centralizado (sin secretos)**

### 5.3 Configurar `app/settings/__init__.py`

```python
from .base import *
from .logging import *
```

### 5.4 Configurar `app/settings/local.py`

```python
from .base import *

DEBUG = True
# Configuraciones específicas de desarrollo
```

---

## 👤 Paso 6: Implementar Modelo de Usuario

### 6.1 Crear `apps/users/models.py`

**Implementar `User` con:**

- `id` (UUID, primary key)
- `full_name` (CharField)
- `id_type` (CharField con choices: CC, CE, NIT, etc.)
- `id_number` (CharField)
- `email_primary` (EmailField, unique, USERNAME_FIELD)
- `email_secondary` (EmailField, nullable)
- `phone` (CharField)
- `address` (TextField, nullable)
- `birth_date` (DateField)
- `profile_photo_url` (URLField, nullable)
- `role` (CharField con TextChoices: ADMIN, CLIENT, INTERVENTORIA, SUPERVISOR)
- `status` (CharField con TextChoices: ACTIVE, SUSPENDED)
- `created_at`, `updated_at` (DateTimeField, auto)
- `last_login_at` (DateTimeField, nullable)

**Requisitos técnicos:**

- Heredar de `AbstractBaseUser` y `PermissionsMixin`
- `email_primary` como `USERNAME_FIELD`
- Crear `UserManager` con `create_user` y `create_superuser`
- Constraints: `unique` en `email_primary`, recomendado `unique_together` en `(id_type, id_number)`
- `is_active` derivado de `status == ACTIVE`
- Usar `set_password()` al crear/actualizar password

### 6.2 Crear `apps/users/admin.py`

```python
from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # Configurar admin según necesidades
    pass
```

### 6.3 Ejecutar migraciones iniciales

```bash
python manage.py makemigrations users
python manage.py migrate
```

---

## 📝 Paso 7: Implementar Auditoría

### 7.1 Crear `apps/audit/models.py`

**Implementar modelo `AuditLog` con:**

- `actor_user` (ForeignKey a User)
- `action` (CharField) - ej: LOGIN_SUCCESS, USER_CREATED, etc.
- `entity` (CharField) - ej: "User", "Policy", etc.
- `entity_id` (UUIDField)
- `metadata` (JSONField)
- `ip_address` (GenericIPAddressField, nullable)
- `created_at` (DateTimeField, auto_now_add)

### 7.2 Crear `apps/audit/services/audit_log.py`

**Implementar función:**

```python
def log_audit_event(actor_user, action, entity, entity_id, metadata=None, ip_address=None):
    """
    Registra un evento de auditoría.
    
    Args:
        actor_user: Usuario que realiza la acción
        action: Tipo de acción (ej: "LOGIN_SUCCESS")
        entity: Entidad afectada (ej: "User")
        entity_id: ID de la entidad
        metadata: Diccionario con información adicional
        ip_address: IP del cliente
    """
    # Implementar creación de AuditLog
    pass
```

### 7.3 Crear `apps/audit/admin.py`

```python
from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'entity', 'actor_user', 'created_at']
    list_filter = ['action', 'entity', 'created_at']
    readonly_fields = ['created_at']
```

### 7.4 Ejecutar migraciones

```bash
python manage.py makemigrations audit
python manage.py migrate
```

---

## 🔨 Paso 8: Implementar Servicios de Usuarios

### 8.1 Crear `apps/users/services/users.py`

**Implementar las siguientes funciones:**

1. **`register_user(data) -> User`**
   - Crear usuario con `role = CLIENT`
   - `status = ACTIVE`
   - Hashear password con `set_password()`
   - Generar `AuditLog` con acción `USER_REGISTERED`

2. **`create_user_by_admin(data, actor_user) -> User`**
   - Validar que `actor_user.role == ADMIN`
   - Crear usuario con `role` y `status` definidos
   - Hashear password
   - Generar `AuditLog` con acción `USER_CREATED_BY_ADMIN`

3. **`update_user_by_admin(user_id, data, actor_user) -> User`**
   - Validar que `actor_user.role == ADMIN`
   - Actualizar usuario
   - Si cambia password, usar `set_password()`
   - Generar `AuditLog` con acción `USER_UPDATED_BY_ADMIN`

4. **`update_self_user(user, data) -> User`**
   - Validar campos permitidos (no `role`, `status`, etc.)
   - Actualizar usuario
   - Generar `AuditLog` con acción `USER_UPDATED_SELF`

5. **`suspend_user(user_id, actor_user) -> User`**
   - Validar que `actor_user.role == ADMIN`
   - Cambiar `status = SUSPENDED`
   - Generar `AuditLog` con acción `USER_SUSPENDED`

6. **`activate_user(user_id, actor_user) -> User`**
   - Validar que `actor_user.role == ADMIN`
   - Cambiar `status = ACTIVE`
   - Generar `AuditLog` con acción `USER_ACTIVATED`

**Regla crítica:** Cada acción debe generar un `AuditLog`.

---

## 🔍 Paso 9: Implementar Selectors de Usuarios

### 9.1 Crear `apps/users/selectors/users.py`

**Implementar funciones:**

1. **`get_user_by_id(user_id) -> User`**
   - Obtener usuario por ID
   - Lanzar excepción si no existe

2. **`get_user_by_email(email) -> User`**
   - Obtener usuario por email_primary
   - Lanzar excepción si no existe

3. **`list_users(filters, actor_user) -> QuerySet`**
   - Validar que `actor_user.role` sea ADMIN, SUPERVISOR o INTERVENTORIA
   - Aplicar filtros (role, status, search)
   - Retornar QuerySet paginado

---

## 📋 Paso 10: Implementar Serializers

### 10.1 Crear `apps/authn/serializers.py`

**Implementar:**

- **`LoginSerializer`**
  - Campos: `email_primary`, `password`
  - Validación de credenciales

### 10.2 Crear `apps/users/serializers.py`

**Implementar:**

1. **`UserPublicSerializer`**
   - Serializer para mostrar datos públicos del usuario
   - Excluir campos sensibles según rol

2. **`UserRegisterSerializer`**
   - Campos: `full_name`, `id_type`, `id_number`, `email_primary`, `phone`, `birth_date`, `password`, `email_secondary`, `address`, `profile_photo_url`
   - Validación de email único

3. **`UserCreateByAdminSerializer`**
   - Incluye `role` y `status`
   - Validación de permisos

4. **`UserUpdateByAdminSerializer`**
   - Permite actualizar todos los campos
   - Validación de permisos

5. **`UserMeUpdateSerializer`**
   - Solo campos permitidos (no `role`, `status`, `email_primary`)
   - Validación de campos editables

---

## 🔐 Paso 11: Implementar Autenticación JWT

### 11.1 Crear `apps/authn/services/jwt.py`

**Implementar funciones para:**
- Generar tokens JWT
- Validar tokens
- Obtener usuario desde token

### 11.2 Crear `apps/authn/views.py`

**Implementar vistas:**

1. **`LoginView`**
   - POST `/api/v1/auth/login/`
   - Validar credenciales
   - Si usuario `ACTIVE` → retornar JWT (access + refresh) + datos de usuario
   - Si usuario `SUSPENDED` → error 403
   - Auditar: `LOGIN_SUCCESS` o `LOGIN_FAILED`

2. **`RegisterView`**
   - POST `/api/v1/auth/register/`
   - Usar `register_user()` del servicio
   - Retornar usuario creado

3. **`RefreshTokenView`**
   - POST `/api/v1/auth/jwt/refresh/`
   - Validar refresh token
   - Retornar nuevo access token

### 11.3 Crear `apps/authn/urls.py`

```python
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginView, RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```

---

## 👥 Paso 12: Implementar Endpoints de Usuarios

### 12.1 Crear `apps/users/permissions.py`

**Implementar permisos personalizados:**

- `IsAdmin` - Solo ADMIN
- `IsAdminOrSupervisor` - ADMIN o SUPERVISOR
- `IsAdminOrReadOnly` - ADMIN puede editar, otros solo leer
- `IsOwnerOrAdmin` - Usuario propietario o ADMIN

### 12.2 Crear `apps/users/views.py`

**Implementar vistas:**

1. **`UserMeView`**
   - GET `/api/v1/users/me/` - Obtener perfil propio
   - PATCH `/api/v1/users/me/` - Actualizar perfil propio
   - Usar `UserMeUpdateSerializer`

2. **`UserListView`**
   - GET `/api/v1/users/` - Listar usuarios (paginado + filtros)
   - POST `/api/v1/users/` - Crear usuario (solo ADMIN)
   - Permisos: ADMIN, SUPERVISOR, INTERVENTORIA (solo lectura)

3. **`UserDetailView`**
   - GET `/api/v1/users/{id}/` - Ver usuario (ADMIN o self)
   - PATCH `/api/v1/users/{id}/` - Actualizar usuario (solo ADMIN)

4. **`UserSuspendView`**
   - POST `/api/v1/users/{id}/suspend/` - Suspender usuario (solo ADMIN)

5. **`UserActivateView`**
   - POST `/api/v1/users/{id}/activate/` - Activar usuario (solo ADMIN)

### 12.3 Crear `apps/users/urls.py`

```python
from django.urls import path
from .views import (
    UserMeView,
    UserListView,
    UserDetailView,
    UserSuspendView,
    UserActivateView,
)

urlpatterns = [
    path('me/', UserMeView.as_view(), name='user-me'),
    path('', UserListView.as_view(), name='user-list'),
    path('<uuid:id>/', UserDetailView.as_view(), name='user-detail'),
    path('<uuid:id>/suspend/', UserSuspendView.as_view(), name='user-suspend'),
    path('<uuid:id>/activate/', UserActivateView.as_view(), name='user-activate'),
]
```

---

## 🏥 Paso 13: Implementar Endpoint Health

### 13.1 Crear `apps/health/views.py`

**Implementar `HealthView`:**

- GET `/api/v1/health/`
- Ejecutar `SELECT 1` en la base de datos
- Retornar:
  ```json
  {
    "status": "ok",
    "service": "insurance-backend",
    "version": "v1",
    "database": "ok"
  }
  ```
- Si falla DB, retornar 503 con `"database": "error"`

### 13.2 Crear `apps/health/urls.py`

```python
from django.urls import path
from .views import HealthView

urlpatterns = [
    path('', HealthView.as_view(), name='health'),
]
```

---

## 🔗 Paso 14: Configurar URLs Principales

### 14.1 Actualizar `app/urls.py`

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/health/', include('apps.health.urls')),
    path('api/v1/auth/', include('apps.authn.urls')),
    path('api/v1/users/', include('apps.users.urls')),
]
```

---

## 🚀 Paso 15: Ejecutar Migraciones

### 15.1 Crear migraciones

```bash
python manage.py makemigrations
```

### 15.2 Aplicar migraciones

```bash
python manage.py migrate
```

### 15.3 Crear superusuario

```bash
python manage.py createsuperuser
# Seguir las instrucciones en pantalla
```

---

## ✅ Paso 16: Verificación Local

### 16.1 Iniciar servidor

```bash
python manage.py runserver
```

### 16.2 Probar endpoints

**1. Health Check:**
```bash
curl http://localhost:8000/api/v1/health/
```

**2. Registro:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Juan Pérez",
    "id_type": "CC",
    "id_number": "1234567890",
    "email_primary": "juan@example.com",
    "phone": "3001234567",
    "birth_date": "1995-05-10",
    "password": "Str0ngPassword!2025"
  }'
```

**3. Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email_primary": "juan@example.com",
    "password": "Str0ngPassword!2025"
  }'
```

**4. Obtener perfil (usar token del login):**
```bash
curl http://localhost:8000/api/v1/users/me/ \
  -H "Authorization: Bearer <access_token>"
```

**5. Listar usuarios (como admin):**
```bash
curl http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer <admin_access_token>"
```

---

## ⚡ Paso 17: Configurar Celery + Redis

### 17.1 Crear `app/celery.py`

```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings.local')

app = Celery('insurance_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

### 17.2 Actualizar `app/__init__.py`

```python
from .celery import app as celery_app

__all__ = ('celery_app',)
```

### 17.3 Configurar en `app/settings/base.py`

```python
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
```

**Nota:** No hay tasks activas aún. Redis está preparado para futuras tareas (emails, reportes, integraciones).

---

## 🐳 Paso 18: Dockerización

### 18.1 Crear `Dockerfile`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar proyecto
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### 18.2 Crear `docker-compose.yml`

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: insurance_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build: .
    command: >
      sh -c "python manage.py migrate &&
             python manage.py runserver 0.0.0.0:8000"
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgres://postgres:postgres@postgres:5432/insurance_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
```

### 18.3 Crear `.dockerignore`

```
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
.env
*.sqlite3
```

### 18.4 Ejecutar con Docker

```bash
# Construir y levantar servicios
docker-compose up --build

# En otra terminal, crear superusuario
docker-compose exec api python manage.py createsuperuser
```

---

## 🔒 Paso 19: Checklist de Seguridad

### Verificar implementación:

- [ ] Password hashing (Django nativo con `set_password()`)
- [ ] JWT access + refresh tokens configurados
- [ ] Permisos cerrados por defecto (`IsAuthenticated`)
- [ ] Auditoría obligatoria en todas las acciones críticas
- [ ] No logs de passwords ni tokens
- [ ] Filtros por usuario autenticado en selectors

### Hardening para producción (configurar en `app/settings/production.py`):

- [ ] `DEBUG = False`
- [ ] `ALLOWED_HOSTS` bien definido
- [ ] `SECRET_KEY` desde env, rotación planificada
- [ ] `DATABASE_URL` con TLS si aplica
- [ ] `SECURE_SSL_REDIRECT = True`
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`
- [ ] Access token corto (15 min)
- [ ] Rate limiting para login
- [ ] `PASSWORD_HASHERS` con Argon2 o PBKDF2 fuerte
- [ ] `AUTH_PASSWORD_VALIDATORS` habilitados
- [ ] Índices en DB para `email_primary`, `(id_type,id_number)`, `role`, `status`
- [ ] Correlation ID por request (middleware)
- [ ] Logs estructurados JSON

---

## 📡 Contratos de API

### 1. Health

#### GET `/api/v1/health/`

**200 OK:**
```json
{
  "status": "ok",
  "service": "insurance-backend",
  "version": "v1",
  "database": "ok"
}
```

**503 Service Unavailable:**
```json
{
  "status": "error",
  "service": "insurance-backend",
  "version": "v1",
  "database": "error"
}
```

---

### 2. Autenticación

#### A) Registro

**POST `/api/v1/auth/register/`**

**Request:**
```json
{
  "full_name": "Juan Pérez",
  "id_type": "CC",
  "id_number": "1234567890",
  "email_primary": "juan@example.com",
  "phone": "3001234567",
  "birth_date": "1995-05-10",
  "password": "Str0ngPassword!2025",
  "email_secondary": "juan.alt@example.com",
  "address": "Calle 1 # 2-3",
  "profile_photo_url": "https://..."
}
```

**201 Created:**
```json
{
  "id": "0b6e1f0f-8e51-4a19-9c2e-1d7ff2b4ef54",
  "full_name": "Juan Pérez",
  "id_type": "CC",
  "id_number": "1234567890",
  "email_primary": "juan@example.com",
  "email_secondary": "juan.alt@example.com",
  "phone": "3001234567",
  "address": "Calle 1 # 2-3",
  "birth_date": "1995-05-10",
  "profile_photo_url": "https://...",
  "role": "CLIENT",
  "status": "ACTIVE",
  "created_at": "2025-12-16T15:20:00-05:00",
  "updated_at": "2025-12-16T15:20:00-05:00",
  "last_login_at": null
}
```

**400 Bad Request:**
```json
{
  "detail": "email_primary already in use"
}
```

---

#### B) Login

**POST `/api/v1/auth/login/`**

**Request:**
```json
{
  "email_primary": "juan@example.com",
  "password": "Str0ngPassword!2025"
}
```

**200 OK:**
```json
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token",
  "user": {
    "id": "0b6e1f0f-8e51-4a19-9c2e-1d7ff2b4ef54",
    "email_primary": "juan@example.com",
    "full_name": "Juan Pérez",
    "role": "CLIENT",
    "status": "ACTIVE"
  }
}
```

**401 Unauthorized:**
```json
{
  "detail": "invalid credentials"
}
```

**403 Forbidden:**
```json
{
  "detail": "user suspended"
}
```

---

#### C) Refresh Token

**POST `/api/v1/auth/jwt/refresh/`**

**Request:**
```json
{
  "refresh": "jwt_refresh_token"
}
```

**200 OK:**
```json
{
  "access": "new_jwt_access_token"
}
```

---

### 3. Usuarios

**Autenticación requerida:** `Authorization: Bearer <access_token>`

#### A) Perfil Propio

**GET `/api/v1/users/me/`**

**200 OK:**
```json
{
  "id": "0b6e1f0f-8e51-4a19-9c2e-1d7ff2b4ef54",
  "full_name": "Juan Pérez",
  "id_type": "CC",
  "id_number": "1234567890",
  "email_primary": "juan@example.com",
  "email_secondary": "juan.alt@example.com",
  "phone": "3001234567",
  "address": "Calle 1 # 2-3",
  "birth_date": "1995-05-10",
  "profile_photo_url": "https://...",
  "role": "CLIENT",
  "status": "ACTIVE",
  "created_at": "2025-12-16T15:20:00-05:00",
  "updated_at": "2025-12-16T15:20:00-05:00",
  "last_login_at": "2025-12-16T15:21:00-05:00"
}
```

---

#### B) Actualizar Perfil Propio

**PATCH `/api/v1/users/me/`**

**Request:**
```json
{
  "phone": "3009998888",
  "address": "Nueva dirección",
  "email_secondary": "nuevo.alt@example.com",
  "profile_photo_url": "https://new..."
}
```

**200 OK:** Retorna el usuario actualizado

**400 Bad Request:**
```json
{
  "detail": "field not allowed: role"
}
```

---

#### C) Listar Usuarios

**GET `/api/v1/users/?role=CLIENT&status=ACTIVE&search=juan&page=1`**

**200 OK:**
```json
{
  "count": 120,
  "next": "http://.../api/v1/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": "0b6e1f0f-8e51-4a19-9c2e-1d7ff2b4ef54",
      "full_name": "Juan Pérez",
      "email_primary": "juan@example.com",
      "phone": "3001234567",
      "role": "CLIENT",
      "status": "ACTIVE",
      "created_at": "2025-12-16T15:20:00-05:00"
    }
  ]
}
```

**403 Forbidden:**
```json
{
  "detail": "permission denied"
}
```

---

#### D) Crear Usuario por Admin

**POST `/api/v1/users/`**

**Request:**
```json
{
  "full_name": "Ana Gómez",
  "id_type": "CC",
  "id_number": "999999999",
  "email_primary": "ana@example.com",
  "phone": "3000000000",
  "birth_date": "1990-01-01",
  "password": "Str0ngPassword!2025",
  "role": "SUPERVISOR",
  "status": "ACTIVE"
}
```

**201 Created:** Usuario completo

---

#### E) Ver Usuario por ID

**GET `/api/v1/users/{id}/`**

**200 OK:** Usuario público/extendido según rol

**404 Not Found:**
```json
{
  "detail": "not found"
}
```

---

#### F) Actualizar Usuario por Admin

**PATCH `/api/v1/users/{id}/`**

**Request:**
```json
{
  "role": "CLIENT",
  "status": "SUSPENDED",
  "phone": "3011111111"
}
```

**200 OK:** Usuario actualizado

---

#### G) Suspender Usuario

**POST `/api/v1/users/{id}/suspend/`**

**200 OK:**
```json
{
  "detail": "user suspended"
}
```

---

#### H) Activar Usuario

**POST `/api/v1/users/{id}/activate/`**

**200 OK:**
```json
{
  "detail": "user activated"
}
```

---

## 🔐 Permisos por Rol

### Matriz de Permisos

| Endpoint | ADMIN | SUPERVISOR | INTERVENTORIA | CLIENT |
|----------|-------|------------|---------------|--------|
| `GET /users/me` | ✅ | ✅ | ✅ | ✅ |
| `PATCH /users/me` | ✅ | ✅ | ✅ | ✅ (solo campos permitidos) |
| `GET /users/` | ✅ | ✅ | ✅ | ❌ |
| `POST /users/` | ✅ | ❌ | ❌ | ❌ |
| `GET /users/{id}` | ✅ | ✅ (read-only) | ✅ (read-only) | ✅ (solo self) |
| `PATCH /users/{id}` | ✅ | ❌ | ❌ | ❌ |
| `POST /users/{id}/suspend` | ✅ | ❌ | ❌ | ❌ |
| `POST /users/{id}/activate` | ✅ | ❌ | ❌ | ❌ |

**Reglas críticas:**
- CLIENT nunca lista usuarios
- CLIENT nunca edita a otros
- SUPERVISOR/INTERVENTORIA solo lectura (recomendado: subset de campos sin datos sensibles)

---

## ❌ No Implementado (Alcance Explícito)

Los siguientes módulos **NO** se implementan en esta fase:

- ❌ OTP / verificación por correo
- ❌ Pagos (Wompi / PSE)
- ❌ Estados de cuenta
- ❌ Pólizas y documentos
- ❌ Cotizaciones
- ❌ Integración CASSE
- ❌ Reportes CSV/PDF
- ❌ Notificaciones push

---

## 🎯 Próximos Pasos Recomendados

1. Payments + Webhooks (idempotencia)
2. Policies + documentos
3. Accounts + ledger
4. CASSE sync
5. Reports + dashboards

---

## 📝 Notas Técnicas

### Custom User (AbstractBaseUser)

**Nota importante:** Django usa el campo `password` para hash. La forma limpia es: guardar hash en `password` (Django) y en tu documentación/capa de negocio lo llamas `password_hash`. No duplicar campos.

### Campos Clave del Modelo User

```
full_name, id_type, id_number, email_primary, email_secondary, 
phone, address, birth_date, profile_photo_url, role, status, 
created_at, updated_at, last_login_at
```
