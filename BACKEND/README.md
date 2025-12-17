# App Integral de Seguros – iOS & Android

## Descripción del Proyecto
Aplicación móvil integral de seguros para iOS y Android, diseñada para permitir a los usuarios consultar, cotizar, descargar y gestionar pólizas, visualizar estados de cuenta, realizar pagos en línea y recibir notificaciones automáticas, con un backend administrativo centralizado.

El sistema está pensado para integrarse con core asegurador (CASSE) y APIs externas para cotización y emisión de pólizas, garantizando sincronización en tiempo real y altos estándares de seguridad.

##Arquitectura General
El proyecto se desarrolla bajo una arquitectura cliente-servidor, desacoplada y escalable:
- **Frontend Mobile:** Flutter (iOS / Android)
- **Backend API:** Python (Django + Django REST Framework)
- **Base de Datos:** PostgreSQL
- **Autenticación:** JWT + OTP por correo
- **Pagos:** PSE / Wompi
- **Notificaciones:** Firebase Cloud Messaging / OneSignal

## Estructura del Proyecto

```
├── BACKEND/
│   ├── app/                    # Configuración principal del proyecto Django
│   ├── users/                  # Gestión de usuarios, roles y autenticación
│   ├── auth/                   # JWT, OTP, recuperación de contraseña
│   ├── policies/               # Gestión de pólizas y cotizaciones
│   ├── accounts/               # Estados de cuenta y movimientos financieros
│   ├── payments/               # Integración pasarela de pagos (PSE / Wompi)
│   ├── notifications/          # Notificaciones push y correo
│   ├── reports/                # Reportes administrativos
│   ├── integrations/           # Integración con CASSE y APIs externas
│   ├── core/                   # Utilidades, excepciones y lógica transversal
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── spect/                  # Especificaciones técnicas del proyecto
```

## Stack Tecnológico

- **Python 3.12+**
- **Django 5.2.6** - Framework web principal
- **PostgreSQL 15** - Sistema de base de datos
- **Django REST Framework 3.14+** - Framework para APIs REST
- **Celery 5.3+ + Redis 7.0+** - Sistema de tareas asíncronas
- **JWT Authentication**
- **Docker / Docker Compose**

### Frontend
- **Flutter** - Lenguaje con tipado estático

### Mobile
- **iOS**: Flutter
- **Android**: Flutter

## Arquitectura

```
Frontend (Flutter)     Mobile Apps (Flutter)
        │                           │
        └─────────┬─────────────────┘
                  │
            Backend API (Django)
                  │
            Database (PostgreSQL)
```

## Entidades del Sistema

### User (Usuario)
> Estructura obligatoria según regla del negocio

- id (UUID)
- full_name (string) — Nombres y Apellidos (obligatorio)
- id_type (enum) — Tipo de identificación (obligatorio)
- id_number (string) — Identificación (obligatorio)
- password_hash (string) — Contraseña o código (obligatorio)
- email_primary (string, unique) — Correo electrónico principal (obligatorio)
- email_secondary (string, nullable) — Correo electrónico opcional
- phone (string) — Celular (obligatorio)
- address (string, nullable) — Dirección residencia (opcional)
- birth_date (date) — Fecha de nacimiento (obligatorio)
- profile_photo_url (string, nullable) — Foto de perfil (opcional)
- role (enum) — ADMIN | CLIENTE | INTERVENTORIA | SUPERVISOR
- status (enum) — ACTIVE | SUSPENDED | PENDING_VERIFICATION
- created_at (datetime)
- updated_at (datetime)
- last_login_at (datetime, nullable)

---

### Role
- id (UUID)
- name (string)
- description (string)

### Permission
- id (UUID)
- code (string)
- description (string)

### RolePermission
- id (UUID)
- role_id (FK → Role)
- permission_id (FK → Permission)

---

### OTPVerification
- id (UUID)
- user_id (FK → User)
- channel (enum) — EMAIL
- code_hash (string)
- expires_at (datetime)
- attempts (int)
- verified_at (datetime, nullable)
- status (enum) — SENT | VERIFIED | EXPIRED | BLOCKED

---

### AccountStatement (Estado de Cuenta)
- id (UUID)
- user_id (FK → User)
- currency (string)
- current_balance (decimal)
- period_start (date)
- period_end (date)
- generated_at (datetime)
- source (enum) — INTERNAL | CASSE

