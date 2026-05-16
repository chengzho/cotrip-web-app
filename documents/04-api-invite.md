# 04 - API Specification: Invite

## 1. Purpose

This document specifies APIs handled by:

```text
InviteFunction
```

The function covers:

- Create trip invite links
- Preview invite information
- Join a trip using invite token

---

# 2. Endpoint Summary

| Method | Path | Description |
|---|---|---|
| `POST` | `/trips/{tripId}/invites` | Create invite link |
| `GET` | `/invites/{inviteToken}` | Preview invite detail |
| `POST` | `/invites/{inviteToken}/join` | Join trip via invite |

---

# 3. POST `/trips/{tripId}/invites`

## 3.1 Description

Create a new invite token for a trip.

## 3.2 Authentication

Required.

## 3.3 Authorization

Default MVP policy:

- Trip owner only.

## 3.4 Path Parameters

| Parameter | Type | Required |
|---|---|---|
| `tripId` | UUID string | Required |

## 3.5 Request Body

| Field | Type | Required | Notes |
|---|---|---|---|
| `expires_in_days` | integer | Optional | Default determined by backend, recommended default: `7` |
| `max_uses` | integer | Optional | Default determined by backend, recommended default: `20` |

## 3.6 Validation Rules

- `expires_in_days` must be positive if provided.
- `max_uses` must be positive if provided.

## 3.7 Example Request

```json
{
  "expires_in_days": 7,
  "max_uses": 20
}
```

## 3.8 Success Response

```json
{
  "success": true,
  "data": {
    "invite": {
      "id": "invite-uuid",
      "trip_id": "trip-uuid",
      "invite_url": "https://frontend.example.com/join/rawInviteToken",
      "expires_at": "2026-05-22T23:59:59+08:00",
      "max_uses": 20
    }
  },
  "error": null,
  "request_id": "request-id"
}
```

---

# 4. GET `/invites/{inviteToken}`

## 4.1 Description

Preview invitation information before the user joins the trip.

## 4.2 Authentication

Not required.

## 4.3 Path Parameters

| Parameter | Type | Required |
|---|---|---|
| `inviteToken` | string | Required |

## 4.4 Token Validation

Backend must validate:

- Token hash exists
- Invite is not expired
- Invite is not revoked
- Invite has remaining capacity

## 4.5 Success Response

```json
{
  "success": true,
  "data": {
    "invite_preview": {
      "trip_title": "Tokyo Graduation Trip",
      "destination": "Tokyo, Japan",
      "start_date": "2026-08-20",
      "end_date": "2026-08-25",
      "invited_by_display_name": "Alice"
    }
  },
  "error": null,
  "request_id": "request-id"
}
```

---

# 5. POST `/invites/{inviteToken}/join`

## 5.1 Description

Allow an authenticated user to join the corresponding trip.

## 5.2 Authentication

Required.

## 5.3 Path Parameters

| Parameter | Type | Required |
|---|---|---|
| `inviteToken` | string | Required |

## 5.4 Request Body

No request body required.

## 5.5 Business Rules

1. Validate invite token.
2. Resolve current authenticated user.
3. Check whether user is already a trip member.
4. If not:
   - Insert into `trip_members`
   - Increment invite `used_count`
5. Return joined trip summary.

## 5.6 Success Response

```json
{
  "success": true,
  "data": {
    "trip": {
      "id": "trip-uuid",
      "title": "Tokyo Graduation Trip",
      "destination": "Tokyo, Japan",
      "current_user_role": "member"
    }
  },
  "error": null,
  "request_id": "request-id"
}
```

---

# 6. Expected Error Cases

| Scenario | Status | Error Code |
|---|---|---|
| Invite token unknown | `404` | `NOT_FOUND` |
| Invite expired | `410` or `400` | `INVITE_EXPIRED` |
| Invite revoked | `400` | `INVITE_REVOKED` |
| Invite usage limit reached | `400` | `INVITE_USAGE_LIMIT_REACHED` |
| User already joined | `409` | `ALREADY_EXISTS` |
| Non-owner attempts invite creation | `403` | `FORBIDDEN` |

---

# 7. Security Notes

- The database stores only the invite token hash.
- The raw token is returned to the client only when the invite is created.
- Do not log the full raw invite token.
- Invite joining must be handled transactionally to avoid inaccurate `used_count`.