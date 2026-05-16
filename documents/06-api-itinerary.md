# 06 - API Specification: Itinerary

## 1. Purpose

This document specifies APIs handled by:

```text
ItineraryFunction
```

The itinerary domain allows trip members to:

- Generate a simple shared itinerary from voted candidate places
- View the current itinerary
- Update itinerary items
- Delete itinerary items

The CoTrip MVP does **not** include reminder or notification APIs.

---

# 2. Endpoint Summary

| Method | Path | Description |
|---|---|---|
| `POST` | `/trips/{tripId}/itinerary/generate` | Generate itinerary |
| `GET` | `/trips/{tripId}/itinerary` | Get itinerary |
| `PATCH` | `/trips/{tripId}/itinerary/items/{itemId}` | Update itinerary item |
| `DELETE` | `/trips/{tripId}/itinerary/items/{itemId}` | Delete itinerary item |

---

# 3. Shared Authorization Policy

All itinerary endpoints require authentication.

Unless explicitly changed later, the MVP policy is:

| Action | Authorization |
|---|---|
| Generate itinerary | Any trip member |
| View itinerary | Any trip member |
| Update itinerary item | Any trip member |
| Delete itinerary item | Any trip member |

The implementation must consistently enforce trip membership checks.

---

# 4. POST `/trips/{tripId}/itinerary/generate`

## 4.1 Description

Generate a simple itinerary based on:

- Trip date range
- Candidate attractions
- Candidate restaurants
- Current vote ranking

The generated itinerary is stored in the database as itinerary items.

---

## 4.2 Authentication

Required.

The request must include:

```http
Authorization: Bearer <JWT>
```

---

## 4.3 Authorization

The authenticated user must be a member of the target trip.

---

## 4.4 Path Parameters

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `tripId` | UUID string | Required | Target trip identifier |

---

## 4.5 Request Body

| Field | Type | Required | Notes |
|---|---|---|---|
| `overwrite_existing` | boolean | Optional | Default: `false` |

---

## 4.6 Example Request

```json
{
  "overwrite_existing": true
}
```

---

## 4.7 Generation Behavior

The MVP itinerary generation logic should be simple, deterministic, and implementation-friendly.

Recommended generation logic:

1. Load the trip date range.
2. Calculate the number of trip days.
3. Fetch candidate places for the trip.
4. Join or aggregate vote counts.
5. Sort candidate places by:
   - vote count descending
   - creation time ascending as deterministic tie-breaker
6. Split candidates by category:
   - `attraction`
   - `restaurant`
7. Fill default day slots using a simple pattern:
   - `morning` → attraction
   - `lunch` → restaurant
   - `afternoon` → attraction
   - `dinner` → restaurant
8. Continue assigning ranked candidates until:
   - all day slots are filled, or
   - available candidates are exhausted
9. Store the generated itinerary in `itinerary_items`.
10. Return the complete grouped itinerary response.

---

## 4.8 Existing Itinerary Conflict Rule

If itinerary items already exist for the trip:

### Case A — `overwrite_existing = false`
Return:

```text
409 Conflict
```

with error code:

```text
ITINERARY_ALREADY_EXISTS
```

### Case B — `overwrite_existing = true`
The backend shall:

1. Remove existing itinerary items for the trip.
2. Generate a new itinerary.
3. Insert the newly generated itinerary items.

This operation must be handled transactionally.

---

## 4.9 Candidate Availability Rule

If no usable candidate places exist:

- The backend should return a business-level error rather than generating an empty itinerary.

Recommended response:

```text
409 Conflict
```

with error code:

```text
CONFLICT
```

and a user-understandable message such as:

```text
No candidate places are available for itinerary generation.
```

---

## 4.10 Success Response

Status:

```text
200 OK
```

