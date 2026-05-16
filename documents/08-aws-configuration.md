# 08 - AWS Configuration

## 1. Purpose

This document defines the AWS infrastructure configuration boundaries for the **CoTrip** collaborative travel planning app.

It clearly separates:

1. Required AWS services for the MVP
2. AWS services intentionally removed or deferred
3. What Claude Code may implement or prepare
4. What requires human intervention
5. Expected environment variables and deployment conventions
6. The role of GitHub Actions in the MVP workflow

This document reflects the simplified CoTrip MVP scope.

---

# 2. Final MVP AWS Service Inventory

The CoTrip MVP uses the following AWS-related services and tools:

| Service / Tool | Purpose |
|---|---|
| Amazon Cognito | User authentication |
| API Gateway HTTP API | Backend API entry point |
| AWS Lambda | Python backend business logic |
| Amazon RDS for PostgreSQL | Relational application database |
| Amazon CloudWatch Logs | Lambda execution logs |
| AWS SAM | Serverless infrastructure definition, local testing, manual deployment |
| GitHub Actions | Frontend build validation and frontend deployment automation |

---

# 3. Explicitly Removed or Deferred AWS Scope

The following previously considered services or capabilities are **not part of the CoTrip MVP**:

| Removed / Deferred Item | MVP Status |
|---|---|
| EventBridge Scheduler | Removed |
| Amazon SES | Removed |
| Notification Lambda | Removed |
| Reminder APIs | Removed |
| Reminder database table | Removed |
| AWS Secrets Manager | Deferred |
| RDS Proxy | Deferred |
| Backend automatic deployment through GitHub Actions | Deferred |
| GitHub OIDC-based backend deployment | Deferred |

Claude Code must not reintroduce these items unless explicitly instructed later.

---

# 4. Recommended Environment Separation

At minimum, use:

```text
dev
```

Optionally later:

```text
prod
```

Each environment may have separate:

- API Gateway URL
- Cognito configuration
- PostgreSQL database instance or database name
- Lambda environment variables
- Frontend environment variables
- GitHub Pages deployment target if needed

For the MVP, a single `dev` environment is sufficient.

---

# 5. Core Resource Naming Convention

Recommended naming prefix:

```text
cotrip
```

Examples:

```text
cotrip-dev-http-api
cotrip-dev-user-pool
cotrip-dev-trip-group-function
cotrip-dev-invite-function
cotrip-dev-candidate-function
cotrip-dev-vote-function
cotrip-dev-itinerary-function
cotrip-dev-postgres
```

Resource names may be adjusted later during actual deployment, but naming should remain consistent and descriptive.

---

# 6. Overall AWS Architecture

```text
┌──────────────────────────────┐
│       React Frontend         │
│  TypeScript + Vite           │
│  GitHub Pages Hosting        │
└──────────────┬───────────────┘
               │
               │ HTTPS + Bearer JWT
               ▼
┌──────────────────────────────┐
│       Amazon Cognito         │
│   User Pool Authentication   │
└──────────────┬───────────────┘
               │
               │ JWT issued to frontend
               ▼
┌──────────────────────────────┐
│   API Gateway HTTP API       │
│   JWT Authorizer             │
└──────────────┬───────────────┘
               │
               ▼
┌───────────────────────────────────────────────────────┐
│                    AWS Lambda Layer                   │
│                                                       │
│  TripGroupFunction                                   │
│  InviteFunction                                      │
│  CandidateFunction                                   │
│  VoteFunction                                        │
│  ItineraryFunction                                   │
└──────────────┬────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────┐
│     RDS for PostgreSQL       │
│     CoTrip application DB    │
└──────────────────────────────┘


Observability:

┌──────────────────────────────┐
│        CloudWatch Logs       │
│   Lambda execution logging   │
└──────────────────────────────┘
```

---

# 7. Frontend Environment Variables

The React + Vite frontend shall use environment variables with the `VITE_` prefix.

Recommended variables:

