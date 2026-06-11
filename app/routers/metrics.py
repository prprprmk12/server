from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import ROIMetric
from app.auth import get_current_user
from app.models import User
from app.schemas import ROIMetricCreate, ROIMetricOut

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/", response_model=List[ROIMetricOut])
async def list_metrics(
    client_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ROIMetric).where(ROIMetric.client_id == client_id).order_by(ROIMetric.recorded_at.desc())
    )
    return result.scalars().all()


@router.post("/", response_model=ROIMetricOut)
async def create_metric(
    data: ROIMetricCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    metric = ROIMetric(**data.model_dump())
    db.add(metric)
    await db.commit()
    await db.refresh(metric)
    return metric
