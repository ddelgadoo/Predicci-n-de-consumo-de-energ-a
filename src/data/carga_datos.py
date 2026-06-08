

import os
from pydataxm.pydatasimem import ReadSIMEM
from datetime import datetime, timedelta
import pandas as pd
import logging
from src.preprocessing.preprocessing import preprocessing


def descargar_rango(fecha_inicio: str, fecha_fin: str, preprocesar: bool = True) -> pd.DataFrame:
    """
    Descarga de la API de XM la base de datos d55202
    "Demanda real energía Colombia" y la preprocesa por lotes.
    Para no aplicar preprocesamiento, indicar preprocesar = False
    """
    start = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    end = datetime.strptime(fecha_fin, '%Y-%m-%d')

    dfs = []
    current = start

    while current < end:
        chunk_end = min(current + timedelta(days=29), end)

        # Formateamos las fechas en texto para la API
        str_inicio = current.strftime('%Y-%m-%d')
        str_fin = chunk_end.strftime('%Y-%m-%d')

        print(f"Descargando periodo: {str_inicio} a {str_fin}...")

        # 1. Descargamos el lote crudo
        df_raw = ReadSIMEM("d55202", str_inicio, str_fin).main(filter=False)

        # 2. Verificamos que la API realmente devolvió datos para no romper el código
        if df_raw is not None and not df_raw.empty:

            print(f" Preprocesando lote de {len(df_raw)} filas")

            if preprocesar:
                # 3. Aplicar pipeline de preprocesamiento al lote
                df_clean = preprocessing(df_raw)
                # 4. Guardamos el lote ya limpio
                dfs.append(df_clean)
            else:
                dfs.append(df_raw)

        else:
            print(f" No se encontraron datos para {str_inicio} - {str_fin}")

        # Avanzar al siguiente periodo
        current = chunk_end + timedelta(days=1)

    print("Concatenando base de datos final")

    # 5. Concatenamos los lotes que ya están preprocesados
    if dfs:
        df_final = pd.concat(dfs, ignore_index=True)
        return df_final
    else:
        print("No se descargó ningún dato en el rango especificado.")
        return pd.DataFrame()








