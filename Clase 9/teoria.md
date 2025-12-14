# Tema 13: Gobernanza y Buenas Prácticas en AIOps con Vertex AI

Este documento desarrolla el **Tema 13 – Gobernanza y Buenas Prácticas en AIOps** del temario del curso “AIOps con Vertex AI: Automatización, Predicción y Observabilidad Inteligente en Google Cloud”.

El foco está en cómo **diseñar, gobernar y operar** soluciones de AIOps basadas en **Vertex AI, BigQuery, Cloud Logging y Cloud Monitoring** en entornos de **IT Operations y SRE**.

---

## 1. ¿Qué es la gobernanza en AIOps y por qué importa?

La **gobernanza en AIOps** es el conjunto de políticas, procesos, roles y controles que aseguran que el uso de IA en operaciones:

- Sea **seguro**, **auditado** y **alineado con los objetivos del negocio**.
- Respete **normativa, seguridad y privacidad** de datos (por ejemplo, logs con información sensible).
- Sea **sostenible** en términos de costes y esfuerzo operativo.
- No degrade la **fiabilidad del servicio** (SLOs, SLAs) por automatizaciones mal diseñadas.

En AIOps, las decisiones del modelo pueden:

- **Disparar alertas** (p. ej. detección de anomalías en métricas de CPU/RAM).
- **Crear tickets de incidente** de forma automática.
- **Ejecutar acciones de auto-remediación** (escalar pods, reiniciar servicios, bloquear IPs sospechosas, etc.).

Sin una buena gobernanza se corre el riesgo de:

- **Alertas masivas falsas** que saturan a los SRE.
- Acciones automáticas que **empeoran una incidencia** (reinicios en cascada, escalado incontrolado).
- **Incumplimiento normativo** (ej. usar datos de logs con información personal sin control).
- **Costes descontrolados** por modelos y pipelines de Vertex AI mal gestionados.

Gobernanza es, en resumen, **poner orden, responsabilidad y trazabilidad** encima de la automatización inteligente.

---

## 2. Definición de roles y responsabilidades en AIOps

Una solución de AIOps en GCP con Vertex AI no es solo un modelo; es una combinación de:

- Infraestructura (GKE, Compute Engine, Cloud Run).
- Observabilidad (Cloud Monitoring, Cloud Logging, Trace).
- Datos (BigQuery, Pub/Sub, Dataflow).
- Modelos (Vertex AI, BigQuery ML).

Para operarla correctamente, se recomienda definir **roles claros**:

### 2.1 Roles típicos

- **SRE Lead / Responsable de Fiabilidad**
  - Define **SLOs/SLIs** y cómo AIOps ayuda a cumplirlos.
  - Prioriza qué incidentes y métricas se abordan con IA (disponibilidad, latencia, errores, saturación de recursos).

- **Plataform Engineer / DevOps**
  - Diseña y mantiene la **plataforma de ejecución**:
    - GKE, Cloud Run, redes, seguridad.
    - Integraciones con Cloud Monitoring / Logging.
  - Implementa la **automatización** (Cloud Functions, Cloud Run, Cloud Composer, Pub/Sub).

- **Data Engineer**
  - Diseña los **pipelines de datos**:
    - Exportación de logs a BigQuery.
    - Procesamiento con Dataflow.
    - Estructuración de features para modelos de Vertex AI.

- **ML Engineer / MLOps Engineer**
  - Diseña, entrena y despliega los **modelos de AIOps**:
    - Detección de anomalías, predicción de saturación de CPU/RAM, etc.
  - Configura **Vertex Pipelines**, Model Registry, endpoints, monitorización de modelos.

- **Security / Compliance Officer**
  - Valida que el uso de datos (logs, métricas, trazas) cumple:
    - Normativa de privacidad.
    - Políticas internas de seguridad.
  - Revisa automatizaciones con impacto en seguridad (p. ej. bloqueo automático de IPs).

- **Product Owner de Operaciones / IT Service Owner**
  - Prioriza los **casos de uso de AIOps** (reducción de MTTR, ahorro de costes, etc.).
  - Valida el **valor aportado** por los modelos (KPIs de negocio y operación).

### 2.2 Matriz RACI simplificada

Para cada flujo de AIOps (por ejemplo, “Detección de anomalías en métricas de CPU de GKE”):

- **R (Responsable)**: quién configura Cloud Monitoring, BigQuery y Vertex AI.
- **A (Aprobador)**: quién decide la puesta en producción de un modelo.
- **C (Consultado)**: SREs que operan el servicio objetivo.
- **I (Informado)**: stakeholders de negocio y seguridad.

Una gobernanza madura documenta esta matriz por **caso de uso** de AIOps.

---

