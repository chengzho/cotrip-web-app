# 07 - Database Schema and Migration Guidelines

## 1. Purpose

This document defines the PostgreSQL relational data model for the **CoTrip** collaborative travel planning app.

Claude Code must treat this document as the single source of truth when:

- Creating SQL migration files
- Implementing repository/query logic
- Designing joins and constraints
- Writing tests that depend on database structure
- Understanding table ownership across Lambda domains

The CoTrip MVP database scope does **not** include reminder or notification tables.

---

# 2. Database Choice

The system uses:

```text
Amazon RDS for PostgreSQL
```

The schema is relational because the app contains strongly connected entities:

- Users participate in multiple trips
- Trips contain multiple members
- Members propose candidate places
- Members vote on candidate places
- Trips generate grouped itinerary items

PostgreSQL is a strong fit for:

- Referential integrity
- Foreign key relationships
- Aggregation queries for vote ranking
- Transactional workflows such as trip creation and invite joining

---

# 3. MVP Table Summary

The CoTrip MVP uses **7 core tables**:

| Table | Purpose |
|---|---|
| `users` | Application-level user profile mapped to Cognito identity |
| `trips` | Travel group metadata |
| `trip_members` | Many-to-many relationship between users and trips |
| `trip_invites` | Invite token metadata |
| `trip_candidates` | Candidate attractions and restaurants |
| `candidate_votes` | User votes on candidate places |
| `itinerary_items` | Generated or manually edited itinerary items |

---

# 4. Naming Conventions

## 4.1 Tables

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

---

## 4.2 Columns

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

---

## 4.3 Timestamps

Use timezone-aware timestamps:

```text
TIMESTAMPTZ
```

---

## 4.4 UUIDs

All primary business entities use UUID identifiers.

Preferred strategy:

- Application-generated UUIDs, for portability and consistent service logic

Database-generated UUIDs may be used only if explicitly configured in migrations and consistently applied.

---

## 4.5 Soft Delete Policy

The MVP generally avoids broad soft-delete complexity.

Recommended policy:

| Entity | MVP Deletion Strategy |
|---|---|
| Candidate places | Hard delete allowed |
| Candidate votes | Delete with candidate or through cleanup logic |
| Trip invites | Do not hard delete initially; use `revoked_at` |
| Itinerary items | Hard delete allowed |
| Trips | Trip deletion is not part of the MVP |

---

# 5. Table Specifications

---

## 5.1 `users`

### Purpose

Stores the application-level user profile associated with Amazon Cognito identity.

Cognito manages authentication.  
The `users` table stores the internal application identity used by CoTrip business logic.

---

### Columns

| Column | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | Yes | Primary key |
| `cognito_sub` | VARCHAR | Yes | Unique Cognito user subject |
| `email` | VARCHAR | Yes | Unique |
| `display_name` | VARCHAR | Yes | User-facing display name |
| `created_at` | TIMESTAMPTZ | Yes | Default current timestamp |
| `updated_at` | TIMESTAMPTZ | Yes | Default current timestamp |

---

### Constraints

- Primary key:
  - `id`
- Unique:
  - `cognito_sub`
  - `email`

---

### Recommended Indexes

- Unique index on `cognito_sub`
- Unique index on `email`

---

## 5.2 `trips`

### Purpose

Stores trip group metadata.

---

### Columns

| Column | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | Yes | Primary key |
| `title` | VARCHAR | Yes | Trip title |
| `destination` | VARCHAR | Yes | Destination text |
| `start_date` | DATE | Yes | Trip start date |
| `end_date` | DATE | Yes | Trip end date |
| `description` | TEXT | No | Optional trip description |
| `created_by` | UUID | Yes | FK to `users.id` |
| `created_at` | TIMESTAMPTZ | Yes | Default current timestamp |
| `updated_at` | TIMESTAMPTZ | Yes | Default current timestamp |

---

### Constraints

- Primary key:
  - `id`
