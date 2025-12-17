# API Documentation - Insurance Backend

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Most endpoints require authentication via the `Authorization` header:

```
Authorization: Bearer <access_token>
```

Access tokens expire after 15 minutes. Use the refresh token endpoint to obtain a new access token.

## Endpoints

### Health Check

#### GET /health/

Check the health status of the service and database connectivity.

**Request:**
```
GET /api/v1/health/
```

**Response 200 OK:**
```json
{
  "status": "ok",
  "service": "insurance-backend",
  "version": "v1",
  "database": "ok"
}
```

**Response 503 Service Unavailable:**
```json
{
  "status": "error",
  "service": "insurance-backend",
  "version": "v1",
  "database": "error"
}
```

---

### Authentication

#### POST /auth/register/

Register a new user account. Creates a user with role CLIENT by default.

**Request:**
```
POST /api/v1/auth/register/
Content-Type: application/json
```

**Request Body:**
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
  "profile_photo_url": "https://example.com/photo.jpg"
}
```

**Required Fields:**
- `full_name`: Full name of the user
- `id_type`: Type of identification (CC, CE, NIT, PASSPORT, TI)
- `id_number`: Identification number
- `email_primary`: Primary email address (must be unique)
- `phone`: Phone number
- `birth_date`: Date of birth (YYYY-MM-DD format)
- `password`: Password (minimum 8 characters, must meet validation requirements)

**Optional Fields:**
- `email_secondary`: Secondary email address
- `address`: Physical address
- `profile_photo_url`: URL to profile photo

**Response 201 Created:**
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
  "profile_photo_url": "https://example.com/photo.jpg",
  "role": "CLIENT",
  "status": "ACTIVE",
  "created_at": "2025-12-16T15:20:00-05:00",
  "updated_at": "2025-12-16T15:20:00-05:00",
  "last_login_at": null
}
```

**Response 400 Bad Request:**
```json
{
  "email_primary": ["Ya existe un/a Usuario con este/a Email Principal."]
}
```

---

#### POST /auth/login/

Authenticate a user and receive JWT tokens.

**Request:**
```
POST /api/v1/auth/login/
Content-Type: application/json
```

**Request Body:**
```json
{
  "email_primary": "juan@example.com",
  "password": "Str0ngPassword!2025"
}
```

**Response 200 OK:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "0b6e1f0f-8e51-4a19-9c2e-1d7ff2b4ef54",
    "email_primary": "juan@example.com",
    "full_name": "Juan Pérez",
    "role": "CLIENT",
    "status": "ACTIVE"
  }
}
```

**Response 401 Unauthorized:**
```json
{
  "non_field_errors": ["Credenciales inválidas"]
}
```

**Response 403 Forbidden:**
```json
{
  "detail": "Usuario suspendido"
}
```

**Rate Limiting:** 5 login attempts per minute per IP address.

---

#### POST /auth/jwt/refresh/

Refresh an access token using a refresh token.

**Request:**
```
POST /api/v1/auth/jwt/refresh/
Content-Type: application/json
```

**Request Body:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response 200 OK:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response 401 Unauthorized:**
```json
{
  "detail": "Token is invalid or expired"
}
```

---

### Users

All user endpoints require authentication. Include the access token in the Authorization header.

#### GET /users/me/

Get the authenticated user's profile information.

**Request:**
```
GET /api/v1/users/me/
Authorization: Bearer <access_token>
```

**Response 200 OK:**
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
  "profile_photo_url": "https://example.com/photo.jpg",
  "role": "CLIENT",
  "status": "ACTIVE",
  "created_at": "2025-12-16T15:20:00-05:00",
  "updated_at": "2025-12-16T15:20:00-05:00",
  "last_login_at": "2025-12-16T15:21:00-05:00"
}
```

---

#### PATCH /users/me/

Update the authenticated user's profile. Only certain fields can be updated by the user.

**Request:**
```
PATCH /api/v1/users/me/
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "phone": "3009998888",
  "address": "Nueva dirección",
  "email_secondary": "nuevo.alt@example.com",
  "profile_photo_url": "https://new-photo.com/photo.jpg",
  "password": "NewPassword123!@#"
}
```

**Allowed Fields for Self-Update:**
- `full_name`
- `phone`
- `address`
- `email_secondary`
- `profile_photo_url`
- `password`

**Prohibited Fields:**
- `role`
- `status`
- `email_primary`
- `id_type`
- `id_number`
- `birth_date`

**Response 200 OK:**
Returns the updated user object.

**Response 400 Bad Request:**
```json
{
  "detail": "No hay campos válidos para actualizar"
}
```

---

#### GET /users/

List users with optional filtering and pagination. Requires ADMIN, SUPERVISOR, or INTERVENTORIA role.

