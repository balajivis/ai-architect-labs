---
title: API Design Guidelines
doc_id: eng-api-design-guidelines
owner: VP Engineering
last_updated: 2026-06-01
status: active
classification: internal
supersedes: ""
supersedes_by: ""
---

# API Design Guidelines

## 1. Overview

Northwind's APIs are RESTful, JSON-based, and designed for consistency, discoverability, and long-term compatibility. All services expose APIs documented in OpenAPI 3.0 format.

## 2. URL Structure

### 2.1 Naming Conventions

- **Resource-based**: `/v1/customers`, `/v1/customers/{id}`, `/v1/customers/{id}/orders`
- **Kebab-case**: `/v1/data-sources`, not `/v1/datasources` or `/v1/DataSources`
- **API versioning**: `/v1/`, `/v2/` (path-based; not header-based)
- **No trailing slashes**: `/v1/customers`, not `/v1/customers/`

### 2.2 HTTP Methods

| Method | Semantics | Idempotent | Cacheable |
|--------|-----------|-----------|-----------|
| GET | Retrieve resource | Yes | Yes |
| POST | Create resource | No | No |
| PUT | Replace entire resource | Yes (if client provides all fields) | No |
| PATCH | Partial update | No | No |
| DELETE | Remove resource | Yes | No |

**Example**:
```
POST   /v1/customers              # Create new customer
GET    /v1/customers/{id}          # Retrieve customer
PUT    /v1/customers/{id}          # Replace customer (all fields required)
PATCH  /v1/customers/{id}          # Update some fields (partial)
DELETE /v1/customers/{id}          # Delete customer
```

## 3. Request/Response Format

### 3.1 Headers

All requests must include:

```
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>
X-Request-ID: <uuid>              # For request tracking (service generates if missing)
```

Optional:
```
X-Idempotency-Key: <uuid>         # For POST requests that should be idempotent
```

### 3.2 Successful Response (2xx)

Status codes and bodies:

```
GET /v1/customers/42
→ 200 OK
{
  "id": "42",
  "email": "alice@example.com",
  "created_at": "2026-01-15T10:30:00Z",
  "links": {
    "self": "/v1/customers/42",
    "orders": "/v1/customers/42/orders"
  }
}

POST /v1/customers
→ 201 Created
Location: /v1/customers/99
{
  "id": "99",
  "email": "bob@example.com",
  ...
}

DELETE /v1/customers/42
→ 204 No Content
(empty body)
```

### 3.3 Error Response (4xx, 5xx)

Consistent error format (RFC 7807 — Problem Details for HTTP APIs):

```
GET /v1/customers/999
→ 404 Not Found
{
  "type": "https://api.northwind.com/errors/not-found",
  "title": "Resource Not Found",
  "status": 404,
  "detail": "Customer with ID 999 does not exist.",
  "instance": "/v1/customers/999",
  "request_id": "req-abc123def456"
}

POST /v1/customers
→ 400 Bad Request
{
  "type": "https://api.northwind.com/errors/validation-error",
  "title": "Validation Failed",
  "status": 400,
  "detail": "Email address is invalid.",
  "instance": "/v1/customers",
  "request_id": "req-xyz789",
  "errors": [
    {
      "field": "email",
      "message": "Must be a valid email address"
    }
  ]
}

PUT /v1/customers/42
→ 409 Conflict
{
  "type": "https://api.northwind.com/errors/conflict",
  "title": "Conflict",
  "status": 409,
  "detail": "Customer has been modified since you last fetched it. Refetch and retry.",
  "instance": "/v1/customers/42"
}
```

### 3.4 Standard Status Codes

| Code | Meaning | When to Use |
|------|---------|-------------|
| 200 | OK | GET success |
| 201 | Created | POST success |
| 204 | No Content | DELETE/PATCH with no response body |
| 400 | Bad Request | Invalid input, validation failed |
| 401 | Unauthorized | Missing/invalid authentication |
| 403 | Forbidden | Authenticated but not authorized (insufficient permissions) |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Concurrent modification, state violation |
| 422 | Unprocessable Entity | Syntax valid but semantic error (e.g., trying to delete in-use resource) |
| 429 | Too Many Requests | Rate limit exceeded (see Rate Limiting section) |
| 500 | Internal Server Error | Unexpected error; never expose implementation details |
| 503 | Service Unavailable | Dependency down (external API, database); client should retry |

## 4. Pagination

For list endpoints returning many results:

