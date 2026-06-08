import pandas as pd
import numpy as np
import mlflow
import mlflow.xgboost
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from datetime import datetime
from src.data.carga_datos import descargar_rango
from src.preprocessing.preprocessing import feature_engineering
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse



# ── Constantes ────────────────────────────────────────────────────────────────
DATA_2026_PATH = "src/data/raw/datos_2026.csv"
FECHA_INICIO_2026 = "2026-01-01"
FECHA_FIN_2026 = datetime.now().strftime("%Y-%m-%d")


# ── Lifespan: se ejecuta al arrancar el servidor ───────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.path.exists(DATA_2026_PATH):
        print("Descargando datos 2026...")
        df = descargar_rango(FECHA_INICIO_2026, FECHA_FIN_2026, preprocesar=True)
        if df.empty:
            raise RuntimeError("No se pudieron descargar los datos de 2026.")
        df = feature_engineering(df, drop_fecha=False)
        df.to_csv(DATA_2026_PATH, index=False)
        print(f"Datos 2026 guardados en {DATA_2026_PATH} ({len(df)} filas)")
    else:
        print(f"Datos 2026 ya existentes, omitiendo descarga.")

    yield

    print("Servidor apagado.")


# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Predicción de Demanda Energética — Colombia",
    version="1.0.0",
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Utilidad: cargar último modelo de MLflow ───────────────────────────────────
def cargar_ultimo_modelo():
    client = mlflow.tracking.MlflowClient()
    experimentos = client.search_runs(
        experiment_ids=["0"],
        order_by=["start_time DESC"],
        max_results=1
    )
    if not experimentos:
        raise HTTPException(status_code=404, detail="No hay modelos entrenados en MLflow.")

    run = experimentos[0]
    print(f"Run ID: {run.info.run_id}")
    print(f"Métricas: {run.data.metrics}")

    run_id = run.info.run_id
    model_uri = f"runs:/{run_id}/model"
    model = mlflow.xgboost.load_model(model_uri)
    return model


# ── Utilidad: construir vector de features para una fecha ─────────────────────
def construir_features(fecha: datetime, df_2026: pd.DataFrame) -> pd.DataFrame:
    # Verificar que existen los lags necesarios
    fecha = pd.Timestamp(fecha)
    for lag in [1, 24, 168]:
        fecha_lag = fecha - pd.Timedelta(hours=lag)
        if fecha_lag not in df_2026.index:
            raise HTTPException(
                status_code=400,
                detail=f"No hay datos disponibles para calcular lag_{lag} (necesita {fecha_lag})"
            )

    lag_1   = df_2026.loc[fecha - pd.Timedelta(hours=1),   'Valor']
    lag_24  = df_2026.loc[fecha - pd.Timedelta(hours=24),  'Valor']
    lag_168 = df_2026.loc[fecha - pd.Timedelta(hours=168), 'Valor']

    # Tendencia: posición relativa al inicio de 2024
    inicio_entrenamiento = pd.Timestamp("2024-01-01")
    tendencia = int((fecha - inicio_entrenamiento).total_seconds() / 3600)

    features = {
        'hora_sin':       np.sin(2 * np.pi * fecha.hour / 24),
        'hora_cos':       np.cos(2 * np.pi * fecha.hour / 24),
        'dia_semana_sin': np.sin(2 * np.pi * fecha.dayofweek / 7),
        'dia_semana_cos': np.cos(2 * np.pi * fecha.dayofweek / 7),
        'mes_sin':        np.sin(2 * np.pi * fecha.month / 12),
        'mes_cos':        np.cos(2 * np.pi * fecha.month / 12),
        'tendencia':      tendencia,
        'lag_1':          lag_1,
        'lag_24':         lag_24,
        'lag_168':        lag_168,
    }
    X = pd.DataFrame([features])
    print(X)
    return pd.DataFrame([features])


# ── Endpoints ──────────────────────────────────────────────────────────────────
@app.post("/train")
def train():
    """Entrena el modelo con datos 2024-2025 y registra en MLflow."""
    from src.tests import run_pipeline
    try:
        run_pipeline("2024-01-01", "2025-12-31")
        return {"status": "ok", "mensaje": "Modelo entrenado y registrado en MLflow."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/predict")
def predict(fecha: str):
    """
    Predice la demanda energética para una fecha dada.
    Formato esperado: YYYY-MM-DDTHH:00:00  (resolución horaria)
    Ejemplo: 2026-03-15T14:00:00
    """
    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usa YYYY-MM-DDTHH:MM:SS")

    # Cargar datos 2026
    try:
        df_2026 = pd.read_csv(DATA_2026_PATH, parse_dates=['FechaHora'], index_col='FechaHora')
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Datos de 2026 no disponibles.")

    # Construir features y predecir
    X = construir_features(fecha_dt, df_2026)
    model = cargar_ultimo_modelo()
    prediccion = model.predict(X)[0]

    return {
        "fecha": fecha,
        "demanda_predicha_kwh": round(float(prediccion), 2)
    }


@app.get("/datos-hasta")
def datos_hasta(fecha: str):
    """
    Devuelve las 168 horas (7 días) anteriores a la fecha dada.
    Formato: YYYY-MM-DDTHH:MM:SS
    """
    try:
        df = pd.read_csv(DATA_2026_PATH, parse_dates=['FechaHora'])
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Datos de 2026 no disponibles.")

    try:
        fecha_dt = pd.Timestamp(fecha)
    except Exception:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido.")

    df = df[df['FechaHora'] < fecha_dt].tail(168)[['FechaHora', 'Valor']]
    df['FechaHora'] = df['FechaHora'].astype(str)

    return df.to_dict(orient='records')


@app.get("/")
def dashboard():
    return FileResponse("dashboard.html")