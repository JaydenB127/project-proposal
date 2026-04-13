"""Unit tests for SDK: buffering, offline sync, env capture"""
import json
import math
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, call

from exp_tracker.client import Run, ExperimentTracker, BATCH_SIZE, PENDING_DIR


def _mock_tracker():
    t = MagicMock(spec=ExperimentTracker)
    t._post_metrics = MagicMock()
    t._finish_run = MagicMock()
    t._fail_run = MagicMock()
    return t


class TestRunBuffering:
    def test_auto_flush_at_batch_size(self):
        tracker = _mock_tracker()
        run = Run("run-123", "test_run", tracker, auto_capture_env=False)
        # Log BATCH_SIZE metrics — should auto-flush
        for i in range(BATCH_SIZE):
            run.log({"loss": 0.1 * i}, step=i)
        tracker._post_metrics.assert_called()

    def test_metrics_buffered_before_flush(self):
        tracker = _mock_tracker()
        run = Run("run-456", "test_run", tracker, auto_capture_env=False)
        run.log({"loss": 0.5}, step=1)
        run.log({"acc": 0.8}, step=1)
        # Only 2 metrics, should not flush yet
        tracker._post_metrics.assert_not_called()
        assert len(run._buffer) == 2

    def test_finish_flushes_remaining(self):
        tracker = _mock_tracker()
        run = Run("run-789", "test_run", tracker, auto_capture_env=False)
        run.log({"loss": 0.3}, step=1)
        run.finish()
        tracker._post_metrics.assert_called_once()
        tracker._finish_run.assert_called_once_with("run-789")

    def test_auto_step_increment(self):
        tracker = _mock_tracker()
        run = Run("run-abc", "test_run", tracker, auto_capture_env=False)
        run.log({"loss": 0.5})
        run.log({"loss": 0.4})
        assert run._step_counter["loss"] == 2

    def test_log_after_finish_raises(self):
        tracker = _mock_tracker()
        run = Run("run-xyz", "test_run", tracker, auto_capture_env=False)
        run.finish()
        with pytest.raises(Exception, match="finished"):
            run.log({"loss": 0.1})


class TestContextManager:
    def test_success_path_calls_finish(self):
        tracker = _mock_tracker()
        run = Run("run-ctx", "test_run", tracker, auto_capture_env=False)
        with run:
            run.log({"loss": 0.2}, step=1)
        tracker._finish_run.assert_called_once()
        tracker._fail_run.assert_not_called()

    def test_exception_path_calls_fail(self):
        tracker = _mock_tracker()
        run = Run("run-fail", "test_run", tracker, auto_capture_env=False)
        with pytest.raises(ValueError):
            with run:
                raise ValueError("Training exploded")
        tracker._fail_run.assert_called_once()
        tracker._finish_run.assert_not_called()


class TestOfflineSync:
    def test_saves_offline_on_network_error(self, tmp_path, monkeypatch):
        monkeypatch.setattr("exp_tracker.client.PENDING_DIR", tmp_path)
        tracker = _mock_tracker()
        tracker._post_metrics.side_effect = ConnectionError("Network down")
        run = Run("run-offline", "test_run", tracker, auto_capture_env=False)
        run._save_offline([{"key": "loss", "value": 0.5, "step": 1}])
        files = list(tmp_path.glob("*.json"))
        assert len(files) == 1
        data = json.loads(files[0].read_text())
        assert data["run_id"] == "run-offline"
        assert data["metrics"][0]["key"] == "loss"

    def test_sync_offline_uploads_and_deletes(self, tmp_path, monkeypatch):
        monkeypatch.setattr("exp_tracker.client.PENDING_DIR", tmp_path)
        # Write a fake pending file
        pending = tmp_path / "run-abc_12345678.json"
        pending.write_text(json.dumps({
            "run_id": "run-abc",
            "metrics": [{"key": "loss", "value": 0.3, "step": 1}]
        }))
        tracker = MagicMock()
        tracker._post_metrics = MagicMock()
        t = ExperimentTracker.__new__(ExperimentTracker)
        t.api_key = "test"
        t.base_url = "http://localhost"
        t._session = MagicMock()
        t._headers = {}
        # Patch to use tmp_path
        with patch("exp_tracker.client.PENDING_DIR", tmp_path):
            from exp_tracker.client import ExperimentTracker as ET
            real = ET.__new__(ET)
            real.api_key = "test"
            real.base_url = "http://localhost"
            real._session = MagicMock()
            real._headers = {}
            real._post_metrics = MagicMock()
            count = real.sync_offline()
        assert count == 1
        assert not pending.exists()


class TestMetricValidation:
    def test_invalid_key_raises(self):
        tracker = _mock_tracker()
        run = Run("r", "n", tracker, auto_capture_env=False)
        with pytest.raises(ValueError, match="Invalid metric key"):
            run.log({"TrainLoss": 0.5})

    def test_valid_underscore_key(self):
        tracker = _mock_tracker()
        run = Run("r", "n", tracker, auto_capture_env=False)
        run.log({"train_loss_v2": 0.5}, step=1)
        assert len(run._buffer) == 1