```json
{
  "success": true,
  "data": {
    "itinerary": {
      "trip_id": "trip-uuid",
      "days": [
        {
          "day_number": 1,
          "date": "2026-08-20",
          "items": [
            {
              "item_id": "item-uuid-1",
              "slot": "morning",
              "title": "Senso-ji Temple",
              "candidate_id": "candidate-uuid-1",
              "category": "attraction",
              "note": "Historic temple district.",
              "sort_order": 1
            },
            {
              "item_id": "item-uuid-2",
              "slot": "lunch",
              "title": "Gyukatsu Motomura",
              "candidate_id": "candidate-uuid-2",
              "category": "restaurant",
              "note": "Highly voted lunch option.",
              "sort_order": 2
            }
          ]
        },
        {
          "day_number": 2,
          "date": "2026-08-21",
          "items": [
            {
              "item_id": "item-uuid-3",
              "slot": "morning",
              "title": "Meiji Shrine",
              "candidate_id": "candidate-uuid-3",
              "category": "attraction",
              "note": null,
              "sort_order": 1
            }
          ]
        }
      ]
    }
  },
  "error": null,
  "request_id": "request-id"
}
```

---

## 4.11 Expected Error Cases

| Scenario | Status | Error Code |
|---|---|---|
| Trip not found | `404` | `NOT_FOUND` |
| User not a trip member | `403` | `FORBIDDEN` |
| Existing itinerary blocks generation | `409` | `ITINERARY_ALREADY_EXISTS` |
| No candidate places available | `409` | `CONFLICT` |
| Invalid `overwrite_existing` value | `400` | `VALIDATION_ERROR` |

---

# 5. GET `/trips/{tripId}/itinerary`

## 5.1 Description

Return the current itinerary for a trip.

The response must group itinerary items by day.

---

## 5.2 Authentication

Required.

---

## 5.3 Authorization

The authenticated user must be a member of the target trip.

---

## 5.4 Path Parameters

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `tripId` | UUID string | Required | Target trip identifier |

---

## 5.5 Query Parameters

No query parameters are required in the MVP.

---

## 5.6 Success Response

Status:

```text
200 OK
```

```json
{
  "success": true,
  "data": {
    "itinerary": {
      "trip_id": "trip-uuid",
      "days": [
        {
          "day_number": 1,
          "date": "2026-08-20",
          "items": [
            {
              "item_id": "item-uuid-1",
              "slot": "morning",
              "title": "Senso-ji Temple",
              "candidate_id": "candidate-uuid-1",
              "category": "attraction",
              "note": "Historic temple district.",
              "sort_order": 1
            },
            {
              "item_id": "item-uuid-2",
              "slot": "lunch",
              "title": "Gyukatsu Motomura",
              "candidate_id": "candidate-uuid-2",
              "category": "restaurant",
              "note": "Highly voted lunch option.",
              "sort_order": 2
            }
          ]
        }
      ]
    }
  },
  "error": null,
  "request_id": "request-id"
}
```

---

## 5.7 Empty Itinerary Response

If the trip exists and the user is authorized, but no itinerary items have been generated yet, return:

```text
200 OK
```

```json
{
  "success": true,
  "data": {
    "itinerary": {
      "trip_id": "trip-uuid",
      "days": []
    }
  },
  "error": null,
  "request_id": "request-id"
}
```

This supports a frontend empty state such as:

```text
尚未產生行程表
```

---

## 5.8 Expected Error Cases

| Scenario | Status | Error Code |
|---|---|---|
| Trip not found | `404` | `NOT_FOUND` |
| User not a trip member | `403` | `FORBIDDEN` |

---

# 6. PATCH `/trips/{tripId}/itinerary/items/{itemId}`

## 6.1 Description

Update a single itinerary item.

This endpoint supports lightweight manual adjustments after the itinerary has been generated.

---

## 6.2 Authentication

Required.

---

## 6.3 Authorization

The authenticated user must be a member of the target trip.

---

## 6.4 Path Parameters

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `tripId` | UUID string | Required | Target trip identifier |
| `itemId` | UUID string | Required | Target itinerary item identifier |

---

## 6.5 Request Body

At least one editable field must be provided.

| Field | Type | Required | Notes |
|---|---|---|---|
| `day_number` | integer | Optional | Must be positive |
| `slot` | string | Optional | Allowed values listed below |
| `title` | string | Optional | Updated display title |
| `note` | string | Optional | Updated note; may be null or empty based on final implementation |
| `sort_order` | integer | Optional | Must be positive |

---

## 6.6 Allowed Slot Values

