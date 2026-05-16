# 05 - API Specification: Candidate Places and Voting

## 1. Purpose

This document specifies APIs for the **CoTrip** candidate-place and voting domains.

The APIs in this document are handled by:

```text
CandidateFunction
VoteFunction
```

These domains allow trip members to:

- Propose candidate attractions and restaurants
- View candidate places for a trip
- Update or delete candidate places when authorized
- Vote for candidate places
- Remove their own votes
- View ranked candidate places sorted by group preference

---

# 2. Endpoint Summary

## 2.1 Candidate Place Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/trips/{tripId}/candidates` | List candidate places |
| `POST` | `/trips/{tripId}/candidates` | Create candidate place |
| `PATCH` | `/trips/{tripId}/candidates/{candidateId}` | Update candidate place |
| `DELETE` | `/trips/{tripId}/candidates/{candidateId}` | Delete candidate place |

---

## 2.2 Voting Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/candidates/{candidateId}/votes` | Vote for a candidate place |
| `DELETE` | `/candidates/{candidateId}/votes` | Remove current user's vote |
| `GET` | `/trips/{tripId}/rankings` | Get ranked candidate places |

---

# 3. Shared Authentication and Authorization Policy

All endpoints in this document require authentication.

Requests must include:

```http
Authorization: Bearer <JWT>
```

---

## 3.1 Trip Membership Requirement

The authenticated user must be a member of the related trip in order to:

- List candidate places
- Create candidate places
- Vote or unvote
- View rankings

---

## 3.2 Candidate Update and Delete Authorization

A candidate place may be updated or deleted by:

1. The user who created the candidate, or
2. The trip owner

Unauthorized modification attempts must return:

```text
403 FORBIDDEN
```

---

# 4. Candidate Places

---

## 4.1 GET `/trips/{tripId}/candidates`

### 4.1.1 Description

Return candidate attractions and restaurants proposed within a trip.

The response should include:

- Candidate place metadata
- Vote count
- Whether the current authenticated user has voted for each candidate

This allows the frontend to render candidate cards without requiring separate vote-state requests.

---

### 4.1.2 Authentication

Required.

---

### 4.1.3 Authorization

The authenticated user must be a member of the target trip.

---

### 4.1.4 Path Parameters

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `tripId` | UUID string | Required | Target trip identifier |

---

### 4.1.5 Query Parameters

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `category` | string | Optional | Allowed values: `attraction`, `restaurant` |

If `category` is omitted, return all candidate places for the trip.

---

### 4.1.6 Sorting

Recommended default ordering:

1. Newer candidates first, or
2. Creation time descending

The final implementation should keep ordering deterministic.

The ranked vote-based ordering is handled separately by:

```text
GET /trips/{tripId}/rankings
```

---

### 4.1.7 Success Response

Status:

```text
200 OK
```

```json
{
  "success": true,
  "data": {
    "candidates": [
      {
        "candidate_id": "candidate-uuid-1",
        "trip_id": "trip-uuid",
        "category": "attraction",
        "name": "Senso-ji Temple",
        "address": "2 Chome-3-1 Asakusa, Taito City, Tokyo",
        "note": "A classic historic stop for the first day.",
        "source_url": "https://example.com/sensoji",
        "created_by": {
          "user_id": "user-uuid-1",
          "display_name": "Sophie"
        },
        "vote_count": 5,
        "current_user_voted": true,
        "created_at": "2026-08-01T10:00:00+08:00",
        "updated_at": "2026-08-01T10:00:00+08:00"
      },
      {
        "candidate_id": "candidate-uuid-2",
        "trip_id": "trip-uuid",
        "category": "restaurant",
        "name": "Gyukatsu Motomura",
        "address": null,
        "note": "Good lunch option near Shibuya.",
        "source_url": null,
        "created_by": {
          "user_id": "user-uuid-2",
          "display_name": "Marcus"
        },
        "vote_count": 3,
        "current_user_voted": false,
        "created_at": "2026-08-02T14:30:00+08:00",
        "updated_at": "2026-08-02T14:30:00+08:00"
      }
    ]
  },
  "error": null,
  "request_id": "request-id"
}
```

---

### 4.1.8 Empty Response

If the trip exists and the user is authorized, but no candidate places exist yet:

```text
200 OK
```

```json
{
  "success": true,
  "data": {
    "candidates": []
  },
  "error": null,
  "request_id": "request-id"
}
```

---

### 4.1.9 Expected Error Cases

| Scenario | Status | Error Code |
|---|---|---|
| Trip not found | `404` | `NOT_FOUND` |
| User not a trip member | `403` | `FORBIDDEN` |
| Invalid category query value | `400` | `VALIDATION_ERROR` |