## 3. Documentación de flujos de AIOps

La documentación es clave para que SRE, DevOps, data y ML hablen el mismo idioma.

### 3.1 Qué documentar

Para cada flujo de AIOps:

1. **Diagrama de arquitectura**
   - Ejemplo típico:
     - Cloud Logging → Sink a Pub/Sub → Dataflow → BigQuery → Vertex AI (entrenamiento) → Vertex Endpoint → Cloud Monitoring alert → Cloud Functions (auto-remediación).

2. **Flujo funcional**
   - ¿Qué evento inicia el flujo?
   - ¿Qué datos se usan (logs, métricas, trazas)?
   - ¿Qué modelo se ejecuta en Vertex AI?
   - ¿Qué salida genera (score, etiqueta de anomalía, tipo de incidente)?
   - ¿Qué acción se dispara (ticket, alerta, runbook, remediación)?

3. **Runbooks y playbooks**
   - Runbook: instrucciones paso a paso para el SRE cuando:
     - El modelo falla.
     - El endpoint de Vertex AI no responde.
     - La automatización genera errores.
   - Playbook: acciones estándar ante una incidencia detectada por AIOps
     (ej. “anomalía de latencia en el servicio auth”).

4. **Requisitos de datos**
   - Retención en BigQuery.
   - Frecuencia de refresco.
   - Campos obligatorios (labels de logs, métricas custom, etc.).

### 3.2 Beneficios

- Facilita **onboarding de nuevos SRE y DevOps**.
- Acelera el **troubleshooting** cuando un modelo toma decisiones erróneas.
- Permite **auditar** qué hace exactamente cada automatización.

---

## 4. Políticas internas de uso de IA en operaciones

La organización debe definir **límites claros** al uso de IA en producción.

### 4.1 Tipos de políticas

1. **Acciones permitidas sin intervención humana**
   - Ajustes conservadores:
     - Aumentar réplicas de un deployment dentro de un rango limitado.
     - Incrementar el tamaño del pool de nodos dentro de un presupuesto.
   - Apertura de tickets en el sistema de ITSM.
   - Notificaciones en Slack/Teams.

2. **Acciones que requieren aprobación humana (“human-in-the-loop”)**
   - Reinicios masivos de pods o servicios críticos.
   - Cambios de configuración de red o seguridad (firewalls, reglas IAM).
   - Despliegues de nuevos modelos o cambios de umbrales críticos.

3. **Acciones prohibidas o altamente restringidas**
   - Cualquier acción que pueda violar políticas de seguridad o compliance.
   - Modificaciones de datos de negocio o de usuarios finales.

4. **Política de datos**
   - Qué datos de logs y métricas se pueden usar para entrenar modelos.
   - Cómo se anonimizan o pseudonimizan campos sensibles.
   - Cómo se gestiona la retención de datos en BigQuery.

### 4.2 Registro y trazabilidad

- Todas las acciones automáticas disparadas por AIOps deben:
  - Quedar registradas en **Cloud Logging**.
  - Etiquetarse con:
    - ID del modelo.
    - Versión del pipeline.
    - Score o explicación de la decisión (cuando sea posible).
- Esto facilita **auditorías internas y externas**.

---

## 5. Control de versiones de modelos y pipelines

En AIOps, los modelos cambian con el tiempo: nuevas features, nuevos rangos de carga, nuevas arquitecturas.

### 5.1 Versionado de modelos en Vertex AI

- Uso del **Vertex AI Model Registry**:
  - Registrar cada versión de modelo con:
    - Nombre del caso de uso (ej. `cpu_anomaly_detector_auth`).
    - Versión (`v1`, `v2`, `v3`).
    - Metadatos:
      - Rango de fechas de entrenamiento (logs/métricas).
      - SLOs objetivo.
      - Métricas de evaluación (precision, recall, F1).

- Estrategias de despliegue:
  - **Blue/Green**: endpoints separados para modelo actual y modelo nuevo.
  - **Canary**: porcentaje de tráfico (alertas/incidentes) evaluados por el modelo nuevo.

### 5.2 Versionado de pipelines

- Pipelines de:
  - Ingesta y transformación de datos (Dataflow, Composer).
  - Entrenamiento (Vertex Pipelines).
  - Deploy y actualización de endpoints.

- Buenas prácticas:
  - Definir pipelines como **código** (Infra as Code + Pipeline as Code).
  - Almacenarlos en **Git** (GitHub, GitLab, Cloud Source Repositories).
  - Versionar:
    - Esquema de features.
    - Hiperparámetros.
    - Configuraciones de alertas.

Esto permite reproducir exactamente el **estado de un sistema AIOps** en un punto del tiempo.

---

## 6. Estrategias de mejora continua en AIOps

