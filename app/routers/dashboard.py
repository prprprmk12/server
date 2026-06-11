from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import Client, ClientStatus, ROIMetric, RevenueRecord
from app.auth import get_current_user
from app.models import User
from app.schemas import DashboardStats

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    total = await db.execute(select(func.count(Client.id)))
    active = await db.execute(select(func.count(Client.id)).where(Client.status == "active"))
    pilot = await db.execute(select(func.count(Client.id)).where(Client.status == "pilot"))
    lead = await db.execute(select(func.count(Client.id)).where(Client.status == "lead"))
    mrr_sum = await db.execute(select(func.sum(Client.mrr_usd)).where(Client.status == "active"))
    nps_avg = await db.execute(select(func.avg(Client.nps_score)).where(Client.nps_score.isnot(None)))
    emp_sum = await db.execute(select(func.sum(Client.employees)))

    total_mrr = mrr_sum.scalar() or 0.0
    return DashboardStats(
        total_clients=total.scalar() or 0,
        active_clients=active.scalar() or 0,
        pilot_clients=pilot.scalar() or 0,
        lead_clients=lead.scalar() or 0,
        total_mrr=total_mrr,
        total_arr=total_mrr * 12,
        avg_nps=round(nps_avg.scalar() or 0, 1),
        total_employees_served=emp_sum.scalar() or 0,
    )


@router.get("/revenue")
async def get_revenue_data(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(RevenueRecord).order_by(RevenueRecord.month.asc()).limit(24)
    )
    records = result.scalars().all()
    return [
        {
            "month": r.month,
            "mrr": r.mrr,
            "arr": r.mrr * 12,
            "new_clients": r.new_clients,
            "churned_clients": r.churned_clients,
            "services_revenue": r.services_revenue,
        }
        for r in records
    ]


@router.get("/funnel")
async def get_funnel(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    statuses = ["lead", "pilot", "active", "churned"]
    result = {}
    for s in statuses:
        count = await db.execute(select(func.count(Client.id)).where(Client.status == s))
        result[s] = count.scalar() or 0
    return result


@router.get("/top-clients")
async def get_top_clients(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Client)
        .where(Client.status == "active")
        .order_by(Client.mrr_usd.desc())
        .limit(10)
    )
    clients = result.scalars().all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "industry": c.industry,
            "mrr_usd": c.mrr_usd,
            "acv_usd": c.acv_usd,
            "nps_score": c.nps_score,
            "status": c.status,
        }
        for c in clients
    ]


@router.get("/industry-breakdown")
async def get_industry_breakdown(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Client.industry, func.count(Client.id).label("count"), func.sum(Client.mrr_usd).label("mrr"))
        .group_by(Client.industry)
    )
    rows = result.all()
    return [{"industry": r.industry, "count": r.count, "mrr": r.mrr or 0} for r in rows]
