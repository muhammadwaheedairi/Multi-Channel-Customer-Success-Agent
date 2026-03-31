# Multi-Channel Customer Success Agent

24/7 AI-powered customer support system handling **Email**, **WhatsApp**, and **Web Form** channels using OpenAI Agents SDK, Kafka event streaming, PostgreSQL with pgvector, and Kubernetes deployment.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    INTAKE CHANNELS                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
    │   Gmail/Email    │         │  WhatsApp/Twilio │         │  Web Form/Next.js│
    │  (Pub/Sub Push)  │         │   (Webhook)      │         │   (React Form)   │
    └────────┬─────────┘         └────────┬─────────┘         └────────┬─────────┘
             │                            │                            │
             ▼                            ▼                            ▼
    ┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
    │ Gmail Handler    │         │ WhatsApp Handler │         │ Support Form API │
    │ gmail_handler.py │         │whatsapp_handler.py│         │support_form.py   │
    │ - Parse email    │         │ - Validate sig   │         │ - Validate input │
    │ - Extract body   │         │ - Extract phone  │         │ - Create customer│
    │ - History API    │         │ - Profile name   │         │ - Create ticket  │
    └────────┬─────────┘         └────────┬─────────┘         └────────┬─────────┘
             │                            │                            │
             └────────────────────────────┼────────────────────────────┘
                                          │
                                          ▼
                              ┌───────────────────────┐
                              │   PostgreSQL + DB     │
                              │   - create_customer   │
                              │   - create_conversation│
                              │   - save_message      │
                              └───────────┬───────────┘
                                          │
                                          ▼
                              ┌───────────────────────┐         ┌──────────────────────────────┐
                              │  Background Task      │         │      Kafka Topics            │
                              │  run_agent()          │         │  (Optional — not used yet)   │
                              │  (FastAPI BG)         │         │                              │
                              └───────────┬───────────┘         │ • fte.tickets.incoming       │
                                          │                     │ • fte.channels.email.inbound │
                                          ▼                     │ • fte.channels.whatsapp.*    │
                    ┌─────────────────────────────────┐         │ • fte.escalations            │
                    │   Customer Success Agent        │         │ • fte.metrics                │
                    │   (OpenAI Agents SDK)           │         │ • fte.dlq                    │
                    │   customer_success_agent.py     │         └──────────────────────────────┘
                    │                                 │
                    │   Model: gpt-4o-mini            │
                    │   System Prompt: prompts.py     │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
        ┌───────────────────────┐     ┌───────────────────────┐
        │   Agent Tools (5)     │     │   PostgreSQL Tables   │
        │   tools.py            │     │                       │
        ├───────────────────────┤     ├───────────────────────┤
        │ • search_knowledge_   │◀────│ • customers           │
        │   base (pgvector)     │     │ • customer_identifiers│
        │                       │     │ • conversations       │
        │ • create_ticket       │────▶│ • messages            │
        │                       │     │ • tickets             │
        │ • get_customer_       │◀────│ • knowledge_base      │
        │   history             │     │   (with embeddings)   │
        │                       │     │ • agent_metrics       │
        │ • escalate_to_human   │────▶│ • channel_configs     │
        │                       │     │                       │
        │ • send_response       │────▶│ (saves outbound msg)  │
        │   (channel-aware)     │     └───────────────────────┘
        └───────────┬───────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │   Response Formatter  │
        │   formatters.py       │
        ├───────────────────────┤
        │ • format_for_email()  │ → Formal, greeting + signature
        │ • format_for_whatsapp()│ → Concise, max 300 chars, emoji
        │ • format_for_web_form()│ → Semi-formal, clear steps
        └───────────┬───────────┘
                    │
                    ▼
        ┌───────────────────────────────────────────────────┐
        │          RESPONSE DELIVERY                        │
        └───────────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┬───────────────────────────┐
        │           │           │                           │
        ▼           ▼           ▼                           ▼
  ┌─────────┐ ┌─────────┐ ┌─────────────┐         ┌──────────────┐
  │ Gmail   │ │ Twilio  │ │ Web Portal  │         │  Sentiment   │
  │ API     │ │ WhatsApp│ │ + Email     │         │  Analysis    │
  │ Reply   │ │ API     │ │ Notify      │         │  sentiment.py│
  └─────────┘ └─────────┘ └─────────────┘         └──────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           KUBERNETES DEPLOYMENT LAYER                                           │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  ┌────────────────────────────────────────┐    ┌────────────────────────────────────────┐     │
