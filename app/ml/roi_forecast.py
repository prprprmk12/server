"""
ROI Forecast module.
Estimates projected ROI based on investment, industry, selected modules, and company size.
Based on aggregated industry benchmarks from McKinsey, IDC, and Gartner AI studies.
"""
from app.schemas import ROIForecastRequest, ROIForecastResponse


# Отраслевые мультипликаторы эффективности AI (на основе публичных кейс-стади)
INDUSTRY_MULTIPLIERS = {
    "manufacturing":    1.35,
    "logistics":        1.40,
    "finance":          1.25,
    "retail":           1.20,
    "telecom":          1.15,
    "healthcare":       1.10,
    "construction":     1.30,
    "energy":           1.25,
    "other":            1.15,
}

# Вклад каждого модуля в экономию (USD на сотрудника в год)
MODULE_SAVINGS_PER_EMPLOYEE = {
    "process_miner":        180,   # Оптимизация процессов
    "doc_intelligence":     320,   # Автоматизация документов (высокий ФОТ-эффект)
    "predict_ops":          250,   # Снижение операционных потерь
    "quality_vision":       400,   # Снижение брака (производство)
    "assist_ai":            210,   # Снижение нагрузки на поддержку
    "auto_flow":            290,   # RPA нового поколения
}

# Базовое время окупаемости по отраслям (месяцев)
INDUSTRY_PAYBACK_BASE = {
    "manufacturing":    10,
    "logistics":         8,
    "finance":          11,
    "retail":            9,
    "telecom":          12,
    "healthcare":       14,
    "construction":     12,
    "energy":           13,
    "other":            12,
}


def forecast_roi(req: ROIForecastRequest) -> ROIForecastResponse:
    industry_key = req.industry.lower().replace(" ", "_")
    multiplier = INDUSTRY_MULTIPLIERS.get(industry_key, 1.15)
    payback_base = INDUSTRY_PAYBACK_BASE.get(industry_key, 12)

    # Считаем экономию по выбранным модулям
    breakdown = {}
    total_savings_per_employee = 0.0
    for module_slug in req.modules:
        per_emp = MODULE_SAVINGS_PER_EMPLOYEE.get(module_slug, 150)
        total_savings_per_employee += per_emp
        breakdown[module_slug] = round(per_emp * req.employees * multiplier)

    # Синергетический бонус при нескольких модулях
    if len(req.modules) >= 3:
        synergy_factor = 1.15
    elif len(req.modules) == 2:
        synergy_factor = 1.08
    else:
        synergy_factor = 1.0

    annual_savings = round(total_savings_per_employee * req.employees * multiplier * synergy_factor)
    
    if req.investment_usd > 0:
        roi_percentage = round((annual_savings - req.investment_usd) / req.investment_usd * 100, 1)
        payback_months = round(req.investment_usd / (annual_savings / 12), 1)
    else:
        roi_percentage = 0.0
        payback_months = 0.0

    # Уверенность в прогнозе (выше при типичных параметрах)
    confidence = 0.75
    if 100 <= req.employees <= 2000:
        confidence += 0.10
    if len(req.modules) >= 2:
        confidence += 0.05
    if industry_key in INDUSTRY_MULTIPLIERS:
        confidence += 0.05
    confidence = round(min(confidence, 0.95), 2)

    return ROIForecastResponse(
        roi_percentage=roi_percentage,
        payback_months=payback_months,
        annual_savings_usd=annual_savings,
        confidence=confidence,
        breakdown=breakdown,
    )
