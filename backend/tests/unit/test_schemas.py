"""Unit tests: Pydantic validation, state machine, schemas"""
import math
import pytest
from pydantic import ValidationError

from app.schemas.schemas import RunCreate, MetricPoint, MetricsBatch, RunFilters
from app.services.run_service import TRANSITIONS, _assert_transition


# ─── Run name validation ───────────────────────────────────────────────────────
class TestRunNameValidation:
    def test_valid_name(self):
        r = RunCreate(
            experiment_name="btc_exp",
            name="btc_LSTM_ohlcv_20240101",
            params={"lr": 0.001},
        )
        assert r.name == "btc_LSTM_ohlcv_20240101"

    def test_invalid_name_no_date(self):
        with pytest.raises(ValidationError, match="pattern"):
            RunCreate(experiment_name="e", name="btc_LSTM_ohlcv", params={})

    def test_invalid_name_uppercase_start(self):
        with pytest.raises(ValidationError, match="pattern"):
            RunCreate(experiment_name="e", name="BTC_LSTM_ohlcv_20240101", params={})

    def test_invalid_name_spaces(self):
        with pytest.raises(ValidationError, match="pattern"):
            RunCreate(experiment_name="e", name="btc lstm ohlcv 20240101", params={})

    def test_valid_name_complex(self):
        r = RunCreate(
            experiment_name="e",
            name="sol_Transformer_btcusd_20260101",
            params={},
        )
        assert r.name.startswith("sol_")


# ─── Metric validation ─────────────────────────────────────────────────────────
class TestMetricValidation:
    def test_valid_metric(self):
        m = MetricPoint(key="train_loss", value=0.42, step=1)
        assert m.key == "train_loss"

    def test_nan_rejected(self):
        with pytest.raises(ValidationError, match="NaN"):
            MetricPoint(key="loss", value=float("nan"))

    def test_inf_rejected(self):
        with pytest.raises(ValidationError, match="Inf"):
            MetricPoint(key="loss", value=math.inf)

    def test_invalid_metric_key_uppercase(self):
        with pytest.raises(ValidationError):
            MetricPoint(key="TrainLoss", value=0.1)

    def test_invalid_metric_key_start_digit(self):
        with pytest.raises(ValidationError):
            MetricPoint(key="1loss", value=0.1)

    def test_valid_metric_key_with_numbers(self):
        m = MetricPoint(key="loss1", value=0.5)
        assert m.key == "loss1"


# ─── Batch validation ──────────────────────────────────────────────────────────
class TestMetricsBatch:
    def test_exceeds_50(self):
        metrics = [MetricPoint(key="loss", value=i * 0.01, step=i) for i in range(51)]
        with pytest.raises(ValidationError, match="Max 50"):
            MetricsBatch(metrics=metrics)

    def test_empty_batch(self):
        with pytest.raises(ValidationError, match="least one"):
            MetricsBatch(metrics=[])

    def test_exactly_50_ok(self):
        metrics = [MetricPoint(key="loss", value=i * 0.01, step=i) for i in range(50)]
        b = MetricsBatch(metrics=metrics)
        assert len(b.metrics) == 50


# ─── State machine ─────────────────────────────────────────────────────────────
class TestStateMachine:
    def test_created_to_running(self):
        _assert_transition("created", "running")  # should not raise

    def test_running_to_completed(self):
        _assert_transition("running", "completed")

    def test_running_to_paused(self):
        _assert_transition("running", "paused")

    def test_paused_to_running(self):
        _assert_transition("paused", "running")

    def test_completed_to_running_blocked(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException, match="Invalid state transition"):
            _assert_transition("completed", "running")

    def test_failed_to_completed_blocked(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException, match="Invalid state transition"):
            _assert_transition("failed", "completed")

    def test_created_to_completed_blocked(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException):
            _assert_transition("created", "completed")


# ─── Run filters ───────────────────────────────────────────────────────────────
class TestRunFilters:
    def test_limit_capped_at_200(self):
        f = RunFilters(limit=9999)
        assert f.limit == 200

    def test_invalid_status(self):
        with pytest.raises(ValidationError):
            RunFilters(status="invalid_status")

    def test_valid_status(self):
        f = RunFilters(status="running")
        assert f.status == "running"
