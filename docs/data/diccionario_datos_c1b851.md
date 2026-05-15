# Diccionario de Datos — Dataset `c1b851`
**Fuente:** SIMEM — Sistema de Información del Mercado de Energía Mayorista  
**Operador:** XM S.A. E.S.P.  
**Variable:** Demanda Real (`DdaReal`)  
**Granularidad:** Horaria  
**Unidad de medida:** KWh  

---

## Descripción general

El dataset `c1b851` contiene el registro horario de la demanda real de energía eléctrica del Sistema Interconectado Nacional (SIN) de Colombia, desagregada por agente del mercado. Es publicado por XM como parte del portal de datos abiertos SIMEM y no requiere autenticación para su consumo.

---

## Estructura del dataset

| # | Columna | Tipo | Valores únicos | Descripción |
|---|---|---|---|---|
| 1 | `FechaHora` | `datetime` | 17,544 | Marca de tiempo del registro en formato `YYYY-MM-DD HH:MM:SS`. Representa cada hora del período consultado. Con ~17,544 valores corresponde aproximadamente a **2 años de datos horarios**. |
| 2 | `Valor` | `float` | Continuo | **Variable objetivo del modelo.** Consumo de energía eléctrica expresado en **KWh**. Aparece como `NaN` en resúmenes categóricos por ser numérica continua. |
| 3 | `CodigoSICAgente` | `string` | 69 | Código único del agente registrado en el Sistema de Información Comercial (SIC). Identifica la empresa distribuidora u operador de red. Son los 69 agentes activos en el mercado. |
| 4 | `MercadoComercializacion` | `string` | 28 | Segmento del mercado al que pertenece el agente (mercado regulado, no regulado, entre otros). Permite segmentar el análisis por tipo de usuario. |
| 5 | `SistemaTransmision` | `string` | 2 | Indica si el agente opera en el **STN** (Sistema de Transmisión Nacional) o en el **STR** (Sistema de Transmisión Regional). |
| 6 | `Version` | `string` | 10 | Versión del dato publicado. XM puede emitir revisiones  del mismo período. |
| 7 | `CodigoVariable` | `string` | 1 | Código de la variable medida. Toma un único valor: `DdaReal` Correspondiente a demanda real|
| 8 | `CodigoDuracion` | `string` | 1 | Código que indica la granularidad temporal del registro. Toma un único valor, correspondiente a medición **horaria**. |
| 9 | `UnidadMedida` | `string` | 1 | Unidad de medida del campo `Valor`. Toma un único valor: **KWh** (kilovatios-hora). |

---

## Columnas relevantes por caso de uso

### Predictor de consumo energético

| Columna | Rol |
|---|---|
| `FechaHora` | Eje temporal (índice de la serie de tiempo) |
| `Valor` | Variable objetivo a predecir |
| `CodigoSICAgente` | Filtro para segmentar por agente o región |
| `Version` | Filtro para conservar solo la versión más reciente |

---

## Notas de calidad de datos

- **Valores nulos en `Valor`:** Verificar con `df['Valor'].isnull().sum()`. Horas sin medición pueden deberse a cortes de comunicación o mantenimiento del sistema de medida.
- **Versiones múltiples:** El campo `Version` puede generar duplicados para el mismo `FechaHora` + `CodigoSICAgente`. Filtrar siempre por la versión más reciente antes de modelar.
- **Agentes inactivos:** Algunos `CodigoSICAgente` pueden no tener registros continuos si el agente entró o salió del mercado durante el período.

---

## Ejemplo de estructura esperada

```
FechaHora            CodigoSICAgente  Valor    Version  MercadoComercializacion  SistemaTransmision  CodigoVariable  CodigoDuracion  UnidadMedida
2024-01-01 01:00:00  EPM              1245.80  TXr6     MERCADO_REGULADO         STN                 DdaReal         H               KWh
2024-01-01 01:00:00  CODENSA          980.30   TXr6     MERCADO_REGULADO         STN                 DdaReal         H               KWh
2024-01-01 01:00:00  ESSA             312.50   TXr6     MERCADO_REGULADO         STR                 DdaReal         H               KWh
```

---

## Datasets relacionados

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
