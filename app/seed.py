"""
Seed script — заполняет базу тестовыми данными для демонстрации.
Запуск: python -m app.seed
"""
import asyncio
from datetime import datetime, timedelta
from app.database import AsyncSessionLocal, init_db
from app.models import User, Client, AIModule, ClientModule, ROIMetric, RevenueRecord
from app.auth import get_password_hash


AI_MODULES = [
    {
        "slug": "process_miner",
        "name": "ProcessMiner",
        "description": "Автоматический анализ и картографирование бизнес-процессов с выявлением узких мест",
        "icon": "GitBranch",
        "price_monthly": 2500,
        "category": "Process Analytics",
    },
    {
        "slug": "doc_intelligence",
        "name": "DocIntelligence",
        "description": "Интеллектуальная обработка документов: контракты, счета, заявки (OCR + LLM)",
        "icon": "FileText",
        "price_monthly": 3000,
        "category": "NLP",
    },
    {
        "slug": "predict_ops",
        "name": "PredictOps",
        "description": "Предиктивная аналитика: прогнозирование спроса, поломок, оттока",
        "icon": "TrendingUp",
        "price_monthly": 3500,
        "category": "Predictive Analytics",
    },
    {
        "slug": "quality_vision",
        "name": "QualityVision",
        "description": "Компьютерное зрение для контроля качества на производственных линиях",
        "icon": "Eye",
        "price_monthly": 5000,
        "category": "Computer Vision",
    },
    {
        "slug": "assist_ai",
        "name": "AssistAI",
        "description": "Корпоративный AI-ассистент на базе RAG поверх внутренних данных компании",
        "icon": "MessageSquare",
        "price_monthly": 2000,
        "category": "Generative AI",
    },
    {
        "slug": "auto_flow",
        "name": "AutoFlow",
        "description": "Оркестрация AI-агентов для автоматизации рутинных бизнес-процессов",
        "icon": "Zap",
        "price_monthly": 4000,
        "category": "AI Agents",
    },
]

CLIENTS = [
    {"name": "МеталлПром", "industry": "manufacturing", "revenue_usd": 85000000, "employees": 1200,
     "status": "active", "contact_name": "Иван Петров", "contact_email": "petrov@metallprom.ru",
     "acv_usd": 145000, "mrr_usd": 12083, "nps_score": 62, "modules": [0, 2, 3]},
    {"name": "СпидЛог", "industry": "logistics", "revenue_usd": 42000000, "employees": 450,
     "status": "active", "contact_name": "Анна Смирнова", "contact_email": "smirnova@speedlog.ru",
     "acv_usd": 88000, "mrr_usd": 7333, "nps_score": 71, "modules": [2, 0]},
    {"name": "Регион Банк", "industry": "finance", "revenue_usd": 210000000, "employees": 2100,
     "status": "active", "contact_name": "Дмитрий Козлов", "contact_email": "kozlov@regionbank.ru",
     "acv_usd": 320000, "mrr_usd": 26667, "nps_score": 55, "modules": [1, 4]},
    {"name": "РитейлМакс", "industry": "retail", "revenue_usd": 67000000, "employees": 890,
     "status": "active", "contact_name": "Ольга Фёдорова", "contact_email": "fedorova@retailmax.ru",
     "acv_usd": 72000, "mrr_usd": 6000, "nps_score": 68, "modules": [4, 5]},
    {"name": "СтройГрупп", "industry": "construction", "revenue_usd": 31000000, "employees": 320,
     "status": "pilot", "contact_name": "Сергей Николаев", "contact_email": "nikolaev@stroygroup.ru",
     "acv_usd": 55000, "mrr_usd": 0, "nps_score": None, "modules": [0]},
    {"name": "ЭнергоТех", "industry": "energy", "revenue_usd": 155000000, "employees": 1800,
     "status": "pilot", "contact_name": "Михаил Волков", "contact_email": "volkov@energotech.ru",
     "acv_usd": 190000, "mrr_usd": 0, "nps_score": None, "modules": [2, 3]},
    {"name": "ФармаПлюс", "industry": "healthcare", "revenue_usd": 28000000, "employees": 280,
     "status": "lead", "contact_name": "Елена Соколова", "contact_email": "sokolova@farmaplus.ru",
     "acv_usd": 48000, "mrr_usd": 0, "nps_score": None, "modules": []},
    {"name": "ТелекомСервис", "industry": "telecom", "revenue_usd": 95000000, "employees": 1500,
     "status": "lead", "contact_name": "Алексей Морозов", "contact_email": "morozov@telecomserv.ru",
     "acv_usd": 210000, "mrr_usd": 0, "nps_score": None, "modules": []},
    {"name": "АгроПром", "industry": "manufacturing", "revenue_usd": 38000000, "employees": 560,
     "status": "active", "contact_name": "Татьяна Лебедева", "contact_email": "lebedeva@agroprom.ru",
     "acv_usd": 95000, "mrr_usd": 7917, "nps_score": 74, "modules": [0, 2]},
    {"name": "МедиаТех", "industry": "telecom", "revenue_usd": 22000000, "employees": 190,
     "status": "churned", "contact_name": "Роман Иванов", "contact_email": "ivanov@mediatech.ru",
     "acv_usd": 42000, "mrr_usd": 0, "nps_score": 22, "modules": [4]},
]

