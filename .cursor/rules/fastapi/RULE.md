---
description: *.py
alwaysApply: false
---
# Development Rules — Django (DRF) Backend | Insurance Mobile App

You are an expert in Python, Django, and scalable REST API development for a mobile insurance application.

---

## Project Context (Mandatory)
Backend for an iOS/Android insurance app that allows users to:
- Register and authenticate using JWT + email OTP
- Manage roles: ADMIN, CLIENT, INTERVENTORIA, SUPERVISOR
- View account statements and make payments (PSE / Wompi)
- Manage insurance policies (view, download PDF, quote, issue)
- Integrate with external core systems (CASSE / insurer APIs)
- Receive notifications (email / push – optional)
- Access administrative dashboards and reports (CSV / PDF)
- Maintain full auditability of sensitive operations

This project prioritizes **security, clarity, maintainability, and correctness** over premature optimization or unnecessary features.

---

## Core Principles
- Write concise, technical responses with accurate Python examples when needed.
- Avoid code duplication through modularization by domain.
- Prefer **functions for business logic** and **classes where they are natural**:
  - Django ORM Models → classes
  - DRF Serializers → classes
  - ViewSets / APIViews → classes
  - Services / integrations → functions or thin classes (use judgment, not dogma)
- Use descriptive variable names with auxiliary verbs:
  - `is_active`, `has_permission`, `should_sync`, `can_issue_policy`
- Use `snake_case` for directories and files  
  Example: `apps/policies/services/sync_policies.py`
- Keep the product focused on **core insurance functionality only**.

---

## Technology Stack
- Django 5.x
- Django REST Framework
- PostgreSQL
- Celery + Redis (async/background jobs)
- JWT authentication (e.g. SimpleJWT)
- Email service for OTP and receipts
- File storage (local or S3-compatible)
- Payment gateways: Wompi / PSE
- External integrations: CASSE / insurer APIs (when allowed)

---

## Recommended Project Structure
Organize by **domain-first architecture**:

backend/
├── app/ # settings, urls, asgi/wsgi
├── apps/
│ ├── users/
│ │ ├── models.py
│ │ ├── serializers.py
│ │ ├── views.py # ViewSets / APIViews
│ │ ├── permissions.py
│ │ ├── services/ # business logic
│ │ ├── selectors/ # read-only queries
│ │ ├── urls.py
│ │ └── tests/
│ ├── authn/ # JWT, OTP, password recovery
│ ├── accounts/ # account statements & ledger
│ ├── payments/ # payments, webhooks, receipts
│ ├── policies/ # policies, coverages, documents
│ ├── quotes/ # quotations & issuance
│ ├── integrations/ # CASSE / external APIs
│ ├── notifications/ # email & push
│ ├── reports/ # exports & dashboards
│ ├── audit/ # audit logs
│ └── common/ # shared utilities & constants
└── manage.py


---

## Django & DRF Guidelines
- Use **APIView / ViewSet** for HTTP layer only.
- Keep views thin; move logic to `services/`.
- Use **Serializers** for validation and response schemas.
- Use **selectors** for read-heavy queries to keep services clean.
- Prefer explicit imports and clear naming over magic abstractions.
- Keep URLs RESTful and versioned if needed.

---

## Error Handling & Validation
- Validate inputs in serializers first.
- Use **guard clauses** in services:
  - Handle invalid states early.
  - Return or raise immediately on error.
- Avoid deeply nested `if/else`.
- Favor:
  ```python
  if not is_valid:
      raise ValidationError(...)```

- Place the **happy path last** in the function.

- Use DRF exceptions for expected errors:
  - `ValidationError`
  - `PermissionDenied`
  - `NotFound`

- Always return consistent, user-friendly error messages.

---

## Security Rules (Mandatory)

- Store passwords using strong hashing algorithms (Argon2 or bcrypt).
- Enforce OTP verification before granting full access.
- Rate-limit OTP requests and login attempts.
- Use JWT access + refresh tokens.
- Protect admin and financial endpoints with role-based permissions.
- Never trust client-side state for:
  - Payments
  - Policy status
  - Account balances

---

## Payments & Webhooks

- All payment confirmations must be validated server-side.
- Implement idempotency for webhooks:
  - Store provider event IDs as unique.
  - Ignore duplicate webhook events safely.
- Persist raw webhook payloads for audit and debugging.
- Update balances and ledger entries atomically (database transactions).

