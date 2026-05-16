# 09 - Lambda Specification: TripGroupFunction

## 1. Function Name

```text
TripGroupFunction
```

---

## 2. Purpose

This Lambda manages trip group core operations:

- Create trip
- List current user's trips
- Get trip detail
- Update trip metadata
- List trip members

---

## 3. API Routes

| Method | Path |
|---|---|
| `POST` | `/trips` |
| `GET` | `/trips` |
| `GET` | `/trips/{tripId}` |
| `PATCH` | `/trips/{tripId}` |
| `GET` | `/trips/{tripId}/members` |

---

## 4. Data Tables Used

| Table | Operation |
|---|---|
| `users` | Read / lazy create current user |
| `trips` | Create / read / update |
| `trip_members` | Create owner membership / authorization / listing |

---

## 5. Required Shared Helpers

Claude Code should reuse shared modules:

```text
common/auth.py
common/db.py
common/response.py
common/errors.py
common/validation.py
```

---

## 6. Authorization Rules

| Operation | Rule |
|---|---|
| Create trip | Any authenticated user |
| List trips | Current user's memberships only |
| Get trip detail | Must be trip member |
| Update trip | Owner only |
| List members | Must be trip member |

---

## 7. Core Implementation Notes

### 7.1 Current User Resolution

The function must:

1. Extract Cognito `sub`
2. Resolve corresponding row from `users`
3. Create user row if not found, according to shared user bootstrap logic

### 7.2 Create Trip Must Be Transactional

Creating a trip requires:

1. Insert into `trips`
2. Insert into `trip_members` with role `owner`

These two operations must occur in a single transaction.

### 7.3 Trip Detail Query

Trip detail should include lightweight summary counts if feasible:

- member count
- candidate count
- itinerary item count

These counts support the frontend overview page.

### 7.4 Date Validation

Trip creation and update must validate:

```text
start_date <= end_date
```

---

## 8. Recommended Handler Internal Structure

```text
lambda_handler
  ├── parse_http_event
  ├── route dispatch
  │   ├── create_trip
  │   ├── list_trips
  │   ├── get_trip_detail
  │   ├── update_trip
  │   └── list_trip_members
  └── standardized response/error handling
```

---

## 9. Expected Error Conditions

| Error | Expected Handling |
|---|---|
| Missing required field | `400 VALIDATION_ERROR` |
| Invalid date range | `400 VALIDATION_ERROR` |
| Trip not found | `404 NOT_FOUND` |
| Non-member access | `403 FORBIDDEN` |
| Non-owner update | `403 FORBIDDEN` |

---

## 10. Logging Requirements

Log:

- Request ID
- Route
- User ID
- Trip ID when relevant
- Operation success/failure

Do not log:

- Raw JWT
- Full user token claims unnecessarily

---

# 11. SAM Test Planning

## 11.1 Unit Tests

Create unit tests for:

- Request validation
- Date validation
- Owner authorization
- Member authorization
- Create-trip transaction service logic

## 11.2 Local SAM API Tests

Use:

```bash
sam build
sam local start-api --env-vars env.local.json
```

Suggested test calls:

```bash
curl -X POST http://127.0.0.1:3000/trips \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Tokyo Trip",
    "destination": "Tokyo, Japan",
    "start_date": "2026-08-20",
    "end_date": "2026-08-25"
  }'
```

Actual deployed JWT authorizer behavior must be tested after AWS deployment.
Local tests may use a development auth stub or prebuilt event claims where appropriate.

## 11.3 Suggested SAM Event Files

```text
events/trip/create-trip.json
events/trip/list-trips.json
events/trip/get-trip-detail.json
events/trip/update-trip.json
events/trip/list-members.json
```

## 11.4 Direct Lambda Invoke Tests

```bash
sam local invoke TripGroupFunction \
  -e events/trip/create-trip.json \
  --env-vars env.local.json
```