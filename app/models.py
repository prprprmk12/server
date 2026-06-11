from datetime import datetime
from sqlalchemy import String, Float, Integer, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    manager = "manager"
    analyst = "analyst"
    viewer = "viewer"


class ClientStatus(str, enum.Enum):
    lead = "lead"
    pilot = "pilot"
    active = "active"
    churned = "churned"


class ModuleStatus(str, enum.Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    active = "active"
    paused = "paused"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.analyst)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="assignee")


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    industry: Mapped[str] = mapped_column(String(100))
    revenue_usd: Mapped[float] = mapped_column(Float, default=0)
    employees: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[ClientStatus] = mapped_column(Enum(ClientStatus), default=ClientStatus.lead)
    contact_name: Mapped[str] = mapped_column(String(255), nullable=True)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str] = mapped_column(String(50), nullable=True)
    acv_usd: Mapped[float] = mapped_column(Float, default=0)  # Annual Contract Value
    mrr_usd: Mapped[float] = mapped_column(Float, default=0)  # Monthly Recurring Revenue
    nps_score: Mapped[int] = mapped_column(Integer, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    contract_start: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    modules: Mapped[list["ClientModule"]] = relationship("ClientModule", back_populates="client")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="client")
    metrics: Mapped[list["ROIMetric"]] = relationship("ROIMetric", back_populates="client")


class AIModule(Base):
    __tablename__ = "ai_modules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    icon: Mapped[str] = mapped_column(String(50), default="cpu")
    price_monthly: Mapped[float] = mapped_column(Float)
    category: Mapped[str] = mapped_column(String(100))

    client_modules: Mapped[list["ClientModule"]] = relationship("ClientModule", back_populates="module")


class ClientModule(Base):
    __tablename__ = "client_modules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    client_id: Mapped[int] = mapped_column(Integer, ForeignKey("clients.id"))
    module_id: Mapped[int] = mapped_column(Integer, ForeignKey("ai_modules.id"))
    status: Mapped[ModuleStatus] = mapped_column(Enum(ModuleStatus), default=ModuleStatus.not_started)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    go_live_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    client: Mapped["Client"] = relationship("Client", back_populates="modules")
    module: Mapped["AIModule"] = relationship("AIModule", back_populates="client_modules")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="todo")  # todo, in_progress, done
    priority: Mapped[str] = mapped_column(String(20), default="medium")  # low, medium, high
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    client_id: Mapped[int] = mapped_column(Integer, ForeignKey("clients.id"), nullable=True)
    assignee_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    client: Mapped["Client"] = relationship("Client", back_populates="tasks")
    assignee: Mapped["User"] = relationship("User", back_populates="tasks")


class ROIMetric(Base):
    __tablename__ = "roi_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    client_id: Mapped[int] = mapped_column(Integer, ForeignKey("clients.id"))
    metric_name: Mapped[str] = mapped_column(String(255))
    metric_value: Mapped[float] = mapped_column(Float)
    metric_unit: Mapped[str] = mapped_column(String(50))  # %, USD, hours, etc.
    baseline_value: Mapped[float] = mapped_column(Float, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    client: Mapped["Client"] = relationship("Client", back_populates="metrics")


class RevenueRecord(Base):
    __tablename__ = "revenue_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    month: Mapped[str] = mapped_column(String(7))  # YYYY-MM
    mrr: Mapped[float] = mapped_column(Float, default=0)
    new_clients: Mapped[int] = mapped_column(Integer, default=0)
    churned_clients: Mapped[int] = mapped_column(Integer, default=0)
    services_revenue: Mapped[float] = mapped_column(Float, default=0)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
