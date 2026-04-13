# SDK Guide

## Installation

```bash
pip install -e sdk/          # basic
pip install -e sdk/[cli]     # with CLI support
```

## Quick Start

```python
from exp_tracker import ExperimentTracker

tracker = ExperimentTracker(
    api_key="YOUR_API_KEY",
    base_url="http://localhost:8000",
)
```

## Context Manager (Recommended)

The `with` block auto-calls `finish()` on success or `fail()` on any exception:

```python
with tracker.run(
    name="btc_LSTM_ohlcv_20260101",   # must match ^[a-z][a-z0-9_]*_[A-Z][a-zA-Z0-9]*_[a-z0-9_]+_\d{8}$
    experiment="btc_experiment",
    params={"lr": 0.001, "hidden_dim": 128, "layers": 2},
    data_version="v1.0",
) as run:
    for epoch in range(1, 11):
        loss, acc = train_epoch(epoch)
        run.log({"train_loss": loss, "train_acc": acc}, step=epoch)
```

## Manual Lifecycle

```python
run = tracker.run("btc_LSTM_ohlcv_20260101", experiment="btc_exp", params={})
try:
    for epoch in range(10):
        run.log({"val_loss": compute_val_loss()}, step=epoch)
    run.finish()
except Exception as e:
    run.fail()
    raise
```

## Logging Metrics

```python
# Single step
run.log({"loss": 0.42, "acc": 0.88}, step=5)

# Auto-incrementing step (per key)
run.log({"loss": 0.5})   # step=1
run.log({"loss": 0.4})   # step=2
```

**Rules:**
- Metric keys: `^[a-z][a-z0-9_]*$` (e.g. `train_loss`, `val_acc_top5`)
- Values: no NaN or Inf
- Max 50 metrics per flush batch

## Buffering & Offline Sync

The SDK batches metrics (default: 20) and auto-flushes on:
- Reaching batch size
- 30-second timeout
- `run.finish()`

If the API is unreachable, metrics are saved to `~/.exp_tracker/pending/` and synced on the next connection:

```python
# Manual sync
count = tracker.sync_offline()
print(f"Synced {count} pending file(s)")
```

## Querying

```python
# List runs
runs = tracker.get_runs(experiment="btc_experiment", status="completed", limit=10)

# Compare
report = tracker.compare_runs(
    ids=["run-id-1", "run-id-2"],
    metrics=["train_loss", "val_loss"],
)
for result in report["results"]:
    print(result["run_name"], result["metrics_summary"])

# Warn on different data_versions
for w in report["warnings"]:
    print("⚠", w)

# Chart data
chart = tracker.get_chart_data(ids=["run-id-1"], metric="train_loss")
```

## Environment Auto-Capture

On `tracker.run(...)`, the SDK auto-captures:
- `python_version`
- `platform`
- `git_commit` (via `git rev-parse HEAD`)
- Library versions: `torch`, `tensorflow`, `numpy`, `pandas`, `sklearn`
- GPU info (if PyTorch + CUDA available)

Disable with `auto_capture_env=False` in the `Run` constructor.

## CLI Reference

```bash
# Create run
exp-cli run create \
  --name btc_LSTM_ohlcv_20260101 \
  --experiment btc_experiment \
  --params lr=0.001 hidden=128 \
  --api-key YOUR_KEY

# List runs
exp-cli run list --experiment btc_experiment --status completed

# Compare
exp-cli run compare \
  --ids "id1,id2" \
  --metrics "train_loss,val_loss"

# Sync offline
exp-cli sync

# Environment variables (avoid repeating flags)
export EXP_API_KEY=your-key
export EXP_BASE_URL=http://localhost:8000
```

## PyTorch Integration Example

```python
import torch
import torch.nn as nn
from exp_tracker import ExperimentTracker

tracker = ExperimentTracker(api_key="YOUR_KEY")

model = nn.LSTM(input_size=10, hidden_size=128, num_layers=2, batch_first=True)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

with tracker.run(
    name="btc_LSTM_ohlcv_20260101",
    experiment="btc_experiment",
    params={"lr": 0.001, "hidden": 128, "layers": 2, "optimizer": "adam"},
    data_version="v1.0",
) as run:
    for epoch in range(1, 51):
        # ... training loop ...
        train_loss = criterion(outputs, targets).item()
        val_loss = evaluate(model, val_loader)

        run.log({
            "train_loss": train_loss,
            "val_loss": val_loss,
            "learning_rate": optimizer.param_groups[0]["lr"],
        }, step=epoch)
```
