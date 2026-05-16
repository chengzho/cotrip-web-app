# 03 - API Specification: Trip and Member

## 1. Purpose

This document specifies APIs handled by:

```text
TripGroupFunction
```

The trip and member domain allows authenticated users to:

- Create a new trip group
- List trips they belong to
- View trip details
- Update core trip metadata
- View the members of a trip

---

# 2. Endpoint Summary

| Method | Path | Description |
|---|---|---|
| `POST` | `/trips` | Create a new trip |
| `GET` | `/trips` | List current user's trips |
| `GET` | `/trips/{tripId}` | Get trip detail |
| `PATCH` | `/trips/{tripId}` | Update trip metadata |
| `GET` | `/trips/{tripId}/members` | List trip members |

---

# 3. Shared Authorization Policy

All endpoints in this document require authentication.

Requests must include:

```http
Authorization: Bearer <JWT>
```

The JWT is issued by Amazon Cognito and validated by API Gateway HTTP API JWT Authorizer.

---

# 4. POST `/trips`

## 4.1 Description

Create a new trip group.

The authenticated user becomes the owner of the trip.

---

## 4.2 Authentication

Required.

---

## 4.3 Authorization

Any authenticated user may create a trip.

---

## 4.4 Request Body

| Field | Type | Required | Notes |
|---|---|---|---|
| `title` | string | Required | Trip title |
| `destination` | string | Required | Destination text |
| `start_date` | string | Required | Format: `YYYY-MM-DD` |
| `end_date` | string | Required | Format: `YYYY-MM-DD` |
| `description` | string | Optional | Optional trip description |

---

## 4.5 Validation Rules

- `title` must not be empty.
- `destination` must not be empty.
- `start_date` must be a valid date string.
- `end_date` must be a valid date string.
- `start_date <= end_date`.
- `description`, if provided, may be empty only if the final backend policy allows it.

---

## 4.6 Transaction Requirement

Trip creation must be transactional.

The backend must complete both operations together:

1. Insert the new row into `trips`.
2. Insert the authenticated user into `trip_members` with:

```text
role = owner
```

If either operation fails, the transaction must roll back.

---

## 4.7 Example Request

```json
{
  "title": "Tokyo Spring Trip",
  "destination": "Tokyo, Japan",
  "start_date": "2026-04-10",
  "end_date": "2026-04-15",
  "description": "A spring trip planned with friends."
}
```

---

## 4.8 Success Response

Status:

```text
201 Created
```

```json
{
  "success": true,
  "data": {
    "trip": {
      "trip_id": "trip-uuid",
      "title": "Tokyo Spring Trip",
      "destination": "Tokyo, Japan",
      "start_date": "2026-04-10",
      "end_date": "2026-04-15",
      "description": "A spring trip planned with friends.",
      "role": "owner",
      "created_at": "2026-03-01T10:00:00+08:00",
      "updated_at": "2026-03-01T10:00:00+08:00"
    }
  },
  "error": null,
  "request_id": "request-id"
}
```

---

## 4.9 Expected Error Cases

| Scenario | Status | Error Code |
|---|---|---|
| Missing required field | `400` | `VALIDATION_ERROR` |
| Empty title | `400` | `VALIDATION_ERROR` |
| Empty destination | `400` | `VALIDATION_ERROR` |
| Invalid date format | `400` | `VALIDATION_ERROR` |
| `start_date > end_date` | `400` | `VALIDATION_ERROR` |

---

# 5. GET `/trips`

## 5.1 Description

Return trips that the authenticated user belongs to.

The endpoint supports an optional `scope` query parameter to filter trips by their lifecycle state.

---

## 5.2 Authentication

Required.

---

## 5.3 Authorization

The backend must return only trips where the authenticated user exists in:

```text
trip_members
```

---

## 5.4 Query Parameters

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `scope` | string | Optional | Allowed values: `upcoming`, `past`, `all`. Default: `upcoming`. |

---

## 5.5 Scope Filtering Semantics

The `scope` parameter must use the following exact rules:

```text
upcoming = trips where end_date >= CURRENT_DATE
past     = trips where end_date < CURRENT_DATE
all      = no date-based filtering
```

The comparison is based on the trip's:

```text
end_date
```

not `start_date`.

This means:

- A trip that has already started but has not yet ended is still considered `upcoming`.
- A trip becomes `past` only after its `end_date` is earlier than the current date.
- `all` returns both upcoming and past trips without a date-based WHERE condition.

