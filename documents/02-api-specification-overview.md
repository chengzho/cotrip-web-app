# 02 - API Specification Overview

## 1. Purpose

This document defines the shared API conventions for the **CoTrip** collaborative travel planning app.

All domain-specific API documents must follow this specification.

This document applies to the MVP API scope, which includes:

- Trip and member management
- Invite flow
- Candidate place management
- Voting and ranking
- Itinerary generation and editing

The MVP API does **not** include reminder or notification endpoints.

---

## 2. API Base

### 2.1 Base URL

The frontend shall use an environment variable:

```text
VITE_API_BASE_URL
```

Example:

```text
https://{api-id}.execute-api.{region}.amazonaws.com
```

---

## 3. Authentication

### 3.1 Protected Routes

All application routes are protected unless explicitly marked as public.

Protected requests must include:

```http
Authorization: Bearer <JWT>
```

The JWT is issued by Amazon Cognito and validated by API Gateway HTTP API JWT Authorizer.

---

### 3.2 Public Routes

The following route is public:

| Route | Public? | Notes |
|---|---|---|
| `GET /invites/{inviteToken}` | Yes | Used to preview invite information before joining |

The following invite-related route is **not public**:

| Route | Public? | Notes |
|---|---|---|
| `POST /invites/{inviteToken}/join` | No | Joining requires authenticated user identity |

---

## 4. API Gateway to Lambda Routing

| Route Group | Lambda Function |
|---|---|
| `/me` | `UserProfileFunction` |
| `/trips`, `/trips/{tripId}`, `/trips/{tripId}/members` | `TripGroupFunction` |
| `/trips/{tripId}/invites`, `/invites/{inviteToken}` | `InviteFunction` |
| `/trips/{tripId}/candidates`, `/trips/{tripId}/candidates/{candidateId}` | `CandidateFunction` |
| `/candidates/{candidateId}/votes`, `/trips/{tripId}/rankings` | `VoteFunction` |
| `/trips/{tripId}/itinerary`, `/trips/{tripId}/itinerary/generate`, `/trips/{tripId}/itinerary/items/{itemId}` | `ItineraryFunction` |

---

## 5. API Document Split

Detailed endpoint specifications are documented in:

1. `03-api-trip-and-member.md`
2. `04-api-invite.md`
3. `05-api-candidate-and-vote.md`
4. `06-api-itinerary.md`
5. `15-api-user-profile.md`

---

## 6. Request Format

### 6.1 Content Type

For JSON request bodies:

```http
Content-Type: application/json
```

---

### 6.2 HTTP API Event Handling

Lambda functions receive API Gateway HTTP API events.

Handlers must use a shared event parsing helper rather than repeatedly parsing raw event fields ad hoc.

Recommended fields to normalize:

- HTTP method
- Raw path
- Path parameters
- Query string parameters
- JSON body
- JWT claims
- Request ID

---

## 7. Shared Response Envelope

All API responses must use the same shape.

### 7.1 Success Response

```json
{
  "success": true,
  "data": {},
  "error": null,
  "request_id": "example-request-id"
}
```

---

