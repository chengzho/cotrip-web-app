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

### 6.2 Vote and Unvote Idempotency Policy

The CoTrip MVP uses idempotent behavior for both voting and unvoting.

#### Repeated Vote Request

If the authenticated user sends:

```text
POST /candidates/{candidateId}/votes
```

for a candidate they already voted for, the function shall:

- keep the existing vote unchanged
- return success
- return the current state:
  - `voted = true`
  - current `vote_count`

This must not return `409 ALREADY_EXISTS`.

#### Repeated Unvote Request

If the authenticated user sends:

```text
DELETE /candidates/{candidateId}/votes
```

for a candidate they have not voted for, the function shall:

- keep the database unchanged
- return success
- return the current state:
  - `voted = false`
  - current `vote_count`

This must not fail merely because the vote row does not exist.

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
| Invalid candidate-to-trip relationship if detected | `404 NOT_FOUND` or `403 FORBIDDEN`, depending on final lookup strategy |

Duplicate vote requests and repeated unvote requests are **not** error conditions in the MVP.  
They must return successful idempotent responses.

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
- Idempotent repeated vote behavior
- Vote deletion behavior
- Idempotent repeated unvote behavior
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