│  │  fte-api Deployment                    │    │  fte-worker Deployment                 │     │
│  │  (FastAPI + Uvicorn)                   │    │  (Kafka Message Processor)             │     │
│  ├────────────────────────────────────────┤    ├────────────────────────────────────────┤     │
│  │  Replicas: 2 (min) → 10 (max)         │    │  Replicas: 2 (min) → 20 (max)         │     │
│  │  HPA: CPU 70% threshold                │    │  HPA: CPU 70% threshold                │     │
│  │  Resources: 256Mi-512Mi, 250m-500m CPU │    │  Resources: 256Mi-512Mi, 250m-500m CPU │     │
│  │  Health: /health endpoint              │    │  Command: message_processor.py         │     │
│  │  Port: 8000                            │    │  Consumes: fte.tickets.incoming        │     │
│  └────────────────────────────────────────┘    └────────────────────────────────────────┘     │
│                                                                                                 │
│  ┌────────────────────────────────────────────────────────────────────────────────────────┐   │
│  │  Services: fte-api-service (ClusterIP:80 → 8000)                                       │   │
│  │  Ingress: nginx → fte-api-service                                                      │   │
│  │  ConfigMap: fte-config (DATABASE_URL, KAFKA_BOOTSTRAP)                                 │   │
│  │  Secrets: fte-secrets (OPENAI_API_KEY, TWILIO_AUTH_TOKEN)                              │   │
│  └────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              INFRASTRUCTURE SERVICES                                            │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│  PostgreSQL (pgvector/pgvector:pg17)  │  Kafka (apache/kafka:3.7.0)  │  Next.js Web Portal    │
│  Port: 5432                            │  Port: 9092                   │  Port: 3000            │
│  DB: fte_db                            │  KRaft mode (no Zookeeper)    │  React 19 + Tailwind   │
│  User: fte_user                        │  Auto-create topics: enabled  │  shadcn/ui components  │
│  Extensions: pgvector                  │  Replication factor: 1        │  API: localhost:8000   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
Multi-Channel-Customer-Success-Agent/
├── README.md                                    # This file — architecture + setup
├── RUNBOOK.md                                   # Operations guide — health checks, incidents
│
├── backend/                                     # Python FastAPI backend
│   ├── Dockerfile                               # Production API container image
│   ├── Dockerfile.worker                        # Worker container for Kafka consumers
│   ├── pyproject.toml                           # uv dependencies (FastAPI, asyncpg, openai-agents)
│   ├── uv.lock                                  # Locked dependency versions
│   ├── pytest.ini                               # Pytest configuration
│   ├── main.py                                  # Legacy entry point (unused)
│   │
│   ├── agent/                                   # OpenAI Agents SDK agent definition
│   │   ├── __init__.py
│   │   ├── customer_success_agent.py            # Agent definition + run_agent() function
│   │   ├── tools.py                             # 5 @function_tool definitions
│   │   ├── prompts.py                           # SYSTEM_PROMPT with workflow rules
│   │   ├── formatters.py                        # Channel-specific response formatting
│   │   ├── sentiment.py                         # Sentiment analysis (keyword-based)
│   │   └── embeddings.py                        # OpenAI embeddings for pgvector search
│   │
│   ├── api/                                     # FastAPI application
│   │   ├── __init__.py
│   │   ├── main.py                              # FastAPI app + lifespan + CORS + routers
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── support_form.py                  # POST /support/submit (web form intake)
│   │       ├── customers.py                     # Customer CRUD endpoints
│   │       ├── tickets.py                       # Ticket CRUD endpoints
│   │       ├── metrics.py                       # GET /metrics/summary, /channels, /latency
│   │       └── conversations.py                 # Conversation history endpoints
│   │
│   ├── channels/                                # Channel-specific webhook handlers
│   │   ├── __init__.py
│   │   ├── gmail_handler.py                     # POST /webhooks/gmail (Pub/Sub push)
│   │   ├── gmail_auth.py                        # OAuth2 token management for Gmail API
│   │   └── whatsapp_handler.py                  # POST /webhooks/whatsapp (Twilio webhook)
│   │
│   ├── core/                                    # Core utilities
│   │   ├── __init__.py
│   │   ├── config.py                            # Pydantic settings (DATABASE_URL, OPENAI_API_KEY)
│   │   ├── logging.py                           # Structlog configuration
│   │   └── exceptions.py                        # Custom exception handlers
│   │
│   ├── database/                                # PostgreSQL connection + queries
│   │   ├── __init__.py
│   │   ├── connection.py                        # asyncpg pool management
│   │   └── queries.py                           # CRUD functions (customers, tickets, messages)
│   │
│   ├── kafka/                                   # Kafka client wrappers
│   │   ├── __init__.py
│   │   ├── client.py                            # FTEProducer + FTEConsumer (aiokafka)
│   │   └── topics.py                            # Topic name constants
│   │
│   ├── workers/                                 # Background workers
│   │   ├── __init__.py
│   │   ├── message_processor.py                 # Kafka consumer → agent processor
│   │   ├── metrics_collector.py                 # Publish DB metrics to Kafka every 60s
│   │   └── daily_report.py                      # Generate daily sentiment report
│   │
│   └── tests/                                   # Test suite
│       ├── conftest.py                          # Pytest fixtures (DB, mock agent)
│       ├── test_agent.py                        # Agent tool tests
│       ├── test_channels.py                     # Channel webhook tests
│       └── load_test.py                         # Locust load test (50 users, 60s)
│
├── context/                                     # Agent context files
│   ├── brand-voice.md                           # Tone guidelines (formal/casual per channel)
│   ├── company-profile.md                       # Company info for agent context
│   ├── product-docs.md                          # Product documentation (seeded to knowledge_base)
│   ├── escalation-rules.md                      # When to escalate (pricing, legal, refunds)
│   ├── sample-tickets.json                      # Sample ticket data for testing
│   ├── credentials.json                         # Gmail OAuth2 credentials (gitignored)
│   ├── token.json                               # Gmail OAuth2 token (gitignored)
│   └── last_history_id.txt                      # Gmail Pub/Sub history tracking
│
├── infra/                                       # Infrastructure as code
│   ├── docker-compose.yml                       # Local dev: PostgreSQL + Kafka
│   └── k8s/                                     # Kubernetes manifests
│       ├── namespace.yaml                       # fte namespace
│       ├── configmap.yaml                       # Environment variables
│       ├── secrets.yaml                         # Sensitive config (base64 encoded)
│       ├── deployment-api.yaml                  # fte-api deployment + service
│       ├── deployment-worker.yaml               # fte-worker deployment
│       ├── service.yaml                         # ClusterIP service for API
│       ├── ingress.yaml                         # Nginx ingress rules
│       ├── hpa.yaml                             # HorizontalPodAutoscaler (2-10 API, 2-20 worker)
│       └── monitoring.yaml                      # Prometheus ServiceMonitor
│
├── specs/                                       # Project documentation
│   ├── customer-success-fte-spec.md             # Original requirements spec
│   ├── discovery-log.md                         # Implementation decisions log
│   ├── skills-manifest.md                       # Agent skills breakdown
│   └── transition-checklist.md                  # Production readiness checklist
│
└── web-portal/                                  # Next.js 16 frontend
    ├── Dockerfile                               # Production Next.js container
    ├── package.json                             # Dependencies (Next 16, React 19, shadcn)
    ├── package-lock.json                        # Locked npm dependencies
    ├── tsconfig.json                            # TypeScript configuration
    ├── next.config.ts                           # Next.js config
    ├── next-env.d.ts                            # Next.js TypeScript declarations
    ├── components.json                          # shadcn/ui configuration
    ├── CLAUDE.md                                # Claude Code instructions
    ├── AGENTS.md                                # Next.js version warning
    │
    ├── app/                                     # Next.js App Router
    │   ├── layout.tsx                           # Root layout (fonts, metadata)
    │   ├── page.tsx                             # Landing page (hero, features, CTA)
    │   ├── globals.css                          # Tailwind CSS imports
    │   │
    │   ├── (public)/                            # Public routes
    │   │   └── support/
    │   │       ├── page.tsx                     # Support form (submit ticket)
    │   │       └── ticket/[id]/
    │   │           └── page.tsx                 # Ticket detail page (messages)
    │   │
    │   └── (admin)/                             # Admin routes
    │       └── dashboard/
    │           └── page.tsx                     # Metrics dashboard
    │
    ├── components/                              # React components
    │   ├── Header.tsx                           # Site header with navigation
    │   ├── Footer.tsx                           # Site footer
    │   └── ui/                                  # shadcn/ui components
    │       ├── button.tsx                       # Button component
    │       ├── card.tsx                         # Card component
    │       ├── input.tsx                        # Input component
    │       ├── label.tsx                        # Label component
    │       ├── select.tsx                       # Select dropdown
    │       ├── textarea.tsx                     # Textarea component
    │       └── badge.tsx                        # Badge component
    │
    └── lib/                                     # Utilities
        ├── api.ts                               # API client functions (fetch wrappers)
        ├── types.ts                             # TypeScript type definitions
        └── utils.ts                             # Utility functions (cn, etc.)
