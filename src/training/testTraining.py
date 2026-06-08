# training/testTraining.py

# Para testear en consola: python -m pytest src/training/testTraining.py -v
import pytest
import pandas as pd
import numpy as np
from src.training.training import entrenar_xgboost
from xgboost import XGBRegressor

@pytest.fixture
def df_dummy():
    """DataFrame sintético que simula la salida de feature_engineering."""
    np.random.seed(0)
    n = 500  # suficiente para el split 80/20
    df = pd.DataFrame({
        'hora_sin':      np.sin(2 * np.pi * np.arange(n) / 24),
        'hora_cos':      np.cos(2 * np.pi * np.arange(n) / 24),
        'dia_semana_sin': np.random.uniform(-1, 1, n),
        'dia_semana_cos': np.random.uniform(-1, 1, n),
        'mes_sin':       np.random.uniform(-1, 1, n),
        'mes_cos':       np.random.uniform(-1, 1, n),
        'tendencia':     np.arange(n),
        'lag_1':         np.random.uniform(1e6, 2e6, n),
        'lag_24':        np.random.uniform(1e6, 2e6, n),
        'lag_168':       np.random.uniform(1e6, 2e6, n),
    })
    X = df.copy()
    y = pd.Series(np.random.uniform(1e6, 2e6, n), name='Valor')
    return X, y

def test_retorna_tres_elementos(df_dummy):
    X, y = df_dummy
    resultado = entrenar_xgboost(X, y, test_size=0.2)
    assert len(resultado) == 3

def test_modelo_predice(df_dummy):
    X, y = df_dummy
    model, y_test, y_pred = entrenar_xgboost(X, y, test_size=0.2)
    assert len(y_pred) == len(y_test)

def test_metricas_razonables(df_dummy):
    X, y = df_dummy
    model, y_test, y_pred = entrenar_xgboost(X, y, test_size=0.2)
    from sklearn.metrics import r2_score
    r2 = r2_score(y_test, y_pred)
    assert r2 > -1  # umbral mínimo — datos sintéticos no tienen patrón real