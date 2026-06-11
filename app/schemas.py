from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# ─── Auth ────────────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# ─── User ────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str
    role: str = "analyst"


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Client ──────────────────────────────────────────────────────────────────

class ClientCreate(BaseModel):
    name: str
    industry: str
    revenue_usd: float = 0
    employees: int = 0
    status: str = "lead"
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    acv_usd: float = 0
    mrr_usd: float = 0
    notes: Optional[str] = None


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    revenue_usd: Optional[float] = None
    employees: Optional[int] = None
    status: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    acv_usd: Optional[float] = None
    mrr_usd: Optional[float] = None
    nps_score: Optional[int] = None
    notes: Optional[str] = None


class ClientOut(BaseModel):
    id: int
    name: str
    industry: str
    revenue_usd: float
    employees: int
    status: str
    contact_name: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    acv_usd: float
    mrr_usd: float
    nps_score: Optional[int]
    notes: Optional[str]
    created_at: datetime
    contract_start: Optional[datetime]

    class Config:
        from_attributes = True


# ─── AI Module ───────────────────────────────────────────────────────────────

class AIModuleOut(BaseModel):
    id: int
    slug: str
    name: str
    description: str
    icon: str
    price_monthly: float
    category: str

    class Config:
        from_attributes = True


class ClientModuleOut(BaseModel):
    id: int
    module: AIModuleOut
    status: str
    started_at: Optional[datetime]
    go_live_at: Optional[datetime]

    class Config:
        from_attributes = True


# ─── Task ────────────────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "todo"
    priority: str = "medium"
    due_date: Optional[datetime] = None
    client_id: Optional[int] = None
    assignee_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    due_date: Optional[datetime]
    client_id: Optional[int]
    assignee_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── ROI Metrics ─────────────────────────────────────────────────────────────

class ROIMetricCreate(BaseModel):
    client_id: int
    metric_name: str
    metric_value: float
    metric_unit: str
    baseline_value: Optional[float] = None


class ROIMetricOut(BaseModel):
    id: int
    client_id: int
    metric_name: str
    metric_value: float
    metric_unit: str
    baseline_value: Optional[float]
    recorded_at: datetime

    class Config:
        from_attributes = True


# ─── Dashboard ───────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_clients: int
    active_clients: int
    pilot_clients: int
    lead_clients: int
    total_mrr: float
    total_arr: float
    avg_nps: Optional[float]
    total_employees_served: int


class RevenueData(BaseModel):
    month: str
    mrr: float
    arr: float
    new_clients: int
    churned_clients: int


# ─── ML Predict ──────────────────────────────────────────────────────────────

class ChurnPredictRequest(BaseModel):
    client_id: int
    months_active: float
    nps_score: float
    mrr_usd: float
    num_modules: int
    last_login_days: float


class ChurnPredictResponse(BaseModel):
    client_id: int
    churn_probability: float
    risk_level: str
    recommendations: List[str]


class ROIForecastRequest(BaseModel):
    investment_usd: float
    industry: str
    modules: List[str]
    employees: int


class ROIForecastResponse(BaseModel):
    roi_percentage: float
    payback_months: float
    annual_savings_usd: float
    confidence: float
    breakdown: dict
