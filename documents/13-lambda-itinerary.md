# 13 - Lambda Specification: ItineraryFunction

## 1. Function Name

```text
ItineraryFunction
```

---

## 2. Purpose

This Lambda manages itinerary generation and itinerary item editing.

Supported operations:

- Generate itinerary
- Get current itinerary
- Update itinerary item
- Delete itinerary item

---

## 3. API Routes

| Method | Path |
|---|---|
| `POST` | `/trips/{tripId}/itinerary/generate` |
| `GET` | `/trips/{tripId}/itinerary` |
| `PATCH` | `/trips/{tripId}/itinerary/items/{itemId}` |
| `DELETE` | `/trips/{tripId}/itinerary/items/{itemId}` |

---

## 4. Data Tables Used

| Table | Operation |
|---|---|
| `trips` | Read trip date range |
| `trip_members` | Authorization |
| `trip_candidates` | Read candidates |
| `candidate_votes` | Ranking input |
| `itinerary_items` | Insert / list / update / delete |

---

## 5. Authorization Rules

| Operation | Rule |
|---|---|
| Generate itinerary | Trip member |
| View itinerary | Trip member |
| Update itinerary item | Trip member |
| Delete itinerary item | Trip member |

Optional future refinement:

- Restrict generate/edit/delete to trip owner

---

## 6. MVP Itinerary Generation Logic

### 6.1 Inputs

- Trip date range
- Candidate places
- Candidate vote counts

### 6.2 Day Count

```text
day_count = end_date - start_date + 1
```

### 6.3 Slot Strategy

Each day may contain:

```text
morning
lunch
afternoon
dinner
```

Optional future expansion:

```text
evening
```

### 6.4 Allocation Strategy

Recommended MVP:

1. Sort attractions by vote count desc.
2. Sort restaurants by vote count desc.
3. Fill:
   - morning → attraction
   - lunch → restaurant
   - afternoon → attraction
   - dinner → restaurant
4. Stop when candidates are exhausted.

### 6.5 Existing Itinerary Policy

If existing itinerary items exist:

- If `overwrite_existing = false`:
  - Return `409 ITINERARY_ALREADY_EXISTS`
- If `overwrite_existing = true`:
  - Delete existing itinerary items
  - Generate new items

This entire operation must be transactional.

---

## 7. Manual Item Editing

PATCH route may update:

- day number
- slot
- title
- note
- sort order

Delete route removes one itinerary item.

---

## 8. Expected Error Conditions

| Error | Expected Handling |
|---|---|
| Trip not found | `404 NOT_FOUND` |
| User not a member | `403 FORBIDDEN` |
| No candidates available | `409 CONFLICT` or backend-defined validation error |
| Existing itinerary blocks generation | `409 ITINERARY_ALREADY_EXISTS` |
| Itinerary item not found | `404 NOT_FOUND` |

---

## 9. Logging Requirements

Log:

- Request ID
- Route
- User ID
- Trip ID
- Number of generated itinerary items

---

# 10. SAM Test Planning

## 10.1 Unit Tests

Create unit tests for:

- Day count calculation
- Ranking input mapping
- Slot distribution
- Existing itinerary conflict
- Overwrite behavior
- Item update validation

## 10.2 Suggested SAM Event Files

```text
events/itinerary/generate-itinerary.json
events/itinerary/get-itinerary.json
events/itinerary/update-item.json
events/itinerary/delete-item.json
```

## 10.3 Direct Lambda Invocation

```bash
sam local invoke ItineraryFunction \
  -e events/itinerary/generate-itinerary.json \
  --env-vars env.local.json
```

## 10.4 Local API Test Sequence

1. Create trip with multi-day range
2. Add candidate attractions and restaurants
3. Add votes
4. Generate itinerary
5. View itinerary
6. Update one item
7. Delete one item