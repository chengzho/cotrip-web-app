# 06 - API Specification: Itinerary and Reminder

## 1. Purpose

This document specifies APIs handled by:

```text
ItineraryFunction
NotificationFunction
```

The system allows members to:

- Generate a simple itinerary from ranked candidates
- View current itinerary
- Update itinerary items
- Delete itinerary items
- Create trip reminders
- View reminders
- Delete reminders

---

# 2. Endpoint Summary

## 2.1 ItineraryFunction

| Method | Path | Description |
|---|---|---|
| `POST` | `/trips/{tripId}/itinerary/generate` | Generate itinerary |
| `GET` | `/trips/{tripId}/itinerary` | Get itinerary |
| `PATCH` | `/trips/{tripId}/itinerary/items/{itemId}` | Update itinerary item |
| `DELETE` | `/trips/{tripId}/itinerary/items/{itemId}` | Delete itinerary item |

## 2.2 NotificationFunction

| Method | Path | Description |
|---|---|---|
| `GET` | `/trips/{tripId}/reminders` | List trip reminders |
| `POST` | `/trips/{tripId}/reminders` | Create reminder |
| `DELETE` | `/trips/{tripId}/reminders/{reminderId}` | Delete reminder |

---

# 3. POST `/trips/{tripId}/itinerary/generate`

## 3.1 Description

Generate a simple itinerary based on:

- Trip date range
- Ranked attractions
- Ranked restaurants

## 3.2 Authentication

Required.

## 3.3 Authorization

The authenticated user must be a trip member.

Recommended MVP policy:

- Any trip member can generate itinerary
- If desired later, restrict to owner only

## 3.4 Path Parameters

| Parameter | Type | Required |
|---|---|---|
| `tripId` | UUID string | Required |

## 3.5 Request Body

| Field | Type | Required | Notes |
|---|---|---|---|
| `overwrite_existing` | boolean | Optional | Default: `false` |

## 3.6 Generation Behavior

Recommended MVP generation logic:

1. Calculate trip day count.
2. Fetch ranked attractions and restaurants.
3. Fill rough slots per day:
   - morning
   - lunch
   - afternoon
   - dinner
4. Prefer attractions for morning/afternoon.
5. Prefer restaurants for lunch/dinner.
6. Store generated rows in `itinerary_items`.

## 3.7 Conflict Rule

If itinerary already exists and `overwrite_existing = false`:

- Return `409 Conflict`
- Error code: `ITINERARY_ALREADY_EXISTS`

## 3.8 Example Request

```json
{
  "overwrite_existing": true
}
```

## 3.9 Success Response

```json
{
  "success": true,
  "data": {
    "itinerary": {
      "trip_id": "trip-uuid",
      "days": [
        {
          "day_number": 1,
          "items": [
            {
              "item_id": "item-uuid-1",
              "slot": "morning",
              "title": "Senso-ji Temple",
              "candidate_id": "candidate-uuid-1",
              "sort_order": 1
            },
            {
              "item_id": "item-uuid-2",
              "slot": "lunch",
              "title": "Gyukatsu Motomura",
              "candidate_id": "candidate-uuid-2",
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

# 4. GET `/trips/{tripId}/itinerary`

## 4.1 Description

Return the current trip itinerary.

## 4.2 Authentication

Required.

## 4.3 Authorization

The authenticated user must be a trip member.

## 4.4 Success Response

```json
{
  "success": true,
  "data": {
    "itinerary": {
      "trip_id": "trip-uuid",
      "days": [
        {
          "day_number": 1,
          "items": [
            {
              "item_id": "item-uuid",
              "slot": "morning",
              "title": "Tokyo Skytree",
              "note": null,
              "candidate_id": "candidate-uuid",
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

# 5. PATCH `/trips/{tripId}/itinerary/items/{itemId}`

## 5.1 Description

Update a single itinerary item.

## 5.2 Authentication

Required.

## 5.3 Authorization

Default MVP policy:

- Any trip member can update itinerary
- If desired later, restrict to owner only

## 5.4 Path Parameters

| Parameter | Type | Required |
|---|---|---|
| `tripId` | UUID string | Required |
| `itemId` | UUID string | Required |

## 5.5 Request Body

At least one field must be provided.

| Field | Type | Required |
|---|---|---|
| `day_number` | integer | Optional |
| `slot` | string | Optional |
| `title` | string | Optional |
| `note` | string | Optional |
| `sort_order` | integer | Optional |

---

# 6. DELETE `/trips/{tripId}/itinerary/items/{itemId}`

## 6.1 Description

Delete one itinerary item.

## 6.2 Authentication

Required.

## 6.3 Authorization

The authenticated user must be a trip member.

---

# 7. GET `/trips/{tripId}/reminders`

## 7.1 Description

Return reminder schedules configured for the trip.

## 7.2 Authentication

Required.

## 7.3 Authorization

The authenticated user must be a trip member.

## 7.4 Success Response

```json
{
  "success": true,
  "data": {
    "reminders": [
      {
        "id": "reminder-uuid",
        "reminder_type": "seven_days_before",
        "scheduled_at": "2026-08-13T09:00:00+08:00",
        "status": "scheduled"
      }
    ]
  },
  "error": null,
  "request_id": "request-id"
}
```

---

# 8. POST `/trips/{tripId}/reminders`

## 8.1 Description

Create a pre-trip reminder schedule.

## 8.2 Authentication

Required.

## 8.3 Authorization

Recommended MVP policy:

- Owner only

## 8.4 Path Parameters

| Parameter | Type | Required |
|---|---|---|
| `tripId` | UUID string | Required |

## 8.5 Request Body

| Field | Type | Required | Notes |
|---|---|---|---|
| `reminder_type` | string | Required | `seven_days_before` or `one_day_before` |

## 8.6 Backend Behavior

1. Load trip date.
2. Compute reminder scheduled time.
3. Insert reminder row into `trip_reminders`.
4. Create EventBridge Scheduler one-time schedule.
5. Save `scheduler_name`.
6. Return reminder summary.

## 8.7 Example Request

```json
{
  "reminder_type": "seven_days_before"
}
```

## 8.8 Success Response

```json
{
  "success": true,
  "data": {
    "reminder": {
      "id": "reminder-uuid",
      "reminder_type": "seven_days_before",
      "scheduled_at": "2026-08-13T09:00:00+08:00",
      "status": "scheduled"
    }
  },
  "error": null,
  "request_id": "request-id"
}
```

---

# 9. DELETE `/trips/{tripId}/reminders/{reminderId}`

## 9.1 Description

Cancel and remove a reminder schedule.

## 9.2 Authentication

Required.

## 9.3 Authorization

Recommended MVP policy:

- Owner only

## 9.4 Backend Behavior

1. Confirm reminder belongs to trip.
2. Delete or disable EventBridge Scheduler schedule.
3. Mark DB reminder status as `cancelled` or delete according to final implementation choice.
4. Return successful result.

---

# 10. Expected Error Cases

| Scenario | Status | Error Code |
|---|---|---|
| Itinerary already exists | `409` | `ITINERARY_ALREADY_EXISTS` |
| No candidates found | `400` or `409` | `CONFLICT` |
| Reminder type invalid | `400` | `VALIDATION_ERROR` |
| Duplicate reminder type | `409` | `ALREADY_EXISTS` |
| Reminder not found | `404` | `NOT_FOUND` |
| Non-owner modifies reminders | `403` | `FORBIDDEN` |