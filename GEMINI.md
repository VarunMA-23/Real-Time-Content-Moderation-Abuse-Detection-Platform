# ShieldAI - Real-Time Content Moderation Platform

ShieldAI is a production-grade, multi-stage content moderation system designed for large-scale applications. It features a synchronous "fast-path" for ultra-low latency decisions and an asynchronous "deep analysis" pipeline utilizing Transformers and LLMs.

## 🏗️ Project Architecture

The system is divided into two main components:
- **`moderation-api/`**: A FastAPI-based backend that handles synchronous moderation requests, manages the policy engine, and coordinates asynchronous deep analysis.
- **`moderation-ui/`**: A React-based dashboard for human reviewers and administrators to monitor content, manage policies, and view analytics.

## 🛠️ Tech Stack

### Backend (`moderation-api/`)
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Alembic
- **Authentication**: JWT (OAuth2 with Password flow)
- **Validation**: Pydantic v2
- **Testing**: Pytest

### Frontend (`moderation-ui/`)
- **Framework**: React 19 (Vite)
- **State Management**: Zustand
- **Routing**: React Router 6
- **Analytics**: Recharts
- **Mocking**: MSW (Mock Service Worker) for API prototyping
- **Styling**: Vanilla CSS / CSS Modules

## 🚀 Getting Started

### Backend Setup
1. Navigate to `moderation-api/`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Configure environment variables in `.env` (copy from `.env.example`).
4. Run migrations: `alembic upgrade head`.
5. Seed the database: `python scripts/seed_db.py`.
6. Start the server: `uvicorn app.main:app --reload --port 8000`.

### Frontend Setup
1. Navigate to `moderation-ui/`.
2. Install dependencies: `npm install`.
3. Start the development server: `npm run dev`.
4. The frontend uses MSW by default to mock API responses. To connect to a real backend, update `VITE_API_URL` in `.env`.

## 📋 Development Conventions

### Backend
- **API Versioning**: All endpoints should be prefixed with `/v1`.
- **Response Format**: Follow the standardized error and success formats as defined in `app/main.py` and the frontend-backend contract.
- **Async/Await**: Use asynchronous database operations and route handlers where possible.
- **Type Hinting**: Maintain strict Pydantic models for request/response validation.

### Frontend
- **State**: Keep global state (auth, policies, queue) in `moderationStore.js`.
- **API Calls**: All external communication should go through the `api.js` service.
- **Components**: Follow the existing atomic-like structure in `src/components/`.
- **Testing**: New features should be prototyped with MSW handlers before backend integration.

## 🗺️ Roadmap & Current State
The project is currently in the **Product Prototype** stage. The frontend is feature-rich but relies heavily on mocks. The backend currently implements authentication and basic user management. 

Refer to `PROJECT_EXECUTION_ROADMAP.md` for the detailed plan to build the Backend MVP and integrate it with the frontend.

## 🛡️ Security & Privacy
- **Auth**: RBAC (Moderator vs. Admin) is planned. Currently, a single admin user can be seeded.
- **Data**: PII redaction should be considered before sending content to external LLM providers (Roadmap item).
- **Secrets**: Never commit `.env` files. Use the provided `.env.example` as a template.
