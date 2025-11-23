# Tema 3 — Observabilidad Inteligente con Google Cloud (Teoría)

> Curso: **AIOps con Vertex AI: Automatización, Predicción y Observabilidad Inteligente en Google Cloud**  
> Módulo: **Tema 3 – Observabilidad Inteligente con GCP**  
> Propósito: Comprender la observabilidad moderna en Google Cloud, cómo instrumentar señales, construir tableros, crear alertas avanzadas, exportar datos para análisis y aplicar IA para detección de anomalías y capacidades predictivas.

---

## 1) Observabilidad: más allá del monitoreo
- **Monitoreo** responde: *¿está bien o mal?* mediante métricas y umbrales.  
- **Observabilidad** responde: *¿por qué está mal?* permitiendo inferir el estado interno de un sistema a partir de sus salidas (**logs**, **métricas**, **trazas**) y **contexto** (labels, metadatos, topología).
- Pilares clásicos (“**las tres señales**”):
  - **Métricas**: valores numéricos agregados y etiquetados (latencia, RPS, CPU…).
  - **Logs**: eventos detallados y textos estructurados/semi-estructurados.
  - **Trazas**: seguimiento distribuido de solicitudes (spans) a través de servicios.
- Objetivo último: **reducir MTTR**, aumentar **disponibilidad** y **predecir** degradaciones.

---

## 2) Stack nativo de Observabilidad en Google Cloud
- **Cloud Monitoring**: métricas, SLO/SLI, alertas (incluye MQL), dashboards y canales de notificación.
- **Cloud Logging**: ingesta, consulta, *log-based metrics*, enrutamiento (Log Router) y *sinks*.
- **Cloud Trace**: trazas distribuidas, dependencia entre servicios y *latency analysis*.
- **Cloud Profiler**: perfiles de CPU/memoria/bloqueo para optimización de rendimiento.
- **Error Reporting**: agregación y deduplicación de excepciones.
- **Ops Agent / OpenTelemetry**: agentes para VMs, contenedores y exportación de señales.
- **Managed Service for Prometheus**: scrape nativo y compatibilidad con ecosistema Prometheus.
- **Integraciones**: Pub/Sub, BigQuery, Dataflow para *pipelines* de análisis/ML.

> **Idea clave**: diseñar un **plano de observabilidad** con etiquetas/labels coherentes (proyecto, servicio, versión, entorno, región) y convenciones de nombres.

---

## 3) Métricas clave en infraestructura y aplicaciones
- **Infraestructura (método USE)**: *Utilización*, *Saturación*, *Errores* por recurso (CPU, memoria, disco, red).
- **Aplicaciones (método RED)**: *Rate*, *Errors*, *Duration* por endpoint/servicio.
- **SLIs** típicos: disponibilidad (uptime), latencia (p50/p90/p99), tasa de errores, *freshness* de jobs.
- **SLOs**: objetivos cuantitativos con presupuestos de error. Alinee SLO ↔ alertas ↔ runbooks.
- **Cardinalidad**: cuide etiquetas para evitar series excesivas y costos innecesarios.

---

## 4) Alertas avanzadas en Cloud Monitoring
- Tipos de condición:
  - **Umbral** (estático/dinámico), **ausencia de datos**, **cambio de tendencia**, **ratio** (errores/total), **percentiles** y **condiciones compuestas**.
- Ventanas de evaluación y **horizontes** (ej.: 5m/15m) para estabilidad vs. sensibilidad.
- **Deduplicación** y **notificación** por canales (email, Slack, Webhook, PagerDuty).  
- **Runbooks** y **anotaciones**: cada alerta debe enlazar pasos de diagnóstico/remediación.
- **MQL** (Monitoring Query Language) permite consultas expresivas. *Ejemplo conceptual*:
  ```
  fetch gce_instance
  | metric 'agent.googleapis.com/cpu/utilization'
  | filter (metadata.system_labels.topology_region = 'europe-west1')
  | group_by 5m, [value_utilization_aggregate: mean(value.utilization)]
  | condition gt(val(), 0.8) for 15m
  ```
- **Anti‑patrones**: “alerta por todo”, umbrales estáticos sin estacionalidad, ausencia de severidades.

---

## 5) Trazas y *profiling* para aplicaciones
- **Trace**: instrumente spans con IDs, tiempos y atributos (cliente, versión, endpoint).  
  - Beneficios: mapas de dependencia, *hot paths*, *tail latency*.
- **Profiler**: perfiles continuos con bajo overhead; base para decisiones de optimización.
- Buenas prácticas: muestreo adaptativo, *context propagation*, etiquetas de despliegue.

