# 11 - Lambda Specification: CandidateFunction

## 1. Function Name

```text
CandidateFunction
```

---

## 2. Purpose

This Lambda manages candidate attractions and restaurants.

Supported operations:

- List candidates
- Create candidate
- Update candidate
- Delete candidate

---

## 3. API Routes

| Method | Path |
|---|---|
| `GET` | `/trips/{tripId}/candidates` |
| `POST` | `/trips/{tripId}/candidates` |
| `PATCH` | `/trips/{tripId}/candidates/{candidateId}` |
| `DELETE` | `/trips/{tripId}/candidates/{candidateId}` |

---

## 4. Data Tables Used

| Table | Operation |
|---|---|
| `users` | Resolve current user |
| `trips` | Check trip existence |
| `trip_members` | Authorization |
| `trip_candidates` | CRUD |
| `candidate_votes` | Vote count in list response if implemented through join |

---

## 5. Authorization Rules

| Operation | Rule |
|---|---|
| List candidates | Trip member |
| Create candidate | Trip member |
| Update candidate | Candidate creator or trip owner |
| Delete candidate | Candidate creator or trip owner |

---

## 6. Core Implementation Notes

### 6.1 Supported Categories

MVP allowed values:

```text
attraction
restaurant
```

### 6.2 Candidate List Response

Recommended list response includes:

- Vote count
- Whether current user has voted

This reduces additional frontend round trips.

### 6.3 Update Rules

At least one editable field must be provided in PATCH.

Editable fields:

- category
- name
- address
- note
- source_url

### 6.4 Delete Rules

Recommended MVP strategy:

- Hard delete candidate
- Related votes deleted through FK cascade or repository cleanup

---

## 7. Expected Error Conditions

| Error | Expected Handling |
|---|---|
| Invalid category | `400 VALIDATION_ERROR` |
| Empty candidate name | `400 VALIDATION_ERROR` |
| Candidate not found | `404 NOT_FOUND` |
| Trip not found | `404 NOT_FOUND` |
| Non-member access | `403 FORBIDDEN` |
| Unauthorized update/delete | `403 FORBIDDEN` |

---

## 8. Logging Requirements

Log:

- Request ID
- Route
- User ID
- Trip ID
- Candidate ID when relevant

---

# 9. SAM Test Planning

## 9.1 Unit Tests

Create unit tests for:

- Category validation
- Required name validation
- Creator authorization
- Owner authorization
- Candidate list mapping with vote count

## 9.2 Suggested SAM Event Files

```text
events/candidate/list-candidates.json
events/candidate/create-candidate.json
events/candidate/update-candidate.json
events/candidate/delete-candidate.json
```

## 9.3 Direct Lambda Invocation

```bash
sam local invoke CandidateFunction \
  -e events/candidate/create-candidate.json \
  --env-vars env.local.json
```

## 9.4 Local API Test Sequence

1. Create trip
2. Add attraction candidate
3. Add restaurant candidate
4. List candidates
5. Update one candidate
6. Delete one candidate