```
GET /v1/customers?page=2&page_size=50
→ 200 OK
{
  "data": [
    { "id": "51", "email": "..." },
    { "id": "52", "email": "..." },
    ...
  ],
  "pagination": {
    "page": 2,
    "page_size": 50,
    "total_count": 1250,
    "has_next": true,
    "has_prev": true
  },
  "links": {
    "self": "/v1/customers?page=2&page_size=50",
    "first": "/v1/customers?page=1&page_size=50",
    "prev": "/v1/customers?page=1&page_size=50",
    "next": "/v1/customers?page=3&page_size=50",
    "last": "/v1/customers?page=25&page_size=50"
  }
}
```

**Defaults**: `page=1`, `page_size=20`  
**Maximum**: `page_size=100` (enforce to prevent excessive queries)

## 5. Filtering, Sorting, Searching

### 5.1 Filtering

```
GET /v1/customers?status=active&country=US

GET /v1/orders?created_at[gte]=2026-01-01&created_at[lt]=2026-02-01
```

### 5.2 Sorting

```
GET /v1/customers?sort=email&sort=-created_at
# Sort by email (ascending), then created_at (descending)
```

### 5.3 Field Selection

```
GET /v1/customers/42?fields=id,email,created_at
# Return only id, email, and created_at (reduces payload)
```

## 6. Deprecation and Versioning

### 6.1 Deprecating Fields

Use HTTP header `Deprecation` to signal upcoming field removal:

```
GET /v1/customers/42
→ 200 OK
Deprecation: true
Sunset: Sun, 01 Dec 2026 23:59:59 GMT
Warning: 299 - "legacy_field is deprecated as of 2026-06-01. Use new_field instead. See https://docs.northwind.com/v1/migration"

{
  "id": "42",
  "email": "alice@example.com",
  "legacy_field": "...",  # Old field (marked for removal)
  "new_field": "..."      # Replacement
}
```

**Timeline**: Deprecated fields supported for minimum 6 months; then removed in next major version.

### 6.2 Versioning Strategy

- **Path-based versioning**: `/v1/`, `/v2/` (preferred; clear and explicit)
- **Header-based**: Not recommended (harder to test and debug)
- **Query parameter**: Not recommended (conflicts with filters)

**Sunset dates** in response headers signal version end-of-life:
```
Sunset: Sun, 01 Dec 2027 23:59:59 GMT
```

## 7. Authentication and Authorization

### 7.1 JWT Bearer Token

All requests must provide valid JWT:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Token claims:
{
  "sub": "user-42",
  "aud": "northwind-api",
  "exp": 1234567890,
  "scopes": ["customers:read", "customers:write"]
}
```

See **Secrets Management Standard** for JWT signing key rotation.

### 7.2 Scopes and Permissions

APIs enforce fine-grained permissions:

```
GET /v1/customers/42  # Requires "customers:read" scope
POST /v1/customers    # Requires "customers:write" scope
DELETE /v1/customers/42  # Requires "customers:admin" scope
```

## 8. Rate Limiting

Rate limits prevent abuse and resource exhaustion:

```
GET /v1/customers
→ 200 OK
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1234567890

# After limit exceeded:
→ 429 Too Many Requests
Retry-After: 60
{
  "type": "https://api.northwind.com/errors/rate-limit-exceeded",
  "detail": "You have exceeded 1000 requests per hour. Retry after 60 seconds."
}
```

**Limits by endpoint**: Documented in OpenAPI spec (see **Service Catalog**).

## 9. Documentation

All APIs must be fully documented in OpenAPI 3.0:

```yaml
# openapi.yaml
openapi: 3.0.0
info:
  title: Northwind API
  version: 1.0.0
  contact:
    name: API Support
    url: https://support.northwind.com
paths:
  /v1/customers:
    get:
      summary: List customers
      parameters:
        - name: page
          in: query
          schema: { type: integer, default: 1 }
        - name: page_size
          in: query
          schema: { type: integer, default: 20 }
      responses:
        200:
          description: Success
          content:
            application/json:
              schema: { $ref: '#/components/schemas/CustomerList' }
        401: { $ref: '#/components/responses/UnauthorizedError' }
```

Tools for API documentation:
- **Swagger UI**: Auto-generated from OpenAPI spec
- **Redoc**: Alternative documentation generator
- **Postman**: Import OpenAPI spec for interactive testing

## 10. Observability

All API calls logged and tracked:

- **Request logging**: Every request logged with method, path, status, response time
- **Metrics**: Prometheus counters for requests by endpoint and status code
- **Tracing**: OpenTelemetry traces for end-to-end request tracing (see **Observability & Monitoring Standards**)

---

**Related policies:**
- See **Microservices Architecture Overview** for service communication patterns
- See **Observability & Monitoring Standards** for API monitoring and alerting
- See **Code Review Standards** for API design code review checklist
