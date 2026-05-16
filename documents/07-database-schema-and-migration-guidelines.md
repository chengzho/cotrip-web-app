# 07 - Database Schema and Migration Guidelines

## 1. Purpose

This document defines the PostgreSQL data model for the Collaborative Travel Planning App.

Claude Code must treat this document as the single source of truth when:

- Creating SQL migrations
- Implementing repository/query logic
- Designing joins and constraints
- Writing unit or integration tests that rely on schema structure

---

# 2. Database Choice

The system uses:

```text
Amazon RDS for PostgreSQL
```

The schema is relational because the system contains:

- User-to-trip membership
- Trip-to-candidate ownership
- Candidate-to-vote aggregation
- Trip-to-itinerary items
- Trip-to-reminder schedules

---

# 3. Naming Conventions

## 3.1 Tables

Use:

```text
snake_case
plural noun
```

Examples:

```text
users
trips
trip_members
```

## 3.2 Columns

Use:

```text
snake_case
```

Examples:

```text
created_at
trip_id
candidate_id
```

## 3.3 Timestamps

Use timezone-aware timestamps:

```text
TIMESTAMPTZ
```

## 3.4 UUIDs

All primary business entities use UUID identifiers.

UUID generation strategy may be:

- Application-generated UUIDs, preferred for portability
- Database-generated UUIDs only if migration explicitly configures support

---

# 4. Entity Summary

| Table | Purpose |
|---|---|
| `users` | Application-level user profile mapped to Cognito |
| `trips` | Travel group |
| `trip_members` | Many-to-many relation between users and trips |
| `trip_invites` | Invite token metadata |
| `trip_candidates` | Candidate attractions/restaurants |
| `candidate_votes` | User votes on candidates |
| `itinerary_items` | Generated or manually edited itinerary items |
| `trip_reminders` | Scheduled pre-trip reminders |

---

# 5. Table Specifications

---

## 5.1 `users`

### Purpose

Stores the app-level user profile associated with Cognito identity.

### Columns

| Column | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | Yes | Primary key |
| `cognito_sub` | VARCHAR | Yes | Unique Cognito user subject |
| `email` | VARCHAR | Yes | Unique |
| `display_name` | VARCHAR | Yes | App display name |
| `created_at` | TIMESTAMPTZ | Yes | Default current time |
| `updated_at` | TIMESTAMPTZ | Yes | Default current time |

### Constraints

- Primary key: `id`
- Unique: `cognito_sub`
- Unique: `email`

---

## 5.2 `trips`

### Purpose

Stores trip group metadata.

### Columns

| Column | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | Yes | Primary key |
| `title` | VARCHAR | Yes | Trip title |
| `destination` | VARCHAR | Yes | Destination text |
| `start_date` | DATE | Yes | Trip start |
| `end_date` | DATE | Yes | Trip end |
| `description` | TEXT | No | Optional |
| `created_by` | UUID | Yes | FK to `users.id` |
| `created_at` | TIMESTAMPTZ | Yes | Default current time |
| `updated_at` | TIMESTAMPTZ | Yes | Default current time |

### Constraints

- Primary key: `id`
- Foreign key: `created_by -> users.id`
- Check: `start_date <= end_date`

### Recommended Indexes

- `created_by`
- `start_date`
- `end_date`

---

## 5.3 `trip_members`

### Purpose

Stores users who belong to trips.

### Columns

| Column | Type | Required | Notes |
|---|---|---|---|
| `trip_id` | UUID | Yes | FK to `trips.id` |
| `user_id` | UUID | Yes | FK to `users.id` |
| `role` | VARCHAR | Yes | `owner` or `member` |
| `joined_at` | TIMESTAMPTZ | Yes | Join time |

### Constraints

- Composite primary key:
  - `(trip_id, user_id)`
- Foreign key:
  - `trip_id -> trips.id`
  - `user_id -> users.id`
- Role enum should be enforced by CHECK or app validation.

### Recommended Indexes

- `user_id`
- `trip_id`

---

## 5.4 `trip_invites`

### Purpose

Stores invite tokens and invite metadata.

### Columns

| Column | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | Yes | Primary key |
| `trip_id` | UUID | Yes | FK to `trips.id` |
| `created_by` | UUID | Yes | FK to `users.id` |
| `token_hash` | VARCHAR | Yes | Unique |
| `expires_at` | TIMESTAMPTZ | Yes | Invite expiration |
| `max_uses` | INTEGER | Yes | Positive integer |
| `used_count` | INTEGER | Yes | Default 0 |
| `revoked_at` | TIMESTAMPTZ | No | Null means active |
| `created_at` | TIMESTAMPTZ | Yes | Default current time |

### Constraints

- Primary key: `id`
- Unique: `token_hash`
- Foreign key:
  - `trip_id -> trips.id`
  - `created_by -> users.id`
- Check:
  - `max_uses > 0`
  - `used_count >= 0`
  - `used_count <= max_uses`

### Recommended Indexes

- `trip_id`
- `expires_at`

---

## 5.5 `trip_candidates`

### Purpose

Stores candidate attractions and restaurants proposed by trip members.

### Columns

| Column | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | Yes | Primary key |
| `trip_id` | UUID | Yes | FK to `trips.id` |
| `created_by` | UUID | Yes | FK to `users.id` |
| `category` | VARCHAR | Yes | `attraction` or `restaurant` |
| `name` | VARCHAR | Yes | Candidate name |
| `address` | TEXT | No | Optional |
| `note` | TEXT | No | Optional |
| `source_url` | TEXT | No | Optional |
| `created_at` | TIMESTAMPTZ | Yes | Default current time |
| `updated_at` | TIMESTAMPTZ | Yes | Default current time |

