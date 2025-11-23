# README — Curso **AIOps con Vertex AI (GCP)**

> Guía principal del curso orientado a profesionales de **DevOps/SRE** para construir soluciones reales de **AIOps** en Google Cloud.

---

## 📚 Índice
- [Objetivo general](#objetivo-general)
- [Resultados de aprendizaje](#resultados-de-aprendizaje)
- [Alcance del proyecto final](#alcance-del-proyecto-final)
- [Tecnologías y herramientas](#tecnologías-y-herramientas)
- [Requisitos previos](#requisitos-previos)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Puesta en marcha rápida](#puesta-en-marcha-rápida)
- [Laboratorios (roadmap)](#laboratorios-roadmap)
- [Convenciones](#convenciones)
- [Métricas de éxito](#métricas-de-éxito)
- [Soporte y dudas](#soporte-y-dudas)
- [Licencia](#licencia)

---

## Objetivo general
Diseñar, implementar y operar **soluciones de AIOps** en GCP que reduzcan **MTTR**, anticipen incidencias y optimicen **costes**, aprovechando **Vertex AI**, **Cloud Monitoring/Logging** y **automatizaciones**.

---

## Resultados de aprendizaje
Al finalizar, podrás:

1. **Modelar y desplegar** predictores (incidencias/anomalías) con **Vertex AI** (AutoML y modelos custom).
2. **Orquestar** pipelines de ML/ETL con **Vertex Pipelines**, **Dataflow** y **Cloud Composer**.
3. **Ingerir/normalizar logs** con **Cloud Logging** y eventos vía **Pub/Sub** para análisis casi en tiempo real.
4. **Detectar anomalías** en métricas integrando **Cloud Monitoring** con modelos de IA.
5. Diseñar **dashboards** y **alertas inteligentes** priorizadas por impacto.
6. **Automatizar remediaciones** con **Cloud Functions** (runbooks codificados).
7. Aplicar **MLOps**: versionado, monitoreo de drift, CI/CD y evaluación continua.
8. Integrar AIOps en **DevOps/SRE** (post-deploy checks, rollback asistido por señal).
9. **Optimizar costes** con predicción y alertas (Billing + BigQuery/Vertex).
10. Usar **IA generativa** para resúmenes de incidentes y documentación técnica.

---

## Alcance del proyecto final
Construcción de una solución **end-to-end** que incluya:

- Ingesta de datos en **BigQuery/Vertex**  
- Entrenamiento y **despliegue** de modelo  
- Integración con **Monitoring/Logging**  
- **Auto-remediación** con Cloud Functions  
- **Dashboard** operativo y de negocio  
- **KPIs**: MTTR, disponibilidad, coste vs. línea base

---

## Tecnologías y herramientas

**Google Cloud (core)**
- **Vertex AI** (Datasets, Training, Endpoints, **Pipelines**, GenAI Studio)
- **BigQuery** / **BigQuery ML**
- **Cloud Monitoring** & **Cloud Logging**
- **Pub/Sub**, **Dataflow**, **Cloud Functions**, **Cloud Composer**
- **Billing** (Export a BigQuery, Reports)
- *(Opcional)* **Chronicle Security**

**Observabilidad & ecosistema**
- **Prometheus** / **Grafana** (integrado con GCP)

**Local/Dev**
- **Python 3.10+**, **Jupyter/Colab**, **Docker**, **Git**, **gcloud CLI**
- Editor recomendado: **VS Code**

---

## Requisitos previos

- Proyecto de **GCP** dedicado con APIs habilitadas: Vertex AI, BigQuery, Monitoring, Logging, Pub/Sub, Dataflow, Composer, Cloud Functions, Billing.
- Permisos para crear datasets, jobs y endpoints en Vertex; lectura/escritura en BigQuery; uso de Pub/Sub y Dataflow.
- **Dataset de ejemplo** o acceso a fuentes de logs/métricas de demo.
- Equipo con **≥16 GB RAM**, **Docker** y buena conexión.
- Cuenta de videoconferencia (Zoom) operativa; ideal **2 pantallas**.

---

## Estructura del repositorio

```text
/labs/                # notebooks y ejercicios guiados
/pipelines/           # DAGs de Composer y Vertex Pipelines
/functions/           # funciones de auto-remediación (Cloud Functions)
/infra/               # infraestructura como código (opcional)
/datasets/            # datos de ejemplo (si procede)
/dashboards/          # definiciones de dashboards/alertas
/docs/                # guías, runbooks y resúmenes
```

---

## Puesta en marcha rápida

```bash
# 1) Clonar el repositorio
git clone <tu-repo> && cd <tu-repo>

# 2) Autenticarse y seleccionar proyecto
gcloud auth login
gcloud config set project <ID_DE_TU_PROYECTO>

# 3) (Opcional) Crear entorno Python
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 4) Habilitar APIs necesarias
gcloud services enable aiplatform.googleapis.com \
  bigquery.googleapis.com monitoring.googleapis.com \
  logging.googleapis.com pubsub.googleapis.com \
  dataflow.googleapis.com composer.googleapis.com \
  cloudfunctions.googleapis.com

---

## Distribución de contenido


Las clases estaran distribuidas de la seguiente manera.

Sesión 1: Tema 1 - DONE

Sesión 2: Tema 2 - DONE

Sesión 3: Tema 3 

Sesión 4: Tema 4, Tema 5

Sesión 5: Tema 6, Tema 7

Sesión 6: Tema 8, Tema 9

Sesión 7: Tema 10, Tema 11

Sesión 8: Tema 12

Sesión 9: Tema 13

Sesión 10: Tema 14