from fastapi import APIRouter, Depends
from app.auth import get_current_user
from app.models import User
from app.schemas import (
    ChurnPredictRequest, ChurnPredictResponse,
    ROIForecastRequest, ROIForecastResponse
)
from app.ml.churn import predict_churn
from app.ml.roi_forecast import forecast_roi

router = APIRouter(prefix="/api/ml", tags=["ml"])


@router.post("/churn-predict", response_model=ChurnPredictResponse)
async def churn_prediction(
    request: ChurnPredictRequest,
    _: User = Depends(get_current_user),
):
    return predict_churn(request)


@router.post("/roi-forecast", response_model=ROIForecastResponse)
async def roi_forecast(
    request: ROIForecastRequest,
    _: User = Depends(get_current_user),
):
    return forecast_roi(request)