ROI_METRICS = [
    (0, "Снижение брака", 34, "%", 0),
    (0, "Экономия ФОТ производство", 580000, "USD/год", 0),
    (0, "Время простоя оборудования", -28, "%", 0),
    (1, "Скорость обработки заказов", 41, "%", 0),
    (1, "Операционные расходы", -22, "%", 0),
    (2, "Скорость обработки заявок", 300, "%", 0),
    (2, "ФОТ back-office", -28, "%", 0),
    (3, "Конверсия рекомендаций", 18, "%", 0),
    (3, "Средний чек", 12, "%", 0),
    (8, "Потери при хранении", -19, "%", 0),
    (8, "Точность прогноза урожая", 87, "%", 0),
]

REVENUE_HISTORY = [
    ("2024-07", 0, 0, 0, 15000),
    ("2024-08", 7333, 1, 0, 28000),
    ("2024-09", 14666, 1, 0, 45000),
    ("2024-10", 19250, 1, 0, 38000),
    ("2024-11", 26583, 1, 0, 52000),
    ("2024-12", 40000, 2, 0, 65000),
    ("2025-01", 52000, 1, 0, 48000),
    ("2025-02", 59917, 1, 0, 71000),
    ("2025-03", 67834, 1, 1, 88000),
    ("2025-04", 60000, 0, 0, 55000),
    ("2025-05", 60000, 0, 0, 62000),
    ("2025-06", 60000, 0, 0, 74000),
]


async def seed():
    print("🌱 Инициализация базы данных...")
    await init_db()

    async with AsyncSessionLocal() as db:
        # Admin user
        from sqlalchemy import select
        existing = await db.execute(select(User).where(User.email == "admin@optimai.io"))
        if not existing.scalar_one_or_none():
            admin = User(
                email="admin@optimai.io",
                full_name="Admin OptimAI",
                hashed_password=get_password_hash("admin123"),
                role="admin",
            )
            demo = User(
                email="demo@optimai.io",
                full_name="Demo User",
                hashed_password=get_password_hash("demo123"),
                role="analyst",
            )
            db.add_all([admin, demo])
            await db.commit()
            print("✅ Пользователи созданы: admin@optimai.io / admin123")

        # AI Modules
        existing_mods = await db.execute(select(AIModule))
        if not existing_mods.scalars().first():
            for m in AI_MODULES:
                db.add(AIModule(**m))
            await db.commit()
            print("✅ AI-модули созданы")

        # Clients
        existing_clients = await db.execute(select(Client))
        if not existing_clients.scalars().first():
            mod_result = await db.execute(select(AIModule))
            modules_list = mod_result.scalars().all()

            client_objects = []
            for i, c in enumerate(CLIENTS):
                module_indices = c.pop("modules")
                client = Client(**c)
                if c.get("status") == "active":
                    client.contract_start = datetime.utcnow() - timedelta(days=180 + i * 20)
                db.add(client)
                await db.flush()

                for mi in module_indices:
                    if mi < len(modules_list):
                        cm = ClientModule(
                            client_id=client.id,
                            module_id=modules_list[mi].id,
                            status="active" if c.get("status") == "active" else "in_progress",
                        )
                        db.add(cm)
                client_objects.append(client)

            await db.commit()
            print("✅ Клиенты и модули созданы")

            # ROI Metrics
            clients_q = await db.execute(select(Client))
            clients_db = clients_q.scalars().all()
            for idx, metric_name, value, unit, _ in ROI_METRICS:
                if idx < len(clients_db):
                    db.add(ROIMetric(
                        client_id=clients_db[idx].id,
                        metric_name=metric_name,
                        metric_value=value,
                        metric_unit=unit,
                        baseline_value=0,
                    ))
            await db.commit()
            print("✅ ROI-метрики созданы")

        # Revenue history
        existing_rev = await db.execute(select(RevenueRecord))
        if not existing_rev.scalars().first():
            for month, mrr, new_c, churn_c, svc in REVENUE_HISTORY:
                db.add(RevenueRecord(
                    month=month,
                    mrr=mrr,
                    new_clients=new_c,
                    churned_clients=churn_c,
                    services_revenue=svc,
                ))
            await db.commit()
            print("✅ История выручки создана")

    print("\n🚀 База данных готова к работе!")
    print("   Логин: admin@optimai.io | Пароль: admin123")
    print("   Логин: demo@optimai.io  | Пароль: demo123")


if __name__ == "__main__":
    asyncio.run(seed())