| Variable | Purpose |
|---|---|
| `VITE_API_BASE_URL` | API Gateway base URL |
| `VITE_COGNITO_DOMAIN` | Cognito hosted auth domain or managed login domain |
| `VITE_COGNITO_CLIENT_ID` | Cognito app client ID |
| `VITE_COGNITO_REDIRECT_URI` | Frontend authentication redirect URI |
| `VITE_COGNITO_LOGOUT_URI` | Frontend logout redirect URI |

---

## 7.1 Frontend Example Environment File

A file such as:

```text
webui/.env.example
```

may contain:

```env
VITE_API_BASE_URL=
VITE_COGNITO_DOMAIN=
VITE_COGNITO_CLIENT_ID=
VITE_COGNITO_REDIRECT_URI=
VITE_COGNITO_LOGOUT_URI=
```

Claude Code may create this example file.  
Real values must not be committed if they are sensitive or environment-specific.

---

# 8. Backend Environment Variables

The MVP backend uses Lambda environment variables for deployment-time configuration.

Recommended variables:

| Variable | Purpose |
|---|---|
| `APP_ENV` | Environment name, e.g. `dev` |
| `LOG_LEVEL` | Logging verbosity, e.g. `INFO` |
| `FRONTEND_BASE_URL` | Used to generate invite links |
| `DB_HOST` | PostgreSQL host |
| `DB_PORT` | PostgreSQL port, usually `5432` |
| `DB_NAME` | PostgreSQL database name |
| `DB_USER` | PostgreSQL username |
| `DB_PASSWORD` | PostgreSQL password |

---

## 8.1 Backend Example Environment Template

A local/example file may be created such as:

```text
backend/env.local.example.json
```

or another SAM-compatible environment template.

Example structure:

```json
{
  "TripGroupFunction": {
    "APP_ENV": "dev",
    "LOG_LEVEL": "INFO",
    "FRONTEND_BASE_URL": "http://localhost:5173",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_NAME": "cotrip_dev",
    "DB_USER": "postgres",
    "DB_PASSWORD": "replace-me"
  }
}
```

The final implementation may choose either:

- One shared environment section per function, or
- Repeated function-specific sections required by SAM local testing

The exact file shape should remain compatible with the chosen SAM workflow.

---

## 8.2 Security Note on DB Credentials

For the MVP:

- Database credentials may be configured through Lambda environment variables.
- Credentials must **not** be committed to GitHub.
- Example files must contain placeholders only.
- Deployment-time real values must be provided manually and securely by the developer.

AWS Secrets Manager is intentionally deferred from the MVP to reduce setup complexity.  
It may be introduced later as a production hardening improvement.

---

# 9. API Gateway Configuration

## 9.1 API Type

Use:

```text
API Gateway HTTP API
```

---

## 9.2 Authentication

Use:

```text
JWT Authorizer
```

Expected token source:

```text
Authorization header
```

Expected request format:

```http
Authorization: Bearer <JWT>
```

---

## 9.3 Public and Protected Routes

### Public Route

| Method | Path |
|---|---|
| `GET` | `/invites/{inviteToken}` |

This route allows unauthenticated invite preview.

---

### Protected Routes

All other application routes are protected unless explicitly documented otherwise.

Examples:

- `/trips`
- `/trips/{tripId}`
- `/trips/{tripId}/members`
- `/trips/{tripId}/invites`
- `/invites/{inviteToken}/join`
- `/trips/{tripId}/candidates`
- `/candidates/{candidateId}/votes`
- `/trips/{tripId}/rankings`
- `/trips/{tripId}/itinerary`

---

## 9.4 CORS

Configure the API to support frontend access.

Expected allowed origins:

- Local frontend development URL
- GitHub Pages frontend deployment URL

Expected allowed methods:

```text
GET
POST
PATCH
DELETE
OPTIONS
```

Expected allowed headers:

```text
Authorization
Content-Type
```

---

# 10. Lambda Configuration

## 10.1 Runtime

Use Python runtime for backend Lambda functions.

