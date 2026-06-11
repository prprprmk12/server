from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import Client, ClientModule, AIModule
from app.auth import get_current_user
from app.models import User
from app.schemas import ClientCreate, ClientUpdate, ClientOut, ClientModuleOut

router = APIRouter(prefix="/api/clients", tags=["clients"])


@router.get("/", response_model=List[ClientOut])
async def list_clients(
    status: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(Client)
    if status:
        query = query.where(Client.status == status)
    if industry:
        query = query.where(Client.industry == industry)
    query = query.offset(skip).limit(limit).order_by(Client.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=ClientOut)
async def create_client(
    data: ClientCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    client = Client(**data.model_dump())
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client


@router.get("/{client_id}", response_model=ClientOut)
async def get_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.patch("/{client_id}", response_model=ClientOut)
async def update_client(
    client_id: int,
    data: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(client, field, value)
    await db.commit()
    await db.refresh(client)
    return client


@router.delete("/{client_id}")
async def delete_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    await db.delete(client)
    await db.commit()
    return {"ok": True}


@router.get("/{client_id}/modules", response_model=List[ClientModuleOut])
async def get_client_modules(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ClientModule).where(ClientModule.client_id == client_id)
    )
    modules = result.scalars().all()
    # Загружаем связанные модули
    out = []
    for cm in modules:
        mod_result = await db.execute(select(AIModule).where(AIModule.id == cm.module_id))
        cm.module = mod_result.scalar_one_or_none()
        out.append(cm)
    return out


@router.post("/{client_id}/modules/{module_id}")
async def add_module_to_client(
    client_id: int,
    module_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    # Проверяем существование
    client_result = await db.execute(select(Client).where(Client.id == client_id))
    if not client_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Client not found")
    module_result = await db.execute(select(AIModule).where(AIModule.id == module_id))
    if not module_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Module not found")

    cm = ClientModule(client_id=client_id, module_id=module_id)
    db.add(cm)
    await db.commit()
    return {"ok": True}
