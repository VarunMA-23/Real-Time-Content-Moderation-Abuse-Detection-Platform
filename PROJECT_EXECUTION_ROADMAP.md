# ShieldAI Project Execution Roadmap

## Purpose

This document is a detailed execution plan for turning the current repository into a complete, properly staged moderation platform.

It is based on:

- `README.md` at the project root
- the implemented frontend inside `moderation-ui`
- the existing backend contract draft in `Covered/frontend-backend-contract.md`

---

## 1. Current Project Reality

The root `README.md` describes a **full real-time content moderation platform** with:

- synchronous moderation
- asynchronous deep analysis
- policy configuration
- human review
- analytics
- learning loop
- scalability and failure handling

The codebase currently implements **only the frontend prototype and mocked integration layer**.

### What already exists

- A React + Vite moderation dashboard in `moderation-ui`
- Login screen
- Message simulation flow
- Review queue screen
- Analytics screen
- Policy configuration screen
- Mock API handlers using `msw`
- A useful frontend/backend API contract draft in `Covered/frontend-backend-contract.md`

### What does not exist yet

- Real backend service
- Real authentication/token flow
- Database schema and persistence
- Job queue system
- Worker services for async moderation
- ML model serving layer
- LLM enrichment pipeline
- Reviewer audit trail storage
- Real analytics aggregation
- Deployment, observability, and production reliability setup

### Bottom line

The project is currently at the **product prototype + system design stage**, not at the runnable platform stage.

That is good news, because the next step is very clear.

---

## 2. What To Develop Next

### Highest-priority next part

The next part to build should be:

**The backend foundation that satisfies the current frontend contract end-to-end.**

This is more important than adding new UI pages or advanced ML right now.

### Why this should come next

1. The frontend is already far enough along to define the required backend behavior.
2. The project README promises a system, but today the app still runs on mocked data.
3. Without a real backend, you cannot validate:
   - moderation workflows
   - reviewer actions
   - policy persistence
   - queue behavior
   - analytics correctness
4. Building ML workers first would be premature because the platform plumbing is not in place yet.

### Exact next milestone

Build a **Backend MVP** that supports:

- `POST /auth/login`
- `POST /moderate`
- `GET /jobs/{jobId}`
- `GET /review`
- `POST /decision`
- `GET /analytics`
- `GET /policies`
- `PUT /policies`

This should use a real database and return the same shapes already expected by the frontend.

---

## 3. Recommended Development Order

Follow this order:

1. Backend core and persistence
2. Frontend integration with real APIs
3. Async job processing
4. Moderation logic and policy engine
5. Analytics and auditability
6. Security and production hardening
7. ML/LLM quality improvements
8. Deployment and scaling

This order reduces rework and keeps the system testable at each stage.

---

## 4. Gap Analysis: README vs Current Code

| Area | README Vision | Current State | Priority |
|---|---|---|---|
| Fast-path moderation | Real-time decision engine | Mocked | Critical |
| Async deep analysis | Queue + worker services | Missing | Critical |
| Reviewer interface | Present | UI exists, backend missing | Critical |
| Policy engine | Configurable rules by platform/region | UI sliders only | High |
| Analytics | Performance and moderation metrics | UI exists, mocked data | High |
| Human feedback loop | Reviewer overrides feed learning | Not implemented | High |
| Security | Auth, RBAC, secure service communication | Minimal mock login only | High |
| Failure handling | Retries, dead-letter, graceful degradation | Missing | Medium |
| Scalability | Autoscaling, queue-based distribution | Architectural only | Medium |
| Model lifecycle | Continuous improvement pipeline | Missing | Medium |

---

## 5. Execution Strategy

### Phase 1 Goal

Get the product to a state where one user can:

- log in
- submit a message
- receive a moderation result
- see flagged messages in a review queue
- take reviewer actions
- save policies
- see analytics based on real stored data

If you complete that, the project moves from concept/demo into a usable application foundation.

---

## 6. Suggested Architecture For Implementation

Use a simple version first.

### Recommended MVP architecture

- `moderation-ui`:
  existing frontend
- `moderation-api`:
  backend HTTP API service
- `database`:
  PostgreSQL
- `queue`:
  Redis + BullMQ, or RabbitMQ
- `worker`:
  async job processor for LLM/image/text enrichment

### Why this architecture works

- It matches the README design direction
- It keeps responsibilities separated early
- It is realistic for scaling later
- It lets you implement async flows without overengineering

---

## 7. Detailed Timeline Planner

This timeline assumes a solo builder or small team working steadily.  
If you work part-time, stretch the schedule proportionally.

### Week 1: Discovery and backend setup

### Objectives

- Freeze the MVP scope
- Choose backend stack
- Define database schema
- Create backend project skeleton

### Deliverables

