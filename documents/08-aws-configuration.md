# 08 - AWS Configuration

## 1. Purpose

This document defines AWS infrastructure configuration boundaries for the Collaborative Travel Planning App.

It clearly separates:

1. What Claude Code is allowed to generate or automate
2. What requires human review or human execution
3. Which AWS resources are required
4. Expected environment variables and deployment conventions

---

# 2. AWS Service Inventory

| Service | Purpose |
|---|---|
| Amazon Cognito | User authentication |
| API Gateway HTTP API | Backend API entry point |
| AWS Lambda | Backend business logic |
| Amazon RDS for PostgreSQL | Relational database |
| AWS Secrets Manager | Database credential management |
| Amazon EventBridge Scheduler | One-time reminder scheduling |
| Amazon SES | Email reminders |
| Amazon CloudWatch Logs | Lambda logging |
| AWS Budgets | Cost alerts |
| AWS SAM | Infrastructure-as-code and deployment basis |
| GitHub Actions + OIDC | CI/CD deployment authentication |

---

# 3. Recommended Environment Separation

At minimum, use:

```text
dev
```

Optionally later:

```text
dev
prod
```

Each environment should have separate:

- API URL
- Cognito configuration
- Database
- Secrets
- SES verification status if needed
- Frontend environment variables

---

# 4. Core Resource Naming Convention

Recommended naming prefix:

```text
travel-planner
```

Examples:

```text
travel-planner-dev-http-api
travel-planner-dev-user-pool
travel-planner-dev-trip-group-function
travel-planner-dev-postgres
travel-planner-dev-db-secret
```

---

# 5. Backend Environment Variables

Lambda functions may require the following environment variables.

## 5.1 Common Variables

| Variable | Purpose |
|---|---|
| `APP_ENV` | `dev` or `prod` |
| `LOG_LEVEL` | Example: `INFO` |
| `DB_SECRET_ARN` | Secrets Manager secret ARN |
| `DB_NAME` | PostgreSQL database name if not inside secret |
| `FRONTEND_BASE_URL` | Used for invite URL generation |

## 5.2 Notification Variables

| Variable | Purpose |
|---|---|
| `SES_SENDER_EMAIL` | Verified sender email |
| `SCHEDULER_GROUP_NAME` | Scheduler group name if used |
| `REMINDER_DEFAULT_HOUR_LOCAL` | Optional reminder default trigger hour |

---

# 6. Frontend Environment Variables

The frontend shall use Vite environment variables:

| Variable | Purpose |
|---|---|
| `VITE_API_BASE_URL` | API Gateway base URL |
| `VITE_COGNITO_DOMAIN` | Cognito hosted auth domain |
| `VITE_COGNITO_CLIENT_ID` | Cognito app client ID |
| `VITE_COGNITO_REDIRECT_URI` | Frontend redirect URI |
| `VITE_COGNITO_LOGOUT_URI` | Frontend logout redirect URI |

---

# 7. API Gateway Configuration

## 7.1 API Type

Use:

```text
API Gateway HTTP API
```

## 7.2 Authentication

Use:

```text
JWT Authorizer
```

Expected token source:

```text
Authorization header
```

Expected format:

```text
Bearer <JWT>
```

## 7.3 CORS

Configure frontend origin explicitly.

Expected allowed origins:

```text
Local development URL
GitHub Pages deployment URL
```

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

# 8. Lambda Configuration

## 8.1 Runtime

Use Python runtime.

Recommended project convention:

```text
python3.13 or later, subject to final environment choice
```

## 8.2 Functions

Required functions:

```text
TripGroupFunction
InviteFunction
CandidateFunction
VoteFunction
ItineraryFunction
NotificationFunction
```

## 8.3 Shared Code

All functions should share common helpers from:

```text
src/common/
```

---

# 9. RDS PostgreSQL Configuration

## 9.1 Database Engine

```text
PostgreSQL
```

## 9.2 Recommended Security Posture

- RDS should not be publicly accessible.
- Lambda functions should connect over the VPC network.
- PostgreSQL port `5432` should be allowed only from the Lambda security group.

## 9.3 Security Group Model

```text
lambda-app-sg
    |
    | allowed to reach PostgreSQL port 5432
    v
rds-postgres-sg
```

## 9.4 Credential Management

Database credentials must not be hardcoded.

Preferred approach:

```text
AWS Secrets Manager
```

---

# 10. VPC and Private Connectivity Notes

## 10.1 Expected VPC-Attached Functions

Functions that require PostgreSQL access:

```text
TripGroupFunction
InviteFunction
CandidateFunction
VoteFunction
ItineraryFunction
NotificationFunction
```

## 10.2 AWS API Access from VPC-Attached Lambda

A Lambda attached to private VPC networking may need additional network configuration when calling AWS service APIs.

This project should use one of:

1. VPC interface endpoints for required services, or
2. NAT-based outbound routing if the human operator chooses it

Likely AWS API dependencies:

- Secrets Manager
- EventBridge Scheduler
- SES

The exact deployment choice must be made intentionally, balancing simplicity and cost.

---

# 11. Cognito Configuration

## 11.1 Required Cognito Elements

- User Pool
- App Client
- Hosted authentication configuration or equivalent frontend OAuth flow
- Redirect URI
- Logout URI

## 11.2 Expected Claims Used by Backend

The backend may use:

- `sub`
- `email`
- `name` or equivalent display field if configured

## 11.3 Application User Sync

Lambda common auth/user helper should ensure the Cognito user has a corresponding row in:

```text
users
```

---

# 12. EventBridge Scheduler Configuration

## 12.1 Purpose

Used to trigger future reminder emails.

## 12.2 Expected Usage

When reminder is created:

```text
NotificationFunction
→ create one-time EventBridge Scheduler schedule
→ target NotificationFunction
```

## 12.3 Stored Metadata

The system must persist:

- Reminder row ID
- Scheduled timestamp
- Scheduler resource name
- Reminder status

---

# 13. SES Configuration

## 13.1 Purpose

Amazon SES is used to send reminder emails.

## 13.2 Required Human-Aware Setup

The sender email or sender domain must be verified before production use.

If the AWS account is in SES sandbox mode, destination restrictions may apply.

---

# 14. CloudWatch Logs

Each Lambda function should emit structured logs suitable for debugging:

- Function name
- Route/event type
- Request ID
- Authenticated user ID if available
- Resource ID when safe
- Error summary

Do not log secrets or raw JWTs.

---

# 15. AWS Budgets

A project-level monthly budget alert should be configured by the human operator.

Recommended initial alert example:

```text
Monthly budget: 5 USD or 10 USD
```

The exact threshold is a human decision.

---

# 16. CI/CD Direction

## 16.1 Frontend Deployment

Frontend can be deployed through:

```text
GitHub Actions
→ build Vite app
→ publish to GitHub Pages
```

## 16.2 Backend Deployment

Backend can be deployed through:

```text
GitHub Actions
→ configure AWS credentials via OIDC
→ sam build
→ sam deploy
```

---

# 17. What Claude Code Can Do

Claude Code may:

1. Create or edit:
   - `template.yaml`
   - Python Lambda source files
   - requirements files
   - SQL migration files
   - GitHub Actions workflow files
   - local SAM test events
   - local test scripts
2. Create environment variable template files:
   - `.env.example`
   - `env.local.example.json`
3. Generate AWS CLI command drafts for human review.
4. Generate CloudFormation/SAM resource definitions.
5. Implement all Lambda handlers according to the documents.
6. Implement request parsing, response formatting, validation, and repository layers.
7. Implement local unit tests and local SAM smoke-test files.

---

# 18. What Requires Human Intervention

The following actions require a human operator, even if Claude Code prepares commands or templates:

## 18.1 AWS Account and Billing

- Choose AWS account and region
- Review expected costs
- Configure AWS Budgets alerts

## 18.2 Credential and Secret Decisions

- Decide how deployment credentials are managed
- Confirm Secrets Manager secret ownership and values
- Approve any secret creation or modification

## 18.3 SES Setup

- Verify sender email or domain
- Request production access if necessary
- Decide whether email reminder testing uses real recipients or test identities

## 18.4 Cognito Frontend Integration

- Confirm actual frontend URL
- Confirm callback URL
- Confirm logout URL
- Confirm hosted UI domain or login integration approach

## 18.5 GitHub OIDC Bootstrap

- Create or approve IAM trust relationship between GitHub Actions and AWS
- Confirm repository name and branch restrictions
- Confirm deploy role permission scope

## 18.6 Database Provisioning Review

- Approve RDS instance size and configuration
- Approve whether the database is created through IaC or console
- Approve VPC/networking choices before deployment

## 18.7 Destructive or Cost-Sensitive Deployment

Claude Code must not perform irreversible or cost-sensitive AWS deployment actions without explicit human direction.

---

# 19. Local Development Expectations

Recommended local development stack:

```text
Frontend:
- npm install
- npm run dev

Backend:
- sam build
- sam local start-api

Database:
- Local PostgreSQL container or developer-managed local PostgreSQL
```

---

# 20. Deployment Readiness Checklist

Before actual AWS deployment:

- [ ] Frontend routes finalized
- [ ] API routes finalized
- [ ] SQL migrations reviewed
- [ ] Lambda unit tests pass
- [ ] SAM local smoke tests pass
- [ ] AWS account/region confirmed
- [ ] Cognito callback URLs confirmed
- [ ] SES sender verified
- [ ] GitHub OIDC setup confirmed
- [ ] Budget alert configured
- [ ] RDS cost and networking reviewed