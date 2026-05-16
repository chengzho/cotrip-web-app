# 01 - System Architecture Overview

## 1. Purpose

This document defines the high-level architecture of **CoTrip**, a collaborative travel planning web app.

CoTrip allows users to:

- Create travel groups
- Invite members to join a trip
- Add candidate attractions and restaurants
- Vote on candidate places
- Generate a simple shared itinerary
- Edit core trip settings

This document is the architectural source of truth for Claude Code during implementation.

---

## 2. Product Scope

### 2.1 MVP Goals

The MVP shall support:

1. User authentication
2. Travel group creation
3. Member invitation and joining
4. Candidate place management
5. Voting and ranking
6. Simple itinerary generation
7. Core trip settings editing
8. Responsive frontend pages for desktop and mobile reference patterns

---

### 2.2 Explicitly Removed from MVP

The following previously considered feature is **removed from the MVP**:

```text
Pre-trip reminder notifications
```

Therefore, the MVP shall **not** include:

- Reminder scheduling
- EventBridge Scheduler
- Amazon SES
- Notification Lambda
- Reminder APIs
- Reminder database tables
- Reminder settings UI

---

### 2.3 Deferred / Future Improvements

The following items are intentionally deferred and should **not** be implemented in the MVP unless explicitly requested later:

- Pre-trip reminder notifications
- Email sending through Amazon SES
- Event scheduling through EventBridge Scheduler
- RDS Proxy
- AWS Secrets Manager
- Backend automatic deployment through GitHub Actions
- AI-powered itinerary optimization
- Google Maps route optimization
- Real-time WebSocket collaboration
- Rich role-based permission system beyond `owner` and `member`
- Payment features
- Public social feed
- Native mobile app

---

## 3. Core Technology Stack

### 3.1 Frontend

- TypeScript
- React
- Vite
- GitHub Pages for static frontend hosting

### 3.2 Authentication

- Amazon Cognito User Pool
- Cognito-issued JWT token
- API Gateway HTTP API JWT Authorizer

### 3.3 Backend

- Amazon API Gateway HTTP API
- AWS Lambda
- Python runtime

### 3.4 Database

- Amazon RDS for PostgreSQL

### 3.5 Observability

- Amazon CloudWatch Logs

### 3.6 Infrastructure and Local Backend Workflow

- AWS SAM

### 3.7 Repository Automation

- GitHub Actions

GitHub Actions may be used for:

- Frontend build validation
- Frontend deployment automation, such as GitHub Pages publishing
- Optional repository-level quality checks

Backend AWS deployment remains **manual through AWS SAM** in the MVP unless explicitly changed later.

---

## 4. High-Level System Architecture

```text
┌─────────────────────────────┐
│       React Frontend        │
│  TypeScript + Vite          │
│  Hosted on GitHub Pages     │
└──────────────┬──────────────┘
               │
               │ HTTPS + Bearer JWT
               ▼
┌─────────────────────────────┐
│     Amazon Cognito          │
│  User Pool Authentication   │
└──────────────┬──────────────┘
               │
               │ JWT used by frontend
               ▼
┌─────────────────────────────┐
│   API Gateway HTTP API      │
│   JWT Authorizer            │
└──────────────┬──────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────┐
│                    AWS Lambda Layer                  │
│                                                      │
│  1. TripGroupFunction                               │
│  2. InviteFunction                                  │
│  3. CandidateFunction                               │
│  4. VoteFunction                                    │
│  5. ItineraryFunction                               │
└──────────────┬───────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────┐
│      PostgreSQL RDS         │
│  Users / Trips / Votes      │
│  Candidates / Itinerary     │
└─────────────────────────────┘


Observability:

┌─────────────────────────────┐
│      CloudWatch Logs        │
│  Lambda execution logging   │
└─────────────────────────────┘
```

---

## 5. Authentication Architecture

### 5.0 MVP Authentication UX Decision

The CoTrip MVP intentionally uses Cognito Managed Login / Hosted UI to reduce authentication implementation complexity.

This means:

- CoTrip owns the product UI and post-login app experience.
- Cognito owns the sign-in, sign-up, password recovery, and related authentication screens.
- The React frontend provides sign-in and sign-out entry points, but does not recreate those authentication forms locally.

### 5.1 Authentication Responsibility

Authentication is handled by:

- Amazon Cognito User Pool
- API Gateway HTTP API JWT Authorizer

Lambda functions must not directly implement:

- User password management
- Login credential verification
- Token signature verification

---

### 5.2 Frontend Authentication Flow

The CoTrip MVP uses:

```text
Amazon Cognito Managed Login / Hosted UI
```

The frontend does **not** implement a custom sign-in, sign-up, or forgot-password flow in the MVP.

Instead, authentication follows this flow:

```text
User clicks the sign-in entry point in the CoTrip frontend
→ Frontend redirects the user to Cognito Managed Login / Hosted UI
→ User signs in or completes account registration through Cognito
→ Cognito redirects the user back to the configured frontend redirect URI
→ Frontend receives the authorization result according to the selected OAuth flow
→ Frontend stores and uses the issued tokens according to the final implementation strategy
→ Frontend sends protected API requests with:
   Authorization: Bearer <JWT>
```

The exact frontend token-handling implementation should be finalized during the frontend authentication phase, but the **authentication UI strategy is locked**:

```text
Use Cognito Managed Login / Hosted UI for MVP.
Do not build a custom local login page in the React app.
```

---

### 5.3 Backend User Identity Handling

Lambda functions shall:

1. Read JWT claims already validated by API Gateway
2. Extract the relevant user identity fields, especially:
   - Cognito subject: `sub`
   - Email, if available
   - Display name, if available
3. Resolve or create the corresponding application-level user record in the `users` table

The `users` table is the system's application profile layer.  
Cognito is the authentication identity layer.

---

### Display Name Fallback Policy

When the backend resolves or lazily creates the application-level `users` record, it must derive `display_name` using the following fallback order:

```text
name
→ preferred_username
→ cognito:username
→ email local part
→ "CoTrip User"
```

This fallback chain prevents user bootstrap from failing when optional Cognito profile claims are unavailable.

Examples:

- If `name` exists, use it.
- Otherwise, if `preferred_username` exists, use it.
- Otherwise, if `cognito:username` exists, use it.
- Otherwise, if `email` exists, use the substring before `@`.
- If none of the above are available, use:

```text
CoTrip User
```

The `users.display_name` column is required by the application schema, so a non-empty fallback value must always be produced during user creation.

---

## 6. Lambda Responsibility Mapping

| Lambda Function | Main Responsibility |
|---|---|
| `TripGroupFunction` | Create trips, list trips, retrieve trip details, update trip metadata, list trip members |
| `InviteFunction` | Create invite tokens, preview invite details, join a trip |
| `CandidateFunction` | Create, list, update, delete candidate attractions/restaurants |
| `VoteFunction` | Vote, remove vote, compute rankings |
| `ItineraryFunction` | Generate and manage itinerary items |

---

## 7. Main Business Flows

### 7.1 Create a Trip

```text
Frontend
→ POST /trips
→ TripGroupFunction
→ Insert into trips
→ Insert owner into trip_members
→ Return created trip summary
```

---

### 7.2 Invite a Member

```text
Frontend
→ POST /trips/{tripId}/invites
→ InviteFunction
→ Generate secure invite token
→ Store token hash in trip_invites
→ Return frontend join URL
```

---

### 7.3 Join a Trip

```text
User opens invite URL
→ Frontend calls GET /invites/{inviteToken}
→ InviteFunction validates token
→ Frontend displays invitation preview

User confirms join
→ POST /invites/{inviteToken}/join
→ InviteFunction inserts trip_members row
→ User becomes a member
```

---

### 7.4 Add Candidate Place

```text
Frontend
→ POST /trips/{tripId}/candidates
→ CandidateFunction
→ Validate trip membership
→ Insert into trip_candidates
→ Return created candidate place
```

---

### 7.5 Vote on Candidate Place

```text
Frontend
→ POST /candidates/{candidateId}/votes
→ VoteFunction
→ Validate trip membership
→ Insert into candidate_votes
→ Return updated vote state and vote count
```

---

### 7.6 View Rankings

```text
Frontend
→ GET /trips/{tripId}/rankings
→ VoteFunction
→ Aggregate votes by candidate
→ Sort candidates by vote count
→ Return ranking list
```

---

### 7.7 Generate Itinerary

```text
Frontend
→ POST /trips/{tripId}/itinerary/generate
→ ItineraryFunction
→ Fetch trip date range
→ Fetch ranked candidate places
→ Apply simple itinerary generation logic
→ Insert itinerary_items
→ Return generated itinerary
```

