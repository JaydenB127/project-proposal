.PHONY: dev test lint db-migrate db-reset install sdk-install demo help

# ── Setup ──────────────────────────────────────────────────────────────────────
install:
	cd backend && pip install -r requirements.txt
	cd sdk && pip install -e ".[cli]"

sdk-install:
	cd sdk && pip install -e ".[cli]"

# ── Development ────────────────────────────────────────────────────────────────
dev:
	cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

dev-docker:
	docker compose up --build

dev-bg:
	docker compose up -d db redis
	@echo "✓ DB + Redis running. Start API with: make dev"

# ── Database ───────────────────────────────────────────────────────────────────
db-migrate:
	cd backend && alembic upgrade head

db-rollback:
	cd backend && alembic downgrade -1

db-reset:
	cd backend && alembic downgrade base && alembic upgrade head

db-revision:
	cd backend && alembic revision --autogenerate -m "$(msg)"

# ── Testing ────────────────────────────────────────────────────────────────────
test:
	cd backend && pytest tests/unit/ -v --tb=short

test-integration:
	cd backend && pytest tests/integration/ -v --tb=short

test-all:
	cd backend && pytest -v --tb=short --cov=app --cov-report=term-missing

test-sdk:
	cd sdk && pytest tests/ -v

# ── Linting ────────────────────────────────────────────────────────────────────
lint:
	cd backend && python -m py_compile $$(find app -name "*.py") && echo "✓ No syntax errors"

# ── Demo helpers ───────────────────────────────────────────────────────────────
demo-register:
	@curl -s -X POST http://localhost:8000/api/v1/auth/register \
	  -H "Content-Type: application/json" \
	  -d '{"username":"demo","email":"demo@exp.local","password":"demo1234"}' | python3 -m json.tool

demo-run:
	@python3 demo/run_demo.py

health:
	@curl -s http://localhost:8000/health | python3 -m json.tool

# ── Help ───────────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "  make install          Install all dependencies"
	@echo "  make dev              Start API in dev mode (hot reload)"
	@echo "  make dev-docker       Start everything via Docker Compose"
	@echo "  make dev-bg           Start only DB + Redis in background"
	@echo "  make db-migrate       Run pending Alembic migrations"
	@echo "  make db-reset         Drop + re-migrate DB"
	@echo "  make test             Run unit tests"
	@echo "  make test-integration Run integration tests (needs DB+Redis)"
	@echo "  make test-all         All tests + coverage"
	@echo "  make test-sdk         Run SDK tests"
	@echo "  make lint             Syntax check all Python"
	@echo "  make demo-register    Create demo user"
	@echo "  make demo-run         Run the BTC-LSTM demo"
	@echo ""