---

### LedgerEntry (Movimiento)
- id (UUID)
- user_id (FK → User)
- type (enum) — DEBIT | CREDIT
- concept (string)
- amount (decimal)
- reference (string)
- created_at (datetime)

---

### Payment (Pago)
- id (UUID)
- user_id (FK → User)
- amount (decimal)
- currency (string)
- method (enum) — PSE | WOMPI
- status (enum) — CREATED | PENDING | PAID | FAILED | CANCELED | REFUNDED
- provider_transaction_id (string, nullable)
- provider_payload (json)
- created_at (datetime)
- paid_at (datetime, nullable)

---

### Receipt (Comprobante)
- id (UUID)
- payment_id (FK → Payment)
- receipt_number (string)
- pdf_url (string)
- sent_to_email_at (datetime, nullable)
- delivery_status (enum) — SENT | FAILED

---

### PaymentProviderConfig
- id (UUID)
- provider (enum) — WOMPI | PSE
- public_key (string)
- private_key (string)
- webhook_secret (string)
- active (boolean)

---

### Policy (Póliza)
- id (UUID)
- policy_number (string)
- user_id (FK → User)
- insurer_id (FK → Insurer)
- product_id (FK → Product)
- status (enum) — ACTIVE | EXPIRED | CANCELED | PENDING
- start_date (date)
- end_date (date)
- premium_amount (decimal)
- coverage_summary (string)
- external_reference (string)
- last_sync_at (datetime, nullable)

---

### PolicyDocument
- id (UUID)
- policy_id (FK → Policy)
- type (enum) — POLICY_PDF | CONDITIONS | RECEIPT
- file_url (string)
- source (enum) — CASSE | EXTERNAL_API | UPLOADED
- created_at (datetime)

---

### Coverage
- id (UUID)
- policy_id (FK → Policy)
- name (string)
- limit_amount (decimal)
- deductible (decimal)
- notes (string, nullable)

---

### Quote (Cotización)
- id (UUID)
- quote_number (string)
- user_id (FK → User)
- product_id (FK → Product)
- insurer_id (FK → Insurer)
- input_data (json)
- result_data (json)
- status (enum) — DRAFT | GENERATED | EXPIRED | CONVERTED
- pdf_url (string, nullable)
- created_at (datetime)

---

### IntegrationProvider
- id (UUID)
- name (string)
- type (enum) — CORE | INSURER_API
- base_url (string)
- auth_type (enum) — API_KEY | OAUTH | BASIC | CERT
- active (boolean)

---

### IntegrationSyncLog
- id (UUID)
- provider_id (FK → IntegrationProvider)
- entity (enum) — POLICY | ACCOUNT | PAYMENT | QUOTE
- status (enum) — SUCCESS | FAILED
- request_payload (json)
- response_payload (json)
- started_at (datetime)
- finished_at (datetime)

---

### NotificationTemplate
- id (UUID)
- code (string)
- channel (enum) — PUSH | EMAIL
- title (string)
- body (string)
- variables_schema (json)

---

### NotificationEvent
- id (UUID)
- user_id (FK → User)
- template_code (string)
- payload (json)
- status (enum) — QUEUED | SENT | FAILED
- sent_at (datetime, nullable)

---

### DeviceToken
- id (UUID)
- user_id (FK → User)
- provider (enum) — FCM | ONESIGNAL
- token (string)
- active (boolean)
- last_seen_at (datetime)

---

### AdminMetricDaily
- id (UUID)
- date (date)
- new_users (int)
- active_users (int)
- payments_total (decimal)
- policies_active (int)
- quotes_generated (int)

---

### ReportExport
- id (UUID)
- requested_by_user_id (FK → User)
- type (enum) — USERS | POLICIES | PAYMENTS | QUOTES
- filters (json)
- status (enum) — GENERATING | READY | FAILED
- file_url (string)
- created_at (datetime)

---

### AuditLog
- id (UUID)
- actor_user_id (FK → User)
- action (string)
- entity (string)
- entity_id (UUID)
- metadata (json)
- ip_address (string)
- created_at (datetime)


## Relaciones entre Entidades

### 1) Usuarios, Roles y Seguridad
- **User (1) → (N) OTPVerification**
  - Un usuario puede tener múltiples OTP (por reintentos, login, verificación, recuperación).

