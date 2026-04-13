# 🧪 Experiment Tracker

A lightweight, reproducible ML experiment tracking system for students & junior practitioners.

> Replace manual Excel/note logging with automated, versioned tracking.

---

## 📁 Project Structure

```
experiment-tracker/
├── backend/          FastAPI + SQLAlchemy + Alembic + Pytest
│   ├── app/
│   │   ├── api/v1/   Route handlers
│   │   ├── core/     Config, Auth, Cache
│   │   ├── db/       Engine & session
│   │   ├── models/   SQLAlchemy ORM
│   │   ├── schemas/  Pydantic validation
│   │   └── services/ Business logic
│   ├── alembic/      DB migrations
│   └── tests/        Unit + integration tests
├── sdk/              Python SDK (pip installable)
│   └── exp_tracker/  client.py, cli.py
├── frontend/         React + TypeScript + Tailwind (Phase 2)
├── demo/             BTC-LSTM demo script
├── docker-compose.yml
└── Makefile
```

---

## 🚀 Quick Start

### Option A: Docker (recommended)

```bash
docker compose up --build
# API → http://localhost:8000
# Docs → http://localhost:8000/docs
```

### Option B: Local dev

```bash
# 1. Start DB + Redis
make dev-bg

# 2. Install & migrate
make install
make db-migrate

# 3. Run API
make dev

# 4. Register demo user
make demo-register
```

---

## 🔑 API Usage

All endpoints require `X-API-Key` header except `/health`.

### Register a user
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@ml.com","password":"secret"}'
# Response includes api_key
```

### Create a run
```bash
curl -X POST http://localhost:8000/api/v1/runs \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "experiment_name": "btc_experiment",
    "name": "btc_LSTM_ohlcv_20260101",
    "params": {"lr": 0.001, "epochs": 10},
    "data_version": "v1.0"
  }'
```

### Log metrics
```bash
curl -X POST http://localhost:8000/api/v1/runs/{run_id}/metrics \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "metrics": [
      {"key": "train_loss", "value": 0.42, "step": 1},
      {"key": "train_acc",  "value": 0.88, "step": 1}
    ]
  }'
```

### Compare runs
```bash
curl "http://localhost:8000/api/v1/runs/compare?ids=ID1,ID2&metrics=train_loss,train_acc" \
  -H "X-API-Key: YOUR_KEY"
```

---

## 🐍 Python SDK

```bash
pip install -e sdk/
```

```python
from exp_tracker import ExperimentTracker

tracker = ExperimentTracker(api_key="YOUR_KEY", base_url="http://localhost:8000")

# Context manager — auto-finish on success, auto-fail on exception
with tracker.run(
    name="btc_LSTM_ohlcv_20260101",
    experiment="btc_experiment",
    params={"lr": 0.001, "hidden": 128},
    data_version="v1.0",
) as run:
    for epoch in range(10):
        loss = train_epoch(epoch)
        run.log({"train_loss": loss, "train_acc": acc}, step=epoch)

# Compare runs
report = tracker.compare_runs(["run-id-1", "run-id-2"], ["train_loss", "val_loss"])

# Get chart data
chart = tracker.get_chart_data(["run-id-1"], "train_loss")
```

---

## 💻 CLI

```bash
# Install SDK with CLI extras
pip install -e sdk/[cli]

# Create a run
exp-cli run create --name btc_LSTM_ohlcv_20260101 \
  --experiment btc_experiment \
  --params lr=0.001 hidden=128 \
  --api-key YOUR_KEY

# List runs
exp-cli run list --experiment btc_experiment

# Compare runs
exp-cli run compare --ids ID1,ID2 --metrics train_loss,val_loss

# Sync offline metrics
exp-cli sync
```

---

## 🧪 Testing

```bash
# Unit tests (no DB needed)
make test

# Integration tests (needs DB + Redis running)
make test-integration

# All tests + coverage
make test-all

# SDK tests
make test-sdk
```

---

## 📋 Run Naming Convention

Runs must follow: `project_ModelName_dataset_YYYYMMDD`

```
✓ btc_LSTM_ohlcv_20260101
✓ sol_Transformer_btcusd_20260201
✗ MyRun          (no date, wrong case)
✗ BTC_lstm_v1    (uppercase project, no date)
```

---

## 🗄️ Database Schema

| Table | Description |
|-------|-------------|
| `users` | API key-based auth |
| `experiments` | Named groups of runs |
| `runs` | Individual training runs with JSONB params |
| `metrics` | Time-series metrics indexed by (run_id, key, step) |
| `tags` | Labels for runs |
| `run_tags` | Many-to-many run↔tag |

---

## 🔄 Run State Machine

```
created → running → completed
                 ↘ failed
                 ↘ paused → running
```

Invalid transitions are blocked with a 422 error.

---

## 📦 Roadmap

| Phase | Duration | Focus |
|-------|----------|-------|
| **MVP** ✅ | 4 weeks | Core loop, DB, SDK, UI table/chart |
| Beta | 3 weeks | Async tasks, tags, auth, offline sync, comparison UI |
| Advanced | Optional | Framework callbacks, stat tests, artifact storage |
