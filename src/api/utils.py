import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Rutas del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_PATH = BASE_DIR / "src" / "data" / "raw" / "preprocesamiento_demanda_colombia_filtrado_agg_hora.csv"

_history_df = None

def load_history() -> pd.DataFrame:
    """Carga y cachea los datos históricos de demanda."""
    global _history_df
    if _history_df is not None:
        return _history_df
        
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"No se encontró el archivo de historial en {DATA_PATH}")
        
    df = pd.read_csv(DATA_PATH)
    df['FechaHora'] = pd.to_datetime(df['FechaHora'])
    df.set_index('FechaHora', inplace=True)
    df.sort_index(inplace=True)
    _history_df = df
    return _history_df

def encode_cyclic_datetime(dt: datetime) -> Dict[str, float]:
    """Genera las codificaciones cíclicas para una fecha y hora dada."""
    # Hora (0-23)
    hora_sin = np.sin(2 * np.pi * dt.hour / 24)
    hora_cos = np.cos(2 * np.pi * dt.hour / 24)
    
    # Día de la semana (0-6)
    dia_semana_sin = np.sin(2 * np.pi * dt.weekday() / 7)
    dia_semana_cos = np.cos(2 * np.pi * dt.weekday() / 7)
    
    # Mes (1-12)
    mes_sin = np.sin(2 * np.pi * dt.month / 12)
    mes_cos = np.cos(2 * np.pi * dt.month / 12)
    
    return {
        "hora_sin": float(hora_sin),
        "hora_cos": float(hora_cos),
        "dia_semana_sin": float(dia_semana_sin),
        "dia_semana_cos": float(dia_semana_cos),
        "mes_sin": float(mes_sin),
        "mes_cos": float(mes_cos)
    }

def forecast_xgboost_autoregressive(model: Any, start_time: datetime, steps: int) -> List[Dict[str, Any]]:
    """Realiza una predicción autorregresiva de XGBoost durante 'steps' horas."""
    history = load_history()
    max_history_dt = history.index.max()
    min_history_dt = history.index.min()
    
    predictions = []
    
    # Cache local de predicciones de esta corrida para usar como lags
    run_predictions: Dict[datetime, float] = {}
    
    for step in range(steps):
        current_dt = start_time + timedelta(hours=step)
        
        # 1. Obtener características cíclicas
        cyclical = encode_cyclic_datetime(current_dt)
        
        # 2. Calcular tendencia
        if current_dt in history.index:
            tendencia = int(history.index.get_loc(current_dt))
        else:
            # Extrapolar tendencia basándonos en la distancia a la última fecha del historial
            seconds_diff = (current_dt - max_history_dt).total_seconds()
            hours_diff = int(seconds_diff / 3600)
            tendencia = len(history) + hours_diff - 1
            
        # 3. Obtener variables de lag (t-1, t-24, t-168)
        lags = {}
        for lag_hours in [1, 24, 168]:
            lag_dt = current_dt - timedelta(hours=lag_hours)
            
            # Buscar primero en las predicciones temporales hechas en esta corrida
            if lag_dt in run_predictions:
                lags[f"lag_{lag_hours}"] = run_predictions[lag_dt]
            # Buscar luego en el historial real de XM
            elif lag_dt in history.index:
                lags[f"lag_{lag_hours}"] = float(history.loc[lag_dt, 'Valor'])
            else:
                # Si está fuera del rango (antes del inicio del dataset), usar la media o el valor más cercano
                nearest_dt = history.index[0] if lag_dt < min_history_dt else max_history_dt
                lags[f"lag_{lag_hours}"] = float(history.loc[nearest_dt, 'Valor'])
                
        # 4. Formar vector de entrada
        # Orden esperado por el modelo:
        # ['hora_sin', 'hora_cos', 'dia_semana_sin', 'dia_semana_cos', 'mes_sin', 'mes_cos', 'tendencia', 'lag_1', 'lag_24', 'lag_168']
        features = [
            cyclical["hora_sin"],
            cyclical["hora_cos"],
            cyclical["dia_semana_sin"],
            cyclical["dia_semana_cos"],
            cyclical["mes_sin"],
            cyclical["mes_cos"],
            tendencia,
            lags["lag_1"],
            lags["lag_24"],
            lags["lag_168"]
        ]
        
        # 5. Predecir
        # XGBoost espera un array 2D
        pred_value = float(model.predict([features])[0])
        
        # Registrar predicción para los siguientes pasos autorregresivos
        run_predictions[current_dt] = pred_value
        
        # Verificar si hay un valor real en el historial para comparar en la gráfica
        actual_val = None
        if current_dt in history.index:
            actual_val = float(history.loc[current_dt, 'Valor'])
            
        predictions.append({
            "timestamp": current_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "predicted_value": pred_value,
            "actual_value": actual_val
        })
        
    return predictions
