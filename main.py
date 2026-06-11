from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import init_db
from app.routers import auth, clients, dashboard, tasks, modules, ml, metrics
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # Auto-seed при первом запуске (если нет пользователей)
    if os.getenv("AUTO_SEED", "true").lower() == "true":
        try:
            from app.seed import seed
            await seed()
        except Exception:
            pass  # Если уже засеяно — игнорируем
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="B2B AI Platform for Enterprise Process Optimization",
    lifespan=lifespan,
)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        FRONTEND_URL,
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(dashboard.router)
app.include_router(tasks.router)
app.include_router(modules.router)
app.include_router(ml.router)
app.include_router(metrics.router)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
