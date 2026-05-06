# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ShieldAI is a production-grade, multi-stage content moderation system for large-scale social and chat applications. It detects hate speech, spam, sexual content, self-harm, and coordinated abuse across text and images in real time.

The system uses a **two-stage architecture**:
1. **Fast Path (Synchronous)**: Lightweight ML model + rules engine for sub-100ms decisions
2. **Deep Analysis (Asynchronous)**: LLM-based analysis via message queue workers for nuanced, contextual analysis

## Architecture

The codebase is split into two main components:

- **`moderation-api/`**: FastAPI backend handling synchronous moderation, policy engine, and async worker coordination
- **`moderation-ui/`**: React dashboard for human reviewers and administrators

### Backend Structure (`moderation-api/`)

```
moderation-api/
├── app/
│   ├── api/
│   │   ├── deps.py           # Dependency injection (auth, DB sessions)
│   │   └── v1/
│   │       ├── api.py       # API router aggregation
│   │       └── endpoints/   # Route handlers (auth, moderate, review, etc.)
│   ├── core/
│   │   ├── config.py        # Pydantic settings (env vars, DB URIs)
│   │   └── security.py      # JWT auth, password hashing
│   ├── db/
│   │   ├── session.py       # SQLAlchemy session factories (sync + async)
│   │   └── base_class.py    # Base model with common fields
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic request/response models
│   └── main.py              # FastAPI app factory with CORS, error handlers
├── scripts/
│   ├── seed_db.py           # Database seeding
│   └── prestart.sh          # Container startup script
└── requirements.txt
```

### Frontend Structure (`moderation-ui/`)

```
moderation-ui/
├── src/
│   ├── components/
│   │   ├── layout/          # Layout components (Sidebar, TopBar, ProtectedLayout)
│   │   ├── shared/          # Reusable UI components (StatusBadge, RiskChip, FilterBar)
│   │   ├── simulate/        # Message simulation UI
│   │   ├── review/          # Review queue components
│   │   ├── analytics/       # Analytics dashboard components
│   │   └── policies/        # Policy configuration components
│   ├── hooks/               # Custom React hooks (useModerate, useQueue, useAnalytics, usePolicies)
│   ├── mock/                # MSW handlers for API mocking
│   ├── routes/              # Page components (Login, Simulate, Review, Analytics, Policies)
│   ├── services/
│   │   └── api.js           # Centralized API client with auth token handling
│   ├── store/
│   │   └── moderationStore.js # Zustand global state (user, messages, queue, policies)
│   └── utils/               # Utility functions (riskLevel, formatTime)
└── vite.config.js
```

## Development Commands

### Backend

```bash
cd moderation-api

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Seed database with initial data
python scripts/seed_db.py

# Start development server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest
```

### Frontend

```bash
cd moderation-ui

# Install dependencies
npm install

# Start development server (uses MSW mocks by default)
npm run dev

# Build for production
npm run build
```

### Docker

```bash
# Start infrastructure (PostgreSQL + backend)
docker-compose up -d

# View logs
docker-compose logs -f backend
```

## Key Architectural Patterns

### API Contract

All API responses follow a standardized format. The frontend expects:

**Success response:**
```json
{
  "data": { ... },
  "meta": { ... }
}
```

**Error response:**
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": null
  }
}
```

**Login response (frontend contract):**
```json
{
  "user": { "id": "...", "name": "...", "email": "..." },
  "accessToken": "jwt_token_here",
  "expiresIn": 691200
}
```

### Authentication

- Backend uses JWT tokens with OAuth2 password flow
- Frontend stores token in `localStorage` as `shieldai_token`
- All API requests include `Authorization: Bearer {token}` header
- Auth dependency: `CurrentUser` in backend, token check in `api.js`

### State Management

Frontend uses Zustand for global state:
- `user`: Current authenticated user
- `messages`: Message history from simulation
- `queue`: Review queue for human moderation
- `selectedMessageId`: Currently selected message in review
- `policies`: Policy configuration thresholds

### Database Models

Current models (in `app/models/`):
- `User`: id, email, hashed_password, is_active, is_superuser, created_at

Planned models (per README):
- `Message`: id, content, content_type, customer_id, user_id, created_at
- `ModerationResult`: id, message_id, stage, risk_score, labels, decision, model_version
- `ReviewerDecision`: id, message_id, reviewer_id, decision, notes
- `PolicyConfig`: id, customer_id, region, rules

### API Endpoints

Implemented:
- `POST /v1/auth/login` - User authentication
- `GET /v1/auth/me` - Get current user
- `GET /health` - Health check

Planned (frontend contract):
- `POST /moderate` - Synchronous content moderation (fast path)
- `GET /jobs/:jobId` - Get async job status
- `GET /review` - Get review queue with filters
- `POST /decision` - Submit reviewer decision
- `GET /analytics` - Get analytics data
- `GET /policies` - Get policy configuration
- `PUT /policies` - Update policy configuration

### Frontend Mocking

The frontend uses MSW (Mock Service Worker) for API prototyping:
- Mock handlers defined in `src/mock/handlers.js`
- Mock data in `src/mock/messages.js`
- To connect to real backend, set `VITE_API_URL` in `.env`

### Environment Configuration

Backend (`.env`):
- `SECRET_KEY`: JWT signing key
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration
- `BACKEND_CORS_ORIGINS`: Comma-separated CORS origins
- `POSTGRES_SERVER`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`: Database connection

Frontend (`.env`):
- `VITE_API_URL`: Backend API base URL (defaults to `http://localhost:3001`)

## Tech Stack

**Backend:**
- FastAPI 0.111.0
- SQLAlchemy 2.0.30 (ORM)
- Alembic (migrations)
- Pydantic v2 (validation)
- PostgreSQL (database)
- JWT (authentication)

**Frontend:**
- React 19 (Vite)
- Zustand (state management)
- React Router 6 (routing)
- MSW (API mocking)
- Recharts (analytics charts)

## Current State

The project is in **Product Prototype** stage:
- Frontend is feature-complete with mock data
- Backend implements authentication and basic user management
- Core moderation endpoints, ML pipeline, and async workers are planned

Refer to `README.md` for the full system architecture and roadmap.