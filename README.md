# Scalable Notification & Task Processing Service

A production-ready distributed system for asynchronous task processing and notifications.

## Architecture

```
┌────────────┐     HTTP      ┌──────────────┐     RPUSH    ┌───────────┐
│  React UI  │ ──────────── │  FastAPI     │ ──────────── │   Redis   │
│  (port 3000)│              │  Backend     │              │   Queue   │
└────────────┘              │  (port 8000) │              └─────┬─────┘
                            └──────┬───────┘                    │ BLPOP
                                   │ R/W                        ▼
                            ┌──────▼───────┐              ┌───────────┐
                            │  PostgreSQL  │ ◄──────────── │   Worker  │
                            │  (port 5432) │   UPDATE      │  Service  │
                            └─────────────┘              └───────────┘
                                                               │
                                                    ┌──────────▼──────────┐
                                                    │  Prometheus Metrics │
                                                    │  (port 9090/9091)   │
                                                    └─────────────────────┘
```

### Components

| Component | Technology | Port |
|-----------|-----------|------|
| Frontend  | React + TypeScript | 3000 |
| Backend API | FastAPI (Python) | 8000 |
| Worker | Python asyncio | — |
| Queue | Redis | 6379 |
| Database | PostgreSQL | 5432 |
| Metrics | Prometheus | 9091 |

## Why This Stack?

- **FastAPI** – async-native, high-throughput Python API with auto OpenAPI docs
- **Redis queue** – lightweight, fast pub/sub and list-based job queue (BLPOP/RPUSH)
- **Separated worker** – decouples processing from API for independent scaling
- **Docker** – reproducible builds and environment parity across dev/staging/prod
- **Async processing** – non-blocking I/O handles thousands of concurrent tasks

## Database Schema

```
users          tasks               notifications
─────────      ──────────────      ─────────────────
id (UUID)      id (UUID)           id (UUID)
username       user_id (FK)        task_id (FK)
email          title               message
created_at     payload             sent_at
               status (enum)
               created_at
               updated_at
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/tasks` | Submit a new task |
| GET | `/tasks/{id}` | Get task by ID |
| GET | `/tasks` | List all tasks |
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |

### Example Requests

**Submit task:**
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Send email", "payload": "{\"to\": \"user@example.com\"}"}'
```

**Get task status:**
```bash
curl http://localhost:8000/tasks/<task-id>
```

**List tasks:**
```bash
curl "http://localhost:8000/tasks?skip=0&limit=10"
```

## Running Locally

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local frontend dev)
- Python 3.11+ (for local backend dev)

### Start with Docker Compose

```bash
cd notification-system
cp .env.example .env
docker compose up --build
```

Services:
- Frontend → http://localhost:3000
- API → http://localhost:8000
- API Docs → http://localhost:8000/docs
- Prometheus → http://localhost:9091

### Local Backend Development

```bash
cd notification-system/backend
pip install -r requirements.txt
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/taskdb"
export REDIS_URL="redis://localhost:6379/0"
uvicorn backend.main:app --reload
```

### Local Frontend Development

```bash
cd notification-system/frontend
npm install --legacy-peer-deps
REACT_APP_API_URL=http://localhost:8000 npm start
```

## Running Tests

```bash
cd notification-system
pip install -r tests/requirements.txt
pytest tests/ -v
```

## Load Testing

```bash
cd notification-system
# 100 requests, 10 concurrent
./scripts/load_test.sh http://localhost:8000 100 10
```

## Seed Data

```bash
./scripts/seed_tasks.sh http://localhost:8000 20
```

## Docker Setup

Each service has its own Dockerfile:

```
backend/Dockerfile    – FastAPI app
worker/Dockerfile     – Async worker
frontend/Dockerfile   – React build + nginx
```

`docker-compose.yml` orchestrates all services with:
- Health checks on db and redis
- Service dependency ordering
- Environment variable injection
- Persistent PostgreSQL volume

## AWS Deployment

### Infrastructure

```
VPC
├── Public Subnet
│   ├── EC2 (Backend API)  ← t3.small
│   ├── EC2 (Worker)       ← t3.small
│   └── EC2 (Frontend)     ← t3.micro
└── Private Subnet
    ├── RDS PostgreSQL     ← db.t3.micro
    └── ElastiCache Redis  ← cache.t3.micro
```

### Steps

1. **Provision RDS** (PostgreSQL 15) in private subnet
2. **Provision ElastiCache** (Redis 7) in private subnet
3. **Launch EC2** instances with Docker installed
4. **Set environment variables** via EC2 user data or AWS SSM Parameter Store:
   ```
   DATABASE_URL=postgresql+asyncpg://<rds-endpoint>/taskdb
   REDIS_URL=redis://<elasticache-endpoint>:6379/0
   ```
5. **Pull and run containers** on each EC2:
   ```bash
   docker compose -f docker-compose.prod.yml up -d
   ```
6. **Configure ALB** (Application Load Balancer) in front of backend EC2
7. **Configure CloudFront** for frontend static assets (or serve via nginx on EC2)

### Scaling

- Scale worker EC2 instances horizontally to increase throughput
- Redis queue is the shared state — no coordination needed between workers
- Backend API is stateless — add instances behind ALB as needed

## Project Structure

```
notification-system/
├── backend/
│   ├── api/            # routes, schemas
│   ├── db/             # session, Base
│   ├── models/         # SQLAlchemy models
│   ├── services/       # business logic, redis
│   ├── config.py       # settings
│   ├── main.py         # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
├── worker/
│   ├── worker.py       # async consumer
│   ├── config.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/ # TaskForm, TaskTable
│   │   ├── services/   # API client
│   │   ├── types/      # TypeScript interfaces
│   │   ├── App.tsx
│   │   └── App.css
│   ├── public/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── infra/
│   └── prometheus.yml
├── scripts/
│   ├── load_test.sh
│   └── seed_tasks.sh
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   └── test_worker.py
├── docker-compose.yml
├── pytest.ini
└── .env.example
```