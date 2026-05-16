# 12 - Lambda Specification: VoteFunction

## 1. Function Name

```text
VoteFunction
```

---

## 2. Purpose

This Lambda manages candidate voting and ranking.

Supported operations:

- Add current user's vote
- Remove current user's vote
- Return ranked candidates within a trip

---

## 3. API Routes

| Method | Path |
|---|---|
| `POST` | `/candidates/{candidateId}/votes` |
| `DELETE` | `/candidates/{candidateId}/votes` |
| `GET` | `/trips/{tripId}/rankings` |

---

## 4. Data Tables Used

| Table | Operation |
|---|---|
| `users` | Resolve current user |
| `trip_candidates` | Determine candidate ownership and trip |
| `trip_members` | Authorization |
| `candidate_votes` | Insert / delete / aggregate |

---

## 5. Authorization Rules

| Operation | Rule |
|---|---|
| Vote | User must be member of owning trip |
| Unvote | User must be member of owning trip |
| View ranking | User must be member of trip |

---

## 6. Core Implementation Notes

### 6.1 MVP Vote Model

The MVP uses simple upvote logic.

Each user may vote once per candidate.

Database uniqueness:

```text
(candidate_id, user_id)
```

### 6.2 Duplicate Vote Behavior

Recommended behavior:

Option A:

```text
Return 409 ALREADY_EXISTS
```

Option B:

```text
Treat repeated POST as idempotent success
```

The final implementation must choose one behavior and remain consistent.

Recommended MVP choice:

```text
Idempotent success is acceptable for better frontend UX.
```

### 6.3 Rankings

Ranking order:

1. Higher vote count first
2. Earlier candidate creation time as deterministic tie breaker

---

## 7. Expected Error Conditions

| Error | Expected Handling |
|---|---|
| Candidate not found | `404 NOT_FOUND` |
| User not trip member | `403 FORBIDDEN` |
| Duplicate vote if non-idempotent policy used | `409 ALREADY_EXISTS` |
| Vote deletion for missing vote | Backend policy, but must be consistent |

---

## 8. Logging Requirements

Log:

- Request ID
- Route
- Candidate ID
- Trip ID when derived
- User ID

---

# 9. SAM Test Planning

## 9.1 Unit Tests

Create unit tests for:

- Candidate membership resolution
- Vote insert logic
- Duplicate vote behavior
- Vote deletion behavior
- Ranking sort order
- Category filter if implemented

## 9.2 Suggested SAM Event Files

```text
events/vote/create-vote.json
events/vote/delete-vote.json
events/vote/get-rankings.json
```

## 9.3 Direct Lambda Invocation

```bash
sam local invoke VoteFunction \
  -e events/vote/create-vote.json \
  --env-vars env.local.json
```

## 9.4 Local API Test Sequence

1. Create trip
2. Add multiple candidates
3. Vote for candidates
4. Fetch rankings
5. Remove vote
6. Fetch rankings again