---

### 7.8 Edit Trip Settings

```text
Frontend
→ PATCH /trips/{tripId}
→ TripGroupFunction
→ Validate owner permission
→ Update trip metadata
→ Return updated trip summary
```

---

## 8. Database Ownership by Domain

| Table | Primary Owner |
|---|---|
| `users` | Shared common layer |
| `trips` | TripGroupFunction |
| `trip_members` | TripGroupFunction / InviteFunction |
| `trip_invites` | InviteFunction |
| `trip_candidates` | CandidateFunction |
| `candidate_votes` | VoteFunction |
| `itinerary_items` | ItineraryFunction |

---

## 9. Security Principles

### 9.1 API Security

- Protected APIs require a valid JWT.
- API Gateway performs JWT authorization.
- Lambda must still perform business authorization:
  - Is the caller a member of this trip?
  - Is the caller allowed to modify this resource?
  - Is the caller the owner when required?

---

### 9.2 Database Security

- PostgreSQL credentials must not be committed to source control.
- Database connection settings shall be provided through deployment-time configuration and Lambda environment variables in the MVP.
- The final AWS networking model must restrict database access appropriately.

---

### 9.3 Invite Token Security

- Raw invite tokens are returned only when the invite is created.
- The database stores only the token hash, not the raw token.
- Invite token validity must check:
  - Expiration
  - Revocation status
  - Maximum usage count

---

## 10. Deployment and Automation Positioning

### 10.1 Frontend

Frontend deployment may use:

```text
GitHub Actions
→ Build Vite frontend
→ Publish static assets to GitHub Pages
```

---

### 10.2 Backend

Backend infrastructure and deployment are handled through:

```text
AWS SAM
```

For the MVP, backend deployment is expected to be initiated manually by the developer, such as:

```text
sam build
sam deploy
```

Automatic backend deployment through GitHub Actions is deferred.

---

## 11. Repository-Level Implementation Guidance

Claude Code must follow these principles:

1. Do not add new AWS services unless explicitly requested.
2. Do not reintroduce reminders, notifications, SES, or EventBridge Scheduler.
3. Do not implement Secrets Manager or RDS Proxy in the MVP.
4. Do not merge all backend logic into one Lambda.
5. Do not hardcode AWS resource identifiers into Python source files.
6. Do not hardcode database credentials into source code.
7. Do not bypass trip membership authorization checks.
8. Keep shared backend code reusable through a `common/` package.
9. Prefer explicit, testable request validation.
10. Treat this document as the high-level architectural source of truth.

---

## 12. Recommended Backend Folder Structure

```text
backend/
├── template.yaml
├── src/
│   ├── common/
│   │   ├── auth.py
│   │   ├── db.py
│   │   ├── response.py
│   │   ├── errors.py
│   │   ├── validation.py
│   │   └── logging_utils.py
│   │
│   ├── trip_group/
│   │   └── app.py
│   ├── invite/
│   │   └── app.py
│   ├── candidate/
│   │   └── app.py
│   ├── vote/
│   │   └── app.py
│   └── itinerary/
│       └── app.py
│
├── migrations/
│   ├── 001_create_users.sql
│   ├── 002_create_trips.sql
│   ├── 003_create_trip_members.sql
│   ├── 004_create_trip_invites.sql
│   ├── 005_create_trip_candidates.sql
│   ├── 006_create_candidate_votes.sql
│   └── 007_create_itinerary_items.sql
│
├── events/
│   ├── trip/
│   ├── invite/
│   ├── candidate/
│   ├── vote/
│   └── itinerary/
│
└── tests/
    ├── unit/
    └── integration/
```

---

## 13. Final Architectural Decision Summary

The CoTrip MVP architecture is:

```text
React + TypeScript + Vite
GitHub Pages
Amazon Cognito User Pool
API Gateway HTTP API + JWT Authorizer
Python AWS Lambda Functions
Amazon RDS for PostgreSQL
CloudWatch Logs
AWS SAM
GitHub Actions
```

The CoTrip MVP explicitly does **not** include:

```text
EventBridge Scheduler
Amazon SES
NotificationFunction
Reminder APIs
Reminder database tables
Reminder UI
Secrets Manager
RDS Proxy
Automatic backend deployment through GitHub Actions
```