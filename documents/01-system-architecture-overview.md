# 01 - System Architecture Overview

## 1. Purpose

This document defines the high-level architecture of the **Collaborative Travel Planning App**.

The system allows users to:

- Create travel groups
- Invite members to join
- Add candidate attractions and restaurants
- Vote on candidate places
- Generate a simple itinerary
- Configure pre-trip reminder notifications

This document is the architectural source of truth for Claude Code during implementation.

---

## 2. Project Goals

### 2.1 MVP Goals

The MVP shall support:

1. User authentication
2. Travel group creation
3. Member invitation and joining
4. Candidate place management
5. Voting and ranking
6. Simple itinerary generation
7. Pre-trip reminder scheduling
8. Basic frontend pages for the above flows

### 2.2 Non-Goals for MVP

The following features are intentionally excluded from the first implementation:

- AI-powered itinerary optimization
- Google Maps route optimization
- Real-time WebSocket collaboration
- Rich role-based permission system beyond `owner` and `member`
- Payment features
- Public social feed
- Mobile native app
- Complex multi-stage approval workflow

---

## 3. Core Technology Stack

### 3.1 Frontend

- TypeScript
- React
- Vite
- GitHub Pages for static hosting

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

### 3.5 Notification

- Amazon EventBridge Scheduler
- Amazon SES

### 3.6 Infrastructure and Deployment

- AWS SAM
- GitHub Actions
- GitHub OIDC to AWS for deployment authentication

### 3.7 Observability and Cost Control

- Amazon CloudWatch Logs
- AWS Budgets

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
│  6. NotificationFunction                            │
└──────────────┬───────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────┐
│      PostgreSQL RDS         │
│  Users / Trips / Votes      │
│  Itinerary / Reminders      │
└─────────────────────────────┘


Reminder Scheduling Flow:

┌─────────────────────────────┐
│ NotificationFunction        │
│ Creates reminder schedule   │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ EventBridge Scheduler       │
│ One-time invocation         │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ NotificationFunction        │
│ Sends reminder email        │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ Amazon SES                  │
└─────────────────────────────┘
```

---

## 5. Authentication Architecture

### 5.1 Authentication Responsibility

Authentication is handled by:

- Amazon Cognito User Pool
- API Gateway HTTP API JWT Authorizer

Lambda functions must not directly implement login or password management.

### 5.2 Frontend Authentication Flow

```text
User opens frontend
→ User clicks Login / Sign up
→ Cognito authentication flow
→ Cognito returns JWT
→ Frontend stores token according to chosen auth strategy
→ Frontend sends API requests with:
   Authorization: Bearer <JWT>
```

### 5.3 Backend User Identity Handling

Lambda functions shall:

1. Read JWT claims already validated by API Gateway
2. Extract:
   - Cognito subject: `sub`
   - Email, if available
   - Display name, if available
3. Resolve or create the application-level user record in the `users` table

The `users` table is the system's application profile layer.
Cognito is the authentication identity layer.

---

## 6. Lambda Responsibility Mapping

| Lambda Function | Main Responsibility |
|---|---|
| `TripGroupFunction` | Create trips, list trips, retrieve trip details, update trip metadata, list trip members |
| `InviteFunction` | Create invite tokens, preview invite details, join a trip |
| `CandidateFunction` | Create, list, update, delete candidate attractions/restaurants |
| `VoteFunction` | Vote, remove vote, compute rankings |
| `ItineraryFunction` | Generate and manage itinerary items |
| `NotificationFunction` | Manage reminder schedules and send reminder emails |

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

### 7.2 Invite a Member

```text
Frontend
→ POST /trips/{tripId}/invites
→ InviteFunction
→ Generate secure invite token
→ Store token hash in trip_invites
→ Return frontend join URL
```

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

### 7.4 Add Candidate Place

```text
Frontend
→ POST /trips/{tripId}/candidates
→ CandidateFunction
→ Validate membership
→ Insert into trip_candidates
```

### 7.5 Vote on Candidate Place

```text
Frontend
→ POST /candidates/{candidateId}/votes
→ VoteFunction
→ Validate membership
→ Insert into candidate_votes
```

### 7.6 Generate Itinerary

```text
Frontend
→ POST /trips/{tripId}/itinerary/generate
→ ItineraryFunction
→ Fetch trip date range
→ Fetch ranked candidate places
→ Apply simple generation logic
→ Insert itinerary_items
→ Return generated itinerary
```

### 7.7 Create Pre-Trip Reminder

```text
Frontend
→ POST /trips/{tripId}/reminders
→ NotificationFunction
→ Validate trip ownership or membership policy
→ Insert reminder record
→ Create EventBridge Scheduler one-time schedule
→ Store scheduler_name in trip_reminders
```

### 7.8 Send Reminder Email

```text
EventBridge Scheduler
→ NotificationFunction
→ Load reminder information
→ Load trip and recipient data
→ Send email using Amazon SES
→ Mark reminder status as sent
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
| `trip_reminders` | NotificationFunction |

---

## 9. Security Principles

### 9.1 API Security

- All protected APIs require a valid JWT.
- API Gateway performs JWT verification.
- Lambda must still perform business authorization:
  - Is the caller a member of this trip?
  - Is the caller allowed to modify this resource?
  - Is the caller the owner when required?

### 9.2 Database Security

- PostgreSQL RDS should not be publicly accessible.
- Lambda functions should connect to RDS through the VPC configuration.
- RDS security group must only allow PostgreSQL access from the Lambda security group.

### 9.3 Secret Management

- Database credentials must not be committed into source control.
- Secret-related values must be stored in AWS Secrets Manager or provided through secure deployment configuration.

### 9.4 Invite Token Security

- Raw invite tokens are returned only once to the client.
- Database stores only the token hash, not the raw token.
- Invite token validity must check:
  - Expiration
  - Revocation status
  - Maximum usage count

---

## 10. Repository-Level Implementation Guidance

Claude Code must follow these principles:

1. Do not add new AWS services unless explicitly requested.
2. Do not invent additional business flows outside this document.
3. Do not merge all backend logic into one Lambda.
4. Do not hardcode AWS resource identifiers into Python source files.
5. Do not hardcode database credentials.
6. Do not bypass trip membership authorization checks.
7. Keep shared code reusable through a `common/` package.
8. Prefer explicit, testable request validation.

---

## 11. Recommended Backend Folder Structure

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
│   ├── itinerary/
│   │   └── app.py
│   └── notification/
│       └── app.py
│
├── migrations/
│   ├── 001_create_users.sql
│   ├── 002_create_trips.sql
│   ├── ...
│
├── events/
│   ├── trip/
│   ├── invite/
│   ├── candidate/
│   ├── vote/
│   ├── itinerary/
│   └── notification/
│
└── tests/
    ├── unit/
    └── integration/
```

---

## 12. Final Architectural Decision Summary

The MVP architecture is:

```text
React + TypeScript + Vite
GitHub Pages
Cognito User Pool
API Gateway HTTP API + JWT Authorizer
Python Lambda Functions
RDS PostgreSQL
EventBridge Scheduler
Amazon SES
AWS SAM
GitHub Actions + OIDC
CloudWatch Logs
AWS Budgets
```