Recommended runtime choice should be finalized during implementation according to the available project environment and SAM support.

---

## 10.2 Required Lambda Functions

The CoTrip MVP requires exactly these five domain-oriented functions:

```text
TripGroupFunction
InviteFunction
CandidateFunction
VoteFunction
ItineraryFunction
```

Claude Code must not create:

```text
NotificationFunction
```

for the MVP.

---

## 10.3 Shared Code

All functions should reuse shared modules from:

```text
backend/src/common/
```

Expected reusable responsibilities include:

- Authentication claim parsing
- User resolution / bootstrap
- Database connection helper
- Standardized API response formatting
- Error helpers
- Validation helpers
- Logging helpers

---

# 11. RDS PostgreSQL Configuration

## 11.1 Database Engine

Use:

```text
PostgreSQL
```

---

## 11.2 MVP Database Role

PostgreSQL stores:

- Users
- Trips
- Trip memberships
- Invite metadata
- Candidate places
- Candidate votes
- Itinerary items

It does **not** store reminders or notification metadata in the MVP.

---

## 11.3 Connectivity Positioning

The final AWS networking configuration must allow Lambda functions to securely connect to RDS PostgreSQL.

The implementation details may be finalized during AWS provisioning, but the design should follow these principles:

- RDS should not be casually exposed without review.
- Database access must be restricted appropriately.
- Lambda database access should use clearly documented connection configuration.
- Any VPC and security group setup must be performed intentionally and documented.

---

## 11.4 RDS Proxy

RDS Proxy is **not part of the MVP**.

It may be reconsidered later if:

- Connection management becomes a problem
- Concurrency increases
- The project evolves toward a production-grade deployment

---

# 12. CloudWatch Logs

CloudWatch Logs is the basic observability layer for the MVP.

Each Lambda function should log:

- Function-level operation context
- Request ID
- Route or handler intent
- Key resource identifiers when safe
- Error summaries

Do not log:

- Raw JWT
- Database passwords
- Full database connection strings containing secrets
- Raw invite token if avoidable

---

# 13. AWS SAM Responsibilities

AWS SAM is used for:

- Defining serverless backend resources
- Organizing function configurations
- Local invocation testing
- Local API testing where appropriate
- Manual backend deployment to AWS

---

## 13.1 Expected SAM Commands

Typical developer workflow may include:

```bash
sam build
sam local invoke
sam local start-api
sam deploy
```

---

## 13.2 Local Testing Expectations

Claude Code may prepare:

- `template.yaml`
- Local SAM event JSON files
- `env.local.example.json`
- Local API testing notes
- Function-specific test planning documents

---

## 13.3 Manual Backend Deployment

For the MVP, backend deployment is expected to be initiated manually by the developer using SAM.

Automatic backend deployment through GitHub Actions is deferred.

---

# 14. GitHub Actions Role in the MVP

GitHub Actions is retained in the MVP, but its scope is intentionally limited.

## 14.1 Expected GitHub Actions Usage

GitHub Actions may be used for:

1. Frontend build validation
2. Frontend deployment to GitHub Pages
3. Optional formatting, linting, or test workflows after the codebase exists

---

## 14.2 Frontend Deployment Direction

Expected high-level flow:

```text
Push to main
→ GitHub Actions workflow runs
→ Install frontend dependencies
→ Build Vite project
→ Publish static site to GitHub Pages
```

---

## 14.3 Backend Deployment Exclusion

GitHub Actions should **not** automatically deploy backend AWS infrastructure in the MVP.

The MVP does not require:

- GitHub Actions `sam deploy`
- GitHub OIDC trust setup for backend deployment
- Automated CloudFormation stack updates from CI

These may be documented later as future improvements.

---

# 15. Human-Intervention Required Procedures

The following procedures require human review or human execution.

---

## 15.1 AWS Account and Region Choice

Human must decide:

- AWS account to use
- Primary AWS region
- Any cost-control decisions for provisioning

---