```

---

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- Docker + Docker Compose
- OpenAI API key

### 1. Start Infrastructure
```bash
cd infra
docker compose up -d
```

### 2. Start Backend API
```bash
cd backend
export OPENAI_API_KEY=sk-...
export DATABASE_URL=postgresql://fte_user:fte_password@localhost:5432/fte_db
uv run uvicorn api.main:app --port 8000 --reload
```

### 3. Start Web Portal
```bash
cd web-portal
npm install
npm run dev
```

### 4. Test Channels
- **Web Form**: http://localhost:3000/support
- **WhatsApp**: POST to `/webhooks/whatsapp/test`
- **Email**: POST to `/webhooks/gmail/test`

---

## Key Features

✅ **Multi-Channel Support** — Email (Gmail API), WhatsApp (Twilio), Web Form
✅ **OpenAI Agents SDK** — Autonomous agent with 5 tools
✅ **pgvector Search** — Semantic knowledge base search
✅ **Sentiment Analysis** — Auto-escalate negative sentiment
✅ **Channel-Aware Formatting** — Formal email vs casual WhatsApp
✅ **Kubernetes Ready** — HPA autoscaling (2-10 API, 2-20 workers)
✅ **Kafka Event Streaming** — Async message processing
✅ **Real-Time Metrics** — Latency, escalation rate, sentiment tracking

---

## Tech Stack

**Backend**: FastAPI, asyncpg, OpenAI Agents SDK, aiokafka, structlog
**Database**: PostgreSQL 17 + pgvector extension
**Agent**: OpenAI gpt-4o-mini with function calling
**Frontend**: Next.js 16, React 19, Tailwind CSS, shadcn/ui
**Infrastructure**: Docker, Kubernetes, Kafka (KRaft mode)
**Channels**: Gmail API (Pub/Sub), Twilio WhatsApp API

---

## Production Deployment

### Kubernetes
```bash
kubectl apply -f infra/k8s/namespace.yaml
kubectl apply -f infra/k8s/configmap.yaml
kubectl apply -f infra/k8s/secrets.yaml
kubectl apply -f infra/k8s/deployment-api.yaml
kubectl apply -f infra/k8s/deployment-worker.yaml
kubectl apply -f infra/k8s/hpa.yaml
kubectl apply -f infra/k8s/ingress.yaml
```

### Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","env":"development","database":"connected","channels":["web_form","whatsapp","email"]}
```

---

## Monitoring

- **Metrics API**: `GET /metrics/summary`, `/metrics/channels`, `/metrics/latency`
- **Daily Report**: `GET /metrics/daily-report`
- **Logs**: Structured JSON logs via structlog
- **Kubernetes**: HPA scales based on CPU (70% threshold)

---

## License

MIT
