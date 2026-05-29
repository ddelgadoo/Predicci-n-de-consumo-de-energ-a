# Reporte del Modelo Baseline

## Descripción del Modelo

El modelo baseline corresponde a un regresor XGBoost (eXtreme Gradient Boosting) entrenado para predecir la demanda horaria de energía eléctrica en Colombia. XGBoost es un algoritmo de ensamble basado en árboles de decisión con boosting por gradiente, ampliamente utilizado en problemas de regresión por su eficiencia computacional y buen desempeño en datos tabulares.

Este modelo se seleccionó como baseline por su facilidad de implementación, interpretabilidad mediante importancia de características y rapidez de entrenamiento, lo que permite establecer una línea de referencia sólida antes de explorar arquitecturas más complejas.

## Variables de Entrada

| Variable | Descripción |
|----------|-------------|
| `hora_sin` / `hora_cos` | Codificación cíclica de la hora del día (0-23) mediante seno y coseno |
| `dia_semana_sin` / `dia_semana_cos` | Codificación cíclica del día de la semana (0=lunes, 6=domingo) |
| `mes_sin` / `mes_cos` | Codificación cíclica del mes del año (1-12) |
| `tendencia` | Índice entero incremental (0 a 17,376) que representa la posición temporal de cada observación, permitiendo capturar el crecimiento estructural de la demanda |
| `lag_1` | Valor de demanda de la hora inmediatamente anterior (t-1) |
| `lag_24` | Valor de demanda de la misma hora del día anterior (t-24) |
| `lag_168` | Valor de demanda de la misma hora de la semana anterior (t-168) |

## Variable Objetivo

La variable objetivo es `Valor`, que representa el consumo de energía eléctrica agregado a nivel nacional en kWh, medido hora a hora. Corresponde a la suma de la demanda de todos los agentes del mercado eléctrico colombiano para cada hora del período 2024-2025.

## Evaluación del Modelo

### Métricas de Evaluación

- **MAE (Mean Absolute Error):** error absoluto promedio en kWh. Representa el error típico de predicción en las mismas unidades de la variable objetivo.
- **RMSE (Root Mean Squared Error):** raíz del error cuadrático medio. Penaliza más los errores grandes que el MAE.
- **R² (Coeficiente de Determinación):** proporción de la varianza explicada por el modelo. Un valor de 1.0 es predicción perfecta; 0.0 equivale a predecir siempre el promedio.

### Resultados de Evaluación

Split temporal: 80% entrenamiento (14,035 observaciones), 20% prueba (3,509 observaciones), sin aleatorización para preservar el orden temporal.

| Métrica | Valor | Interpretación |
|---------|-------|----------------|
| MAE | 76,343 kWh | Error promedio por hora |
| RMSE | 113,253 kWh | Error penalizando outliers |
| R² | 0.9864 | 98.6% de varianza explicada |

## Análisis de los Resultados

**Fortalezas:**
- Excelente desempeño en predicción de corto plazo (1 hora adelante), con R² de 0.9864.
- El MAE de 76,343 kWh representa menos del 1% del valor típico de demanda (~7-9 millones de kWh/hora), lo que indica alta precisión relativa.
- Las variables de lag, especialmente `lag_168` y `lag_24`, capturan efectivamente los patrones cíclicos semanales y diarios.
- La variable `tendencia` permite al modelo distinguir el nivel de demanda entre 2024 y 2025, corrigiendo el sesgo sistemático que aparece sin ella.

**Debilidades:**
- El modelo depende de valores reales históricos (lags) para predecir. En un escenario de predicción a largo plazo, los lags deben alimentarse con predicciones previas, lo que genera acumulación de error.
- No es apto para predecir horizontes de días o semanas completas sin datos reales intermedios.
- La variable `tendencia` solo extrapola bien en el corto plazo; para períodos muy lejanos del entrenamiento, su extrapolación puede deteriorarse.

## Conclusiones

El modelo XGBoost con variables de lag constituye un baseline de alto desempeño para la predicción de demanda energética a corto plazo en Colombia, alcanzando un R² de 0.9864. Su principal limitación es la dependencia de datos históricos recientes, lo que restringe su aplicación a horizontes de predicción cortos (1 hora adelante).

Para predicción a largo plazo se requiere una arquitectura diferente, como modelos de series de tiempo (Prophet) o redes neuronales recurrentes (LSTM), que serán explorados en el modelo final del proyecto.

## Referencias

- XM - Expertos en Mercado. Datos de demanda del Sistema Interconectado Nacional. https://www.xm.com.co
- Chen, T., & Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. KDD 2016.
- SIMEM - Sistema de Información del Mercado de Energía Mayorista. https://www.simem.co
