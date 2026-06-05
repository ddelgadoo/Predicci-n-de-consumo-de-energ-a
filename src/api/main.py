import json
import pickle
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from xgboost import XGBRegressor

from src.api.schemas import (
    XGBoostManualRequest,
    XGBoostAutoRequest,
    ProphetRequest,
    PredictResponse,
    PredictionPoint
)
from src.api.utils import (
    load_history,
    encode_cyclic_datetime,
    forecast_xgboost_autoregressive
)

# Rutas de modelos
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = BASE_DIR / "src" / "models"
XGB_PATH = MODELS_DIR / "xgb_model.json"
PROPHET_PATH = MODELS_DIR / "prophet_model.pkl"
METRICS_PATH = MODELS_DIR / "metrics.json"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eventos de inicio y fin de la API (Carga de modelos en memoria)."""
    print("[INFO] Iniciando API y cargando modelos...")
    
    # Cargar XGBoost
    if not XGB_PATH.exists():
        print(f"[WARN] No se encontro el archivo del modelo XGBoost en {XGB_PATH}. Por favor ejecuta el script de entrenamiento.")
        app.state.xgb_model = None
    else:
        model = XGBRegressor()
        model.load_model(str(XGB_PATH))
        app.state.xgb_model = model
        print("[OK] Modelo XGBoost cargado correctamente.")
        
    # Cargar Prophet
    if not PROPHET_PATH.exists():
        print(f"[WARN] No se encontro el archivo del modelo Prophet en {PROPHET_PATH}. Por favor ejecuta el script de entrenamiento.")
        app.state.prophet_model = None
    else:
        with open(PROPHET_PATH, "rb") as f:
            app.state.prophet_model = pickle.load(f)
        print("[OK] Modelo Prophet cargado correctamente.")
        
    # Cargar métricas
    if METRICS_PATH.exists():
        with open(METRICS_PATH, "r", encoding="utf-8") as f:
            app.state.metrics = json.load(f)
        print("[OK] Metricas cargadas correctamente.")
    else:
        app.state.metrics = {}
        print("[WARN] No se encontraron métricas registradas.")
        
    # Cargar datos históricos en cache
    try:
        load_history()
        print("[OK] Historial de datos XM precargado.")
    except Exception as e:
        print(f"[WARN] No se pudo precargar el historial: {e}")
        
    yield
    print("[INFO] Apagando API...")

app = FastAPI(
    title="API de Predicción de Demanda Energética en Colombia",
    description="API REST para predecir el consumo de energía eléctrica usando modelos XGBoost (corto plazo) y Prophet (largo plazo).",
    version="1.0.0",
    lifespan=lifespan
)

# Habilitar CORS para desarrollo local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
def health_check():
    """Verifica la disponibilidad de la API y el estado de carga de los modelos."""
    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "models": {
            "xgboost_loaded": app.state.xgb_model is not None,
            "prophet_loaded": app.state.prophet_model is not None
        }
    }

@app.get("/api/v1/metrics")
def get_metrics():
    """Retorna las métricas históricas de rendimiento y la importancia de características de XGBoost."""
    if not app.state.metrics:
        raise HTTPException(status_code=404, detail="No hay métricas registradas en el servidor.")
    return app.state.metrics

@app.post("/api/v1/predict/xgboost/manual", response_model=PredictResponse)
def predict_xgboost_manual(req: XGBoostManualRequest):
    """Predice la demanda de una hora específica utilizando variables de lag ingresadas manualmente."""
    if app.state.xgb_model is None:
        raise HTTPException(status_code=503, detail="Modelo XGBoost no cargado en el servidor.")
        
    try:
        # Codificaciones cíclicas
        cyclical = encode_cyclic_datetime(datetime(2026, req.mes, req.dia_semana + 1, req.hora)) # Año dummy para dia_semana
        
        # En la request manual, se pasa directamente la hora_sin, etc., o se re-calcula.
        # Para alineación exacta con las columnas de entrenamiento:
        # ['hora_sin', 'hora_cos', 'dia_semana_sin', 'dia_semana_cos', 'mes_sin', 'mes_cos', 'tendencia', 'lag_1', 'lag_24', 'lag_168']
        features = [
            cyclical["hora_sin"],
            cyclical["hora_cos"],
            cyclical["dia_semana_sin"],
            cyclical["dia_semana_cos"],
            cyclical["mes_sin"],
            cyclical["mes_cos"],
            req.tendencia,
            req.lag_1,
            req.lag_24,
            req.lag_168
        ]
        
        prediction = float(app.state.xgb_model.predict([features])[0])
        
        timestamp_str = f"Hour {req.hora} (Trend {req.tendencia})"
        
        return PredictResponse(
            model="XGBoost (Manual Input)",
            predictions=[
                PredictionPoint(
                    timestamp=timestamp_str,
                    predicted_value=prediction
                )
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la prediccion: {str(e)}")

@app.post("/api/v1/predict/xgboost/auto", response_model=PredictResponse)
def predict_xgboost_auto(req: XGBoostAutoRequest):
    """Predice la demanda de forma autorregresiva a partir de una fecha/hora inicial."""
    if app.state.xgb_model is None:
        raise HTTPException(status_code=503, detail="Modelo XGBoost no cargado en el servidor.")
        
    try:
        start_dt = datetime.fromisoformat(req.start_time)
    except ValueError:
        raise HTTPException(status_code=400, detail="El formato de start_time debe ser ISO (YYYY-MM-DDTHH:MM:SS)")
        
    try:
        forecast_points = forecast_xgboost_autoregressive(
            model=app.state.xgb_model,
            start_time=start_dt,
            steps=req.steps
        )
        
        predictions = [PredictionPoint(**p) for p in forecast_points]
        
        return PredictResponse(
            model="XGBoost (Autoregressive)",
            predictions=predictions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la simulación XGBoost: {str(e)}")

@app.post("/api/v1/predict/prophet", response_model=PredictResponse)
def predict_prophet(req: ProphetRequest):
    """Predice la demanda para un rango de fechas a largo plazo."""
    if app.state.prophet_model is None:
        raise HTTPException(status_code=503, detail="Modelo Prophet no cargado en el servidor.")
        
    try:
        start_date = pd.to_datetime(req.start_date)
        end_date = pd.to_datetime(req.end_date)
        
        # Validar fechas
        if end_date < start_date:
            raise HTTPException(status_code=400, detail="La fecha de fin debe ser posterior a la de inicio.")
            
        # Generar rango horario completo
        future_dates = pd.date_range(start=start_date, end=end_date + pd.Timedelta(hours=23), freq='h')
        future_df = pd.DataFrame({"ds": future_dates})
        
        # Predicción
        forecast = app.state.prophet_model.predict(future_df)
        
        # Cargar historial para buscar valores reales
        history = load_history()
        
        predictions = []
        for _, row in forecast.iterrows():
            ds_dt = row['ds']
            pred_val = float(row['yhat'])
            lower_val = float(row['yhat_lower'])
            upper_val = float(row['yhat_upper'])
            
            actual_val = None
            if ds_dt in history.index:
                actual_val = float(history.loc[ds_dt, 'Valor'])
                
            predictions.append(
                PredictionPoint(
                    timestamp=ds_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                    predicted_value=pred_val,
                    yhat_lower=lower_val,
                    yhat_upper=upper_val,
                    actual_value=actual_val
                )
            )
            
        return PredictResponse(
            model="Prophet (Long-Term)",
            predictions=predictions
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la predicción de Prophet: {str(e)}")

# Montar los archivos estáticos para servir el tablero web
static_dir = BASE_DIR / "src" / "api" / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