- Foreign key:
  - `created_by -> users.id`
- Check constraint:
  - `start_date <= end_date`

---

### Recommended Indexes

- Index on `created_by`
- Index on `start_date`
- Index on `end_date`

---

## 5.3 `trip_members`

### Purpose

Stores membership relationships between users and trips.

A user may belong to multiple trips.  
A trip may contain multiple users.

---

### Columns

| Column | Type | Required | Notes |
|---|---|---|---|
| `trip_id` | UUID | Yes | FK to `trips.id` |
| `user_id` | UUID | Yes | FK to `users.id` |
| `role` | VARCHAR | Yes | `owner` or `member` |
| `joined_at` | TIMESTAMPTZ | Yes | Membership creation timestamp |

---

### Constraints

- Composite primary key:
  - `(trip_id, user_id)`
- Foreign keys:
  - `trip_id -> trips.id`
  - `user_id -> users.id`
- Role value must be restricted to:
  - `owner`
  - `member`

Role validation may be enforced through:

- Database CHECK constraint, or
- Application validation plus test coverage

A CHECK constraint is preferred.

---

### Recommended Indexes

- Index on `user_id`
- Index on `trip_id`
- Optional index on `(trip_id, role)` if role-based trip queries become useful

---

## 5.4 `trip_invites`

### Purpose

Stores invite token metadata for joining trips.

The raw invite token must **not** be stored.  
Only a token hash is persisted.

---

### Columns

| Column | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | Yes | Primary key |
| `trip_id` | UUID | Yes | FK to `trips.id` |
| `created_by` | UUID | Yes | FK to `users.id` |
| `token_hash` | VARCHAR | Yes | Unique secure hash of raw invite token |
| `expires_at` | TIMESTAMPTZ | Yes | Invite expiration timestamp |
| `max_uses` | INTEGER | Yes | Maximum allowed joins through this invite |
| `used_count` | INTEGER | Yes | Default `0` |
| `revoked_at` | TIMESTAMPTZ | No | Null means active |
| `created_at` | TIMESTAMPTZ | Yes | Default current timestamp |

---

### Constraints

- Primary key:
  - `id`
- Unique:
  - `token_hash`
- Foreign keys:
  - `trip_id -> trips.id`
  - `created_by -> users.id`
- Check constraints:
  - `max_uses > 0`
  - `used_count >= 0`
  - `used_count <= max_uses`

---

### Recommended Indexes

- Unique index on `token_hash`
- Index on `trip_id`
- Index on `expires_at`

---

## 5.5 `trip_candidates`

### Purpose

Stores candidate attractions and restaurants proposed by trip members.

---

### Columns

| Column | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | Yes | Primary key |
| `trip_id` | UUID | Yes | FK to `trips.id` |
| `created_by` | UUID | Yes | FK to `users.id` |
| `category` | VARCHAR | Yes | `attraction` or `restaurant` |
| `name` | VARCHAR | Yes | Candidate place name |
| `address` | TEXT | No | Optional address |
| `note` | TEXT | No | Optional reason or note |
| `source_url` | TEXT | No | Optional external reference URL |
| `created_at` | TIMESTAMPTZ | Yes | Default current timestamp |
| `updated_at` | TIMESTAMPTZ | Yes | Default current timestamp |

---

### Constraints

- Primary key:
  - `id`
- Foreign keys:
  - `trip_id -> trips.id`
  - `created_by -> users.id`
- Category value must be restricted to:
  - `attraction`
  - `restaurant`

A CHECK constraint is preferred.

---

### Recommended Indexes

- Index on `trip_id`
- Index on `created_by`
- Index on `category`
- Optional composite index on `(trip_id, category)`

---

## 5.6 `candidate_votes`

### Purpose

Stores user votes on candidate places.

Each user may vote at most once for a given candidate.

---

### Columns