---

## 6) Exportación de datos a BigQuery para análisis avanzado
- **Log Router** → **Sinks** a **BigQuery** para almacenamiento analítico/SQL.  
- **Particionado** por tiempo de ingesta y **clustering** (servicio, severidad) para coste/rendimiento.
- Combinar **logs + métricas + metadatos** para *root cause analysis* y *capacity planning*.
- Usos: *forensics*, auditoría, *postmortems*, *cost allocation*, entrenamiento de modelos.
- Gobierno: retención, clasificación por sensibilidad, *data catalog* y control de acceso IAM.

---

## 7) Dashboards personalizados en Cloud Monitoring
- Diseñe por **objetivo** (SLOs, latencia, errores, saturación) y por **audiencia** (NOC, dev, negocio).
- Widgets útiles: *time series*, *heatmaps*, *top‑N*, *service map*, paneles de despliegue.
- **Higiene visual**: jerarquía, contexto (líneas objetivo/SLO), periodos comparativos, anotaciones.
- Reutilice plantillas por proyecto/entorno; mantenga **versionado** (IaC) de paneles.

---

## 8) Integración con herramientas de terceros
- **Grafana**: visualización avanzada, *provisioning* y *alerting* (cuando aplique).
- **Prometheus**: *scrape* de *exporters*, reglas y *recording rules*; opción gestionada en GCP.
- Consideraciones: SSO/identidad, *multi‑tenancy*, costos, latencia entre planos de datos/control.

---

## 9) IA aplicada a detección de anomalías
- **Enfoques**:
  - **Univariado** (ej.: *seasonal decomposition* + puntaje de anomalía).
  - **Multivariado** (correlación entre métricas; p.ej. latencia + errores + saturación).
  - **Supervisado** vs **no supervisado** (cuando no hay etiquetas).
- **Retos**: estacionalidad, *drift*, cardinalidad, *alert gating* para reducir falsos positivos.
- **Arquitectura tipo**: Monitoring/Logging → Export (Pub/Sub/BigQuery) → *Feature Store* → **Vertex AI / BigQuery ML** → *scoring* en línea (*alert enrichment*) → canal de alerta.
- **Gobierno**: versionado, *model monitoring*, *feedback loop* y evaluación coste‑beneficio.

---

## 10) Casos prácticos de observabilidad predictiva
1. **Prevención de saturación**: forecasting de CPU/pods → *scale out* preventivo.
2. **Degradación de latencia p95**: correlación con *error rate* + cambios recientes de *deploy*.
3. **Anomalías en logs**: picos de HTTP 5xx por servicio/versión/cluster.
4. **Capacidad de almacenamiento**: tendencia de uso de disco/objetos y umbrales dinámicos.
5. **Detección temprana en CI/CD**: *canary* con SLOs y *rollback* automatizado.

---

## 11) Buenas prácticas y anti‑patrones
**Buenas prácticas**
- Definir **SLIs/SLOs** por servicio y enlazarlos a alertas y *runbooks*.
- Etiquetado/labels consistente (servicio, entorno, región, versión, equipo).
- Limitar cardinalidad y retener lo necesario; estimar costos desde el diseño.
- Mapear dependencias (topología) y anotar cambios (deploys/incidentes).
- *Postmortems* sin culpa y aprendizaje continuo; *SRE error budget*.

**Anti‑patrones**
- Paneles repletos sin jerarquía; alertas ruidosas sin severidad.
- Logs sin estructura; ausencia de corrección de *noise* (muestreo, agregación).
- Métricas sin contexto (sin labels de despliegue) → difícil *root cause analysis*.

---

## 12) FIN

Examen: https://forms.gle/a45asjaLCVHx9NYCA
FeedBack: (https://imagina-formacion.typeform.com/to/IkO83DnN)

---

## Glosario corto
- **SLI/SLO/SLA**: Indicador / objetivo / acuerdo de servicio.
- **MQL**: Lenguaje de consultas de Monitoring.
- **Span**: unidad mínima de traza distribuida.
- **RED/USE**: Métodos prácticos para seleccionar métricas clave.
- **Cardinalidad**: cantidad de series distintas por combinación de etiquetas.

---

## Recursos sugeridos
- Documentación de Cloud Operations (Monitoring, Logging, Trace, Profiler, Error Reporting). https://docs.cloud.google.com/monitoring/docs
- Guías de OpenTelemetry y Managed Service for Prometheus en GCP.
- Diseño de SLOs y prácticas SRE aplicadas a observabilidad.  https://docs.cloud.google.com/stackdriver/docs/solutions/slo-monitoring/ui/create-slo