---

## 5.6 Default Scope

If the client does not provide a `scope` query parameter, the backend must behave as:

```text
scope = upcoming
```

---

## 5.7 Validation Rules

If `scope` is provided, it must be one of:

```text
upcoming
past
all
```

Any other value must return:

```text
400 VALIDATION_ERROR
```

---

## 5.8 Recommended Sorting

The backend should sort returned trips in a user-friendly order.

Recommended MVP behavior:

### For `upcoming`
Sort by:

```text
start_date ASC
```

### For `past`
Sort by:

```text
end_date DESC
```

### For `all`
A reasonable implementation may sort by:

```text
start_date ASC
```

or use a clearly documented alternative if later changed.

---

## 5.9 Example Request

```http
GET /trips?scope=upcoming
```

---

## 5.10 Success Response

Status:

```text
200 OK
```

```json
{
  "success": true,
  "data": {
    "trips": [
      {
        "trip_id": "trip-uuid-1",
        "title": "Tokyo Spring Trip",
        "destination": "Tokyo, Japan",
        "start_date": "2026-04-10",
        "end_date": "2026-04-15",
        "role": "owner",
        "member_count": 4,
        "candidate_count": 12,
        "itinerary_item_count": 16
      },
      {
        "trip_id": "trip-uuid-2",
        "title": "Lisbon Weekend",
        "destination": "Lisbon, Portugal",
        "start_date": "2026-07-03",
        "end_date": "2026-07-05",
        "role": "member",
        "member_count": 3,
        "candidate_count": 8,
        "itinerary_item_count": 0
      }
    ]
  },
  "error": null,
  "request_id": "request-id"
}
```

---

## 5.11 Empty Response

If the authenticated user has no trips matching the requested scope, return:

```text
200 OK
```

```json
{
  "success": true,
  "data": {
    "trips": []
  },
  "error": null,
  "request_id": "request-id"
}
```

---

## 5.12 Expected Error Cases

| Scenario | Status | Error Code |
|---|---|---|
| Unsupported `scope` value | `400` | `VALIDATION_ERROR` |

---

# 6. GET `/trips/{tripId}`

## 6.1 Description

Return the detail of one trip.

This endpoint should provide the frontend with core trip metadata and lightweight summary counts used by the workspace overview page.

---

## 6.2 Authentication

Required.

---

## 6.3 Authorization

The authenticated user must be a member of the target trip.

---

## 6.4 Path Parameters

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `tripId` | UUID string | Required | Target trip identifier |

---

## 6.5 Success Response

Status:

```text
200 OK
```

```json
{
  "success": true,
  "data": {
    "trip": {
      "trip_id": "trip-uuid",
      "title": "Tokyo Spring Trip",
      "destination": "Tokyo, Japan",
      "start_date": "2026-04-10",
      "end_date": "2026-04-15",
      "description": "A spring trip planned with friends.",
      "current_user_role": "owner",
      "summary": {
        "member_count": 4,
        "candidate_count": 12,
        "vote_count": 31,
        "itinerary_item_count": 16
      },
      "created_at": "2026-03-01T10:00:00+08:00",
      "updated_at": "2026-03-01T10:00:00+08:00"
    }
  },
  "error": null,
  "request_id": "request-id"
}
```

---

## 6.6 Expected Error Cases

| Scenario | Status | Error Code |
|---|---|---|
| Trip not found | `404` | `NOT_FOUND` |
| User not a trip member | `403` | `FORBIDDEN` |

---

# 7. PATCH `/trips/{tripId}`

## 7.1 Description

Update core trip metadata.

Only the trip owner may perform this operation.

---

## 7.2 Authentication

Required.

---

## 7.3 Authorization

The authenticated user must be:

```text
owner
```

of the target trip.

---

## 7.4 Path Parameters

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `tripId` | UUID string | Required | Target trip identifier |

---

## 7.5 Request Body

At least one editable field must be provided.

| Field | Type | Required | Notes |
|---|---|---|---|
| `title` | string | Optional | Updated trip title |
| `destination` | string | Optional | Updated destination text |
| `start_date` | string | Optional | Format: `YYYY-MM-DD` |
| `end_date` | string | Optional | Format: `YYYY-MM-DD` |
| `description` | string | Optional | Updated optional description |

---

## 7.6 Validation Rules

