# Deployment Guide

## Local Development (Quickest)

```bash
# 1. Clone and enter project
cd experiment-tracker

# 2. Start infrastructure
docker compose up -d db redis

# 3. Install backend
cd backend && pip install -r requirements.txt
cp .env.example .env   # edit as needed

# 4. Run migrations
alembic upgrade head

# 5. Start API
uvicorn app.main:app --reload --port 8000

# 6. Install + start frontend
cd ../frontend
cp .env.example .env
npm install && npm run dev
```

Access:
- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- Frontend: http://localhost:5173

---

## Docker Compose (Full Stack)

```bash
docker compose up --build
```

Services started:
| Service  | Port  | Notes                        |
|----------|-------|------------------------------|
| api      | 8000  | FastAPI + hot-reload         |
| frontend | 5173  | Vite dev server              |
| db       | 5432  | PostgreSQL 16                |
| redis    | 6379  | Redis 7 (cache + rate limit) |

### First-time setup after `docker compose up`:

```bash
# Register a user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@ml.com","password":"secret"}'

# Copy the api_key from the response, then open Settings in the frontend
# and paste it in.
```

---

## Production Checklist

- [ ] Change `SECRET_KEY` in `.env` (`openssl rand -hex 32`)
- [ ] Change `ADMIN_API_KEY`
- [ ] Set `DEBUG=false`, `APP_ENV=production`
- [ ] Use a real password for PostgreSQL
- [ ] Put API behind nginx/Caddy with TLS
- [ ] Set `CORS` origins to your frontend domain in `app/main.py`
- [ ] Run `alembic upgrade head` on first deploy
- [ ] Set up DB backups (pg_dump cron or Supabase)

---

## Makefile Shortcuts

```bash
make dev              # start API with hot-reload
make dev-docker       # full docker compose up --build
make dev-bg           # only DB + Redis in background
make db-migrate       # alembic upgrade head
make db-reset         # drop all + re-migrate (⚠ destroys data)
make test             # unit tests
make test-integration # needs DB + Redis running
make test-all         # all tests + coverage report
make test-sdk         # SDK tests
make demo-register    # create demo user
make demo-run         # run the BTC-LSTM demo script
make health           # curl /health
```

---

## Environment Variables

| Variable                  | Default                             | Description                    |
|---------------------------|-------------------------------------|--------------------------------|
| `DATABASE_URL`            | postgres+asyncpg://...              | Async DB URL                   |
| `SYNC_DATABASE_URL`       | postgres+psycopg2://...             | Sync DB URL (Alembic)          |
| `REDIS_URL`               | redis://localhost:6379/0            | Redis URL                      |
| `SECRET_KEY`              | dev-secret-key                      | App secret (change in prod!)   |
| `ADMIN_API_KEY`           | admin-dev-key                       | Bootstrap admin key            |
| `APP_ENV`                 | development                         | `development` or `production`  |
| `DEBUG`                   | true                                | SQLAlchemy echo, verbose logs  |
| `RATE_LIMIT_PER_MINUTE`   | 100                                 | API rate limit per IP          |
| `CACHE_TTL`               | 300                                 | Redis cache TTL (seconds)      |
| `MAX_RUNS_PER_EXPERIMENT` | 100                                 | Retention limit per experiment |