| Column | Type | Required | Notes |
|---|---|---|---|
| `candidate_id` | UUID | Yes | FK to `trip_candidates.id` |
| `user_id` | UUID | Yes | FK to `users.id` |
| `vote_value` | SMALLINT | Yes | MVP default value: `1` |
| `created_at` | TIMESTAMPTZ | Yes | Default current timestamp |

---

### Constraints

- Composite primary key:
  - `(candidate_id, user_id)`
- Foreign keys:
  - `candidate_id -> trip_candidates.id`
  - `user_id -> users.id`
- Recommended CHECK:
  - `vote_value = 1` for MVP upvote model

---

### Recommended Indexes

- Index on `candidate_id`
- Index on `user_id`

---

## 5.7 `itinerary_items`

### Purpose

Stores generated or manually adjusted itinerary items.

The itinerary is represented as rows grouped by:

- trip
- day number
- slot
- sort order

Each itinerary item stores a **category snapshot** at generation time.

This avoids losing important display information when:

- the original candidate place is later deleted
- `candidate_id` becomes null through `ON DELETE SET NULL`
- the frontend still needs to render the correct category badge in the itinerary UI

---

### Columns

| Column | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | Yes | Primary key |
| `trip_id` | UUID | Yes | FK to `trips.id` |
| `day_number` | INTEGER | Yes | Starts from `1` |
| `slot` | VARCHAR | Yes | `morning`, `lunch`, `afternoon`, `dinner`, or `evening` |
| `candidate_id` | UUID | No | FK to `trip_candidates.id`, nullable |
| `category` | VARCHAR | Yes | Snapshot category: `attraction` or `restaurant` |
| `title` | VARCHAR | Yes | Display title |
| `note` | TEXT | No | Optional note |
| `sort_order` | INTEGER | Yes | Sort position within the day |
| `created_at` | TIMESTAMPTZ | Yes | Default current timestamp |
| `updated_at` | TIMESTAMPTZ | Yes | Default current timestamp |

---

### Constraints

- Primary key:
  - `id`
- Foreign keys:
  - `trip_id -> trips.id`
  - `candidate_id -> trip_candidates.id`
- Check constraints:
  - `day_number > 0`
  - `sort_order > 0`
- Slot value must be restricted to:
  - `morning`
  - `lunch`
  - `afternoon`
  - `dinner`
  - `evening`
- Category value must be restricted to:
  - `attraction`
  - `restaurant`

CHECK constraints are preferred for both `slot` and `category`.

---

### Recommended Indexes

- Index on `trip_id`
- Index on `category`
- Composite index on:
  - `(trip_id, day_number, sort_order)`

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
  └──< itinerary_items

trip_candidates
  ├──< candidate_votes
  └── optional reference from itinerary_items
