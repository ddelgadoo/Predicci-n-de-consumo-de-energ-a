import pandas as pd

from src.preprocessing.preprocessing import feature_engineering,preprocessing
from src.data.carga_datos import descargar_rango
from src.training.training import entrenar_xgboost
from src.visualization.visualizacion import plot_prediccion, plot_importancias


def run_pipeline(fecha_inicio: str, fecha_fin: str) -> None:
    """
    Ejecuta el pipeline completo de predicción de demanda energética:
        1. Descarga y preprocesa datos desde la API de XM
        2. Feature engineering (tendencia + lags)
        3. Entrenamiento con XGBoost y registro en MLflow
        4. Visualizaciones
    """

    # 1. Descarga y preprocesamiento por lotes
    print("=== 1. Descargando datos ===")
    df = descargar_rango(fecha_inicio, fecha_fin)

    if df.empty:
        print("No se obtuvieron datos. Abortando pipeline.")
        return

    #2. Feature engineering
    df = feature_engineering(df,drop_fecha=True)

    X = df.drop(columns='Valor')
    y = df['Valor']

    # 3. Entrenamiento + MLflow
    print("=== 3. Entrenando modelo ===")
    model, y_test, y_pred = entrenar_xgboost(X, y, test_size=0.2)

    # 4. Visualizaciones
    print("=== 4. Generando visualizaciones ===")
    plot_prediccion(y_test, y_pred)
    plot_importancias(model, X)

    print("=== Pipeline finalizado ===")


if __name__ == "__main__":
    run_pipeline("2024-01-01", "2025-12-31")