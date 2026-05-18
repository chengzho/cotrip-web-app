# 16 - Lambda Specification: UserProfileFunction

## 1. Function Name

```text
UserProfileFunction
```

---

## 2. Purpose

This Lambda manages the current user's CoTrip profile.

Supported operations:

- Read current user's profile
- Update current user's display name

---

## 3. API Routes

| Method | Path |
|---|---|
| `GET` | `/me` |
| `PATCH` | `/me` |

---

## 4. Data Tables Used

| Table | Operation |
|---|---|
| `users` | Read current user / update display name |

---

## 5. Required Shared Helpers

Reuse existing shared modules:

```text
common/auth.py
common/db.py
common/request.py
common/response.py
common/errors.py
common/validation.py
common/repositories/user_repository.py
```

No new repository file is needed for the MVP.  
The existing `user_repository.py` should be extended with the profile update operation (`update_user_display_name` already introduced in Phase 8E-1).

---

## 6. Authorization Rules

| Operation | Rule |
|---|---|
| `GET /me` | Authenticated user only; returns their own profile |
| `PATCH /me` | Authenticated user only; updates their own profile |

There is no cross-user profile access.

---

## 7. Handler Implementation Notes

### 7.1 User Resolution

Both routes must resolve the current user via `resolve_or_create_user()`.

This ensures:

- Lazy user row creation for first-time logins
- Display name self-heal for stale stored values (introduced in Phase 8E-1)

### 7.2 GET /me

Return the resolved user dict directly.

No additional DB query is needed beyond user resolution.

Suggested response shape under `data`:

```json
{
  "user": {
    "user_id": "<uuid>",
    "email": "<email>",
    "display_name": "<display_name>"
  }
}
```

### 7.3 PATCH /me

After resolving the current user:

1. Read `display_name` from the request body.
2. Apply validation:
   - Must be a string.
   - Trim leading/trailing whitespace.
   - Must not be empty after trimming.
   - Must not exceed 50 characters after trimming.
3. Call `update_user_display_name(conn, user_id, trimmed_display_name)`.
4. Return the updated user dict in the same shape as `GET /me`.

### 7.4 Error Handling

Follow the shared error response envelope for all failure cases.

| Condition | Error Class | HTTP Status |
|---|---|---|
| Missing JWT | `UnauthorizedError` | `401` |
| Empty or missing `display_name` | `ValidationError` | `400` |
| `display_name` exceeds 50 characters | `ValidationError` | `400` |
| `display_name` not a string | `ValidationError` | `400` |
| Route not matched | `NotFoundError` | `404` |

---

## 8. SAM Template Requirements

Add `UserProfileFunction` to `backend/template.yaml`:

### 8.1 Function Properties

```yaml
UserProfileFunction:
  Type: AWS::Serverless::Function
  Properties:
    CodeUri: src/user_profile/
    Handler: app.lambda_handler
    # inherit Runtime, Architectures, Environment, VpcConfig, Role from Globals
    Events:
      GetMe:
        Type: HttpApi
        Properties:
          ApiId: !Ref HttpApi
          Method: GET
          Path: /me
          Auth:
            Authorizer: CognitoAuthorizer
      PatchMe:
        Type: HttpApi
        Properties:
          ApiId: !Ref HttpApi
          Method: PATCH
          Path: /me
          Auth:
            Authorizer: CognitoAuthorizer
```

### 8.2 Source Directory

```text
backend/src/user_profile/
└── app.py
```

---

## 9. Repository Extension

`update_user_display_name()` was added to `user_repository.py` in Phase 8E-1.

No further repository additions are required for the MVP User Profile Lambda.

If a `nickname_set_at` timestamp column is added in a future phase, the repository update function should be extended to also set that column.

---

## 10. Routing Table Update

After adding `UserProfileFunction`, update the routing table in `02-api-specification-overview.md`:

| Route Group | Lambda Function |
|---|---|
| `/me` | `UserProfileFunction` |
| `/trips`, `/trips/{tripId}`, `/trips/{tripId}/members` | `TripGroupFunction` |
| `/trips/{tripId}/invites`, `/invites/{inviteToken}` | `InviteFunction` |
| `/trips/{tripId}/candidates`, `/trips/{tripId}/candidates/{candidateId}` | `CandidateFunction` |
| `/candidates/{candidateId}/votes`, `/trips/{tripId}/rankings` | `VoteFunction` |
| `/trips/{tripId}/itinerary`, `/trips/{tripId}/itinerary/generate`, `/trips/{tripId}/itinerary/items/{itemId}` | `ItineraryFunction` |

---

## 11. Testing Requirements

### 11.1 Unit Tests

Create unit test file at:

```text
backend/tests/unit/user_profile/test_user_profile_handler.py
```

Minimum coverage:

| Test case | Description |
|---|---|
| `GET /me` success | Returns 200 with correct user payload |
| `PATCH /me` success | Returns 200 with updated display name |
| `PATCH /me` missing display_name | Returns 400 with VALIDATION_ERROR |
| `PATCH /me` empty display_name | Returns 400 with VALIDATION_ERROR |
| `PATCH /me` display_name too long | Returns 400 with VALIDATION_ERROR |
| `PATCH /me` whitespace-only display_name | Returns 400 with VALIDATION_ERROR |
| Route not matched | Returns 404 |
| Unexpected exception | Returns 500 with INTERNAL_SERVER_ERROR |

### 11.2 Integration Tests

No new integration test flow is required at MVP launch.

The `GET /me` and `PATCH /me` routes can be verified as part of future end-to-end flows if a smoke test script is later added.

---

## 12. Frontend Integration

After the Lambda is deployed, the frontend should:

1. Call `GET /me` after login to confirm the current display name.
2. Display an edit entry point in the authenticated header user area (see `15-api-user-profile.md` section 7 and `17-ui-nickname.md` when written).
3. Call `PATCH /me` on form submission and refresh the displayed name without requiring a full page reload.

---

## 13. MVP Scope Boundaries

This Lambda covers only the current user's self-service profile.

Out of scope:

| Feature | Status |
|---|---|
| Avatar upload | Deferred |
| First-login onboarding flow | Deferred |
| Admin user management | Not applicable |
| Cross-user profile read | Not applicable |
