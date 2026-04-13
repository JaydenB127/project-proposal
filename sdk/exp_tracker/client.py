"""
exp-tracker Python SDK
Usage:
    from exp_tracker import ExperimentTracker
    tracker = ExperimentTracker(api_key="...", base_url="http://localhost:8000")
    with tracker.run("btc_LSTM_ohlcv_20260101", experiment="btc_experiment", params={"lr": 0.001}) as run:
        for epoch in range(10):
            run.log({"train_loss": 0.5, "train_acc": 0.8}, step=epoch)
"""
from __future__ import annotations

import json
import logging
import os
import platform
import re
import subprocess
import sys
import time
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Generator, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger("exp_tracker")

METRIC_KEY_RE = re.compile(r"^[a-z][a-z0-9_]*$")
PENDING_DIR = Path.home() / ".exp_tracker" / "pending"
STATE_DIR = Path.home() / ".exp_tracker" / "state"
BATCH_SIZE = 20
FLUSH_TIMEOUT = 30  # seconds


class ExperimentTrackerError(Exception):
    pass


def _make_session(retries: int = 3) -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def _capture_env() -> dict:
    env = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "hostname": platform.node(),
    }
    # Git commit
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
        env["git_commit"] = commit
    except Exception:
        env["git_commit"] = None

    # Library versions
    for lib in ["torch", "tensorflow", "numpy", "pandas", "sklearn"]:
        try:
            mod = __import__(lib)
            env[f"{lib}_version"] = getattr(mod, "__version__", "unknown")
        except ImportError:
            pass

    # GPU info
    try:
        import torch
        if torch.cuda.is_available():
            env["gpu_name"] = torch.cuda.get_device_name(0)
            env["gpu_count"] = torch.cuda.device_count()
    except Exception:
        pass

    return env


class Run:
    """Represents an active experiment run. Use as context manager for auto-finish."""

    def __init__(
        self,
        run_id: str,
        name: str,
        tracker: "ExperimentTracker",
        auto_capture_env: bool = True,
    ):
        self.run_id = run_id
        self.name = name
        self._tracker = tracker
        self._buffer: list[dict] = []
        self._last_flush = time.time()
        self._step_counter: dict[str, int] = {}
        self._finished = False
        self._env = _capture_env() if auto_capture_env else {}

    def log(self, metrics: dict[str, float], step: Optional[int] = None):
        """Log a dictionary of metrics at an optional step."""
        if self._finished:
            raise ExperimentTrackerError(f"Run {self.run_id} is already finished")

        for key, value in metrics.items():
            if not METRIC_KEY_RE.match(key):
                raise ValueError(f"Invalid metric key '{key}'. Must match ^[a-z][a-z0-9_]*$")

            # Auto-increment step per key if not provided
            if step is None:
                self._step_counter[key] = self._step_counter.get(key, 0) + 1
                s = self._step_counter[key]
            else:
                s = step

            self._buffer.append({"key": key, "value": float(value), "step": s})

        if len(self._buffer) >= BATCH_SIZE or (time.time() - self._last_flush) > FLUSH_TIMEOUT:
            self._flush()

    def _flush(self, force: bool = False):
        if not self._buffer:
            return
        batch = self._buffer[:50]
        self._buffer = self._buffer[50:]
        try:
            self._tracker._post_metrics(self.run_id, batch)
            self._last_flush = time.time()
        except Exception as e:
            logger.warning(f"Flush failed, buffering offline: {e}")
            self._save_offline(batch)

    def _save_offline(self, batch: list[dict]):
        PENDING_DIR.mkdir(parents=True, exist_ok=True)
        fname = PENDING_DIR / f"{self.run_id}_{uuid.uuid4().hex[:8]}.json"
        with open(fname, "w") as f:
            json.dump({"run_id": self.run_id, "metrics": batch}, f)
        logger.info(f"Saved {len(batch)} metrics offline → {fname}")

    def finish(self):
        if self._finished:
            return
        self._flush(force=True)
        while self._buffer:
            self._flush(force=True)
        self._tracker._finish_run(self.run_id)
        self._finished = True
        logger.info(f"Run '{self.name}' ({self.run_id}) finished ✓")

    def fail(self):
        if self._finished:
            return
        self._flush(force=True)
        self._tracker._fail_run(self.run_id)
        self._finished = True

    def __enter__(self) -> "Run":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logger.error(f"Run failed due to: {exc_val}")
            try:
                self.fail()
            except Exception:
                pass
        else:
            self.finish()
        return False  # don't suppress exceptions


class ExperimentTracker:
    """Main SDK client for the Experiment Tracker API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000",
        auto_sync_offline: bool = True,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._session = _make_session()
        self._headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

        if auto_sync_offline:
            try:
                self.sync_offline()
            except Exception:
                pass

    # ── Public API ─────────────────────────────────────────────────────────────
    def run(
        self,
        name: str,
        experiment: str,
        params: dict[str, Any] = None,
        metadata: dict[str, Any] = None,
        data_version: Optional[str] = None,
        auto_capture_env: bool = True,
    ) -> Run:
        """Create and return a Run (use as context manager)."""
        env = _capture_env() if auto_capture_env else {}
        payload = {
            "experiment_name": experiment,
            "name": name,
            "params": params or {},
            "metadata": {**(metadata or {}), **env},
            "git_commit": env.get("git_commit"),
            "data_version": data_version,
        }
        resp = self._post("/api/v1/runs", payload)
        run_id = resp["data"]["run_id"]
        r = Run(run_id=run_id, name=name, tracker=self, auto_capture_env=False)
        r._env = env
        logger.info(f"Created run '{name}' ({run_id})")
        return r

    def get_runs(
        self,
        experiment: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict]:
        params = {"limit": limit}
        if experiment:
            params["experiment_name"] = experiment
        if status:
            params["status"] = status
        return self._get("/api/v1/runs", params=params)["data"]

    def compare_runs(self, ids: list[str], metrics: list[str]) -> dict:
        return self._get(
            "/api/v1/runs/compare",
            params={"ids": ",".join(ids), "metrics": ",".join(metrics)},
        )["data"]

    def get_chart_data(self, ids: list[str], metric: str) -> dict:
        return self._get(
            "/api/v1/runs/chart",
            params={"ids": ",".join(ids), "metric": metric},
        )["data"]

    def sync_offline(self) -> int:
        """Sync any pending offline metrics. Returns number of files synced."""
        if not PENDING_DIR.exists():
            return 0
        files = list(PENDING_DIR.glob("*.json"))
        synced = 0
        for f in files:
            try:
                data = json.loads(f.read_text())
                self._post_metrics(data["run_id"], data["metrics"])
                f.unlink()
                synced += 1
            except Exception as e:
                logger.warning(f"Could not sync {f.name}: {e}")
        if synced:
            logger.info(f"Synced {synced} offline metric file(s)")
        return synced

    # ── Internal helpers ───────────────────────────────────────────────────────
    def _post_metrics(self, run_id: str, metrics: list[dict]):
        self._post(f"/api/v1/runs/{run_id}/metrics", {"metrics": metrics})

    def _finish_run(self, run_id: str):
        self._post(f"/api/v1/runs/{run_id}/finish", {})

    def _fail_run(self, run_id: str):
        self._post(f"/api/v1/runs/{run_id}/fail", {})

    def _post(self, path: str, payload: dict) -> dict:
        url = f"{self.base_url}{path}"
        resp = self._session.post(url, json=payload, headers=self._headers, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def _get(self, path: str, params: dict = None) -> dict:
        url = f"{self.base_url}{path}"
        resp = self._session.get(url, params=params, headers=self._headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
