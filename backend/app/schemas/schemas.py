import re
import math
from uuid import UUID
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, field_validator, model_validator, ConfigDict

# ─── Regex patterns ────────────────────────────────────────────────────────────
RUN_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*_[A-Z][a-zA-Z0-9]*_[a-z0-9_]+_\d{8}$")
METRIC_KEY_RE = re.compile(r"^[a-z][a-z0-9_]*$")


# ─── Base response wrapper ─────────────────────────────────────────────────────
class APIResponse(BaseModel):
    success: bool
    data: Any = None
    meta: dict = {}
    errors: list[str] = []


# ─── User schemas ──────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    username: str
    email: str
    api_key: str
    is_admin: bool
    created_at: datetime


# ─── Experiment schemas ────────────────────────────────────────────────────────
class ExperimentCreate(BaseModel):
    name: str
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Experiment name cannot be empty")
        return v.strip()


class ExperimentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    description: Optional[str]
    user_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime


# ─── Run schemas ───────────────────────────────────────────────────────────────
class RunCreate(BaseModel):
    experiment_name: str
    name: str
    params: dict[str, Any] = {}
    metadata: dict[str, Any] = {}
    git_commit: Optional[str] = None
    data_version: Optional[str] = None
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_run_name(cls, v: str) -> str:
        if not RUN_NAME_RE.match(v):
            raise ValueError(
                f"Run name '{v}' does not match required pattern: "
                "<project>_<ModelName>_<dataset>_YYYYMMDD "
                "(e.g. btc_LSTM_ohlcv_20240101)"
            )
        return v


class RunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    experiment_id: UUID
    name: str
    params: dict
    metadata_: dict
    git_commit: Optional[str]
    data_version: Optional[str]
    status: str
    user_id: Optional[UUID]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    updated_at: datetime


class RunSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    experiment_id: UUID
    status: str
    params: dict
    git_commit: Optional[str]
    data_version: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]


# ─── Metric schemas ────────────────────────────────────────────────────────────
class MetricPoint(BaseModel):
    key: str
    value: float
    step: Optional[int] = None

    @field_validator("key")
    @classmethod
    def validate_metric_key(cls, v: str) -> str:
        if not METRIC_KEY_RE.match(v):
            raise ValueError(
                f"Metric key '{v}' invalid. Must match ^[a-z][a-z0-9_]*$"
            )
        return v

    @field_validator("value")
    @classmethod
    def reject_nan_inf(cls, v: float) -> float:
        if math.isnan(v) or math.isinf(v):
            raise ValueError("Metric value cannot be NaN or Inf")
        return v


class MetricsBatch(BaseModel):
    metrics: list[MetricPoint]

    @field_validator("metrics")
    @classmethod
    def limit_batch_size(cls, v: list) -> list:
        if len(v) > 50:
            raise ValueError("Max 50 metrics per batch")
        if len(v) == 0:
            raise ValueError("At least one metric required")
        return v


class MetricOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    run_id: UUID
    key: str
    value: float
    step: Optional[int]
    timestamp: datetime


# ─── Comparison schemas ────────────────────────────────────────────────────────
class RunCompareResult(BaseModel):
    run_id: UUID
    run_name: str
    params: dict
    data_version: Optional[str]
    metrics_summary: dict[str, dict]   # key → {min, max, last, count}
    data_version_warning: bool = False


class ComparisonReport(BaseModel):
    run_ids: list[UUID]
    metrics_compared: list[str]
    results: list[RunCompareResult]
    warnings: list[str] = []


# ─── Chart data schema ─────────────────────────────────────────────────────────
COLORS = [
    "#3B82F6", "#EF4444", "#10B981", "#F59E0B",
    "#8B5CF6", "#EC4899", "#06B6D4", "#84CC16",
]


class ChartSeries(BaseModel):
    id: str
    name: str
    color: str
    data: list[dict]   # [{step, value, timestamp}]


class ChartData(BaseModel):
    metric: str
    runs: list[ChartSeries]


# ─── Filter params ─────────────────────────────────────────────────────────────
class RunFilters(BaseModel):
    experiment_name: Optional[str] = None
    status: Optional[str] = None
    tag: Optional[str] = None
    git_commit: Optional[str] = None
    limit: int = 50
    offset: int = 0
    sort_by: str = "created_at"
    sort_order: str = "desc"

    @field_validator("limit")
    @classmethod
    def cap_limit(cls, v: int) -> int:
        return min(v, 200)

    @field_validator("status")
    @classmethod
    def valid_status(cls, v: Optional[str]) -> Optional[str]:
        allowed = {"created", "running", "completed", "failed", "paused", None}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed - {None}}")
        return v