La mejora continua es el corazón de SRE y debe extenderse a AIOps.

### 6.1 Ciclo de feedback

1. El modelo de AIOps detecta una anomalía o predice un incidente.
2. Se genera un ticket o alerta.
3. El SRE:
   - Confirma si era un **verdadero incidente** o un **falso positivo**.
4. Esa etiqueta se almacena (por ejemplo en BigQuery).
5. Periódicamente, se **reentrena** el modelo con:
   - Nuevos datos.
   - Etiquetas de validación humana.

### 6.2 Métricas de mejora continua

- Métricas de modelo:
  - Tasa de falsos positivos (alertas que no eran problemas).
  - Tasa de falsos negativos (incidentes no detectados).
- Métricas de operaciones:
  - Reducción de **MTTR** gracias a AIOps.
  - Reducción del número de **incidentes críticos**.
  - Disminución de **alert fatigue**.

### 6.3 Automatización del ciclo

- Uso de:
  - **Cloud Scheduler** o **Cloud Composer** para lanzar reentrenamientos periódicos.
  - **Vertex Pipelines** para:
    - Evaluar el modelo nuevo.
    - Compararlo con el modelo en producción.
    - Rechazar automáticamente modelos peores.

La gobernanza define **cada cuánto** se revisan modelos, quién aprueba cambios y qué criterios se exigen para promocionar una nueva versión.

---

## 7. Supervisión de costes y beneficios en AIOps

La IA en operaciones tiene coste: entrenamiento, inferencia, almacenamiento de datos. La gobernanza debe asegurar que el valor generado compensa ese coste.

### 7.1 Costes a controlar

- **Vertex AI**
  - Entrenamientos (GPU/TPU, CPUs).
  - Inferencias en endpoints online.
- **BigQuery**
  - Almacenamiento de logs/métricas.
  - Coste de consultas de entrenamiento y análisis.
- **Dataflow, Pub/Sub, Cloud Composer**
  - Procesamiento continuo de eventos.

### 7.2 Beneficios esperados

- Reducción de:
  - MTTR.
  - Número de incidentes críticos.
  - Tiempo empleado por SRE y NOC en tareas repetitivas.
- Aumento de:
  - Disponibilidad del servicio (uptime).
  - Estabilidad durante picos de tráfico.

### 7.3 KPIs financieros y operativos

Ejemplos de KPIs:

- “El sistema de predicción de saturación de CPU reduce en un 30 % el número de incidentes por overload”.
- “El sistema de detección de anomalías en logs reduce en un 40 % el tiempo medio de detección (MTTD)”.

La gobernanza debe exigir **revisiones periódicas de ROI** y permitir **apagar modelos** que no aporten suficiente valor.

---

## 8. Gestión del ciclo de vida de modelos de AIOps

La **gestión del ciclo de vida (ML lifecycle)** incluye:

1. **Diseño del caso de uso**
   - Ejemplo: “Detectar anomalías en la latencia p95 del API de autenticación”.
2. **Recopilación y preparación de datos**
   - Exportar métricas de Cloud Monitoring a BigQuery.
   - Crear features en Dataform/Dataflow.
3. **Entrenamiento y validación**
   - Usar Vertex AI (AutoML o modelos custom).
   - Definir métricas objetivo (ej. F1-score en detección de anomalías).
4. **Despliegue en producción**
   - Endpoints en Vertex AI.
   - Integración con Cloud Monitoring / Functions.
5. **Monitorización del modelo**
   - Data drift (distribución de métricas de entrada).
   - Degradación del rendimiento del modelo.
6. **Reentrenamiento**
   - Por tiempo (mensual, trimestral) o por umbral (drift alto, caída de métricas).
7. **Retirada y archivado**
   - Retirar modelos obsoletos.
   - Documentar los motivos.
   - Mantener artefactos por motivos regulatorios.

La gobernanza debe definir **políticas claras** para cada fase.

---

## 9. Auditoría de resultados en AIOps

La auditoría busca responder a preguntas como:

- “¿Por qué el sistema de AIOps ejecutó esta acción?”
- “¿Qué versión de modelo y pipeline estaba en producción en ese momento?”
- “¿Qué datos se usaron para entrenar ese modelo?”

### 9.1 Requerimientos de auditoría

- **Trazabilidad completa**:
  - De la acción ejecutada → alerta o ticket → decisión del modelo → versión del modelo → dataset de entrenamiento.

- **Logs estructurados**:
  - Cada decisión del modelo registrada en Cloud Logging con:
    - `model_name`, `model_version`.
    - `input_summary` (resumen, no datos sensibles).
    - `score` o etiqueta de salida.
    - Acción elegida (alerta, ticket, remediación).
    - Resultado de la acción (éxito/fallo).

