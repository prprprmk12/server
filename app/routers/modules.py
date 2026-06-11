from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import AIModule
from app.auth import get_current_user
from app.models import User
from app.schemas import AIModuleOut

router = APIRouter(prefix="/api/modules", tags=["modules"])


@router.get("/", response_model=List[AIModuleOut])
async def list_modules(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(AIModule))
    return result.scalars().all()