**Request:**
```
GET /api/v1/users/?role=CLIENT&status=ACTIVE&search=juan&page=1
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `role`: Filter by role (ADMIN, CLIENT, INTERVENTORIA, SUPERVISOR)
- `status`: Filter by status (ACTIVE, SUSPENDED)
- `search`: Search in full_name, email_primary, id_number, phone
- `page`: Page number for pagination (default: 1)

**Response 200 OK:**
```json
{
  "count": 120,
  "next": "http://localhost:8000/api/v1/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": "0b6e1f0f-8e51-4a19-9c2e-1d7ff2b4ef54",
      "full_name": "Juan Pérez",
      "email_primary": "juan@example.com",
      "phone": "3001234567",
      "role": "CLIENT",
      "status": "ACTIVE",
      "created_at": "2025-12-16T15:20:00-05:00",
      "updated_at": "2025-12-16T15:20:00-05:00",
      "last_login_at": null
    }
  ]
}
```

**Response 403 Forbidden:**
```json
{
  "detail": "No tiene permisos para listar usuarios"
}
```

---

#### POST /users/

Create a new user. Requires ADMIN role.

**Request:**
```
POST /api/v1/users/
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
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

**Response 201 Created:**
Returns the complete user object.

**Response 403 Forbidden:**
```json
{
  "detail": "Solo los administradores pueden crear usuarios"
}
```

---

#### GET /users/{id}/

Get a specific user by ID. Access depends on the requesting user's role.

**Request:**
```
GET /api/v1/users/{id}/
Authorization: Bearer <access_token>
```

**Response 200 OK:**
Returns user object. Fields shown depend on the requesting user's role:
- ADMIN, SUPERVISOR, INTERVENTORIA: Full user details
- CLIENT: Only own profile or limited fields for other users

**Response 404 Not Found:**
```json
{
  "detail": "Usuario no encontrado"
}
```

---

#### PATCH /users/{id}/

Update a user by ID. Requires ADMIN role.

**Request:**
```
PATCH /api/v1/users/{id}/
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "role": "CLIENT",
  "status": "SUSPENDED",
  "phone": "3011111111",
  "password": "NewPassword123!@#"
}
```

**Response 200 OK:**
Returns the updated user object.

**Response 403 Forbidden:**
```json
{
  "detail": "Solo los administradores pueden actualizar usuarios"
}
```

---

#### POST /users/{id}/suspend/

Suspend a user account. Requires ADMIN role.

**Request:**
```
POST /api/v1/users/{id}/suspend/
Authorization: Bearer <access_token>
```

**Response 200 OK:**
```json
{
  "detail": "Usuario suspendido exitosamente"
}
```

**Response 403 Forbidden:**
```json
{
  "detail": "Solo los administradores pueden suspender usuarios"
}
```

---

#### POST /users/{id}/activate/

Activate a suspended user account. Requires ADMIN role.

**Request:**
```
POST /api/v1/users/{id}/activate/
Authorization: Bearer <access_token>
```

**Response 200 OK:**
```json
{
  "detail": "Usuario activado exitosamente"
}
```

**Response 403 Forbidden:**
```json
{
  "detail": "Solo los administradores pueden activar usuarios"
}
```

---

## Permissions Matrix

| Endpoint | ADMIN | SUPERVISOR | INTERVENTORIA | CLIENT |
|----------|-------|------------|---------------|--------|
| GET /users/me | Yes | Yes | Yes | Yes |
| PATCH /users/me | Yes | Yes | Yes | Yes (limited fields) |
| GET /users/ | Yes | Yes | Yes | No |
| POST /users/ | Yes | No | No | No |
| GET /users/{id} | Yes | Yes (read-only) | Yes (read-only) | Yes (own profile only) |
| PATCH /users/{id} | Yes | No | No | No |
| POST /users/{id}/suspend | Yes | No | No | No |
| POST /users/{id}/activate | Yes | No | No | No |

## Error Responses

All error responses follow a consistent format:

**400 Bad Request:**
```json
{
  "field_name": ["Error message"],
  "non_field_errors": ["General error message"]
}
```

**401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**404 Not Found:**
```json
{
  "detail": "Not found."
}
```

**500 Internal Server Error:**
```json
{
  "detail": "A server error occurred."
}
```

## Rate Limiting

- Anonymous users: 100 requests per hour
- Authenticated users: 1000 requests per hour
- Login endpoint: 5 attempts per minute per IP address

## Correlation ID

All responses include an `X-Correlation-ID` header for request tracking and debugging.

## Notes

- All timestamps are in ISO 8601 format with timezone
- UUIDs are used for all resource IDs
- Passwords must meet Django's password validation requirements (minimum 8 characters, not too common, etc.)
- The password hashing algorithm uses Argon2 by default
- All user actions are logged in the audit system

