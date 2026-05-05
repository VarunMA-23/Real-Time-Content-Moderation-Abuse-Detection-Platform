# ReadMe file final

# 🛡️ ShieldAI — Real-Time Content Moderation Platform

<aside>
🛡️

> A production-grade, multi-stage content moderation system built for large-scale social and chat applications. Detects hate speech, spam, sexual content, self-harm, and coordinated abuse across text and images — in real time.
> 
</aside>

---

## 📌 Table of Contents

- [Overview]
- [System Architecture]
- [System Flow]
- [Core Features]
- [Tech Stack]
- [ML Pipeline]
- [Datasets]
- [Database Schema]
- [Scalability Design]
- [Security Design]
- [Failure Handling]
- [Human-in-the-Loop Learning]
- [Getting Started]
- [Project Structure]
- [Roadmap]

---

## Overview

ShieldAI is a platform used by large social and chat applications to moderate user-generated content in real time. It supports **millions of messages per day** with sub-second latency on the fast path, a multi-stage ML pipeline for deep analysis, and a human reviewer console with feedback loops.

**Key design goals:**

- Ultra-low latency for the synchronous "pre-send" API
- Scalable async pipeline for LLM-based deep analysis
- Configurable policy engine per customer and region
- Human-in-the-loop feedback to continuously improve models
- Graceful degradation if any ML service goes down

---

## System Architecture

```
Client App
    │
    ▼
API Gateway
    │
    ▼
Moderation API (FastAPI)
    ├── Fast Path (inline): Lightweight ML model + Rules Engine
    │       └── Decision: ALLOW / WARN / BLOCK  ──────────────► Response to Client
    │
    └── Enqueue to `moderation_jobs` topic (Kafka/RabbitMQ)
                │
                ▼
        ┌───────────────────────────────────┐
        │         Worker Services           │
        │                                   │
        │  ┌─────────────────────────────┐  │
        │  │  Text Classification Worker │  │
        │  │  (Transformers - fast)      │  │
        │  └─────────────────────────────┘  │
        │                                   │
        │  ┌─────────────────────────────┐  │
        │  │  LLM Moderation Worker      │  │
        │  │  (GPT / Claude / Local LLM) │  │
        │  └─────────────────────────────┘  │
        │                                   │
        │  ┌─────────────────────────────┐  │
        │  │  Image Moderation Worker    │  │
        │  │  (CV / NSFW models)         │  │
        │  └─────────────────────────────┘  │
        └───────────────────────────────────┘
                │
                ▼
        `moderation_results` topic
                │
                ▼
        Moderation DB (PostgreSQL)
                │
                ├──► Review Console (Flagged content queues)
                │
                └──► Data Warehouse (Analytics + Model training)
```

---

## System Flow

### Stage 1 — Fast Path (Synchronous, <100ms)

When a user sends a message, the **Moderation API** immediately runs:

1. A lightweight, fine-tuned ML classifier to score the message.
2. The Policy Engine (cached in Redis) to apply platform-specific rules.
3. Returns a decision: `ALLOW`, `WARN`, or `BLOCK`.

### Stage 2 — Deep Analysis (Asynchronous)

In parallel, the message is enqueued to Kafka and consumed by worker services:

1. **Text Classification Worker** — transformer-based toxicity/spam detection.
2. **LLM Worker** — uses an LLM with few-shot prompts tuned to the platform policy for nuanced, contextual analysis.
3. **Image Worker** — runs CV models for NSFW/graphic content detection.

Results are written to the Moderation DB and surfaced in the Reviewer Console.

### Stage 3 — Human Review

Flagged content lands in a reviewer queue. Reviewers approve, reject, or escalate decisions. All decisions feed back as labeled training data.

### Stage 4 — Learning Loop

When the lightweight ML model and the LLM disagree (e.g., ML says `safe`, LLM says `toxic`), the disagreement is stored separately in the Data Warehouse and flagged for active learning — prioritizing labeling on uncertain/conflicting cases to improve the fast model over time.

---

## Core Features

| Feature | Description |
| --- | --- |
| **Pre-send Moderation API** | Synchronous scoring with <100ms target latency |
| **Async Deep Pipeline** | LLM + image moderation via message queue workers |
| **Policy Engine** | Configurable rules per customer, region, and platform |
| **Reviewer Console** | Queues, decision history, appeal workflow |
| **Analytics Dashboard** | Policy impact, false positive/negative tracking |
| **Human-in-the-Loop** | Reviewer decisions fed back as training labels |
| **Conflict Detection** | ML vs. LLM disagreements flagged for retraining |
| **Bulk Replay** | Re-scan historical messages after policy/model changes |

