import logging
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.models import Run, Experiment, Metric, User
from app.schemas.schemas import (
    RunCreate, RunFilters, MetricsBatch, RunCompareResult,
    ComparisonReport, ChartData, ChartSeries, COLORS,
)
from app.core.cache import cache_get, cache_set, cache_delete_pattern
from app.core.config import settings

logger = logging.getLogger(__name__)

# ─── Valid state transitions ───────────────────────────────────────────────────
TRANSITIONS: dict[str, set[str]] = {
    "created": {"running", "failed"},
    "running": {"completed", "failed", "paused"},
    "paused":  {"running", "failed"},
    "completed": set(),
    "failed":  set(),
}


def _utcnow():
    return datetime.now(timezone.utc)


async def _get_or_create_experiment(db: AsyncSession, name: str, user: User) -> Experiment:
    result = await db.execute(select(Experiment).where(Experiment.name == name))
    exp = result.scalar_one_or_none()
    if not exp:
        exp = Experiment(name=name, user_id=user.id)
        db.add(exp)
        await db.flush()
    return exp


async def create_run(db: AsyncSession, payload: RunCreate, user: User) -> Run:
    exp = await _get_or_create_experiment(db, payload.experiment_name, user)

    # Enforce max runs per experiment
    count_result = await db.execute(
        select(func.count()).select_from(Run).where(Run.experiment_id == exp.id)
    )
    count = count_result.scalar_one()
    if count >= settings.max_runs_per_experiment:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=422,
            detail=f"Experiment '{payload.experiment_name}' has reached max {settings.max_runs_per_experiment} runs"
        )

    run = Run(
        experiment_id=exp.id,
        name=payload.name,
        params=payload.params,
        metadata_=payload.metadata,
        git_commit=payload.git_commit,
        data_version=payload.data_version,
        status="created",
        user_id=user.id,
    )
    db.add(run)
    await db.flush()
    await cache_delete_pattern(f"runs:list:{exp.id}*")
    logger.info(f"Created run {run.id} in experiment '{exp.name}'")
    return run


async def start_run(db: AsyncSession, run_id: UUID) -> Run:
    run = await _get_run_or_404(db, run_id)
    _assert_transition(run.status, "running")
    run.status = "running"
    run.started_at = _utcnow()
    await db.flush()
    await cache_delete_pattern(f"runs:detail:{run_id}")
    return run


async def finish_run(db: AsyncSession, run_id: UUID) -> Run:
    run = await _get_run_or_404(db, run_id)
    _assert_transition(run.status, "completed")
    run.status = "completed"
    run.completed_at = _utcnow()
    await db.flush()
    await cache_delete_pattern(f"runs:detail:{run_id}")
    await cache_delete_pattern(f"runs:list:{run.experiment_id}*")
    logger.info(f"Finished run {run_id}")
    return run


async def fail_run(db: AsyncSession, run_id: UUID) -> Run:
    run = await _get_run_or_404(db, run_id)
    _assert_transition(run.status, "failed")
    run.status = "failed"
    run.completed_at = _utcnow()
    await db.flush()
    await cache_delete_pattern(f"runs:detail:{run_id}")
    return run


async def log_metrics(db: AsyncSession, run_id: UUID, batch: MetricsBatch) -> dict:
    run = await _get_run_or_404(db, run_id)
    if run.status not in {"running", "created"}:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail=f"Cannot log metrics to a run with status '{run.status}'")

    # Auto-transition to running if still created
    if run.status == "created":
        run.status = "running"
        run.started_at = _utcnow()

    buffered = 0
    for m in batch.metrics:
        metric = Metric(
            run_id=run_id,
            key=m.key,
            value=m.value,
            step=m.step,
        )
        db.add(metric)
        buffered += 1

    await db.flush()
    await cache_delete_pattern(f"runs:detail:{run_id}")
    return {"ack": True, "buffered": buffered}


