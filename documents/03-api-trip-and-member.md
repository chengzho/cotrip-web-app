# 03 - API Specification: Trip and Member

## 1. Purpose

This document specifies APIs handled by:

```text
TripGroupFunction
```

The function covers:

- Create a trip
- List current user's trips
- Retrieve trip details
- Update trip metadata
- List trip members

---

# 2. Endpoint Summary

| Method | Path | Description |
|---|---|---|
| `POST` | `/trips` | Create a new trip |
| `GET` | `/trips` | List trips for current user |
| `GET` | `/trips/{tripId}` | Get trip detail |
| `PATCH` | `/trips/{tripId}` | Update trip metadata |
| `GET` | `/trips/{tripId}/members` | List trip members |

---

# 3. POST `/trips`

## 3.1 Description

Create a new trip and automatically add the authenticated user as the trip owner.

## 3.2 Authentication

Required.

## 3.3 Request Body

| Field | Type | Required | Notes |
|---|---|---|---|
| `title` | string | Required | Trip name |
| `destination` | string | Required | Destination city/country |
| `start_date` | string | Required | Format: `YYYY-MM-DD` |
| `end_date` | string | Required | Format: `YYYY-MM-DD` |
| `description` | string | Optional | Short notes |

## 3.4 Validation Rules

- `title` must not be empty.
- `destination` must not be empty.
- `start_date` must be valid.
- `end_date` must be valid.
- `start_date <= end_date`.

## 3.5 Example Request

```json
{
  "title": "Tokyo Graduation Trip",
  "destination": "Tokyo, Japan",
  "start_date": "2026-08-20",
  "end_date": "2026-08-25",
  "description": "A group trip after graduation."
}
```

## 3.6 Success Response

Status:

```text
201 Created
```

```json
{
  "success": true,
  "data": {
    "trip": {
      "id": "trip-uuid",
      "title": "Tokyo Graduation Trip",
      "destination": "Tokyo, Japan",
      "start_date": "2026-08-20",
      "end_date": "2026-08-25",
      "description": "A group trip after graduation.",
      "created_by": "user-uuid",
      "current_user_role": "owner"
    }
  },
  "error": null,
  "request_id": "request-id"
}
```

---

# 4. GET `/trips`

## 4.1 Description

Return trips joined by the current authenticated user.

## 4.2 Authentication

Required.

## 4.3 Query Parameters

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `scope` | string | Optional | `upcoming`, `past`, or `all`; default: `all` |

## 4.4 Example Request

```text
GET /trips?scope=upcoming
```

## 4.5 Success Response

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
        "id": "trip-uuid",
        "title": "Tokyo Graduation Trip",
        "destination": "Tokyo, Japan",
        "start_date": "2026-08-20",
        "end_date": "2026-08-25",
        "member_count": 5,
        "current_user_role": "owner"
      }
    ]
  },
  "error": null,
  "request_id": "request-id"
}
```

---

# 5. GET `/trips/{tripId}`

## 5.1 Description

Return detailed information for a trip.

## 5.2 Authentication

Required.

## 5.3 Path Parameters

| Parameter | Type | Required |
|---|---|---|
| `tripId` | UUID string | Required |

## 5.4 Authorization

The authenticated user must be a member of the trip.

## 5.5 Success Response

Status:

```text
200 OK
```

```json
{
  "success": true,
  "data": {
    "trip": {
      "id": "trip-uuid",
      "title": "Tokyo Graduation Trip",
      "destination": "Tokyo, Japan",
      "start_date": "2026-08-20",
      "end_date": "2026-08-25",
      "description": "A group trip after graduation.",
      "created_by": "user-uuid",
      "current_user_role": "owner",
      "member_count": 5,
      "candidate_count": 12,
      "itinerary_item_count": 8
    }
  },
  "error": null,
  "request_id": "request-id"
}
```

---

# 6. PATCH `/trips/{tripId}`

## 6.1 Description

Update editable trip metadata.

## 6.2 Authentication

Required.

## 6.3 Authorization

Default MVP policy:

- Owner only.

## 6.4 Path Parameters

| Parameter | Type | Required |
|---|---|---|
| `tripId` | UUID string | Required |

## 6.5 Request Body

At least one field must be provided.

| Field | Type | Required | Notes |
|---|---|---|---|
| `title` | string | Optional | Updated trip title |
| `destination` | string | Optional | Updated destination |
| `start_date` | string | Optional | Format: `YYYY-MM-DD` |
| `end_date` | string | Optional | Format: `YYYY-MM-DD` |
| `description` | string | Optional | Updated description |

## 6.6 Validation Rules

- If both dates exist after update:
  - `start_date <= end_date`
- Empty strings are not allowed for `title` or `destination`.

## 6.7 Example Request

```json
{
  "title": "Tokyo Summer Trip",
  "description": "Updated group planning notes."
}
```

## 6.8 Success Response

```json
{
  "success": true,
  "data": {
    "trip": {
      "id": "trip-uuid",
      "title": "Tokyo Summer Trip",
      "destination": "Tokyo, Japan",
      "start_date": "2026-08-20",
      "end_date": "2026-08-25",
      "description": "Updated group planning notes."
    }
  },
  "error": null,
  "request_id": "request-id"
}
```

---

# 7. GET `/trips/{tripId}/members`

## 7.1 Description

Return trip member list.

## 7.2 Authentication

Required.

## 7.3 Authorization

The authenticated user must be a member of the trip.

## 7.4 Path Parameters

| Parameter | Type | Required |
|---|---|---|
| `tripId` | UUID string | Required |

## 7.5 Success Response

```json
{
  "success": true,
  "data": {
    "members": [
      {
        "user_id": "user-uuid-1",
        "display_name": "Alice",
        "email": "alice@example.com",
        "role": "owner",
        "joined_at": "2026-05-15T10:00:00+08:00"
      },
      {
        "user_id": "user-uuid-2",
        "display_name": "Bob",
        "email": "bob@example.com",
        "role": "member",
        "joined_at": "2026-05-16T09:00:00+08:00"
      }
    ]
  },
  "error": null,
  "request_id": "request-id"
}
```

---

# 8. Expected Error Cases

| Scenario | Status | Error Code |
|---|---|---|
| Missing required create field | `400` | `VALIDATION_ERROR` |
| Invalid date range | `400` | `VALIDATION_ERROR` |
| Trip not found | `404` | `NOT_FOUND` |
| User not a trip member | `403` | `FORBIDDEN` |
| Non-owner attempts PATCH | `403` | `FORBIDDEN` |