---

## 4.2 POST `/trips/{tripId}/candidates`

### 4.2.1 Description

Create a candidate attraction or restaurant within a trip.

---

### 4.2.2 Authentication

Required.

---

### 4.2.3 Authorization

The authenticated user must be a member of the target trip.

---

### 4.2.4 Path Parameters

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `tripId` | UUID string | Required | Target trip identifier |

---

### 4.2.5 Request Body

| Field | Type | Required | Notes |
|---|---|---|---|
| `category` | string | Required | `attraction` or `restaurant` |
| `name` | string | Required | Candidate place name |
| `address` | string | Optional | Free-form address text |
| `note` | string | Optional | Reason, comment, or planning note |
| `source_url` | string | Optional | External reference URL |

---

### 4.2.6 Validation Rules

- `category` must be one of:
  - `attraction`
  - `restaurant`
- `name` must not be empty.
- `source_url`, if provided, should be a valid URL or a reasonably validated URL-like string according to final implementation.
- Text length limits should be enforced where reasonable.

---

### 4.2.7 Example Request

```json
{
  "category": "attraction",
  "name": "Tokyo Skytree",
  "address": "1 Chome-1-2 Oshiage, Sumida City, Tokyo",
  "note": "Would be nice for evening city views.",
  "source_url": "https://example.com/skytree"
}
```

---

### 4.2.8 Success Response

Status:

```text
201 Created
```

```json
{
  "success": true,
  "data": {
    "candidate": {
      "candidate_id": "candidate-uuid",
      "trip_id": "trip-uuid",
      "category": "attraction",
      "name": "Tokyo Skytree",
      "address": "1 Chome-1-2 Oshiage, Sumida City, Tokyo",
      "note": "Would be nice for evening city views.",
      "source_url": "https://example.com/skytree",
      "created_by": {
        "user_id": "user-uuid",
        "display_name": "Sophie"
      },
      "vote_count": 0,
      "current_user_voted": false,
      "created_at": "2026-08-03T09:00:00+08:00",
      "updated_at": "2026-08-03T09:00:00+08:00"
    }
  },
  "error": null,
  "request_id": "request-id"
}
```

---

### 4.2.9 Expected Error Cases

| Scenario | Status | Error Code |
|---|---|---|
| Trip not found | `404` | `NOT_FOUND` |
| User not a trip member | `403` | `FORBIDDEN` |
| Missing required field | `400` | `VALIDATION_ERROR` |
| Invalid category | `400` | `VALIDATION_ERROR` |
| Invalid source URL if validation is enforced | `400` | `VALIDATION_ERROR` |

---

## 4.3 PATCH `/trips/{tripId}/candidates/{candidateId}`

### 4.3.1 Description

Update an existing candidate place.

---

### 4.3.2 Authentication

Required.

---

### 4.3.3 Authorization

The authenticated user must satisfy one of:

- Candidate creator, or
- Trip owner

---

### 4.3.4 Path Parameters

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `tripId` | UUID string | Required | Target trip identifier |
| `candidateId` | UUID string | Required | Target candidate identifier |

---

### 4.3.5 Request Body

At least one editable field must be provided.

| Field | Type | Required | Notes |
|---|---|---|---|
| `category` | string | Optional | `attraction` or `restaurant` |
| `name` | string | Optional | Candidate place name |
| `address` | string | Optional | Free-form address text |
| `note` | string | Optional | Reason, comment, or planning note |
| `source_url` | string | Optional | External reference URL |

---

### 4.3.6 Validation Rules

- Request body must not be empty.
- `category`, if provided, must be one of:
  - `attraction`
  - `restaurant`
- `name`, if provided, must not be empty.
- `source_url`, if provided, should satisfy the selected URL validation policy.
- Fields omitted from the request must retain their existing values.

---

### 4.3.7 Example Request

```json
{
  "note": "Better for sunset than afternoon.",
  "source_url": "https://example.com/updated-skytree"
}
```

---

### 4.3.8 Success Response

Status:

```text
200 OK
```

```json
{
  "success": true,
  "data": {
    "candidate": {
      "candidate_id": "candidate-uuid",
      "trip_id": "trip-uuid",
      "category": "attraction",
      "name": "Tokyo Skytree",
      "address": "1 Chome-1-2 Oshiage, Sumida City, Tokyo",
      "note": "Better for sunset than afternoon.",
      "source_url": "https://example.com/updated-skytree",
      "created_by": {
        "user_id": "user-uuid",
        "display_name": "Sophie"
      },
      "vote_count": 5,
      "current_user_voted": true,
      "created_at": "2026-08-03T09:00:00+08:00",
      "updated_at": "2026-08-03T13:45:00+08:00"
    }
  },
  "error": null,
  "request_id": "request-id"
}
```