```text
morning
lunch
afternoon
dinner
evening
```

The MVP UI may primarily use:

```text
morning
lunch
afternoon
dinner
```

but the backend may support `evening` as a valid optional slot.

---

## 6.7 Validation Rules

- Request body must not be empty.
- `day_number`, if provided, must be a positive integer.
- `sort_order`, if provided, must be a positive integer.
- `slot`, if provided, must be one of the supported enum values.
- `title`, if provided, must not be an empty string.

---

## 6.8 Example Request

```json
{
  "slot": "afternoon",
  "title": "Tokyo Skytree",
  "note": "Moved to later in the day.",
  "sort_order": 3
}
```

---

## 6.9 Success Response

Status:

```text
200 OK
```

```json
{
  "success": true,
  "data": {
    "item": {
      "item_id": "item-uuid",
      "trip_id": "trip-uuid",
      "day_number": 1,
      "slot": "afternoon",
      "title": "Tokyo Skytree",
      "candidate_id": "candidate-uuid",
      "category": "attraction",
      "note": "Moved to later in the day.",
      "sort_order": 3
    }
  },
  "error": null,
  "request_id": "request-id"
}
```

---

## 6.10 Expected Error Cases

| Scenario | Status | Error Code |
|---|---|---|
| Trip not found | `404` | `NOT_FOUND` |
| Item not found | `404` | `NOT_FOUND` |
| User not a trip member | `403` | `FORBIDDEN` |
| Empty PATCH body | `400` | `VALIDATION_ERROR` |
| Invalid slot | `400` | `VALIDATION_ERROR` |
| Invalid positive integer field | `400` | `VALIDATION_ERROR` |

---

# 7. DELETE `/trips/{tripId}/itinerary/items/{itemId}`

## 7.1 Description

Delete one itinerary item from the trip itinerary.

---

## 7.2 Authentication

Required.

---

## 7.3 Authorization

The authenticated user must be a member of the target trip.

---

## 7.4 Path Parameters

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `tripId` | UUID string | Required | Target trip identifier |
| `itemId` | UUID string | Required | Target itinerary item identifier |

---

## 7.5 Request Body

No request body is required.

---

## 7.6 Success Response Option A

Status:

```text
204 No Content
```

No response body.

---

## 7.7 Success Response Option B

If the implementation prefers to keep the standard JSON response envelope, use:

Status:

```text
200 OK
```

```json
{
  "success": true,
  "data": {
    "deleted_item_id": "item-uuid"
  },
  "error": null,
  "request_id": "request-id"
}
```

### Recommendation

For consistency with the project-wide response envelope, the MVP may prefer:

```text
200 OK with JSON response body
```

The final implementation must remain consistent across similar DELETE endpoints.

---

## 7.8 Expected Error Cases

| Scenario | Status | Error Code |
|---|---|---|
| Trip not found | `404` | `NOT_FOUND` |
| Item not found | `404` | `NOT_FOUND` |
| User not a trip member | `403` | `FORBIDDEN` |

---

# 8. Frontend Integration Notes

The frontend itinerary page should support the following states:

## 8.1 Empty State

When:

```text
GET /trips/{tripId}/itinerary
```

returns:

```json
"days": []
```

the frontend should show a Traditional Chinese empty state such as:

```text
尚未產生行程表
```

and provide a primary CTA to generate one.

---

## 8.2 Existing Itinerary Conflict

If:

```text
POST /trips/{tripId}/itinerary/generate
```

returns:

```text
ITINERARY_ALREADY_EXISTS
```

the frontend may ask the user whether to regenerate with overwrite.

---

## 8.3 Successful Generation

After successful generation:

- Navigate or remain on the itinerary page
- Render the returned grouped itinerary days
- Show the newly generated trip plan immediately

---

# 9. Itinerary MVP Scope Summary

The CoTrip MVP itinerary API includes:

| Capability | Included? |
|---|---|
| Generate itinerary from votes | Yes |
| Read current itinerary | Yes |
| Update itinerary item | Yes |
| Delete itinerary item | Yes |
| Reminder scheduling | No |
| Notification-related endpoints | No |

Reminder and notification APIs must not be implemented in the CoTrip MVP.