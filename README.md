# CoTrip

**CoTrip** is a collaborative travel planning web app that helps a group organize a trip together.

Users can:

- Create a trip group
- Invite members to join
- Propose attractions and restaurants
- Vote on candidate places
- Generate a simple shared itinerary
- Manage core trip settings

The project is designed as a practical full-stack AWS web application and will be implemented through an AI-assisted agentic development workflow.

---

## Project Status

This repository is currently in the:

```text
Architecture, specification, and UI handoff completed
→ Ready to enter Claude Code AI Agentic Workflow
```

The following planning assets are already prepared:

- System architecture documents
- API specification documents
- Database schema and migration guidelines
- AWS configuration scope
- Lambda function specifications
- Finalized desktop and mobile Pencil UI design
- Frontend UI implementation overview

---

## MVP Scope

The CoTrip MVP focuses on the core collaborative travel planning workflow.

### Included Features

- User authentication
- Trip group creation
- Invite link creation and join flow
- Candidate attraction / restaurant management
- Candidate voting and ranking
- Shared itinerary generation
- Itinerary item editing
- Trip settings editing
- Responsive frontend design for desktop and mobile patterns

---

## Explicitly Excluded from MVP

To reduce implementation complexity and keep the project focused, the following features are intentionally excluded from the first version:

- Pre-trip reminder notifications
- Email notifications
- EventBridge Scheduler
- Amazon SES
- Notification Lambda
- Reminder APIs and reminder database tables
- AWS Secrets Manager
- RDS Proxy
- Automatic backend deployment through GitHub Actions

These may be reconsidered as future improvements after the MVP is completed.

---

## Planned Tech Stack

### Frontend

- TypeScript
- React
- Vite
- GitHub Pages

### Backend

- Amazon API Gateway HTTP API
- AWS Lambda with Python
- AWS SAM

### Authentication

- Amazon Cognito User Pool
- API Gateway JWT Authorizer

### Database

- Amazon RDS for PostgreSQL

### Observability

- Amazon CloudWatch Logs

### Repository Automation

- GitHub Actions
  - Frontend build validation
  - Frontend GitHub Pages deployment
  - Optional repository-level checks

Backend AWS deployment is expected to remain manual through AWS SAM during the MVP stage.

---

## Core Product Flow

```text
Create a trip
→ Invite members
→ Propose attractions and restaurants
→ Vote together
→ Generate a shared itinerary
→ Edit trip details or itinerary items
```

---

## Repository Structure

Current repository structure:

```text
cotrip-web-app/
├── documents/
│   ├── 01-system-architecture-overview.md
│   ├── 02-api-specification-overview.md
│   ├── 03-api-trip-and-member.md
│   ├── 04-api-invite.md
│   ├── 05-api-candidate-and-vote.md
│   ├── 06-api-itinerary.md
│   ├── 07-database-schema-and-migration-guidelines.md
│   ├── 08-aws-configuration.md
│   ├── 09-lambda-trip-group.md
│   ├── 10-lambda-invite.md
│   ├── 11-lambda-candidate.md
│   ├── 12-lambda-vote.md
│   ├── 13-lambda-itinerary.md
│   └── 14-ui-frontend-design-overview.md
│
├── webui/
│   └── ui_design.pen
│
├── .gitignore
└── README.md
```

---

## Documentation Overview

### Architecture and API

| File | Purpose |
|---|---|
| `01-system-architecture-overview.md` | High-level architecture and MVP scope |
| `02-api-specification-overview.md` | Shared API conventions and routing overview |
| `03-api-trip-and-member.md` | Trip and member APIs |
| `04-api-invite.md` | Invite creation, preview, and join APIs |
| `05-api-candidate-and-vote.md` | Candidate place and voting APIs |
| `06-api-itinerary.md` | Itinerary generation and editing APIs |

### Database and AWS

| File | Purpose |
|---|---|
| `07-database-schema-and-migration-guidelines.md` | PostgreSQL schema and migration rules |
| `08-aws-configuration.md` | AWS services, boundaries, and human-intervention procedures |

### Lambda Specifications

| File | Purpose |
|---|---|
| `09-lambda-trip-group.md` | `TripGroupFunction` specification |
| `10-lambda-invite.md` | `InviteFunction` specification |
| `11-lambda-candidate.md` | `CandidateFunction` specification |
| `12-lambda-vote.md` | `VoteFunction` specification |
| `13-lambda-itinerary.md` | `ItineraryFunction` specification |

### Frontend and UI

| File | Purpose |
|---|---|
| `14-ui-frontend-design-overview.md` | Final frontend UI structure and implementation guidance |
| `webui/ui_design.pen` | Final Pencil UI design reference |

---

## UI and Product Direction

The finalized UI direction for CoTrip is:

> A warm, editorial, collaborative travel planning workspace.

Key UI decisions:

- Product name: **CoTrip**
- Interface language: primarily **Traditional Chinese**
- Desktop trip workspace:
  - Left sidebar navigation
- Mobile trip workspace:
  - Bottom navigation
  - More menu overlay
- Visual style:
  - Warm parchment background
  - Near-white cards
  - Dark pill-shaped primary buttons
  - Muted badges
  - Calm, spacious information hierarchy

---

## Planned Implementation Workflow

The project will proceed through a phase-based AI Agentic Workflow using Claude Code.

### Phase 0 — Project Intake and Implementation Plan

Claude Code will:

- Read all specification documents
- Review the Pencil UI design
- Summarize system understanding
- Propose the concrete implementation roadmap
- Confirm repository structure and development sequence

No code changes should be made in Phase 0.

---

### Later Planned Phases

Expected later implementation stages include:

1. Repository scaffolding
2. Frontend project setup
3. Static UI implementation from Pencil design
4. PostgreSQL migration setup
5. Shared backend utilities
6. Lambda-by-Lambda backend implementation
7. Frontend API integration
8. Cognito integration
9. Manual AWS SAM deployment
10. GitHub Actions frontend deployment

The exact workflow may be refined after Phase 0.

---

## Current Design Reference

The current approved Pencil design is stored at:

```text
webui/ui_design.pen
```

This design file includes:

- Desktop landing page
- Dashboard
- Invite page
- Trip creation page
- Trip workspace pages
- Key mobile responsive screens

Claude Code should use the Pencil design together with:

```text
documents/14-ui-frontend-design-overview.md
```

when implementing the frontend.

---

## Development Principle

CoTrip is intentionally scoped as a focused MVP:

- Strong enough to demonstrate a complete AWS web application
- Small enough to complete within a constrained project timeline
- Designed for phased implementation and continuous verification

The project should prioritize:

1. Correct architecture
2. Clear domain boundaries
3. Maintainable backend structure
4. Usable frontend flow
5. Completion of the core collaborative travel planning experience