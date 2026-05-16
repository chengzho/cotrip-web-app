# 14 - Lambda Specification: NotificationFunction

## 1. Function Name

```text
NotificationFunction
```

---

## 2. Purpose

This Lambda handles two event categories:

1. API Gateway requests for reminder schedule management
2. EventBridge Scheduler invocation for actual reminder email sending

---

# 3. Invocation Modes

## 3.1 API Gateway Invocation

Routes:

| Method | Path |
|---|---|
| `GET` | `/trips/{tripId}/reminders` |
| `POST` | `/trips/{tripId}/reminders` |
| `DELETE` | `/trips/{tripId}/reminders/{reminderId}` |

## 3.2 EventBridge Scheduler Invocation

Triggered event type:

```text
Scheduled reminder execution event
```

---

# 4. Data Tables Used

| Table | Operation |
|---|---|
| `trips` | Read trip date/title |
| `trip_members` | Read reminder recipients or authorize access |
| `users` | Retrieve recipient emails |
| `trip_reminders` | Create / list / delete / mark sent |

---

# 5. External AWS Services Used

| AWS Service | Usage |
|---|---|
| EventBridge Scheduler | Create / delete reminder schedules |
| Amazon SES | Send reminder email |

---

# 6. Reminder Types

MVP supports:

```text
seven_days_before
one_day_before
```

---

# 7. API Authorization Rules

| Operation | Rule |
|---|---|
| List reminders | Trip member |
| Create reminder | Trip owner |
| Delete reminder | Trip owner |

---

# 8. Core Implementation Notes

## 8.1 Create Reminder

Steps:

1. Validate trip existence.
2. Validate caller is owner.
3. Validate reminder type.
4. Calculate `scheduled_at`.
5. Prevent duplicate `(trip_id, reminder_type)` schedule.
6. Insert reminder row with status:
   ```text
   scheduled
   ```
7. Create EventBridge Scheduler one-time schedule targeting `NotificationFunction`.
8. Save `scheduler_name`.

## 8.2 Delete Reminder

Steps:

1. Validate reminder belongs to trip.
2. Validate owner permission.
3. Delete or disable EventBridge Scheduler schedule.
4. Mark reminder row as:
   ```text
   cancelled
   ```
   or apply final agreed deletion policy.

## 8.3 Scheduled Reminder Execution

When triggered by EventBridge Scheduler:

1. Validate reminder/event payload.
2. Load reminder row.
3. Confirm status is `scheduled`.
4. Load trip and recipient data.
5. Build reminder email content.
6. Send via SES.
7. Mark reminder as:
   ```text
   sent
   ```
8. If sending fails:
   - Log failure
   - Mark reminder as `failed` if final implementation requires it

---

# 9. Suggested Scheduled Event Payload

```json
{
  "event_type": "trip_reminder",
  "reminder_id": "reminder-uuid",
  "trip_id": "trip-uuid"
}
```

---

# 10. Reminder Time Calculation

Recommended default reminder send time:

```text
09:00 Asia/Taipei
```

This can be implemented later as configuration.

For MVP, scheduled time must be deterministic and documented in code.

---

# 11. Expected Error Conditions

| Error | Expected Handling |
|---|---|
| Invalid reminder type | `400 VALIDATION_ERROR` |
| Duplicate reminder | `409 ALREADY_EXISTS` |
| Reminder not found | `404 NOT_FOUND` |
| Non-owner create/delete | `403 FORBIDDEN` |
| Scheduler creation failure | `500 INTERNAL_SERVER_ERROR` with logged context |
| SES send failure | Log and update status according to implementation policy |

---

# 12. Logging Requirements

Log:

- Request ID for API requests
- Event type for Scheduler invocations
- Reminder ID
- Trip ID
- Final reminder status

Do not log:

- SES credentials
- Raw database secrets
- Full email body if it contains user data

---

# 13. SAM Test Planning

## 13.1 Unit Tests

Create unit tests for:

- Reminder time calculation
- Duplicate reminder detection
- Scheduler create payload generation
- Scheduler deletion path
- Email message template generation
- Scheduled event dispatch

## 13.2 Suggested SAM Event Files

```text
events/notification/list-reminders.json
events/notification/create-reminder.json
events/notification/delete-reminder.json
events/notification/scheduled-reminder.json
```

## 13.3 Direct API-Mode Invocation

```bash
sam local invoke NotificationFunction \
  -e events/notification/create-reminder.json \
  --env-vars env.local.json
```

## 13.4 Direct Scheduled-Mode Invocation

```bash
sam local invoke NotificationFunction \
  -e events/notification/scheduled-reminder.json \
  --env-vars env.local.json
```

## 13.5 Local Integration Limits

Actual creation of EventBridge Scheduler schedules and actual SES email delivery must be validated in deployed AWS integration testing.

Local tests should focus on:

- Request validation
- Correct AWS SDK call preparation or mocking
- Reminder business logic