- **Informes periódicos**:
  - Número de acciones automáticas.
  - Porcentaje de acciones revertidas por humanos.
  - Incidentes relacionados con errores de AIOps.

### 9.2 Herramientas útiles

- BigQuery para análisis histórico de:
  - Decisiones de modelos.
  - Acciones ejecutadas.
- Dashboards en Cloud Monitoring / Looker Studio para:
  - Visibilidad de la “salud” de los modelos de AIOps.

---

## 10. Checklist de gobernanza corporativa en AIOps

Ejemplo de checklist que tus alumnos pueden usar en sus proyectos:

| Dimensión                  | Pregunta clave                                                                 | Estado (Sí/No/Parcial) | Responsable principal     |
|---------------------------|-------------------------------------------------------------------------------|------------------------|---------------------------|
| Roles                     | ¿Hay roles definidos (SRE, DevOps, Data, ML, Seguridad) para este caso AIOps? |                        | SRE Lead                  |
| Datos                     | ¿Los datos de logs/métricas cumplen las políticas de privacidad y retención?  |                        | Data Engineer / Security  |
| Modelos                   | ¿El modelo está registrado y versionado en Vertex AI Model Registry?          |                        | ML Engineer               |
| Automatizaciones          | ¿Están documentadas las acciones automáticas y sus límites?                   |                        | DevOps / Platform         |
| Seguridad y Compliance    | ¿Existe revisión de seguridad para las acciones de AIOps?                     |                        | Security Officer          |
| Costes                    | ¿Se monitorizan los costes de entrenamiento e inferencia?                     |                        | FinOps / Platform         |
| Documentación             | ¿Hay diagramas, runbooks y playbooks actualizados?                            |                        | SRE / DevOps              |
| Monitorización de modelos | ¿Se monitoriza el rendimiento y drift de los modelos?                         |                        | MLOps                     |
| Auditoría                 | ¿Se registran todas las decisiones y acciones para auditoría?                 |                        | SRE / Security            |
| Mejora continua           | ¿Existen ciclos de feedback y retraining planificados?                        |                        | ML Engineer / SRE         |

Este checklist puede usarse como **plantilla práctica** durante sesiones de laboratorio.

---

## 11. Casos de fallo y aprendizajes en AIOps

### Caso 1: Autoescalado agresivo por predicción de carga

- **Contexto**:
  - Modelo en Vertex AI predice picos de CPU en un clúster GKE.
  - Automatización escala el número de nodos de forma agresiva.
- **Problema**:
  - El modelo sobreestima la carga.
  - El clúster escala por encima de lo necesario.
  - Resultado: **sobrecoste elevado** sin mejora real de SLO.
- **Fallo de gobernanza**:
  - No había límites máximos de escalado.
  - No existían revisiones periódicas de coste-beneficio del modelo.
- **Aprendizaje**:
  - Definir **umbrales y límites duros** en automatizaciones.
  - Revisar periódicamente el **ROI del caso de uso**.

### Caso 2: Modelo de anomalías desactualizado

- **Contexto**:
  - Modelo de detección de anomalías en latencia de un API.
  - La arquitectura del servicio cambia (nueva versión, nuevo patrón de tráfico).
- **Problema**:
  - El modelo fue entrenado con datos antiguos.
  - Disminuye la capacidad de detectar incidentes reales.
  - Se producen **incidentes que el modelo no ve**.
- **Fallo de gobernanza**:
  - No existía política de **reentrenamiento** clara.
  - No se monitorizaba el rendimiento del modelo.
- **Aprendizaje**:
  - Definir **frecuencia mínima de revisión y reentrenamiento**.
  - Monitorizar métricas específicas del modelo en producción.

### Caso 3: Automatización sin “circuit breaker” operativo

- **Contexto**:
  - Sistema AIOps que reinicia pods cuando detecta un patrón de error en logs.
- **Problema**:
  - Bug en la lógica de detección del modelo.
  - Se reinician pods sanos durante una incidencia de red.
  - Se genera un **efecto cascada** que agrava la indisponibilidad.
- **Fallo de gobernanza**:
  - Falta de “circuit breaker” para desactivar automatización en caso de anomalía.
  - No existía un proceso rápido de rollback de automatizaciones.
- **Aprendizaje**:
  - Toda automatización crítica debe tener:
    - **Mecanismo de desactivación rápida** (flag, config).
    - **Monitorización específica** de su impacto.
    - **Runbook** claro para revertir cambios.

---

## 12 FIN


Examen: (https://forms.gle/jNkYyoK1iMpUayvp7)

FeedBack: (https://imagina-formacion.typeform.com/to/IkO83DnN)