## 15.2 Cognito Setup Decisions

Human must confirm:

- User Pool creation
- App client settings
- Redirect URI
- Logout URI
- Hosted auth domain or final authentication approach

Claude Code may prepare implementation notes or suggested configuration, but should not assume final live resource values.

---

## 15.3 RDS Provisioning Decisions

Human must confirm:

- Whether RDS is provisioned immediately or later
- PostgreSQL instance sizing
- Database network exposure model
- Database administrator credentials
- Security group and VPC choices if applicable

---

## 15.4 Lambda Environment Variable Values

Human must provide real values for:

- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `FRONTEND_BASE_URL`
- Cognito-related frontend environment variables

Claude Code may create example files, but not invent real deployment secrets.

---

## 15.5 GitHub Pages and Actions Setup

Human may need to confirm:

- Repository Pages deployment settings
- Whether GitHub Actions is selected as the Pages publishing source
- Repository branch settings if required

---

## 15.6 Cost-Sensitive or Live AWS Operations

Claude Code must not perform irreversible, live, or cost-sensitive AWS actions without explicit human instruction.

Examples:

- Creating RDS instances
- Deploying SAM stacks
- Changing Cognito production settings
- Altering IAM configurations
- Publishing frontend publicly if not instructed

---

# 16. What Claude Code Can Do

Claude Code may:

1. Create or edit:
   - `backend/template.yaml`
   - Python Lambda source files
   - shared backend helpers
   - SQL migrations
   - local test events
   - `.env.example` or local environment example files
   - GitHub Actions workflow files
   - frontend project files

2. Implement:
   - API routes
   - Lambda handler structure
   - Repository layer
   - Common response/error helpers
   - Local SAM-compatible project setup
   - Frontend build workflows

3. Prepare:
   - shell command suggestions
   - deployment notes
   - local testing instructions
   - README updates

---

# 17. What Claude Code Must Not Do

Claude Code must not:

1. Reintroduce reminder or notification features.
2. Reintroduce:
   - EventBridge Scheduler
   - Amazon SES
   - NotificationFunction
3. Add AWS Secrets Manager to the MVP architecture.
4. Add RDS Proxy to the MVP architecture.
5. Add backend auto-deployment through GitHub Actions.
6. Hardcode credentials in source files.
7. Commit real environment secrets.
8. Invent live AWS resource IDs or secrets.
9. Perform live AWS deployment actions without explicit human direction.

---

# 18. Local Development Expectations

Recommended local workflow:

```text
Frontend:
- npm install
- npm run dev

Backend:
- sam build
- sam local invoke
- sam local start-api

Database:
- Local PostgreSQL for development/testing where appropriate
```

The project may connect to RDS only after the relevant AWS infrastructure is intentionally configured.

---

# 19. Deployment Readiness Checklist

Before live AWS deployment, confirm:

- [ ] Frontend routes finalized
- [ ] Backend API routes finalized
- [ ] PostgreSQL schema reviewed
- [ ] SQL migrations reviewed
- [ ] Lambda source structure reviewed
- [ ] Local SAM tests pass
- [ ] AWS account and region confirmed
- [ ] Cognito redirect/logout URLs confirmed
- [ ] RDS provisioning and network strategy confirmed
- [ ] Real environment variable values prepared securely
- [ ] GitHub Pages deployment approach confirmed
- [ ] CloudWatch Logs visibility understood
- [ ] Cost expectations reviewed

---

# 20. MVP AWS Scope Summary

The CoTrip MVP includes:

```text
Amazon Cognito
API Gateway HTTP API
AWS Lambda
Amazon RDS for PostgreSQL
CloudWatch Logs
AWS SAM
GitHub Actions
```

The CoTrip MVP excludes:

```text
EventBridge Scheduler
Amazon SES
NotificationFunction
Reminder APIs
Reminder UI
Reminder database tables
AWS Secrets Manager
RDS Proxy
Backend automatic deployment through GitHub Actions
GitHub OIDC-based backend deployment
```