---

### 4.3.9 Expected Error Cases

| Scenario | Status | Error Code |
|---|---|---|
| Trip not found | `404` | `NOT_FOUND` |
| Candidate not found | `404` | `NOT_FOUND` |
| User not authorized to edit candidate | `403` | `FORBIDDEN` |
| Empty PATCH body | `400` | `VALIDATION_ERROR` |
| Invalid category | `400` | `VALIDATION_ERROR` |
| Empty candidate name | `400` | `VALIDATION_ERROR` |

---

## 4.4 DELETE `/trips/{tripId}/candidates/{candidateId}`

### 4.4.1 Description

Delete an existing candidate place.

Related candidate votes should also be removed through:

- database cascade behavior, or
- repository cleanup logic

The final implementation must remain consistent with the database schema policy.

---

### 4.4.2 Authentication

Required.

---

### 4.4.3 Authorization

The authenticated user must satisfy one of:

- Candidate creator, or
- Trip owner

---

### 4.4.4 Path Parameters

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `tripId` | UUID string | Required | Target trip identifier |
| `candidateId` | UUID string | Required | Target candidate identifier |

---

### 4.4.5 Request Body

No request body is required.

---

### 4.4.6 Success Response

Status:

```text
200 OK
```

```json
{
  "success": true,
  "data": {
    "deleted_candidate_id": "candidate-uuid"
  },
  "error": null,
  "request_id": "request-id"
}
```

The CoTrip MVP uses `200 OK` with the shared JSON response envelope for DELETE endpoints.

Do not return:

```text
204 No Content
```

for candidate deletion.

---

### 4.4.7 Expected Error Cases

| Scenario | Status | Error Code |
|---|---|---|
| Trip not found | `404` | `NOT_FOUND` |
| Candidate not found | `404` | `NOT_FOUND` |
| User not authorized to delete candidate | `403` | `FORBIDDEN` |

---

# 5. Voting

---

## 5.1 POST `/candidates/{candidateId}/votes`

### 5.1.1 Description

Add the current user's vote to a candidate place.

The CoTrip MVP uses a simple upvote model:

- One user may vote at most once per candidate.
- Each active vote represents one positive vote.

---

### 5.1.2 Authentication

Required.

---

### 5.1.3 Authorization

The authenticated user must be a member of the trip that owns the candidate.

---

### 5.1.4 Path Parameters

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `candidateId` | UUID string | Required | Target candidate identifier |

---

### 5.1.5 Request Body

No request body is required.

---

### 5.1.6 Duplicate Vote Idempotency Policy

The CoTrip MVP uses **idempotent success** for repeated vote requests.

If the authenticated user has already voted for the candidate, the backend shall:

- keep the existing vote unchanged
- return `200 OK`
- return the current voted state as `true`
- return the current vote count

This operation must not return:

```text
409 ALREADY_EXISTS
```

for duplicate vote submission.

---

### 5.1.7 Success Response

Status:

```text
200 OK
```

```json
{
  "success": true,
  "data": {
    "candidate_id": "candidate-uuid",
    "voted": true,
    "vote_count": 5
  },
  "error": null,
  "request_id": "request-id"
}
```

This same success response shape is used for:

- the first successful vote creation
- repeated vote requests when the user has already voted

---

### 5.1.8 Expected Error Cases

| Scenario | Status | Error Code |
|---|---|---|
| Candidate not found | `404` | `NOT_FOUND` |
| User not a member of owning trip | `403` | `FORBIDDEN` |

Duplicate vote submission is **not** an error in the MVP.

---

## 5.2 DELETE `/candidates/{candidateId}/votes`

### 5.2.1 Description

Remove the current user's vote from a candidate place.

---

### 5.2.2 Authentication

Required.

---

### 5.2.3 Authorization

The authenticated user must be a member of the trip that owns the candidate.

---

### 5.2.4 Path Parameters

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `candidateId` | UUID string | Required | Target candidate identifier |

---

### 5.2.5 Request Body

No request body is required.

---

### 5.2.6 Missing Vote Idempotency Policy

The CoTrip MVP uses **idempotent success** when removing a vote.

If the authenticated user has not voted for the candidate, the backend shall:

- leave the database unchanged
- return `200 OK`
- return the current voted state as `false`
- return the current vote count

This operation must not fail merely because the vote row does not exist.

---

### 5.2.7 Success Response

Status:

```text
200 OK
```

