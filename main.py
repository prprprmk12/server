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
        except Exception as e:
            # Логируем но не падаем — таблицы уже созданы
            import logging
            logging.getLogger("uvicorn").warning(f"Seed warning (ok if already seeded): {e}")
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="B2B AI Platform for Enterprise Process Optimization",
    lifespan=lifespan,
)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Собираем список разрешённых origins
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
if FRONTEND_URL and FRONTEND_URL not in ALLOWED_ORIGINS:
    ALLOWED_ORIGINS.append(FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",  # все vercel-домены через regex
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
