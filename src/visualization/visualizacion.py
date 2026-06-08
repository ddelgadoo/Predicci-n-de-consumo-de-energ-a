import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from xgboost import XGBRegressor


def plot_prediccion(y_test: pd.Series, y_pred: np.ndarray,
                    n_horas: int = 200) -> None:
    """
    Grafica las primeras n_horas del conjunto de test:
    valores reales vs predichos.
    """
    plt.figure(figsize=(14, 4))
    plt.plot(y_test.values[:n_horas], label='Real', color='steelblue')
    plt.plot(y_pred[:n_horas], label='Predicho', color='orange')
    plt.legend()
    plt.title(f'XGBoost — Real vs Predicho (primeras {n_horas} horas del test)')
    plt.xlabel('Hora')
    plt.ylabel('kWh')
    plt.tight_layout()
    plt.show()


def plot_importancias(model: XGBRegressor, X: pd.DataFrame) -> None:
    """
    Grafica la importancia de características del modelo entrenado.
    """
    importancias = pd.Series(model.feature_importances_, index=X.columns)
    importancias = importancias.sort_values(ascending=True)

    plt.figure(figsize=(8, 5))
    importancias.plot(kind='barh', color='steelblue')
    plt.title('Importancia de características — XGBoost')
    plt.xlabel('Importancia')
    plt.tight_layout()
    plt.show()