```json
{
  "success": true,
  "data": {
    "candidate_id": "candidate-uuid",
    "voted": false,
    "vote_count": 4
  },
  "error": null,
  "request_id": "request-id"
}
```

This same success response shape is used for:

- a successful vote removal
- repeated unvote requests when the user already has no active vote

The CoTrip MVP uses `200 OK` with the shared JSON response envelope for DELETE endpoints.

---

### 5.2.8 Expected Error Cases

| Scenario | Status | Error Code |
|---|---|---|
| Candidate not found | `404` | `NOT_FOUND` |
| User not a member of owning trip | `403` | `FORBIDDEN` |

A missing vote row is **not** an error in the MVP.

---

# 6. Rankings

---

## 6.1 GET `/trips/{tripId}/rankings`

### 6.1.1 Description

Return candidate places ranked by vote count within a trip.

This endpoint supports the Voting page and provides an ordered representation of group preference.

---

### 6.1.2 Authentication

Required.

---

### 6.1.3 Authorization

The authenticated user must be a member of the target trip.

---

### 6.1.4 Path Parameters

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `tripId` | UUID string | Required | Target trip identifier |

---

### 6.1.5 Query Parameters

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `category` | string | Optional | Allowed values: `attraction`, `restaurant` |

If `category` is omitted, return ranked candidates from all categories.

---

### 6.1.6 Ranking Logic

Rank candidates using:

1. Higher `vote_count` first
2. Earlier `created_at` first as deterministic tie-breaker

Candidate places with zero votes should still be included in the response, after candidates with higher vote counts.

---

### 6.1.7 Success Response

Status:

```text
200 OK
```

```json
{
  "success": true,
  "data": {
    "rankings": [
      {
        "rank": 1,
        "candidate_id": "candidate-uuid-1",
        "trip_id": "trip-uuid",
        "category": "attraction",
        "name": "Senso-ji Temple",
        "note": "A classic historic stop for the first day.",
        "created_by": {
          "user_id": "user-uuid-1",
          "display_name": "Sophie"
        },
        "vote_count": 7,
        "current_user_voted": true,
        "created_at": "2026-08-01T10:00:00+08:00"
      },
      {
        "rank": 2,
        "candidate_id": "candidate-uuid-2",
        "trip_id": "trip-uuid",
        "category": "restaurant",
        "name": "Gyukatsu Motomura",
        "note": "Good lunch option near Shibuya.",
        "created_by": {
          "user_id": "user-uuid-2",
          "display_name": "Marcus"
        },
        "vote_count": 4,
        "current_user_voted": false,
        "created_at": "2026-08-02T14:30:00+08:00"
      }
    ]
  },
  "error": null,
  "request_id": "request-id"
}
```

---

### 6.1.8 Empty Response

If the trip exists and the user is authorized, but no candidate places exist:

```text
200 OK
```

```json
{
  "success": true,
  "data": {
    "rankings": []
  },
  "error": null,
  "request_id": "request-id"
}
```

---

### 6.1.9 Expected Error Cases

| Scenario | Status | Error Code |
|---|---|---|
| Trip not found | `404` | `NOT_FOUND` |
| User not a trip member | `403` | `FORBIDDEN` |
| Invalid category query value | `400` | `VALIDATION_ERROR` |

---

# 7. Frontend Integration Notes

## 7.1 Places Page

The frontend Places page should use:

```text
GET /trips/{tripId}/candidates
```

to render:

- Candidate cards
- Vote count
- Current user's voted state
- Optional category filter

---

## 7.2 Voting Page

The frontend Voting page should use:

```text
GET /trips/{tripId}/rankings
```

to render:

- Ranked candidate list
- Top-voted places
- Vote count
- Current user's voted state
- Optional category filter

---

## 7.3 Vote Button Behavior

The frontend may implement the vote button as a toggle:

- If `current_user_voted = false`
  - Call `POST /candidates/{candidateId}/votes`
- If `current_user_voted = true`
  - Call `DELETE /candidates/{candidateId}/votes`

Because both endpoints are idempotent, repeated clicks or repeated requests should not create inconsistent vote state.

---

# 8. Candidate and Voting MVP Scope Summary

The CoTrip MVP candidate and voting APIs include:

| Capability | Included? |
|---|---|
| List candidate places | Yes |
| Create candidate place | Yes |
| Update candidate place | Yes |
| Delete candidate place | Yes |
| Add current user's vote | Yes |
| Remove current user's vote | Yes |
| Idempotent repeated vote behavior | Yes |
| Idempotent repeated unvote behavior | Yes |
| Ranked candidate listing | Yes |
| Weighted voting | No |
| Downvotes | No |
| Comment threads on candidates | No |