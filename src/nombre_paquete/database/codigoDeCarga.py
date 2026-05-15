
#Para que funcione se debe instalar la librería pydataxm
# Descargar los datos toma alrededor de 20 min

# !pip install pydataxm
import pandas as pd
from pydataxm.pydatasimem import ReadSIMEM
from datetime import datetime, timedelta

def descargar_rango(dataset_id, fecha_inicio, fecha_fin):
    start = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    end = datetime.strptime(fecha_fin, '%Y-%m-%d')
    
    dfs = []
    current = start
    while current < end:
        chunk_end = min(current + timedelta(days=29), end)
        df = ReadSIMEM(
            dataset_id,
            current.strftime('%Y-%m-%d'),
            chunk_end.strftime('%Y-%m-%d')
        ).main(filter=False)
        dfs.append(df)
        current = chunk_end + timedelta(days=1)
    
    return pd.concat(dfs, ignore_index=True)

# Descargar 2 año completo de demanda
df_demanda = descargar_rango('c1b851', '2024-01-01', '2025-12-31')
df_demanda.to_csv('demanda_colombia.csv', index=False)
