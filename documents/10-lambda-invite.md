# 10 - Lambda Specification: InviteFunction

## 1. Function Name

```text
InviteFunction
```

---

## 2. Purpose

This Lambda manages invite workflows:

- Create trip invitation token
- Preview invite information
- Join a trip through invite token

---

## 3. API Routes

| Method | Path |
|---|---|
| `POST` | `/trips/{tripId}/invites` |
| `GET` | `/invites/{inviteToken}` |
| `POST` | `/invites/{inviteToken}/join` |

---

## 4. Data Tables Used

| Table | Operation |
|---|---|
| `users` | Resolve current authenticated user |
| `trips` | Read trip summary |
| `trip_members` | Check ownership / insert member |
| `trip_invites` | Create / read / validate invite |

---

## 5. Authorization Rules

| Operation | Rule |
|---|---|
| Create invite | Owner only |
| Preview invite | Public |
| Join via invite | Authenticated user only |

---

## 6. Token Security Requirements

### 6.1 Token Generation

Generate a cryptographically strong raw token.

### 6.2 Token Storage

Store:

```text
SHA-256 hash of token
```

Do not store the raw token.

### 6.3 Invite URL

Returned invite URL format:

```text
{FRONTEND_BASE_URL}/join/{rawInviteToken}
```

---

## 7. Core Implementation Notes

### 7.1 Invite Preview

Preview must validate:

- Token exists
- Invite not expired
- Invite not revoked
- `used_count < max_uses`

Then return trip summary.

### 7.2 Join Trip Transaction

Joining must be handled transactionally:

1. Resolve invite from token hash.
2. Validate invite state.
3. Resolve current user.
4. Check membership.
5. Insert into `trip_members`.
6. Increment `trip_invites.used_count`.

### 7.3 Already Joined Policy

If the user already belongs to the trip:

Recommended MVP behavior:

```text
Return 409 ALREADY_EXISTS
```

---

## 8. Expected Error Conditions

| Error | Expected Handling |
|---|---|
| Invite not found | `404 NOT_FOUND` |
| Invite expired | `400 INVITE_EXPIRED` |
| Invite revoked | `400 INVITE_REVOKED` |
| Usage limit reached | `400 INVITE_USAGE_LIMIT_REACHED` |
| Already member | `409 ALREADY_EXISTS` |
| Non-owner creating invite | `403 FORBIDDEN` |

---

## 9. Logging Requirements

Log:

- Request ID
- Route
- Invite ID when available
- Trip ID when available
- User ID for authenticated routes

Do not log:

- Raw invite token
- Invite URL containing raw token

---

# 10. SAM Test Planning

## 10.1 Unit Tests

Create unit tests for:

- Token hashing
- Invite expiration logic
- Revocation logic
- Usage limit logic
- Join transaction workflow
- Owner-only invite creation

## 10.2 Suggested SAM Event Files

```text
events/invite/create-invite.json
events/invite/preview-invite.json
events/invite/join-invite.json
```

## 10.3 Local Invocation Examples

```bash
sam local invoke InviteFunction \
  -e events/invite/create-invite.json \
  --env-vars env.local.json
```

```bash
sam local invoke InviteFunction \
  -e events/invite/preview-invite.json \
  --env-vars env.local.json
```

## 10.4 Local API Testing

```bash
sam build
sam local start-api --env-vars env.local.json
```

Suggested API sequence:

1. Create a trip
2. Create invite
3. Copy returned raw invite token
4. Preview invite
5. Join invite

---

## 11. Integration Test Cases

After deployment, verify:

- A logged-out user can preview invite
- A logged-in user can join invite
- An expired invite fails
- A non-owner cannot create invite