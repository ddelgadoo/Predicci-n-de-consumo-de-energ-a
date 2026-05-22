# Reporte de Datos
**Dataset:** Demanda real de energía eléctrica — Colombia 2024–2025  
**Fuente:** SIMEM / XM S.A. E.S.P.  
**Elaborado por:** Análisis Exploratorio de Datos

---

## 1. Resumen general de los datos

El dataset contiene registros horarios de demanda real de energía eléctrica del Sistema Interconectado Nacional (SIN) de Colombia, desagregados por agente del mercado para el período enero 2024 – diciembre 2025.

| Característica | Valor |
|----------------|-------|
| Registros totales | 4.450.032 |
| Variables | 8 |
| Período | Enero 2024 – Diciembre 2025 |
| Granularidad | Horaria (PT1H) |
| Agentes únicos | 65 |
| Fechas únicas | ~17.000 |

Dado que cada registro corresponde a la combinación de un agente, una fecha-hora y una versión del dato, la presencia de ~17.000 fechas únicas sobre 4,45 millones de registros es el comportamiento esperado del sistema de liquidación de XM.

---

## 2. Resumen de calidad de los datos

### Valores faltantes

No se encontraron valores nulos en ninguna columna del dataset.

| Columna | Nulos | % |
|---------|-------|---|
| Todas | 0 | 0,00% |

### Duplicados

No se encontraron filas completamente duplicadas en el dataset.

### Valores negativos

La variable `Valor` no presenta registros negativos, lo cual es consistente con una variable de consumo energético.

### Valores en cero

Se identificaron **129.813 registros con `Valor = 0`**, equivalentes al **2,9% del total**.

| Hallazgo | Detalle |
|----------|---------|
| Mercado concentrador | 91,7% de los ceros pertenecen al mercado No Regulado |
| Agentes involucrados | GSAC (40.822), BCCC (34.236), TRPC (33.024) |
| Distribución horaria | Uniforme en las 24 horas — no corresponde a inactividad real |

Dado que representan menos del 3% de los datos y no existe una hipótesis clara sobre su origen, **se decide eliminarlos del dataset final.**

### Outliers en `Valor`

La distribución presenta fuerte asimetría positiva. Aplicando el criterio IQR (Q3 + 1,5×IQR), se identifica un porcentaje significativo de valores extremos, correspondientes principalmente a grandes agentes industriales del mercado No Regulado. Dado que estos valores pueden representar eventos reales del sistema eléctrico, **no se aplica tratamiento de outliers.**

---

## 3. Variable objetivo

La variable objetivo es **`Valor`**, que representa el consumo de energía eléctrica expresado en **kWh** por agente y por hora.

### Estadísticas descriptivas

| Estadístico | Valor |
|-------------|-------|
| Registros (tras limpieza) | ~4,32 millones |
| Media | 104.831 kWh |
| Mediana | 16.507 kWh |
| Desv. estándar | 233.928 kWh |
| Mínimo | 0,001 kWh |
| Percentil 25 | 1.859 kWh |
| Percentil 75 | 80.238 kWh |
| Máximo | 1.682.582 kWh |

La brecha entre la mediana (16.507 kWh) y la media (104.831 kWh) confirma el fuerte sesgo positivo de la distribución, característico de variables de consumo energético donde la mayoría de agentes tienen demandas moderadas pero algunos grandes consumidores elevan significativamente el promedio.

### Comportamiento temporal

La demanda promedio mensual se mantiene **estable** en el rango de 100.000–110.000 kWh a lo largo del período, sin tendencias crecientes o decrecientes marcadas. Las variaciones observadas son consistentes con ciclos estacionales propios del sistema eléctrico colombiano.

---

## 4. Variables individuales

### `CodigoVariable`
Toma un único valor (`DdaReal`) en la totalidad del dataset. **Descartada** por ausencia de variabilidad.

### `FechaHora`
Variable temporal en formato `YYYY-MM-DDTHH:MM:SS`. Todas las fechas cumplen el formato esperado. Transformada a tipo `datetime` para el análisis. La distribución de registros por mes muestra un salto abrupto entre diciembre 2024 y enero 2025, explicado por la diferencia en versiones disponibles entre ambos años (ver sección `Version`).

### `CodigoSICAgente`
65 agentes únicos sin valores nulos ni espacios en blanco. La distribución de registros por agente es **equilibrada** — la curva de Pareto muestra un comportamiento casi lineal, donde el 60% de los registros se concentran en los primeros 28 agentes.

### `TipoMercado`
Dos categorías: **Regulado** (hogares y pequeños consumidores) y **No Regulado** (grandes consumidores industriales). Distribución aproximadamente balanceada entre ambos segmentos (~50/50), sin valores nulos.

### `Version`
9 versiones distintas del dato, correspondientes al ciclo de liquidación de XM. Los datos de 2024 contienen exclusivamente versiones de reconciliación tardía (TX4–TX8), mientras que 2025 incluye versiones preliminares (TXR) y finales (TXF). Esta diferencia explica el mayor volumen de registros en 2025. Las versiones TX4 y TX5 son las únicas compartidas entre ambos años.

### `Valor`
Variable objetivo. Ver sección 3.

### `UnidadMedida` y `CodigoDuracion`
Ambas toman un único valor en todo el dataset (`kWh` y `PT1H` respectivamente). **Descartadas** por ausencia de variabilidad.

---

## 5. Relación entre variables explicativas y variable objetivo

### Patrones temporales

El análisis gráfico por grupos revela los siguientes patrones en la demanda:

- **Por hora del día:** La demanda presenta variaciones a lo largo del día, con niveles más bajos en la madrugada y valores más altos durante la jornada laboral, consistente con los ciclos de actividad industrial y comercial.
- **Por día de la semana:** Se observan diferencias entre días hábiles (lunes a viernes) y fines de semana, con menor demanda en sábado y domingo.
- **Por mes:** Las variaciones estacionales son moderadas, sin picos extremos, lo cual es característico del sistema eléctrico colombiano dado su clima relativamente estable a lo largo del año.

### Conclusión

La demanda energética está influenciada por **patrones temporales** a distintas escalas (horaria, semanal, mensual). Estas variables derivadas de `FechaHora` son candidatos relevantes como features para el modelo predictivo, especialmente bajo enfoques que capturen relaciones no lineales.

---

## 7. Dataset final

Tras el preprocesamiento, el dataset final `final_demanda_colombia` tiene las siguientes características:

| Característica | Valor |
|----------------|-------|
| Registros | ~4,32 millones |
| Columnas | 5 (`FechaHora`, `CodigoSICAgente`, `TipoMercado`, `Version`, `Valor`) |
| Columnas eliminadas | `CodigoVariable`, `UnidadMedida`, `CodigoDuracion` |
| Registros eliminados | 129.813 (valores en cero) |
