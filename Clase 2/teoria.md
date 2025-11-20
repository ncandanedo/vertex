# Sesión 2 — Introducción a Vertex AI


## 1. ¿Qué es Vertex AI?
Vertex AI es la plataforma unificada de machine learning de Google Cloud que permite **preparar datos, entrenar modelos, desplegar predicciones y operar MLOps** desde un mismo entorno. Su objetivo es reducir el tiempo de puesta en producción, estandarizar procesos y facilitar la gobernanza de modelos en escala.

Características clave:
- Experiencia unificada para AutoML y entrenamiento personalizado.
- Integración nativa con los servicios de datos de GCP (BigQuery, Dataflow, Pub/Sub, Cloud Storage).
- Capacidades de MLOps: pipelines, registro de modelos, versionado, despliegue y monitorización.
- Compatibilidad con frameworks populares (TensorFlow, PyTorch, XGBoost, scikit-learn) mediante **custom containers**.

## 2. Componentes principales de Vertex AI
- **Vertex AI Workbench**: entornos gestionados de notebooks para exploración y desarrollo.
- **Datasets & Labeling**: administración de conjuntos de datos e interfaces para etiquetado humano (imágenes, texto, vídeo, tabular).
- **Training**: entrenamiento administrado (AutoML o personalizado) con **aceleradores** (GPU/TPU) y **hyperparameter tuning** con **Vertex AI Vizier**.
- **Pipelines**: orquestación reproducible de flujos de ML (basado en Kubeflow Pipelines) con artefactos y tracking.
- **Model Registry**: catálogo central para **versionado, linaje, aprobaciones** y promociones entre entornos.
- **Endpoints (Online Prediction)**: servicio gestionado para publicar modelos con **autoscaling**, **A/B testing** y división de tráfico.
- **Batch Prediction**: inferencia por lotes sobre grandes volúmenes desde Cloud Storage o BigQuery.
- **Model Monitoring & Evaluation**: métricas, detección de **skew/drift**, logging de predicciones y alertas.
- **Feature Store (v2)**: almacenamiento y servicio de **features** consistentes para entrenamiento e inferencia.
- **Matching Engine**: búsqueda vectorial de baja latencia (RAG, recomendaciones, similitud).
- **Generative AI Studio / Model Garden**: acceso a modelos fundacionales y APIs generativas (texto, visión, multimodal) para casos de operaciones (resúmenes, copilots, QA).

## 3. Servicios gestionados vs. modelos personalizados
**Servicios gestionados (AutoML / APIs pre-entrenadas)**
- Ventajas: rapidez, menor mantenimiento, baseline sólido, seguridad y escalado automáticos.
- Limitaciones: menos control sobre arquitectura/hiperparámetros; interpretabilidad y personalización acotadas.

**Modelos personalizados (custom training)**
- Ventajas: control total de datos, arquitectura, métricas y costes; optimización específica del dominio.
- Retos: mayor complejidad operativa (entrenamiento, despliegue, MLOps) y necesidad de perfiles especializados.

**Criterio de elección**
- Empezar con servicios gestionados si el caso lo permite (baseline). Escalar a personalizado cuando **los requisitos de calidad, latencia o costes** lo exijan.

## 4. Integración con BigQuery y Dataflow
- **BigQuery** como *data warehouse* para **almacenar datasets de entrenamiento/evaluación**, servir *features* (mediante tablas/materialized views) y realizar análisis exploratorio a gran escala. Compatible con **Batch Prediction** y exportaciones a Cloud Storage.
- **Dataflow** (Apache Beam) para **ETL/ELT** y procesamiento **streaming** de métricas y logs que alimentan modelos (p. ej., ventanas temporales, agregaciones, limpieza y enriquecimiento).
- Patrón típico AIOps: *fuentes (Monitoring/Logging/Pub/Sub) → Dataflow → BigQuery/Cloud Storage → Vertex Pipelines/Training → Endpoints → Monitoring*.

## 5. Uso de AutoML para modelos rápidos
- **AutoML Tabular**: clasificación/regresión para KPIs operacionales (SLA, SLO, tiempos de respuesta, riesgo de incidente).
- **AutoML Image/Text/Video**: detección de anomalías visuales, clasificación de tickets o análisis de transcripciones.
- Flujo: ingesta → preparación de dataset → entrenamiento AutoML → evaluación → *batch/online prediction* → monitoreo.
- Buenas prácticas: separar *train/val/test*, balancear clases, tratar *data leakage*, y validar con **muestras recientes** (evitar *concept drift*).

## 6. APIs pre-entrenadas aplicables a AIOps
- **Cloud Natural Language / Vertex Text**: clasificación y *topic modeling* de tickets y logs textuales.
- **Speech-to-Text / Translation / Text-to-Speech**: centros de soporte multilingües y automatización de runbooks hablados.
- **Vision / Document AI**: extracción de información de documentos operativos y detección visual de fallos en entornos físicos.
- **Vertex AI generativo (LLMs)**: *summarization* de incidentes, redacción de *post-mortems*, copilotos de SRE.

## 7. Creación de datasets en Vertex AI
- **Fuentes**: BigQuery, Cloud Storage (CSV/Parquet/TFRecord/JSONL), Pub/Sub (vía Dataflow), APIs internas.
- **Esquema y *metadata***: definición de tipos, *labels*, *timestamps* y claves; **particionamiento temporal** para casos operacionales.
- **Particiones**: *train/validation/test* con división temporal cuando hay dependencia de tiempo.
- **Calidad de datos**: tratamiento de valores ausentes, outliers, normalización/estandarización y codificación de categorías.
- **Etiquetado**: guías claras, *golden set*, métricas de acuerdo inter-anotador; auditoría de cambios.
- **Versionado de dataset**: *snapshots*, *data lineage* y *data contracts* para reproducibilidad.

## 8. Entrenamiento y despliegue de modelos
- **Entrenamiento**: jobs administrados con aceleradores, **custom containers**, *distributed training* y **Vertex AI Vizier** para tuning.
- **Evaluación**: métricas por tipo de problema (AUC/ROC, F1, RMSE, MAE, PR-AUC); *confusion matrix* y curvas de calibración.
- **Despliegue**:
  - **Online** en **Endpoints** (autoscaling, *traffic splitting*, *canary* y *shadow*).
  - **Batch** para scoring masivo desde BigQuery/Cloud Storage.
- **Integración**: autenticación IAM, VPC-SC/Private Service Connect, registro de predicciones (a BigQuery/Cloud Logging).

## 9. Monitorización del rendimiento de modelos
- **Model Monitoring**: deriva de datos (*data drift*), sesgo entre entrenamiento y producción (*skew*), y calidad de predicciones.
- **Alertas**: umbrales operativos integrados con **Cloud Monitoring** y Pub/Sub para *auto-remediation*.
- **Observabilidad**: *latencia*, *QPS*, *error rate*, *feature attributions*; *audit logs* y *prediction logs* para trazabilidad.
- **Ciclo continuo**: captura de muestras de producción → re-entrenamiento programado → validación → promoción de versión.

## 10. Gestión de versiones en Vertex AI
- **Model Registry** como fuente de verdad: versiones con **artefactos, métricas, permisos y estados** (staging/production).
- **Lineage**: trazabilidad de datasets, pipelines y modelos (cumplimiento y auditoría).
- **Promoción controlada**: *gates* de calidad, *rollbacks* rápidos, y *blue/green* en Endpoints.


## 11. Fin
Examen: https://forms.gle/r83hcynhSC64SrB16
FeedBack: (https://imagina-formacion.typeform.com/to/IkO83DnN)