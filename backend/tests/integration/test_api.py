"""Integration tests: full create → log → finish → query → compare flow.

Run with: pytest tests/integration/ -v
Requires: running Postgres + Redis (use docker compose up -d db redis)
"""
import pytest
import pytest_asyncio
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.db.database import Base, get_db
from app.models.models import User
import hashlib

# ── Test DB (in-process override) ─────────────────────────────────────────────
TEST_DB_URL = "postgresql+asyncpg://expuser:exppass@localhost:5432/exptracker_test"

test_engine = create_async_engine(TEST_DB_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def api_key():
    """Create a test user and return their API key."""
    async with TestSessionLocal() as session:
        key = str(uuid.uuid4())
        user = User(
            username=f"testuser_{uuid.uuid4().hex[:6]}",
            email=f"test_{uuid.uuid4().hex[:6]}@test.com",
            password_hash=hashlib.sha256(b"password").hexdigest(),
            api_key=key,
        )
        session.add(user)
        await session.commit()
        return key


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


# ── Tests ──────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_create_run(client, api_key):
    r = await client.post(
        "/api/v1/runs",
        json={
            "experiment_name": "btc_experiment",
            "name": "btc_LSTM_ohlcv_20260101",
            "params": {"lr": 0.001, "epochs": 10},
            "git_commit": "abc1234",
            "data_version": "v1.0",
        },
        headers={"X-API-Key": api_key},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["success"] is True
    assert "run_id" in data["data"]
    assert data["data"]["status"] == "created"
    return data["data"]["run_id"]


@pytest.mark.asyncio
async def test_full_tracking_flow(client, api_key):
    """End-to-end: create → log metrics → finish → query"""
    # 1. Create run
    r = await client.post(
        "/api/v1/runs",
        json={
            "experiment_name": "integration_test",
            "name": "itg_LSTM_ohlcv_20260101",
            "params": {"lr": 0.001, "hidden": 128},
            "data_version": "v2.0",
        },
        headers={"X-API-Key": api_key},
    )
    assert r.status_code == 200
    run_id = r.json()["data"]["run_id"]

    # 2. Log 10 epochs of metrics
    for epoch in range(1, 11):
        loss = 1.0 - (epoch * 0.08)
        acc = 0.5 + (epoch * 0.04)
        r = await client.post(
            f"/api/v1/runs/{run_id}/metrics",
            json={
                "metrics": [
                    {"key": "train_loss", "value": loss, "step": epoch},
                    {"key": "train_acc", "value": acc, "step": epoch},
                ]
            },
            headers={"X-API-Key": api_key},
        )
        assert r.status_code == 200, f"Epoch {epoch}: {r.text}"
        assert r.json()["data"]["buffered"] == 2

    # 3. Finish run
    r = await client.post(
        f"/api/v1/runs/{run_id}/finish",
        headers={"X-API-Key": api_key},
    )
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "completed"

    # 4. Query run detail
    r = await client.get(
        f"/api/v1/runs/{run_id}",
        headers={"X-API-Key": api_key},
    )
    assert r.status_code == 200
    detail = r.json()["data"]
    assert detail["status"] == "completed"

    # 5. List runs
    r = await client.get(
        "/api/v1/runs?experiment_name=integration_test",
        headers={"X-API-Key": api_key},
    )
    assert r.status_code == 200
    assert r.json()["meta"]["count"] >= 1


@pytest.mark.asyncio
async def test_compare_runs(client, api_key):
    """Create 2 runs with different LR → compare → check data_version warning"""
    run_ids = []
    for i, lr in enumerate([0.001, 0.01]):
        r = await client.post(
            "/api/v1/runs",
            json={
                "experiment_name": "compare_exp",
                "name": f"cmp_GRU_btc_2026010{i+1}",
                "params": {"lr": lr},
                "data_version": f"v{i+1}.0",  # different versions → warning
            },
            headers={"X-API-Key": api_key},
        )
        run_id = r.json()["data"]["run_id"]
        run_ids.append(run_id)

        # Log metrics
        await client.post(
            f"/api/v1/runs/{run_id}/metrics",
            json={"metrics": [
                {"key": "val_loss", "value": 0.5 - (i * 0.1), "step": 1},
                {"key": "val_acc", "value": 0.7 + (i * 0.05), "step": 1},
            ]},
            headers={"X-API-Key": api_key},
        )
        await client.post(f"/api/v1/runs/{run_id}/finish", headers={"X-API-Key": api_key})

    ids_param = ",".join(run_ids)
    r = await client.get(
        f"/api/v1/runs/compare?ids={ids_param}&metrics=val_loss,val_acc",
        headers={"X-API-Key": api_key},
    )
    assert r.status_code == 200
    report = r.json()["data"]
    assert len(report["results"]) == 2
    # Should warn about different data_versions
    assert any("data_version" in w for w in report["warnings"])


@pytest.mark.asyncio
async def test_invalid_run_name_rejected(client, api_key):
    r = await client.post(
        "/api/v1/runs",
        json={"experiment_name": "e", "name": "BadName", "params": {}},
        headers={"X-API-Key": api_key},
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_nan_metric_rejected(client, api_key):
    # First create a valid run
    r = await client.post(
        "/api/v1/runs",
        json={"experiment_name": "e", "name": "nan_LSTM_test_20260101", "params": {}},
        headers={"X-API-Key": api_key},
    )
    run_id = r.json()["data"]["run_id"]

    r = await client.post(
        f"/api/v1/runs/{run_id}/metrics",
        json={"metrics": [{"key": "loss", "value": float("nan"), "step": 1}]},
        headers={"X-API-Key": api_key},
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_state_machine_blocks_invalid_transition(client, api_key):
    r = await client.post(
        "/api/v1/runs",
        json={"experiment_name": "e", "name": "sm_LSTM_test_20260101", "params": {}},
        headers={"X-API-Key": api_key},
    )
    run_id = r.json()["data"]["run_id"]

    # Finish without ever starting → created → completed is invalid
    r = await client.post(f"/api/v1/runs/{run_id}/finish", headers={"X-API-Key": api_key})
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_no_api_key_rejected(client):
    r = await client.get("/api/v1/runs")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_chart_data(client, api_key):
    r = await client.post(
        "/api/v1/runs",
        json={"experiment_name": "chart_exp", "name": "chrt_CNN_mnist_20260101", "params": {}},
        headers={"X-API-Key": api_key},
    )
    run_id = r.json()["data"]["run_id"]

    await client.post(
        f"/api/v1/runs/{run_id}/metrics",
        json={"metrics": [
            {"key": "loss", "value": 0.8, "step": 1},
            {"key": "loss", "value": 0.5, "step": 2},
            {"key": "loss", "value": 0.3, "step": 3},
        ]},
        headers={"X-API-Key": api_key},
    )

    r = await client.get(
        f"/api/v1/runs/chart?ids={run_id}&metric=loss",
        headers={"X-API-Key": api_key},
    )
    assert r.status_code == 200
    chart = r.json()["data"]
    assert chart["metric"] == "loss"
    assert len(chart["runs"][0]["data"]) == 3