### Constraints

- Primary key: `id`
- Foreign key:
  - `trip_id -> trips.id`
  - `created_by -> users.id`
- Category enum should be enforced by CHECK or app validation.

### Recommended Indexes

- `trip_id`
- `created_by`
- `category`

---

## 5.6 `candidate_votes`

### Purpose

Stores user votes on candidate places.

### Columns

| Column | Type | Required | Notes |
|---|---|---|---|
| `candidate_id` | UUID | Yes | FK to `trip_candidates.id` |
| `user_id` | UUID | Yes | FK to `users.id` |
| `vote_value` | SMALLINT | Yes | MVP default value: `1` |
| `created_at` | TIMESTAMPTZ | Yes | Default current time |

### Constraints

- Composite primary key:
  - `(candidate_id, user_id)`
- Foreign key:
  - `candidate_id -> trip_candidates.id`
  - `user_id -> users.id`

### Recommended Indexes

- `user_id`
- `candidate_id`

---

## 5.7 `itinerary_items`

### Purpose

Stores generated or manually edited itinerary items.

### Columns

| Column | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | Yes | Primary key |
| `trip_id` | UUID | Yes | FK to `trips.id` |
| `day_number` | INTEGER | Yes | Starts from 1 |
| `slot` | VARCHAR | Yes | `morning`, `lunch`, `afternoon`, `dinner`, `evening` |
| `candidate_id` | UUID | No | FK to `trip_candidates.id`, nullable |
| `title` | VARCHAR | Yes | Display title |
| `note` | TEXT | No | Optional |
| `sort_order` | INTEGER | Yes | Position inside day |
| `created_at` | TIMESTAMPTZ | Yes | Default current time |
| `updated_at` | TIMESTAMPTZ | Yes | Default current time |

### Constraints

- Primary key: `id`
- Foreign key:
  - `trip_id -> trips.id`
  - `candidate_id -> trip_candidates.id`
- Check:
  - `day_number > 0`
  - `sort_order > 0`

### Recommended Indexes

- `trip_id`
- `(trip_id, day_number, sort_order)`

---

## 5.8 `trip_reminders`

### Purpose

Stores pre-trip reminder schedules.

### Columns

| Column | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | Yes | Primary key |
| `trip_id` | UUID | Yes | FK to `trips.id` |
| `reminder_type` | VARCHAR | Yes | `seven_days_before` or `one_day_before` |
| `scheduled_at` | TIMESTAMPTZ | Yes | Actual future trigger time |
| `scheduler_name` | VARCHAR | Yes | EventBridge Scheduler resource name |
| `status` | VARCHAR | Yes | `scheduled`, `cancelled`, `sent`, `failed` |
| `created_at` | TIMESTAMPTZ | Yes | Default current time |
| `updated_at` | TIMESTAMPTZ | Yes | Default current time |

### Constraints

- Primary key: `id`
- Foreign key:
  - `trip_id -> trips.id`
- Unique:
  - `scheduler_name`
- Recommended uniqueness:
  - `(trip_id, reminder_type)` to prevent duplicate type

### Recommended Indexes

- `trip_id`
- `scheduled_at`
- `status`

---

# 6. Relationship Summary

```text
users
  ├──< trips.created_by
  ├──< trip_members >── trips
  ├──< trip_candidates.created_by
  └──< candidate_votes

trips
  ├──< trip_members
  ├──< trip_invites
  ├──< trip_candidates
  ├──< itinerary_items
  └──< trip_reminders

trip_candidates
  ├──< candidate_votes
  └── optional reference from itinerary_items
```

---

# 7. Migration Guidelines

## 7.1 Migration Folder

Use:

```text
backend/migrations/
```

## 7.2 Migration Naming

Use ordered naming:

```text
001_create_users.sql
002_create_trips.sql
003_create_trip_members.sql
004_create_trip_invites.sql
005_create_trip_candidates.sql
006_create_candidate_votes.sql
007_create_itinerary_items.sql
008_create_trip_reminders.sql
```

## 7.3 Migration Principles

Claude Code must:

1. Create tables in foreign-key-safe order.
2. Add indexes explicitly.
3. Avoid destructive changes without explicit instruction.
4. Keep schema aligned with API and Lambda documents.
5. Add constraints where data integrity matters.
6. Avoid storing raw invite tokens.

---

# 8. Deletion Policy

Recommended MVP behavior:

| Entity | Strategy |
|---|---|
| Candidate | Hard delete allowed |
| Candidate votes | Delete with candidate |
| Trip invite | Do not hard delete initially; use `revoked_at` |
| Reminder | Prefer status transition to `cancelled` |
| Trip | Deletion not included in MVP |

---

# 9. Data Access Guidance

Lambda implementation should avoid scattered raw SQL.
Recommended structure:

```text
src/common/db.py
src/common/repositories/
```

Suggested repository modules:

```text
trip_repository.py
invite_repository.py
candidate_repository.py
vote_repository.py
itinerary_repository.py
reminder_repository.py
user_repository.py
```

---

# 10. Transaction Requirements

The following operations must use database transactions:

1. Create trip + owner membership
2. Join trip via invite:
   - validate invite
   - insert membership
   - increment used_count
3. Generate itinerary:
   - optionally clear old items
   - insert new items
4. Delete reminder:
   - update DB state
   - coordinate with scheduler cancellation strategy

---

# 11. Future Schema Extension Possibilities

Not implemented in MVP, but future-friendly:

- `trip_roles`
- `candidate_comments`
- `itinerary_versions`
- `place_coordinates`
- `notification_delivery_logs`