- final backend tech stack decision
- API folder scaffold
- environment setup
- database connection working
- migration strategy chosen
- initial schema draft

### Tasks

- Review and clean `Covered/frontend-backend-contract.md`
- Pick backend framework
  - good options: Node.js + Express/Fastify, or NestJS
- Choose ORM/query layer
  - good options: Prisma, Drizzle, or TypeORM
- Create entities/tables for:
  - users
  - messages
  - moderation_results
  - decision_events
  - policy_configs
  - jobs
- Define status enums and action enums clearly
- Resolve mismatch between:
  - `approve/reject/ban/escalate`
  - `allowed/flagged/blocked/escalated`

### Exit criteria

- Backend service starts locally
- Database schema is defined
- API contract is stable enough to implement

---

### Week 2: Authentication and core CRUD

### Objectives

- Build real authentication
- Persist users and basic records
- Secure protected routes

### Deliverables

- `POST /auth/login`
- JWT auth middleware
- role support for moderator/admin
- seed user for local development

### Tasks

- Implement login validation
- Add password hashing
- Return user profile and token
- Update frontend API layer to send `Authorization` header
- Add route guards server-side
- Create local seed script for test moderators

### Exit criteria

- Frontend can log in against the real backend
- Protected endpoints reject unauthorized calls properly

---

### Week 3: Moderation submission flow

### Objectives

- Implement the synchronous moderation path
- Persist submitted messages and initial scoring

### Deliverables

- `POST /moderate`
- message persistence
- basic scoring engine
- policy-based initial decisioning

### Tasks

- Create request validation for text input
- Implement a first-pass moderation engine:
  - start with rules/keyword heuristics
  - optionally combine with simple model scoring later
- Save:
  - message text
  - author/user metadata if available
  - scores
  - decision
  - timestamps
- If decision is not allowed, enqueue async job

### Exit criteria

- Submitting from the Simulate page creates real stored moderation records
- The UI displays real backend decisions

---

### Week 4: Review queue and moderator actions

### Objectives

- Make the review page fully functional
- Persist moderator decisions and history

### Deliverables

- `GET /review`
- `POST /decision`
- review filters
- decision event history

### Tasks

- Implement queue retrieval with filters:
  - status
  - risk
  - date range
  - category
- Support moderator actions:
  - approve
  - reject
  - ban
  - escalate
- Write decision history into the database
- Update final message state after decision
- Handle race conditions where another moderator already resolved an item

### Exit criteria

- Review screen works against the live backend
- Decision history is stored and returned correctly

---

### Week 5: Policies and business rules

### Objectives

- Turn policy settings into real operating rules
- Persist policy versions and updates

### Deliverables

- `GET /policies`
- `PUT /policies`
- policy validation
- policy versioning basics

### Tasks

- Store threshold values in DB
- Enforce validation on range values
- Apply stored policies during moderation decisions
- Add `updatedBy` and `updatedAt`
- Restrict policy writes to admin users

### Exit criteria

- Changes on the Policies screen affect moderation behavior
- Policy changes are auditable

---

### Week 6: Async jobs and LLM enrichment

### Objectives

- Implement the asynchronous moderation stage promised in the README

### Deliverables

- job queue
- worker process
- `GET /jobs/{jobId}`
- enrichment persistence

### Tasks

- Add queue producer in `POST /moderate`
- Add worker for non-allowed content
- Store job status:
  - pending
  - processing
  - completed
  - failed
- Save:
  - `llmExplanation`
  - `policyViolation`
- Add retry behavior for failed jobs

### Exit criteria

- The Simulate screen can poll job status and later receive stored enrichment data

---

### Week 7: Analytics foundation

### Objectives

- Replace mocked analytics with real aggregations

### Deliverables

- `GET /analytics`
- aggregated moderation metrics
- date-range filtering

### Tasks

- Compute totals:
  - total messages
  - blocked percent
  - flagged percent
  - reviewed count
- Build timeline aggregation
- Add simple model-performance reporting from recorded data
- Decide how to represent precision/recall until ground truth expands

### Exit criteria

- Analytics page renders from real database data

---

### Week 8: Reliability and observability

### Objectives

- Make the system debuggable and safer to operate

### Deliverables

- centralized logging
- structured errors
- request IDs
- health checks
- retry/dead-letter design

### Tasks

- Standardize error payloads
- Add request logging and job logging
- Add `/health` and readiness checks
- Add dead-letter queue strategy
- Handle backend degradation gracefully

### Exit criteria

- Failures are observable and recoverable without manual guesswork

---

### Week 9: Testing and quality gates

### Objectives

- Reduce regression risk
- Make iteration safer

### Deliverables

- unit tests
- API integration tests
- contract tests
- frontend integration checks

### Tasks

- Test auth flows
- Test moderation decisions
- Test queue lifecycle
- Test policy validation
- Test decision conflicts
- Test analytics response shapes
- Test frontend against live backend in a local environment

