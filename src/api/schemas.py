from pydantic import BaseModel, Field
from typing import List, Optional

class XGBoostManualRequest(BaseModel):
    hora: int = Field(..., ge=0, le=23, description="Hora del día (0-23)")
    dia_semana: int = Field(..., ge=0, le=6, description="Día de la semana (0=Lunes, 6=Domingo)")
    mes: int = Field(..., ge=1, le=12, description="Mes del año (1-12)")
    tendencia: int = Field(..., description="Índice incremental de tendencia")
    lag_1: float = Field(..., description="Demanda de la hora anterior (t-1) en kWh")
    lag_24: float = Field(..., description="Demanda de la misma hora el día anterior (t-24) en kWh")
    lag_168: float = Field(..., description="Demanda de la misma hora la semana anterior (t-168) en kWh")

class XGBoostAutoRequest(BaseModel):
    start_time: str = Field(..., example="2025-12-01T00:00:00", description="Fecha y hora inicial en formato YYYY-MM-DDTHH:MM:SS")
    steps: int = Field(24, ge=1, le=168, description="Número de horas a predecir adelante (máximo 168 horas / 1 semana)")

class ProphetRequest(BaseModel):
    start_date: str = Field(..., example="2026-01-01", description="Fecha de inicio (YYYY-MM-DD)")
    end_date: str = Field(..., example="2026-01-07", description="Fecha de fin (YYYY-MM-DD)")

class PredictionPoint(BaseModel):
    timestamp: str
    predicted_value: float
    yhat_lower: Optional[float] = None
    yhat_upper: Optional[float] = None
    actual_value: Optional[float] = None

class PredictResponse(BaseModel):
    model: str
    predictions: List[PredictionPoint]
    status: str = "success"
