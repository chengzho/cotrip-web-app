# 15 - API Specification: User Profile

## 1. Purpose

This document specifies the User Profile API for the **CoTrip** collaborative travel planning app.

The User Profile domain allows authenticated users to:

- Read their own current profile
- Update their display name (nickname)

This domain does **not** include avatar upload, password management, or account deletion.

---

# 2. Endpoint Summary

| Method | Path | Description |
|---|---|---|
| `GET` | `/me` | Get current user's profile |
| `PATCH` | `/me` | Update current user's display name |

---

# 3. Shared Authorization Policy

All endpoints in this document require authentication.

Requests must include:

```http
Authorization: Bearer <JWT>
```

The JWT is issued by Amazon Cognito and validated by API Gateway HTTP API JWT Authorizer.

The authenticated user may only read and update their own profile.  
There is no admin or cross-user profile access in the MVP.

---

# 4. GET `/me`

## 4.1 Description

Returns the current authenticated user's application profile.

This endpoint is the canonical source of the user's CoTrip identity, including their current display name.

---

## 4.2 Authentication

Required.

---

## 4.3 Authorization

Returns only the profile of the authenticated user.  
No `user_id` path parameter is accepted.

---

## 4.4 Request Body

None.

---

## 4.5 Success Response

HTTP status: `200`

```json
{
  "success": true,
  "data": {
    "user": {
      "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "email": "jczho.mg14@nycu.edu.tw",
      "display_name": "小周"
    }
  },
  "error": null,
  "request_id": "example-request-id"
}
```

---

## 4.6 Response Field Notes

| Field | Notes |
|---|---|
| `user_id` | Internal CoTrip UUID for this user |
| `email` | Email address from Cognito identity |
| `display_name` | Current display name; may be a system-derived fallback if the user has not yet set one explicitly |

---

## 4.7 Error Responses

| Condition | Status | Error Code |
|---|---|---|
| Missing or invalid JWT | `401` | `UNAUTHORIZED` |

---

# 5. PATCH `/me`

## 5.1 Description

Updates the current authenticated user's display name.

This is the primary entry point for users to set or change their CoTrip nickname.

---

## 5.2 Authentication

Required.

---

## 5.3 Authorization

Updates only the profile of the authenticated user.

---

## 5.4 Request Body

```json
{
  "display_name": "小周"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `display_name` | string | Required | The new display name |

---

## 5.5 Validation Rules

- `display_name` must be a string.
- Leading and trailing whitespace must be trimmed before validation.
- `display_name` must not be empty after trimming.
- `display_name` must not exceed **50 characters** after trimming.
- No special character restrictions in the MVP; users may use CJK characters, Latin, or mixed names.

---

## 5.6 Success Response

HTTP status: `200`

```json
{
  "success": true,
  "data": {
    "user": {
      "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "email": "jczho.mg14@nycu.edu.tw",
      "display_name": "小周"
    }
  },
  "error": null,
  "request_id": "example-request-id"
}
```

The response reflects the persisted value after trimming and update.

---

## 5.7 Error Responses

| Condition | Status | Error Code |
|---|---|---|
| Missing or invalid JWT | `401` | `UNAUTHORIZED` |
| Missing `display_name` field | `400` | `VALIDATION_ERROR` |
| `display_name` is empty or blank | `400` | `VALIDATION_ERROR` |
| `display_name` exceeds maximum length | `400` | `VALIDATION_ERROR` |
| `display_name` is not a string | `400` | `VALIDATION_ERROR` |

---

# 6. Display Name and Fallback Relationship

The `users.display_name` column always holds the current display name for a user.

At first login, if the user has not yet explicitly set a nickname, the backend derives a temporary display name from Cognito JWT claims using this fallback chain:

```text
name
→ preferred_username
→ email local-part
→ "CoTrip User"
```

Once the user calls `PATCH /me` with a chosen display name, that value replaces the fallback and becomes the canonical nickname.

## 6.1 Detecting Whether a Nickname Has Been Explicitly Set

The MVP does not add a separate boolean flag such as `nickname_set` to track whether the user has actively chosen a name.

The recommended MVP approach is:

**Treat any stored value as the current display name, regardless of origin.**

The self-heal logic introduced in Phase 8E-1 ensures that clearly stale values (raw Cognito sub UUIDs or `cognito:username` identifiers) are automatically replaced with a friendlier fallback on login. After `PATCH /me` is used, the stored value will always reflect the user's explicit choice.

If a future phase requires distinguishing between fallback-derived and user-chosen names — for example, to show a "You haven't set a nickname yet" prompt — a simple `nickname_set_at TIMESTAMPTZ` column can be added to the `users` table at that time without disrupting existing behavior.

---

# 7. Impact on Collaborative Surfaces

After a user updates their display name via `PATCH /me`, the new value propagates automatically to all surfaces that live-query `users.display_name`, including:

| Surface | Behavior |
|---|---|
| Authenticated header | Reflects updated display name on next page load |
| Candidate proposer label | Reflects updated name on next candidate list fetch |
| Trip member list | Reflects updated name on next member list fetch |
| Invite preview inviter label | Reflects updated name when invite info is next requested |

No snapshot or denormalization is required for these surfaces in the MVP because all of them join `users.display_name` at query time.

---

# 8. MVP Scope Boundaries

This document covers the MVP User Profile API.

The following features are **out of scope** for this API version:

| Feature | Status |
|---|---|
| Avatar / profile picture | Deferred |
| First-login mandatory nickname onboarding | Deferred |
| Public user profile pages | Deferred |
| Account deletion | Deferred |
| Password or credential management | Not applicable (Cognito-managed) |
| Admin user management | Not applicable |