---

## Integrations (CASSE / External APIs)

- Treat all external systems as unreliable by default.
- Implement retries and request timeouts.
- Log every synchronization attempt:
  - Request payload
  - Response payload
- Never block user-facing requests with long-running sync operations.
- Use Celery for background synchronization tasks.
- Store external references for reconciliation and traceability.

---

## Auditing & Traceability

- Log all sensitive actions, including:
  - User suspension
  - Role changes
  - Payment confirmation
  - Policy synchronization or issuance
  - Configuration changes

- Audit logs must include:
  - Actor user
  - Action performed
  - Target entity and entity ID
  - Timestamp
  - Metadata (JSON)

---

## Performance & Maintainability

- Use `select_related` and `prefetch_related` to avoid N+1 queries.
- Paginate all list endpoints.
- Avoid heavy computations inside views.
- Cache static or rarely changing data where appropriate.
- Prefer clarity and correctness over micro-optimizations.

---

## Non-Goals (Explicit)

- No chat systems
- No real-time tracking
- No social features
- No non-insurance-related functionality

---

---

## Data Model Rules (Mandatory)

- All user fields must match the business-required structure:
  - `full_name` (required)
  - `id_type` (required)
  - `id_number` (required)
  - `password_hash` (required; never store plain passwords)
  - `email_primary` (required, unique)
  - `email_secondary` (optional)
  - `phone` (required)
  - `address` (optional)
  - `birth_date` (required)
  - `profile_photo_url` (optional)

- Enforce uniqueness constraints:
  - `email_primary` unique
  - (recommended) `id_type + id_number` unique

- Use enums/choices for status fields:
  - `user.status`, `payment.status`, `policy.status`, `quote.status`

---

## Transactions & Consistency

- Use database transactions for multi-step operations:
  - Payment confirmation + ledger update + receipt creation
  - Policy issuance + document creation + audit log
- Favor `select_for_update()` where race conditions can occur (e.g. balance updates).

---

## Idempotency & Webhook Processing (Mandatory)

- Store all webhook events in `webhook_event` with:
  - `provider` (WOMPI/PSE)
  - `event_id` (unique)
  - `payload` (json)
  - `received_at`
  - `processed_at` (nullable)
  - `status` (RECEIVED/PROCESSED/FAILED)

- Webhook handlers must:
  - Validate signature (if provider supports it)
  - Be idempotent (ignore already processed events)
  - Never trust payment status from client

---

## Background Jobs (Celery) Rules

- Use Celery for long-running tasks:
  - CASSE sync (policies, statements)
  - Sending emails (OTP, receipts)
  - Report generation (CSV/PDF)
  - Push notification dispatch

- Never call external APIs directly inside request/response when it can exceed timeouts.

---

## API Contracts & Versioning

- All endpoints must live under a versioned prefix:
  - `/api/v1/...`

- Use consistent response shapes:
  - Success responses return predictable objects
  - Error responses return `{ "detail": "..." }` (DRF standard)

- Use pagination for list endpoints (mandatory).

---

## Permissions & Access Control (Mandatory)

- Enforce role-based access:
  - ADMIN: full access to admin endpoints
  - CLIENT: only own policies, own statements, own payments
  - INTERVENTORIA/SUPERVISOR: read-only or restricted admin views (define explicitly)

- Always filter queries by the authenticated user unless role explicitly allows broader access.

---

## Logging & Monitoring

- Log every critical flow with correlation IDs:
  - login/OTP verification attempts
  - payment creation + webhook confirmations
  - CASSE sync requests

- Never log secrets:
  - JWT tokens
  - OTP codes
  - payment provider keys
  - passwords

---

## Configuration & Secrets

- All secrets must come from environment variables:
  - `SECRET_KEY`, `DATABASE_URL`, `JWT_KEYS`, `EMAIL_*`, `WOMPI_*`, `PSE_*`, `CASSE_*`

- Provide `.env.example` with placeholders (never commit real secrets).

---

## Testing Rules (Minimum)

- Add tests for critical paths:
  - OTP verify flow (success, expired, max attempts)
  - payment webhook idempotency
  - permission boundaries (client cannot read another client’s policies)
  - CASSE sync failure handling

---

## Guiding Rule

> If a feature is not explicitly required by the insurance scope, do not implement it.
This backend must remain secure, auditable, and predictable above all else.
