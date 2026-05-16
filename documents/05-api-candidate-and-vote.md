# 05 - API Specification: Candidate and Vote

## 1. Purpose

This document specifies APIs handled by:

```text
CandidateFunction
VoteFunction
```

The system allows members to:

- Add candidate attractions or restaurants
- Edit or remove candidate places
- Vote or unvote
- View current ranking

---

# 2. Endpoint Summary

## 2.1 CandidateFunction

| Method | Path | Description |
|---|---|---|
| `GET` | `/trips/{tripId}/candidates` | List candidate places |
| `POST` | `/trips/{tripId}/candidates` | Create candidate place |
| `PATCH` | `/trips/{tripId}/candidates/{candidateId}` | Update candidate |
| `DELETE` | `/trips/{tripId}/candidates/{candidateId}` | Delete candidate |

## 2.2 VoteFunction

| Method | Path | Description |
|---|---|---|
| `POST` | `/candidates/{candidateId}/votes` | Vote candidate |
| `DELETE` | `/candidates/{candidateId}/votes` | Remove current user's vote |
| `GET` | `/trips/{tripId}/rankings` | View ranked candidates |

---

# 3. GET `/trips/{tripId}/candidates`

## 3.1 Description

Return candidate attractions and restaurants for a trip.

## 3.2 Authentication

Required.

## 3.3 Authorization

The authenticated user must be a trip member.

## 3.4 Path Parameters

| Parameter | Type | Required |
|---|---|---|
| `tripId` | UUID string | Required |

## 3.5 Query Parameters

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `category` | string | Optional | `attraction` or `restaurant` |
| `sort` | string | Optional | `created_desc`, `votes_desc`; default backend decision |

## 3.6 Success Response

```json
{
  "success": true,
  "data": {
    "candidates": [
      {
        "id": "candidate-uuid",
        "trip_id": "trip-uuid",
        "category": "attraction",
        "name": "Tokyo Skytree",
        "address": "1 Chome-1-2 Oshiage, Sumida City",
        "note": "Good night view.",
        "source_url": "https://example.com",
        "created_by": {
          "user_id": "user-uuid",
          "display_name": "Alice"
        },
        "vote_count": 5,
        "current_user_has_voted": true,
        "created_at": "2026-05-15T10:00:00+08:00"
      }
    ]
  },
  "error": null,
  "request_id": "request-id"
}
```

---

# 4. POST `/trips/{tripId}/candidates`

## 4.1 Description

Create a candidate attraction or restaurant.

## 4.2 Authentication

Required.

## 4.3 Authorization

The authenticated user must be a trip member.

## 4.4 Path Parameters

| Parameter | Type | Required |
|---|---|---|
| `tripId` | UUID string | Required |

## 4.5 Request Body

| Field | Type | Required | Notes |
|---|---|---|---|
| `category` | string | Required | `attraction` or `restaurant` |
| `name` | string | Required | Candidate place name |
| `address` | string | Optional | Plain text |
| `note` | string | Optional | Why the user suggests it |
| `source_url` | string | Optional | External reference URL |

## 4.6 Example Request

```json
{
  "category": "restaurant",
  "name": "Gyukatsu Motomura",
  "address": "Shibuya, Tokyo",
  "note": "Popular beef cutlet restaurant.",
  "source_url": "https://example.com"
}
```

## 4.7 Success Response

```json
{
  "success": true,
  "data": {
    "candidate": {
      "id": "candidate-uuid",
      "trip_id": "trip-uuid",
      "category": "restaurant",
      "name": "Gyukatsu Motomura",
      "address": "Shibuya, Tokyo",
      "note": "Popular beef cutlet restaurant.",
      "source_url": "https://example.com",
      "vote_count": 0,
      "current_user_has_voted": false
    }
  },
  "error": null,
  "request_id": "request-id"
}
```

---

# 5. PATCH `/trips/{tripId}/candidates/{candidateId}`

## 5.1 Description

Update an existing candidate place.

## 5.2 Authentication

Required.

## 5.3 Authorization

Default MVP policy:

- Candidate creator can edit
- Trip owner can edit

## 5.4 Path Parameters

| Parameter | Type | Required |
|---|---|---|
| `tripId` | UUID string | Required |
| `candidateId` | UUID string | Required |

## 5.5 Request Body

At least one field is required.

| Field | Type | Required |
|---|---|---|
| `category` | string | Optional |
| `name` | string | Optional |
| `address` | string | Optional |
| `note` | string | Optional |
| `source_url` | string | Optional |

---

# 6. DELETE `/trips/{tripId}/candidates/{candidateId}`

## 6.1 Description

Delete a candidate place.

## 6.2 Authentication

Required.

## 6.3 Authorization

Default MVP policy:

- Candidate creator can delete
- Trip owner can delete

## 6.4 Deletion Behavior

Recommended MVP behavior:

- Hard delete candidate
- Related votes are removed via database cascade or explicit cleanup

---

# 7. POST `/candidates/{candidateId}/votes`

## 7.1 Description

Add current user's vote to a candidate place.

## 7.2 Authentication

Required.

## 7.3 Authorization

The authenticated user must be a member of the trip that owns this candidate.

## 7.4 Path Parameters

| Parameter | Type | Required |
|---|---|---|
| `candidateId` | UUID string | Required |

## 7.5 Request Body

No body required.

## 7.6 Success Response

```json
{
  "success": true,
  "data": {
    "candidate_id": "candidate-uuid",
    "current_user_has_voted": true,
    "vote_count": 6
  },
  "error": null,
  "request_id": "request-id"
}
```

---

# 8. DELETE `/candidates/{candidateId}/votes`

## 8.1 Description

Remove the current user's vote from a candidate place.

## 8.2 Authentication

Required.

## 8.3 Success Response

```json
{
  "success": true,
  "data": {
    "candidate_id": "candidate-uuid",
    "current_user_has_voted": false,
    "vote_count": 5
  },
  "error": null,
  "request_id": "request-id"
}
```

---

# 9. GET `/trips/{tripId}/rankings`

## 9.1 Description

Return ranked candidate places sorted by vote count.

## 9.2 Authentication

Required.

## 9.3 Authorization

The authenticated user must be a trip member.

## 9.4 Query Parameters

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `category` | string | Optional | `attraction` or `restaurant` |

## 9.5 Success Response

```json
{
  "success": true,
  "data": {
    "rankings": [
      {
        "rank": 1,
        "candidate_id": "candidate-uuid-1",
        "category": "attraction",
        "name": "Tokyo Skytree",
        "vote_count": 7,
        "current_user_has_voted": true
      },
      {
        "rank": 2,
        "candidate_id": "candidate-uuid-2",
        "category": "restaurant",
        "name": "Gyukatsu Motomura",
        "vote_count": 5,
        "current_user_has_voted": false
      }
    ]
  },
  "error": null,
  "request_id": "request-id"
}
```

---

# 10. Expected Error Cases

| Scenario | Status | Error Code |
|---|---|---|
| Candidate not found | `404` | `NOT_FOUND` |
| Trip not found | `404` | `NOT_FOUND` |
| User not trip member | `403` | `FORBIDDEN` |
| Duplicate vote | `409` or idempotent `200` | `ALREADY_EXISTS` if not idempotent |
| Delete non-existing vote | `404` or idempotent `200` | Backend decision |
| Invalid category | `400` | `VALIDATION_ERROR` |