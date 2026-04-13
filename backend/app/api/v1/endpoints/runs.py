from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.auth import get_current_user, api_key_header
from app.models.models import User
from app.schemas.schemas import (
    APIResponse, RunCreate, RunOut, RunSummary,
    MetricsBatch, ComparisonReport, ChartData, RunFilters,
)
from app.services import run_service

router = APIRouter(prefix="/runs", tags=["runs"])


def _db_and_user(
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(api_key_header),
):
    return db, api_key


@router.post("", response_model=APIResponse)
async def create_run(payload: RunCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    run = await run_service.create_run(db, payload, user)
    return APIResponse(success=True, data={"run_id": str(run.id), "status": run.status})


@router.post("/{run_id}/metrics", response_model=APIResponse)
async def log_metrics(
    run_id: UUID,
    batch: MetricsBatch,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await run_service.log_metrics(db, run_id, batch)
    return APIResponse(success=True, data=result)


@router.get("", response_model=APIResponse)
async def list_runs(
    experiment_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    git_commit: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    filters = RunFilters(
        experiment_name=experiment_name,
        status=status,
        git_commit=git_commit,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    runs = await run_service.list_runs(db, filters)
    return APIResponse(
        success=True,
        data=[RunSummary.model_validate(r).model_dump() for r in runs],
        meta={"count": len(runs), "limit": limit, "offset": offset},
    )


@router.get("/compare", response_model=APIResponse)
async def compare_runs(
    ids: str = Query(..., description="Comma-separated run IDs"),
    metrics: str = Query(..., description="Comma-separated metric keys"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    run_ids = [UUID(i.strip()) for i in ids.split(",") if i.strip()]
    metric_keys = [m.strip() for m in metrics.split(",") if m.strip()]
    report = await run_service.compare_runs(db, run_ids, metric_keys)
    return APIResponse(success=True, data=report.model_dump())


@router.get("/chart", response_model=APIResponse)
async def chart_data(
    ids: str = Query(..., description="Comma-separated run IDs"),
    metric: str = Query(..., description="Metric key to chart"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    run_ids = [UUID(i.strip()) for i in ids.split(",") if i.strip()]
    chart = await run_service.get_chart_data(db, run_ids, metric)
    return APIResponse(success=True, data=chart.model_dump())


@router.get("/{run_id}", response_model=APIResponse)
async def get_run(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    run = await run_service.get_run(db, run_id)
    if isinstance(run, dict):
        return APIResponse(success=True, data=run)
    data = RunOut.model_validate(run).model_dump()
    data["metrics"] = [
        {"id": m.id, "key": m.key, "value": m.value, "step": m.step, "timestamp": str(m.timestamp)}
        for m in (run.metrics or [])
    ]
    return APIResponse(success=True, data=data)


@router.post("/{run_id}/start", response_model=APIResponse)
async def start_run(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    run = await run_service.start_run(db, run_id)
    return APIResponse(success=True, data={"run_id": str(run.id), "status": run.status})


@router.post("/{run_id}/finish", response_model=APIResponse)
async def finish_run(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    run = await run_service.finish_run(db, run_id)
    return APIResponse(success=True, data={"run_id": str(run.id), "status": run.status})


@router.post("/{run_id}/fail", response_model=APIResponse)
async def fail_run(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    run = await run_service.fail_run(db, run_id)
    return APIResponse(success=True, data={"run_id": str(run.id), "status": run.status})