```

---

# 7. Domain Ownership Summary

| Domain | Primary Tables |
|---|---|
| Shared user/auth layer | `users` |
| Trip group domain | `trips`, `trip_members` |
| Invite domain | `trip_invites` |
| Candidate domain | `trip_candidates` |
| Voting domain | `candidate_votes` |
| Itinerary domain | `itinerary_items` |

---

# 8. Migration Guidelines

## 8.1 Migration Folder

Use:

```text
backend/migrations/
```

---

## 8.2 Migration Naming

Use ordered naming:

```text
001_create_users.sql
002_create_trips.sql
003_create_trip_members.sql
004_create_trip_invites.sql
005_create_trip_candidates.sql
006_create_candidate_votes.sql
007_create_itinerary_items.sql
```

---

## 8.3 Migration Principles

Claude Code must:

1. Create tables in foreign-key-safe order.
2. Add indexes explicitly.
3. Add data integrity constraints where appropriate.
4. Avoid destructive schema changes unless explicitly requested.
5. Keep schema aligned with:
   - API documents
   - Lambda specification documents
   - System architecture documents
6. Avoid storing raw invite tokens.
7. Avoid introducing reminder or notification tables in the MVP.
8. Preserve the itinerary item `category` snapshot in the `itinerary_items` table.

---

# 9. Transaction Requirements

The following database operations must be transactional.

---

## 9.1 Create Trip

The following operations must happen in one transaction:

1. Insert into `trips`
2. Insert owner membership into `trip_members`

If either operation fails, the transaction must roll back.

---

## 9.2 Join Trip Through Invite

The following operations must happen in one transaction:

1. Resolve invite by hashed token
2. Validate:
   - not expired
   - not revoked
   - usage count below limit
3. Check current user is not already a trip member
4. Insert into `trip_members`
5. Increment `trip_invites.used_count`

If any step fails, the transaction must roll back.

---

## 9.3 Generate Itinerary

When generating a new itinerary:

### If overwrite is false
- Do not modify existing itinerary items.
- Return the appropriate conflict response.

### If overwrite is true
The following operations must happen in one transaction:

1. Delete existing itinerary items for the trip
2. Insert newly generated itinerary items

Each inserted itinerary item must persist:

- `candidate_id`, if applicable
- `category`
- `title`
- `note`
- generated day/slot/sort information

If generation or insertion fails, the transaction must roll back.

---

# 10. Delete and Cascade Guidance

## 10.1 Candidate Place Deletion

When a candidate place is deleted:

- Related rows in `candidate_votes` should be removed.
- This may be handled by:
  - `ON DELETE CASCADE`, or
  - explicit application-layer cleanup

A database cascade is acceptable and recommended for simplicity.

---

## 10.2 Candidate References from Itinerary Items

The `candidate_id` field in `itinerary_items` is nullable.

If a candidate place used by an itinerary item is deleted, the implementation should preserve itinerary readability by ensuring:

- the itinerary item `title` remains available
- the itinerary item `category` remains available
- the candidate reference may be set to null if using `ON DELETE SET NULL`

Recommended foreign key behavior:

```text
candidate_id -> trip_candidates.id ON DELETE SET NULL
```

The `category` column is stored directly on `itinerary_items` so the frontend can continue rendering the correct badge even if the referenced candidate no longer exists.

---

## 10.3 Trip Deletion

Trip deletion is **not part of the MVP**.

No dedicated cascade strategy for deleting a full trip is required in the initial implementation unless explicitly added later.

---

# 11. Updated-at Timestamp Guidance

Tables with an `updated_at` column:

- `users`
- `trips`
- `trip_candidates`
- `itinerary_items`

The MVP may choose either:

1. Update `updated_at` explicitly in application SQL, or
2. Introduce database triggers later

Recommended MVP approach:

```text
Update updated_at explicitly in application queries.
```

This avoids unnecessary trigger complexity.

---

# 12. Repository Layer Guidance

Lambda implementation should avoid scattering raw SQL throughout handlers.

Recommended data access structure:

```text
backend/src/common/repositories/
├── user_repository.py
├── trip_repository.py
├── invite_repository.py
├── candidate_repository.py
├── vote_repository.py
└── itinerary_repository.py
```

Handlers should remain focused on:

- event parsing
- authorization
- request validation
- response construction

Repositories should manage:

- SQL queries
- transaction helpers
- data mapping

---

# 13. Future Schema Extension Possibilities

The following future extensions are intentionally **not** part of the MVP, but the schema can evolve later to support them:

- Reminder notification tables
- Notification delivery logs
- Advanced trip roles
- Candidate comments
- Itinerary versions
- Place geographic coordinates
- Shared expense tracking
- Map route data
- Activity categories beyond attraction / restaurant

---

# 14. MVP Schema Scope Summary

The CoTrip MVP database includes:

```text
users
trips
trip_members
trip_invites
trip_candidates
candidate_votes
itinerary_items
```

The CoTrip MVP database explicitly excludes:

```text
trip_reminders
notification_logs
scheduler metadata tables
```

No reminder or notification-related schema should be created in the MVP.

The `itinerary_items` table must persist a `category` snapshot so itinerary responses remain stable and renderable even if the original candidate record is later deleted.