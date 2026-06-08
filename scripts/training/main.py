import json
import pickle
from pathlib import Path
import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

# Directorios del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "src" / "data" / "raw"
MODELS_DIR = BASE_DIR / "src" / "models"

# Asegurar que el directorio de modelos existe
MODELS_DIR.mkdir(parents=True, exist_ok=True)

def entrenar_xgboost():
    print("[INFO] Entrenando XGBoost...")
    csv_path = DATA_DIR / "preprocesamiento_final.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo {csv_path}")
        
    data = pd.read_csv(csv_path)
    
    # Crear variables temporales
    data['tendencia'] = np.arange(len(data))
    data['lag_1']   = data['Valor'].shift(1)
    data['lag_24']  = data['Valor'].shift(24)
    data['lag_168'] = data['Valor'].shift(168)
    
    # Eliminar filas con NaN generados por los shifts
    data = data.dropna()
    
    X = data.drop(columns='Valor')
    y = data['Valor']
    
    # Split temporal
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False, random_state=0
    )
    
    # Entrenar modelo
    model = XGBRegressor(n_estimators=500, learning_rate=0.05, random_state=0)
    model.fit(X_train, y_train)
    
    # Evaluar modelo
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    print(f"[OK] XGBoost Entrenado. Metricas en Test:")
    print(f"   MAE:  {mae:,.2f} kWh")
    print(f"   RMSE: {rmse:,.2f} kWh")
    print(f"   R2:   {r2:.4f}")
    
    # Guardar modelo
    model_path = MODELS_DIR / "xgb_model.json"
    model.save_model(str(model_path))
    print(f"[INFO] Modelo XGBoost guardado en {model_path}")
    
    # Obtener importancia de características
    importancias = {col: float(val) for col, val in zip(X.columns, model.feature_importances_)}
    
    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2)
    }, importancias

def entrenar_prophet():
    print("[INFO] Entrenando Prophet (esto puede tomar un momento)...")
    csv_path = DATA_DIR / "preprocesamiento_demanda_colombia_filtrado_agg_hora.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo {csv_path}")
        
    data = pd.read_csv(csv_path)
    
    # Preprocesar para Prophet
    data_prophet = (
        data.copy()
        .drop(columns=[x for x in data.columns if x != 'FechaHora' and x != 'Valor'])
        .rename(columns={'FechaHora': 'ds', 'Valor': 'y'})
    )
    
    # Entrenar modelo
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=True
    )
    model.fit(data_prophet)
    
    print("[OK] Prophet Entrenado.")
    
    # Guardar modelo
    model_path = MODELS_DIR / "prophet_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    print(f"[INFO] Modelo Prophet guardado en {model_path}")
    
    # Métricas basadas en la validación cruzada reportada en model_report.md
    return {
        "mae_3d": 988598.0,
        "rmse_3d": 1144970.0,
        "mape_3d": 0.127
    }

def main():
    xgb_metrics, xgb_importances = entrenar_xgboost()
    prophet_metrics = entrenar_prophet()
    
    # Guardar métricas en un JSON para la API
    metrics_data = {
        "xgboost": {
            "metrics": xgb_metrics,
            "feature_importance": xgb_importances
        },
        "prophet": {
            "metrics": prophet_metrics
        }
    }
    
    metrics_path = MODELS_DIR / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=4, ensure_ascii=False)
    print(f"[INFO] Metricas guardadas en {metrics_path}")
    print("[SUCCESS] Proceso de entrenamiento finalizado con exito.")

if __name__ == "__main__":
    main()