- **Role (N) ↔ (N) Permission** *(vía RolePermission)*
  - Un rol agrupa múltiples permisos.
  - Un permiso puede pertenecer a múltiples roles.

- **Role (1) → (N) RolePermission**
- **Permission (1) → (N) RolePermission**

> Nota: si se usa `User.role` como enum (simple), no se requiere `UserRole`.  
> Si se decide multirol: **User (N) ↔ (N) Role** (vía `UserRole`).

---

### 2) Estados de Cuenta y Movimientos
- **User (1) → (N) AccountStatement**
  - Un usuario tiene múltiples estados de cuenta (por periodos).

- **User (1) → (N) LedgerEntry**
  - Un usuario tiene múltiples movimientos (débitos/créditos).

- *(Opcional, si se desea agrupar por periodos)*  
  **AccountStatement (1) → (N) LedgerEntry**
  - Movimientos asociados a un periodo específico.

---

### 3) Pagos y Comprobantes
- **User (1) → (N) Payment**
  - Un usuario puede realizar múltiples pagos.

- **Payment (1) → (0..1) Receipt**
  - Un pago genera 0 o 1 comprobante PDF (cuando queda confirmado).

- **PaymentProviderConfig**
  - No se relaciona directo por FK con Payment necesariamente.
  - Se usa como configuración activa del proveedor (Wompi/PSE) para operar y validar webhooks.

---

### 4) Pólizas, Documentos y Coberturas
- **User (1) → (N) Policy**
  - Un usuario puede tener múltiples pólizas.

- **Policy (1) → (N) PolicyDocument**
  - Una póliza puede tener múltiples documentos (PDF póliza, condiciones, recibos, etc.).

- **Policy (1) → (N) Coverage**
  - Una póliza tiene múltiples coberturas.

---

### 5) Cotizaciones
- **User (1) → (N) Quote**
  - Un usuario puede generar múltiples cotizaciones.

- *(Opcional)* **Quote (1) → (N) QuoteItem**
  - Si se requiere desglosar items, coberturas o valores.

- **Quote (0..1) → (0..1) Policy**
  - Una cotización puede convertirse en póliza (cuando se emite).
  - Una póliza puede provenir de una cotización (si se guarda ese vínculo).

---

### 6) Catálogos (Aseguradoras y Productos)
- **Insurer (1) → (N) Policy**
- **Product (1) → (N) Policy**
- **Insurer (1) → (N) Quote**
- **Product (1) → (N) Quote**

> (Insurer y Product son catálogos para filtrar, reportar y estandarizar emisiones/cotizaciones.)

---

### 7) Integraciones y Sincronización
- **IntegrationProvider (1) → (N) IntegrationSyncLog**
  - Un proveedor (CASSE / Aseguradora API) genera múltiples logs de sincronización.

- **IntegrationSyncLog** referencia entidades del sistema por `entity` (POLICY/ACCOUNT/PAYMENT/QUOTE)
  - No siempre se modela como FK directa por flexibilidad; suele ser referencia lógica.

- **Policy (0..1) ←→ external_reference (CASSE/API)**
  - La póliza guarda referencia externa para sincronización.

- **AccountStatement / LedgerEntry / Payment / Quote**
  - Pueden tener `reference` o `external_id` para conciliar con CASSE/pasarela.

---

### 8) Notificaciones
- **User (1) → (N) DeviceToken**
  - Un usuario puede tener múltiples tokens (varios dispositivos).

- **NotificationTemplate (1) → (N) NotificationEvent**
  - Un template se usa para múltiples envíos/eventos.

- **User (1) → (N) NotificationEvent**
  - Un usuario puede recibir múltiples notificaciones.

---

### 9) Administración y Reportes
- **User (1) → (N) ReportExport**
  - Un usuario (admin/interventoría/supervisor) puede generar múltiples reportes.

- **AdminMetricDaily**
  - Entidad independiente (agregados diarios).  
  - Puede derivarse de Users/Policies/Payments/Quotes, pero no necesita FK.

---

### 10) Auditoría
- **User (1) → (N) AuditLog** *(actor_user_id)*
  - Un usuario genera múltiples acciones auditables (crear/suspender, pagos, cambios de configuración).

- **AuditLog** referencia entidades afectadas por `entity` y `entity_id`
  - No siempre es FK por ser multi-entidad; se usa referencia flexible.

---