async def get_run(db: AsyncSession, run_id: UUID) -> Run:
    cached = await cache_get(f"runs:detail:{run_id}")
    if cached:
        return cached   # return raw dict for serialization

    result = await db.execute(
        select(Run)
        .options(selectinload(Run.metrics))
        .where(Run.id == run_id)
    )
    run = result.scalar_one_or_none()
    if not run:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return run


async def list_runs(db: AsyncSession, filters: RunFilters) -> list[Run]:
    q = select(Run)
    if filters.experiment_name:
        exp_result = await db.execute(
            select(Experiment.id).where(Experiment.name == filters.experiment_name)
        )
        exp_id = exp_result.scalar_one_or_none()
        if not exp_id:
            return []
        q = q.where(Run.experiment_id == exp_id)
    if filters.status:
        q = q.where(Run.status == filters.status)
    if filters.git_commit:
        q = q.where(Run.git_commit == filters.git_commit)

    order_col = getattr(Run, filters.sort_by, Run.created_at)
    if filters.sort_order == "asc":
        q = q.order_by(order_col.asc())
    else:
        q = q.order_by(order_col.desc())

    q = q.limit(filters.limit).offset(filters.offset)
    result = await db.execute(q)
    return result.scalars().all()


async def compare_runs(
    db: AsyncSession, run_ids: list[UUID], metric_keys: list[str]
) -> ComparisonReport:
    results = []
    warnings = []
    data_versions = set()

    for run_id in run_ids:
        result = await db.execute(
            select(Run).options(selectinload(Run.metrics)).where(Run.id == run_id)
        )
        run = result.scalar_one_or_none()
        if not run:
            warnings.append(f"Run {run_id} not found, skipping")
            continue

        if run.data_version:
            data_versions.add(run.data_version)

        metrics_summary: dict[str, dict] = {}
        for key in metric_keys:
            values = [m.value for m in run.metrics if m.key == key]
            if values:
                metrics_summary[key] = {
                    "min": min(values),
                    "max": max(values),
                    "last": values[-1],
                    "count": len(values),
                }
            else:
                metrics_summary[key] = {}

        results.append(RunCompareResult(
            run_id=run.id,
            run_name=run.name,
            params=run.params,
            data_version=run.data_version,
            metrics_summary=metrics_summary,
        ))

    if len(data_versions) > 1:
        warnings.append(
            f"WARNING: Runs use different data_versions: {data_versions}. "
            "Comparison may not be meaningful."
        )

    return ComparisonReport(
        run_ids=run_ids,
        metrics_compared=metric_keys,
        results=results,
        warnings=warnings,
    )


async def get_chart_data(
    db: AsyncSession, run_ids: list[UUID], metric_key: str
) -> ChartData:
    series_list = []
    for i, run_id in enumerate(run_ids):
        result = await db.execute(
            select(Run)
            .options(selectinload(Run.metrics))
            .where(Run.id == run_id)
        )
        run = result.scalar_one_or_none()
        if not run:
            continue
        points = sorted(
            [
                {"step": m.step or 0, "value": m.value, "timestamp": str(m.timestamp)}
                for m in run.metrics if m.key == metric_key
            ],
            key=lambda p: p["step"],
        )
        series_list.append(ChartSeries(
            id=str(run.id),
            name=run.name,
            color=COLORS[i % len(COLORS)],
            data=points,
        ))
    return ChartData(metric=metric_key, runs=series_list)


# ─── Helpers ───────────────────────────────────────────────────────────────────
async def _get_run_or_404(db: AsyncSession, run_id: UUID) -> Run:
    result = await db.execute(select(Run).where(Run.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return run


def _assert_transition(current: str, target: str):
    if target not in TRANSITIONS.get(current, set()):
        from fastapi import HTTPException
        raise HTTPException(
            status_code=422,
            detail=f"Invalid state transition: {current} → {target}. "
                   f"Allowed from '{current}': {TRANSITIONS.get(current, set())}",
        )
