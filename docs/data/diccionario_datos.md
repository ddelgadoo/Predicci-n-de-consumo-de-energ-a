# Diccionario de Datos — Dataset `d55202`
**Fuente:** SIMEM — Sistema de Información del Mercado de Energía Mayorista  
**Operador:** XM S.A. E.S.P.  
**Variable:** Demanda Real (`DdaReal`)  
**Período:** Enero 2024 – Diciembre 2025  
**Granularidad:** Horaria (PT1H)  
**Unidad de medida:** kWh  

---

## Descripción general

El dataset `d55202` contiene el registro horario de la demanda real de energía eléctrica del Sistema Interconectado Nacional (SIN) de Colombia, desagregada por agente del mercado. Es publicado por XM como parte del portal de datos abiertos SIMEM y no requiere autenticación para su consumo.

El dataset cubre **65 agentes** del mercado eléctrico colombiano (operadores de red y grandes consumidores), con registros horarios para el período 2024–2025. El volumen total es de aproximadamente **4,45 millones de registros** antes del preprocesamiento.

---

## Estructura del dataset

| # | Columna | Tipo | Descripción | Valores únicos | Relevancia |
|---|---------|------|-------------|----------------|------------|
| 1 | `CodigoVariable` | `string` | Código de la variable medida. Toma un único valor: `DdaReal`, correspondiente a demanda real |
| 2 | `FechaHora` | `datetime` | Marca de tiempo en formato `YYYY-MM-DDTHH:MM:SS`. Representa cada hora del período consultado |
| 3 | `CodigoSICAgente` | `string` | Código único del agente en el Sistema de Información Comercial (SIC). Identifica la empresa distribuidora u operador de red |
| 4 | `TipoMercado` | `string` | Segmento del mercado: **Regulado** (hogares y pequeños consumidores) o **No Regulado** (grandes consumidores industriales que negocian contratos directamente) |
| 5 | `Version` | `string` | Versión del dato publicado por XM. TX1 es la estimación más preliminar y TXF el dato definitivo. XM puede demorar hasta un año en publicar TXF |
| 6 | `Valor` | `float` | **Variable objetivo.** Consumo de energía eléctrica en **kWh**  |
| 7 | `UnidadMedida` | `string` | Unidad de medida del campo `Valor`. Toma un único valor: `kWh`  |
| 8 | `CodigoDuracion` | `string` | Granularidad temporal del registro. Toma un único valor: `PT1H` (medición horaria)|

---

## Versiones del dato (campo `Version`)

XM publica el mismo registro varias veces a medida que avanza el proceso de liquidación del mercado. Las versiones disponibles en el dataset son:

| Versión | Descripción | Presente en |
|---------|-------------|-------------|
| `TXR` | Tiempo real — estimación inmediata | 2025 |
| `TXF` | Dato final — la versión más precisa | 2025 |
| `TX2` a `TX8` | Versiones intermedias de reconciliación, en orden creciente de precisión | 2024 (TX4–TX8), 2025 (TX2–TX5) |

> **Nota:** Los datos de 2024 solo contienen versiones TX4–TX8 (reconciliación tardía), mientras que 2025 incluye TXR y TXF. Ambos años comparten TX4 y TX5 como versiones en común.

---

## Columnas relevantes para el modelo predictivo

| Columna | Rol |
|---------|-----|
| `FechaHora` | Eje temporal — índice de la serie de tiempo |
| `Valor` | Variable objetivo a predecir |
| `CodigoSICAgente` | Segmentación por agente o región |
| `TipoMercado` | Variable categórica explicativa |
| `Version` | Filtro de calidad — usar TXF para 2025, TX8 para 2024 |

---

## Datasets relacionados en SIMEM

| Dataset ID | Variable | Descripción |
|---|---|---|
| `b7917a` | `DdaRealRegulada` | Demanda real de usuarios regulados (hogares y pequeñas empresas) |
| `b7917a` | `DdaRealNoRegulada` | Demanda real de grandes consumidores industriales |
| `b7917a` | `DdaRealOR` | Demanda real desagregada por operador de red (nivel regional) |
| `d55202` | `DdaCom` | Demanda comercial — lo que se factura. Útil para calcular pérdidas no técnicas |
| `E17D25` | `GeneracionRealEstimada` | Generación real por planta. Complementa el análisis de balance oferta-demanda |

---

## Referencias

- Portal SIMEM: [https://www.simem.co](https://www.simem.co)
- Librería Python: `pip install pydataxm`
- Repositorio oficial XM: [https://github.com/EquipoAnaliticaXM/API_XM](https://github.com/EquipoAnaliticaXM/API_XM)
- Documentación API: [https://www.simem.co/recursos/Documentacion%20API%20SIMEM.pdf](https://www.simem.co/recursos/Documentacion%20API%20SIMEM.pdf)
- Registro de agentes SIC: [https://www.xm.com.co/transacciones/registros/registro-agentes-y-contactos/estructura-del-mercado](https://www.xm.com.co/transacciones/registros/registro-agentes-y-contactos/estructura-del-mercado)