---

## Tech Stack

| Layer | Technology |
| --- | --- |
| **API** | FastAPI |
| **Async Workers** | Celery / Custom Kafka consumers |
| **Message Queue** | Kafka / RabbitMQ |
| **Primary DB** | PostgreSQL |
| **Search / Audit** | Elasticsearch / OpenSearch |
| **Cache** | Redis (policies, trust scores) |
| **ML — Fast** | Transformers (fine-tuned BERT/DistilBERT) |
| **ML — Deep** | OpenAI / Anthropic / Local LLM via LangChain |
| **Image ML** | CV-based NSFW detection models |
| **Deployment** | Docker + Kubernetes (autoscaled by queue depth) |

---

## ML Pipeline

```
Incoming Message
       │
       ▼
  ┌──────────────────────────────────┐
  │   Stage 1: Lightweight Classifier │   ← <50ms target
  │   (fine-tuned DistilBERT)        │
  └──────────────────────────────────┘
       │
       ├── Clearly Safe → ALLOW
       ├── Clearly Harmful → BLOCK
       └── Borderline / Uncertain
                   │
                   ▼
          ┌─────────────────────────┐
          │  Stage 2: LLM Analysis  │   ← async, deeper context
          │  (few-shot, policy-aware│
          └─────────────────────────┘
                   │
                   └── Detailed risk label + explanation → DB
```

**Conflict case:** If Stage 1 says `safe` and Stage 2 says `toxic` (or vice versa), the result is stored in the warehouse as a high-value training example.

---

## Datasets

The lightweight ML model is trained on a fused combination of three public datasets:

| Dataset | Use Case |
| --- | --- |
| [Jigsaw Toxic Comment Dataset](https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge) | Toxicity, insults, obscenity, threats |
| [Hate Speech and Offensive Language Dataset](https://github.com/t-davidson/hate-speech-and-offensive-language) | Hate speech vs. offensive language classification |
| [SMS Spam Collection Dataset](https://archive.ics.uci.edu/ml/datasets/SMS+Spam+Collection) | Spam detection |

> **Note:** These datasets have no common schema, so a key challenge is the fusion strategy — mapping heterogeneous labels into a unified multi-label taxonomy (`toxic`, `hate`, `spam`, `safe`, etc.) before training.
> 

---

## Database Schema

The Moderation DB stores the full lifecycle of every moderated message:

```sql
messages (
  id              UUID PRIMARY KEY,
  content         TEXT,
  content_type    ENUM('text', 'image', 'voice'),
  customer_id     UUID,
  user_id         UUID,
  created_at      TIMESTAMP
)

moderation_results (
  id              UUID PRIMARY KEY,
  message_id      UUID REFERENCES messages(id),
  stage           ENUM('fast_model', 'llm', 'image'),
  risk_score      FLOAT,
  labels          JSONB,        -- e.g. {"toxic": 0.91, "spam": 0.02}
  decision        ENUM('allow', 'warn', 'block', 'hold_for_review'),
  model_version   VARCHAR,
  created_at      TIMESTAMP
)

reviewer_decisions (
  id              UUID PRIMARY KEY,
  message_id      UUID REFERENCES messages(id),
  reviewer_id     UUID,
  decision        ENUM('confirm', 'override', 'escalate'),
  notes           TEXT,
  created_at      TIMESTAMP
)

policy_configs (
  id              UUID PRIMARY KEY,
  customer_id     UUID,
  region          VARCHAR,
  rules           JSONB,
  updated_at      TIMESTAMP
)
```

---

## Scalability Design

- **Fast path** and **LLM workers** are separate deployments — independently scaled based on queue depth and CPU/GPU availability.
- **Redis** caches policy configs and user trust scores to avoid DB hits on every request.
- **Per-customer rate limiting** to prevent abuse and burst spam attacks.
- **K8s autoscaling** on both API tier and worker tier, triggered by Kafka consumer lag.

---

## Security Design

- **Auth:** OAuth2/OIDC for the reviewer console; RBAC for reviewer vs. admin roles.
- **Internal services:** mTLS between all microservices; strict Kubernetes network policies.
- **Privacy:** PII detection and redaction before content is sent to external LLM APIs.
- **Adversarial robustness:** Detection of obfuscation attempts (l33tspeak, homoglyphs, zero-width characters).
- **IP reputation:** Integration with abuse intelligence feeds for coordinated attack detection.

---

## Failure Handling

| Failure | Response |
| --- | --- |
| LLM service down | Fall back to rule-based conservative blocking or hold for review |
| Image service down | Hold for review, no silent allow |
| Message processing failure | Dead Letter Queue (DLQ) + alert surfaced to ops |
| Repeated DLQ failures | Manual review escalation |
| Analytics warehouse slow | Graceful degradation — UI shows cached/stale data |
| Policy update | Bulk replay job to re-scan last N hours of messages |

---

## Human-in-the-Loop Learning

Reviewer decisions are the core feedback signal for model improvement:

```
Reviewer Decision
       │
       ▼
  ┌─────────────────────────────────────┐
  │  Was there a model disagreement?    │
  └─────────────────────────────────────┘
       │                    │
      YES                   NO
       │                    │
       ▼                    ▼
  High-priority         Standard
  training example      training example
  (active learning)
       │
       ▼
  Data Warehouse → Periodic fine-tuning → Updated fast model
```

This enables the fast lightweight model to continuously improve from real-world reviewer corrections — a classic **active learning** loop that prioritizes the most uncertain or conflicting cases.

---

## Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Node.js 18+ (for the reviewer console UI)

### Local Setup

```bash
# Clone the repository
git clone <https://github.com/your-username/shieldai.git>
cd shieldai

# Start infrastructure (Kafka, Redis, PostgreSQL)
docker-compose up -d

# Install Python dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the Moderation API
uvicorn app.main:app --reload --port 8000

# Start workers (in a separate terminal)
celery -A app.workers worker --loglevel=info
```

### API Usage

```bash
# Score a message (synchronous fast path)
curl -X POST <http://localhost:8000/v1/moderate> \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Your content here",
    "customer_id": "abc123",
    "user_id": "user456"
  }'

# Response
{
  "decision": "allow",
  "risk_score": 0.04,
  "labels": { "toxic": 0.02, "spam": 0.04 },
  "latency_ms": 43
}
```

---

## Project Structure

```
shieldai/
├── app/
│   ├── api/              # FastAPI routes (moderation, review, policy)
│   ├── workers/          # Celery workers (text, LLM, image)
│   ├── models/           # ML model loading and inference
│   ├── policy/           # Policy engine logic
│   ├── db/               # SQLAlchemy models and migrations
│   └── core/             # Config, auth, shared utilities
├── ml/
│   ├── datasets/         # Dataset fusion and preprocessing scripts
│   ├── training/         # Fine-tuning scripts
│   └── evaluation/       # Metrics and evaluation notebooks
├── console/              # Reviewer console frontend (React)
├── infra/
│   ├── docker-compose.yml
│   └── k8s/              # Kubernetes manifests
├── tests/
└── README.md
```

---

## Roadmap

- [ ]  Voice moderation pipeline (Whisper-based transcription + text moderation)
- [ ]  Multilingual support (cross-lingual toxicity detection)
- [ ]  Real-time reviewer dashboard with WebSocket updates
- [ ]  A/B testing framework for policy changes
- [ ]  On-device / edge moderation for mobile clients
- [ ]  Coordinated inauthentic behavior (CIB) detection module

---

## Ethical Considerations

This system involves real tradeoffs:

- **Latency vs. Accuracy:** The fast path sacrifices some accuracy for speed. The LLM path is more accurate but cannot be synchronous at scale.
- **Fairness:** Toxicity models are known to have demographic biases (e.g., higher false positive rates for AAVE). Reviewer feedback loops are critical to monitoring and correcting this.
- **Policy subjectivity:** What counts as "harmful" varies by culture, region, and platform. The configurable policy engine exists precisely to avoid one-size-fits-all moderation.
- **Over-moderation:** False positives suppress legitimate speech. The false positive tracking in analytics is a first-class metric, not an afterthought.

---

## Resume Impact

This project demonstrates:

- Multi-stage ML pipelines (fast model → LLM cascade)
- Real-time and async system design with message queues
- Human-in-the-loop and active learning workflows
- Content safety domain expertise
- Distributed systems: autoscaling, caching, graceful degradation
- Security: zero-trust, PII redaction, adversarial robustness

---

> <p align="center">Built with ❤️ for safer online communities.</p>
