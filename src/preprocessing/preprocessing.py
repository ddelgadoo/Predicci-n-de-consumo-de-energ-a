import pandas as pd
import numpy as np
import re
import sys


def verificacionFormatoFecha(df:pd.DataFrame):
    patron_fecha = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$'
    fechas = df['FechaHora']
    cumple_formato = fechas.str.match(patron_fecha)

    if cumple_formato.all():
        print('Todas las fechas cumplen el formato YYYY-MM-DDTHH:MM:SS')
    else:
        raise ValueError("Se encontraron fechas que no cumplen el formato YYYY-MM-DDTHH:MM:SS\n",fechas[~cumple_formato])


def reformatoFecha(df:pd.DataFrame) -> pd.DataFrame:

    df['FechaHora'] = pd.to_datetime(df['FechaHora'])
    print("reformato exitoso\n")
    print("------------------")
    return df

def borrarCerosValores(df:pd.DataFrame) -> pd.DataFrame:

    index_ceros = df[df['Valor'] == 0].index
    df = df.drop(index_ceros)
    print("Borrado de ceros exitoso\n")
    print("------------------")
    return df

def borrar_columnas(df :pd.DataFrame, cols: list ) -> pd.DataFrame:

    df = df.drop(cols, axis=1)
    print("Borrado de columnas exitoso\n")
    return df


def ordenar_versiones_por_dato(df: pd.DataFrame) -> pd.DataFrame:

    orden_versiones = {'TXF': 9, 'TXR': 8, 'TX8': 7, 'TX7': 6,
                       'TX6': 5, 'TX5': 4, 'TX4': 3, 'TX3': 2, 'TX2': 1}

    df['version_orden'] = (df['Version'].map(orden_versiones))
    df = (df.sort_values('version_orden', ascending=False).
          drop_duplicates(subset=['FechaHora', 'CodigoSICAgente'], keep='first'))
    print("Ordenado exitoso\n")
    return df

def groupbyPorHora(df: pd.DataFrame):

    df = df.groupby('FechaHora', as_index=False)['Valor'].sum()
    print("Groupby por hora exitoso\n")
    return df

def horasCíclicas(df:pd.DataFrame) -> pd.DataFrame:

    df['hora_sin'] = np.sin(
        2 * np.pi * df['FechaHora'].dt.hour / 24)

    df['hora_cos'] = np.cos(
        2 * np.pi * df['FechaHora'].dt.hour / 24)

    df['dia_semana_sin'] = np.sin(
        2 * np.pi * df['FechaHora'].dt.dayofweek / 7)

    df['dia_semana_cos'] = np.cos(
        2 * np.pi * df['FechaHora'].dt.dayofweek / 7)

    df['mes_sin'] = np.sin(
        2 * np.pi * df['FechaHora'].dt.month / 12)

    df['mes_cos'] = np.cos(
        2 * np.pi * df['FechaHora'].dt.month / 12)

    print("Horas exitoso\n")
    return df

def feature_engineering(df: pd.DataFrame, drop_fecha: bool = True) -> pd.DataFrame:
    df = df.copy()
    df['tendencia'] = np.arange(len(df))
    df['lag_1']     = df['Valor'].shift(1)
    df['lag_24']    = df['Valor'].shift(24)
    df['lag_168']   = df['Valor'].shift(168)
    df = df.dropna()

    if drop_fecha:
        df = df.drop(columns=['FechaHora'])

    print(f"Feature engineering exitoso. Filas resultantes: {len(df)}\n")
    return df

def preprocessing(df: pd.DataFrame) -> pd.DataFrame:
    verificacionFormatoFecha(df)

    df = df.copy()
    df_preprocesado = (df
                       .pipe(reformatoFecha)
                       .pipe(borrarCerosValores)
                       .pipe(borrar_columnas,cols = ['CodigoVariable','CodigoDuracion', 'UnidadMedida'])
                       .pipe(groupbyPorHora)
                       .pipe(horasCíclicas)
                       )
    return df_preprocesado