- Request body must not be empty.
- `title`, if provided, must not be empty.
- `destination`, if provided, must not be empty.
- `start_date`, if provided, must be a valid date string.
- `end_date`, if provided, must be a valid date string.
- The resulting trip date range must satisfy:

```text
start_date <= end_date
```

This validation must consider both updated and existing stored values.

Example:

- If only `end_date` is updated, compare it with the current stored `start_date`.
- If only `start_date` is updated, compare it with the current stored `end_date`.

---

## 7.7 Example Request

```json
{
  "title": "Tokyo & Kyoto Spring Trip",
  "end_date": "2026-04-17",
  "description": "Updated plan after extending the trip."
}
```

---

## 7.8 Success Response

Status:

```text
200 OK
```

```json
{
  "success": true,
  "data": {
    "trip": {
      "trip_id": "trip-uuid",
      "title": "Tokyo & Kyoto Spring Trip",
      "destination": "Tokyo, Japan",
      "start_date": "2026-04-10",
      "end_date": "2026-04-17",
      "description": "Updated plan after extending the trip.",
      "updated_at": "2026-03-02T14:30:00+08:00"
    }
  },
  "error": null,
  "request_id": "request-id"
}
```

---

## 7.9 Expected Error Cases

| Scenario | Status | Error Code |
|---|---|---|
| Trip not found | `404` | `NOT_FOUND` |
| User not trip owner | `403` | `FORBIDDEN` |
| Empty PATCH body | `400` | `VALIDATION_ERROR` |
| Empty title | `400` | `VALIDATION_ERROR` |
| Empty destination | `400` | `VALIDATION_ERROR` |
| Invalid date format | `400` | `VALIDATION_ERROR` |
| Resulting `start_date > end_date` | `400` | `VALIDATION_ERROR` |

---

# 8. GET `/trips/{tripId}/members`

## 8.1 Description

Return the members of a trip.

---

## 8.2 Authentication

Required.

---

## 8.3 Authorization

The authenticated user must be a member of the target trip.

---

## 8.4 Path Parameters

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `tripId` | UUID string | Required | Target trip identifier |

---

## 8.5 Success Response

Status:

```text
200 OK
```

```json
{
  "success": true,
  "data": {
    "members": [
      {
        "user_id": "user-uuid-1",
        "display_name": "Sophie Lin",
        "email": "sophie@example.com",
        "role": "owner",
        "joined_at": "2026-03-01T10:00:00+08:00"
      },
      {
        "user_id": "user-uuid-2",
        "display_name": "Marcus Chen",
        "email": "marcus@example.com",
        "role": "member",
        "joined_at": "2026-03-03T09:15:00+08:00"
      }
    ]
  },
  "error": null,
  "request_id": "request-id"
}
```

---

## 8.6 Empty Member List Policy

A valid trip should always contain at least one member: its owner.

Therefore, an empty `members` array would normally indicate unexpected data inconsistency and should not occur during normal MVP behavior.

---

## 8.7 Expected Error Cases

| Scenario | Status | Error Code |
|---|---|---|
| Trip not found | `404` | `NOT_FOUND` |
| User not a trip member | `403` | `FORBIDDEN` |

---

# 9. Frontend Integration Notes

## 9.1 Dashboard Trip List

The frontend dashboard may call:

```http
GET /trips?scope=upcoming
```

to render the default “My Trips” dashboard state.

Optional UI extensions may later allow switching between:

- Upcoming trips
- Past trips
- All trips

---

## 9.2 Workspace Overview

The trip detail endpoint:

```http
GET /trips/{tripId}
```

provides summary counts that support:

- overview metric cards
- quick status display
- lightweight workspace context

---

## 9.3 Settings Page

The settings page should call:

```http
PATCH /trips/{tripId}
```

and is owner-only according to the MVP authorization policy.

---

# 10. Trip and Member MVP Scope Summary

The CoTrip MVP trip/member API includes:

| Capability | Included? |
|---|---|
| Create trip | Yes |
| List current user's trips | Yes |
| Filter trip list by `scope` | Yes |
| Get trip detail | Yes |
| Update trip metadata | Yes |
| List trip members | Yes |
| Delete trip | No |
| Remove member | No |
| Change member role | No |

The `/trips?scope=` behavior is formally defined as:

```text
upcoming = end_date >= CURRENT_DATE
past     = end_date < CURRENT_DATE
all      = no date-based filtering
```