### 7.2 Error Response

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "title is required"
  },
  "request_id": "example-request-id"
}
```

---

## 8. HTTP Status Code Policy

| Status Code | Meaning |
|---|---|
| `200` | Successful read, update, delete, or idempotent state confirmation |
| `201` | Resource created |
| `400` | Invalid request body or query |
| `401` | Missing or invalid authentication |
| `403` | Authenticated but not authorized |
| `404` | Resource not found |
| `409` | Business conflict, e.g. already joined, itinerary already exists |
| `422` | Semantically invalid input if used |
| `500` | Unexpected server error |

---

## 8.1 DELETE Response Policy

For the CoTrip MVP, DELETE endpoints shall use:

```text
200 OK
```

with the standard JSON response envelope.

The MVP shall **not** use:

```text
204 No Content
```

for application DELETE endpoints.

This keeps frontend response handling consistent across all mutation APIs.

Examples of DELETE-style operations include:

- Deleting a candidate place
- Removing the current user's vote
- Deleting an itinerary item

Each DELETE response should return a meaningful `data` object appropriate to the endpoint, such as:

- deleted resource identifier
- current voted state
- updated vote count when relevant

---

## 9. Standard Error Codes

| Error Code | Usage |
|---|---|
| `VALIDATION_ERROR` | Invalid request parameter |
| `UNAUTHORIZED` | Authentication missing or invalid |
| `FORBIDDEN` | No permission for resource |
| `NOT_FOUND` | Resource does not exist |
| `ALREADY_EXISTS` | Duplicate logical resource |
| `CONFLICT` | Operation conflicts with current state |
| `INVITE_EXPIRED` | Invite token expired |
| `INVITE_REVOKED` | Invite token revoked |
| `INVITE_USAGE_LIMIT_REACHED` | Invite token use limit reached |
| `ITINERARY_ALREADY_EXISTS` | Existing itinerary blocks generation |
| `INTERNAL_SERVER_ERROR` | Unhandled server failure |

---

## 10. Parameter Requirement Notation

Each API document uses the following notation:

| Label | Meaning |
|---|---|
| Required | Must be provided |
| Optional | May be omitted |
| Conditional | Required only in stated cases |

---

## 11. Date and Time Format

### 11.1 Date

Use ISO-style date strings:

```text
YYYY-MM-DD
```

Example:

```text
2026-08-20
```

---

### 11.2 Timestamp

Use timezone-aware ISO 8601 strings:

```text
2026-08-20T09:00:00+08:00
```

---

## 12. Identifier Format

System identifiers use UUID strings unless otherwise specified.

Examples:

```text
trip_id
user_id
candidate_id
item_id
invite_id
```

Invite token values are opaque token strings and are **not** UUIDs.

---

## 13. Authorization Rules

### 13.1 Trip Membership

Any route that accesses a trip-specific resource must verify that the authenticated user is a member of the trip.

Examples:

- `GET /trips/{tripId}`
- `GET /trips/{tripId}/members`
- `GET /trips/{tripId}/candidates`
- `GET /trips/{tripId}/rankings`
- `GET /trips/{tripId}/itinerary`

---

### 13.2 Owner-Only Actions

Unless otherwise specified, the following actions are owner-only:

- Updating core trip metadata
- Creating invite links

The MVP should default to stricter authorization when uncertain.

---

### 13.3 Candidate Ownership and Trip Owner Override

For candidate place modification:

- The candidate creator may update or delete their own candidate place.
- The trip owner may also update or delete candidate places in the trip.

---

### 13.4 Itinerary Editing Policy

For the MVP, itinerary generation and itinerary item editing may be available to any trip member unless the final implementation deliberately restricts them further.

The chosen implementation must remain consistent across:

- API behavior
- Frontend UI
- Lambda authorization checks

---

## 14. Request Validation Rules

Claude Code must implement explicit validation for:

- Required body fields
- UUID-like identifiers where applicable
- Date ordering:
  - `start_date <= end_date`
- Text length limits where reasonable
- Enum values
- Duplicate operations
- Empty PATCH payloads
- Invalid category values
- Invalid itinerary slot values

---

## 15. CORS Requirements

The API must allow requests from the deployed frontend origin.

Minimum expected CORS support:

- Allowed origins:
  - GitHub Pages frontend URL
  - Local development URL if configured

- Allowed methods:
  - `GET`
  - `POST`
  - `PATCH`
  - `DELETE`
  - `OPTIONS`

- Allowed headers:
  - `Content-Type`
  - `Authorization`

---

## 16. Logging Requirements

All Lambda-backed API handlers must log:

- Request ID
- Route key or normalized route
- Authenticated user identifier if available
- Important failure reason

Never log:

- Raw JWT
- Database password
- Full invite token if avoidable
- Sensitive credentials
- Raw database connection strings containing secrets

---

## 17. API MVP Scope Summary

The CoTrip MVP API includes:

| Domain | Included? |
|---|---|
| User identity resolution through Cognito JWT claims | Yes |
| User profile read and display name update (`/me`) | Yes |
| Trip creation and editing | Yes |
| Trip member listing | Yes |
| Invite creation, preview, and joining | Yes |
| Candidate place CRUD | Yes |
| Voting and ranking | Yes |
| Itinerary generation and editing | Yes |
| Reminder APIs | No |
| Notification APIs | No |

Reminder and notification endpoints must not be implemented in the MVP.