### Exit criteria

- Critical flows are covered by automated tests

---

### Week 10: Security hardening

### Objectives

- Align the implementation with the security direction in the README

### Deliverables

- RBAC enforcement
- rate limiting
- safer secrets management
- audit improvements

### Tasks

- Add rate limits for login and moderation routes
- Review token handling in frontend
- Add basic audit trails for admin actions
- Add input-size limits and validation hardening
- Prepare for PII redaction workflow

### Exit criteria

- The app is safer for internal/demo use and closer to production standards

---

### Week 11: ML pipeline improvement

### Objectives

- Move beyond heuristic moderation into stronger classification quality

### Deliverables

- improved text classification stage
- disagreement capture
- training data export design

### Tasks

- Integrate a baseline moderation model or external moderation provider
- Record uncertainty/conflict cases
- Mark human-overridden cases as feedback records
- Define label taxonomy clearly:
  - toxic
  - hate
  - spam
  - self-harm
  - safe

### Exit criteria

- The learning loop begins to exist as a real data process, not just a README idea

---

### Week 12: Deployment and scale-ready packaging

### Objectives

- Prepare the project for demonstration, collaboration, and real hosting

### Deliverables

- Docker setup
- environment config docs
- staging deployment
- operations README

### Tasks

- Containerize frontend, API, worker, database dependencies
- Add `docker-compose` for local full-stack startup
- Document environment variables
- Document deployment order
- Add backup and migration notes

### Exit criteria

- A new developer can run the full platform locally with minimal friction

---

## 8. Priority Breakdown

### Critical now

- backend service
- database schema
- real auth
- moderation endpoint
- review queue endpoint
- decision endpoint
- policy persistence

### Important soon after

- async worker pipeline
- analytics aggregation
- audit history
- tests
- logging

### Later, after the foundation is stable

- image moderation
- multilingual support
- active learning workflow
- WebSockets/SSE
- policy A/B testing
- coordinated abuse detection
- voice moderation

---

## 9. Recommended MVP Scope Boundary

To avoid getting stuck, the first complete version should **not** include everything from the README.

### Include in MVP

- text moderation only
- role-based login
- policy thresholds
- reviewer actions
- async text enrichment
- analytics based on stored events

### Exclude from MVP for now

- image moderation
- voice moderation
- multilingual support
- advanced fairness monitoring
- autoscaling infrastructure
- active retraining pipelines
- edge/on-device moderation

That keeps the build focused and finishable.

---

## 10. Suggested Folder Expansion

One clean direction would be:

```text
/
|-- README.md
|-- PROJECT_EXECUTION_ROADMAP.md
|-- Covered/
|-- moderation-ui/
|-- moderation-api/
|   |-- src/
|   |-- prisma/ or db/
|   |-- tests/
|   `-- package.json
|-- moderation-worker/
|   |-- src/
|   `-- package.json
`-- docker-compose.yml
```

---

## 11. Risks You Should Manage Early

### 1. Contract drift

The frontend, README vision, and backend implementation can drift apart fast.  
Keep `Covered/frontend-backend-contract.md` updated as the source of truth for integration.

### 2. Enum confusion

Action names and status names are already mixed in the current prototype.  
Standardize this before backend implementation goes too far.

### 3. Analytics ambiguity

Metrics like precision and recall require trustworthy labels and definitions.  
Do not fake "model quality" metrics in production without a clear source of truth.

### 4. Overbuilding too early

Do not start with microservices, Kubernetes, or multiple model types unless the basic product loop works first.

### 5. Security shortcuts

The current frontend stores only a user object in memory.  
Real auth and RBAC should be added early, not postponed until the end.

---

## 12. Recommended Immediate Action List

If you want the sharpest next move, do these next:

1. Create `moderation-api`
2. Choose backend stack and ORM
3. Implement database schema
4. Build auth flow
5. Build `POST /moderate`
6. Build `GET /review` and `POST /decision`
7. Connect frontend to real backend
8. Replace MSW mocks route by route

---

## 13. Definition of "Project Properly Completed"

You should consider the project properly complete when all of the following are true:

- frontend uses real APIs in all main flows
- moderation requests are persisted
- reviewer queue works end-to-end
- policy settings affect actual decisions
- async enrichment works through real jobs
- analytics are generated from real system data
- auth and RBAC are enforced
- tests cover critical workflows
- the app can be run locally as a full stack
- deployment documentation exists

---

## 14. Final Recommendation

Do **not** build more frontend pages next.

The correct next development move is to build the **backend MVP and persistence layer** that fulfills the current UI contract. Once that exists, every later part of the README becomes much easier to implement in a disciplined way.

If executed in order, this roadmap will move the project from:

**system design + demo UI**

to:

**working moderation platform foundation**

which is the most important transition for this repository right now.
