"""
Churn prediction module.
Uses a rule-based + simple logistic regression approach.
In production, replace with a trained scikit-learn model persisted via joblib.
"""
import numpy as np
from app.schemas import ChurnPredictRequest, ChurnPredictResponse


# Логистическая функция
def _sigmoid(x: float) -> float:
    return 1 / (1 + np.exp(-x))


def predict_churn(req: ChurnPredictRequest) -> ChurnPredictResponse:
    """
    Модель оценки риска оттока клиента на основе ключевых признаков.
    
    Признаки и их веса (на основе отраслевых бенчмарков B2B SaaS):
    - NPS ниже 30 → высокий риск
    - Мало модулей (< 2) → зависимость от одного продукта
    - MRR падает или низкий → финансовый риск
    - Давно не использовал → engagement риск
    - Мало месяцев активности → нет habit formation
    """
    
    # Нормализация входных данных
    nps_norm = (req.nps_score - 50) / 50          # -1..+1, 50 = нейтральный
    mrr_norm = min(req.mrr_usd / 10000, 1.0)       # 0..1, $10K = максимум
    modules_norm = min(req.num_modules / 5, 1.0)    # 0..1, 5 = max
    recency_risk = min(req.last_login_days / 90, 1.0)  # 0..1, 90 дней = опасно
    tenure_bonus = min(req.months_active / 24, 1.0)    # 0..1, 2 года = зрелый

    # Линейная комбинация (веса подобраны под B2B SaaS метрики)
    score = (
        -0.35 * nps_norm          # NPS снижает риск
        - 0.20 * mrr_norm         # Высокий MRR снижает риск  
        - 0.20 * modules_norm     # Больше модулей → ниже риск
        + 0.30 * recency_risk     # Неактивность повышает риск
        - 0.15 * tenure_bonus     # Долгий клиент → ниже риск
        + 0.10                    # Базовый bias (~10% базовый churn)
    )
    
    probability = round(float(_sigmoid(score)), 3)

    # Уровень риска
    if probability < 0.25:
        risk_level = "low"
        recommendations = [
            "Запланировать QBR для обсуждения расширения",
            "Предложить дополнительные модули (upsell)",
            "Попросить референс/кейс для маркетинга",
        ]
    elif probability < 0.55:
        risk_level = "medium"
        recommendations = [
            "Провести health check звонок в течение 2 недель",
            "Убедиться, что все KPI из контракта достигнуты",
            "Рассмотреть скидку при продлении контракта",
        ]
    else:
        risk_level = "high"
        recommendations = [
            "🚨 Немедленный звонок с Customer Success Manager",
            "Провести аудит использования платформы",
            "Предложить дополнительное обучение / onboarding",
            "Рассмотреть реструктуризацию контракта",
            "Эскалировать до уровня CEO если нет ответа 5+ дней",
        ]

    return ChurnPredictResponse(
        client_id=req.client_id,
        churn_probability=probability,
        risk_level=risk_level,
        recommendations=recommendations,
    )
