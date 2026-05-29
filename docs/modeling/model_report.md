# Reporte del Modelo Final

## Resumen Ejecutivo

Se desarrollaron y compararon dos modelos para la predicción de la demanda de energía eléctrica en Colombia: XGBoost con variables de lag (modelo baseline) y Prophet (modelo de series de tiempo). El modelo XGBoost alcanzó un R² de 0.9864 con un MAE de 76,343 kWh, siendo óptimo para predicción de corto plazo. Prophet, orientado a predicción de largo plazo, obtuvo un MAPE de 12.7% a 3 días, adecuado para planeación estratégica del sistema eléctrico nacional.

Ambos modelos se complementan: XGBoost para operación horaria y Prophet para planeación de mediano plazo, cubriendo los principales casos de uso del sector energético colombiano.

## Descripción del Problema

El Sistema Interconectado Nacional (SIN) de Colombia requiere estimaciones precisas de la demanda eléctrica para garantizar el balance entre generación y consumo. XM, como administrador del mercado eléctrico, publica datos históricos horarios de consumo por agente a través de SIMEM.

El problema consiste en predecir el consumo total de energía eléctrica en Colombia (en kWh) para horizontes de tiempo variables, desde la siguiente hora hasta varias semanas adelante, utilizando únicamente datos históricos de demanda y variables temporales derivadas.

Los datos comprenden el período 2024-2025, con granularidad horaria y cobertura de todos los agentes del mercado regulado y no regulado. Tras el preprocesamiento, el dataset final contiene 17,544 observaciones (una por hora).

## Descripción del Modelo

### Preprocesamiento

- **Filtrado de versiones:** para cada par (FechaHora, agente) se conservó únicamente la versión más actualizada, siguiendo la jerarquía `TXF > TXR > TX8 > ... > TX2`.
- **Agregación nacional:** se sumó el `Valor` de todos los agentes por hora, reduciendo el dataset a una serie temporal univariada de demanda total del país.
- **Eliminación de registros en cero:** se descartaron 129,813 registros (2.9%) correspondientes a agentes sin medición real.
- **Codificación cíclica:** hora, día de la semana y mes se transformaron con funciones seno y coseno para preservar su naturaleza circular.

### Modelo 1: XGBoost (Corto Plazo)

XGBoost es un algoritmo de ensamble basado en árboles de decisión con boosting por gradiente. Se configuró con 500 estimadores y learning rate de 0.05. Las variables de entrada incluyen las codificaciones cíclicas, una variable de tendencia lineal y tres lags (t-1, t-24, t-168). El split temporal fue 80/20 sin aleatorización.

### Modelo 2: Prophet (Largo Plazo)

Prophet es un modelo de descomposición de series de tiempo desarrollado por Meta, que modela la serie como la suma de tendencia, estacionalidad anual, semanal y diaria. Se entrenó con estacionalidades diaria, semanal y anual activadas, sobre el dataset completo con columnas `ds` (FechaHora) e `y` (Valor). No requiere variables de lag, lo que le permite proyectar cualquier horizonte futuro.

## Evaluación del Modelo

### Comparación de Modelos

| Modelo | MAE (kWh) | RMSE (kWh) | R² | Horizonte |
|--------|-----------|------------|-----|-----------|
| XGBoost + lags | 76,343 | 113,253 | 0.9864 | Corto plazo (1h) |
| Prophet | ~990,000 | ~1,144,970 | N/A | Largo plazo (días) |

### Evaluación Prophet — Validación Cruzada Temporal

Se realizó validación cruzada temporal con `initial=600 días`, `period=30 días` y `horizon=30 días`. Los resultados muestran un MAPE de 12.7% a 3 días que crece gradualmente con el horizonte, lo esperado en modelos de largo plazo.

| Horizonte | MAE (kWh) | RMSE (kWh) | MAPE |
|-----------|-----------|------------|------|
| 3 días | 988,598 | 1,144,970 | 12.7% |
| 7 días | ~1,010,000 | ~1,170,000 | ~13.1% |
| 30 días | ~1,050,000 | ~1,220,000 | ~13.8% |

## Conclusiones y Recomendaciones

**Conclusiones:**
- XGBoost con variables de lag es el modelo más preciso para predicción horaria, con un error relativo menor al 1% del valor típico de demanda.
- Prophet ofrece predicción honesta a largo plazo con un error de ~12-13%, viable para planeación estratégica donde no se dispone de datos reales intermedios.
- La codificación cíclica seno/coseno y la variable de tendencia son fundamentales para capturar patrones temporales sin introducir discontinuidades artificiales.
- Los lags (especialmente `lag_168`) son los predictores más importantes en XGBoost, ya que incorporan el nivel actual de demanda directamente en la predicción.

**Limitaciones:**
- XGBoost depende de datos históricos recientes; no es apto para predicción autónoma de largo plazo sin retroalimentación de valores reales.
- Prophet no captura eventos atípicos (festivos, cortes de energía) a menos que se especifiquen explícitamente como regresores externos.
- Ambos modelos fueron entrenados con datos 2024-2025; su desempeño puede degradarse ante cambios estructurales en el sistema eléctrico.

**Trabajo Futuro:**
- Implementar una red neuronal LSTM para capturar dependencias temporales largas sin necesidad de lags explícitos, potencialmente combinando la precisión de XGBoost con la capacidad de largo plazo de Prophet.
- Incorporar variables exógenas como temperatura, festivos colombianos y eventos del sector energético.
- Desplegar el modelo XGBoost como API REST para predicción operativa en tiempo real.

## Referencias

- XM - Expertos en Mercado. Datos de demanda del Sistema Interconectado Nacional. https://www.xm.com.co
- SIMEM - Sistema de Información del Mercado de Energía Mayorista. https://www.simem.co
- Chen, T., & Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. KDD 2016.
- Taylor, S.J., & Letham, B. (2018). Forecasting at scale. The American Statistician, 72(1), 37-45.
