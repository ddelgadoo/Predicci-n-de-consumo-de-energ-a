# Project Charter - Entendimiento del Negocio

## Nombre del Proyecto

Predicción del consumo de energía

## Objetivo del Proyecto

Desarrollar un modelo de machine learning que permita estimar el consumo de energía eléctrica en Colombia a partir de los datos históricos proporcionados por XM, con el fin de mejorar la planeación del sistema eléctrico, optimizar la toma de decisiones operativas y contribuir a la eficiencia del mercado energético.

## Alcance del Proyecto
El proyecto contempla el desarrollo y validación de un modelo de predicción del consumo de energía eléctrica en Colombia, basado en datos históricos de XM, incluyendo su depuración, análisis y modelamiento mediante técnicas estadísticas o de aprendizaje automático.


### Incluye:

- Tratamiento de datos históricos de consumo energético provenientes de XM.
- Análisis exploratorio para identificar patrones, tendencias y estacionalidad.
- Desarrollo e implementación de modelos predictivos.
- Evaluación del desempeño de los modelos mediante métricas.
- Despliegue del modelo.

### Excluye:

- Implementación del modelo en sistemas operativos en tiempo real.
- Intervención directa en la operación del Sistema Interconectado Nacional.
- Uso de datos no disponibles públicamente o información confidencial.
- Desarrollo de infraestructura tecnológica para despliegue productivo.

## Metodología

La metodología utilizada sera CRISP-DM (Cross Industry Standard Process for Data Mining), un enfoque estructurado y ampliamente utilizado en proyectos de analítica y ciencia de datos. 
Su objetivo es guiar el desarrollo de soluciones basadas en datos mediante un proceso iterativo y organizado en seis fases principales

## Cronograma

| Etapa | Duración Estimada | Fechas |
|------|---------|-------|
| Entendimiento del negocio y carga de datos | 1 semanas | del 8 de mayo al 14 de mayo |
| Preprocesamiento, análisis exploratorio | 1 semanas | del 15 de mayo al 21 de mayo |
| Modelamiento y extracción de características | 1 semanas | del 22 de mayo al 28 de mayo |
| Despliegue | 1 semanas | del 29 de mayo al 04 de junio |
| Evaluación y entrega final | 1 semanas | del 05 de junio al 11 de junio |

## Equipo del Proyecto

- | MLOps Engineer | David Delgado |
- | Data Scientist | Daniel Trillos|

## Presupuesto

| Categoría de Gasto | Descripción | Costo Estimado (USD) | Notas |
|---|---|---|---|
| **I. Personal** | | | |
| Data Scientist | EDA, modelado, evaluación | $4,000 | 1 mese a tiempo parcial |
| MLOps Engineer | API, deploy, infraestructura | $4,000 | 1 mese a tiempo parcial |
| **II. Infraestructura y Software** | | | |
| Almacenamiento | Datos descargados de SIMEM + artefactos del modelo | $0 | Dataset mediano; cabe en almacenamiento local o gratuito |
| **TOTAL ESTIMADO** | | **$8000** | |

## Stakeholders

- **Equipo de proyecto:** Daniel Trillos y David Delgado, responsables del desarrollo técnico y despliegue.
- **Usuarios potenciales:** Profesionales del sector energético colombiano (analistas de XM, EPM, Codensa, ISA) interesados en herramientas de predicción de demanda.
- **Validadores de dominio:** Ingenieros eléctricos o especialistas en mercados de energía que puedan verificar la coherencia de las predicciones con el comportamiento real del SIN.
- **Expectativas:** Entrega de un modelo funcional con métricas verificables, una demo pública accesible y documentación clara del proceso y las decisiones técnicas tomadas.

## Aprobaciones

- David Delgado
- Daniel Trillos
