# Temas 10 y 11 – AIOps con Vertex AI en Google Cloud  
Gestión de costes, seguridad y cumplimiento para Operaciones y SRE 

---

## Índice

- [Tema 10 – Gestión de costes con AIOps](#tema-10--gestión-de-costes-con-aiops)
  - [10.1. Costes como problema de SRE y Operaciones](#101-costes-como-problema-de-sre-y-operaciones)
  - [10.2. Optimización de recursos cloud con IA](#102-optimización-de-recursos-cloud-con-ia)
  - [10.3. Predicción de costes en Google Cloud](#103-predicción-de-costes-en-google-cloud)
  - [10.4. Modelos para estimar consumos futuros](#104-modelos-para-estimar-consumos-futuros)
  - [10.5. Automatización de apagado de recursos ociosos](#105-automatización-de-apagado-de-recursos-ociosos)
  - [10.6. Análisis de gasto con BigQuery y Vertex AI](#106-análisis-de-gasto-con-bigquery-y-vertex-ai)
  - [10.7. Identificación de ineficiencias en proyectos](#107-identificación-de-ineficiencias-en-proyectos)
  - [10.8. Integración con Billing Reports de GCP](#108-integración-con-billing-reports-de-gcp)
  - [10.9. Simulaciones de escenarios de costes](#109-simulaciones-de-escenarios-de-costes)
  - [10.10. Alertas de sobrecostes basadas en IA](#1010-alertas-de-sobrecostes-basadas-en-ia)
  - [10.11. Buenas prácticas en optimización financiera](#1011-buenas-prácticas-en-optimizacion-financiera)
- [Tema 11 – Seguridad y cumplimiento en AIOps](#tema-11--seguridad-y-cumplimiento-en-aiops)
  - [11.1. Seguridad como requisito en AIOps](#111-seguridad-como-requisito-en-aiops)
  - [11.2. Riesgos de seguridad en automatización](#112-riesgos-de-seguridad-en-automatización)
  - [11.3. Cumplimiento normativo en entornos cloud](#113-cumplimiento-normativo-en-entornos-cloud)
  - [11.4. Control de accesos en Vertex AI y GCP](#114-control-de-accesos-en-vertex-ai-y-gcp)
  - [11.5. Monitorización y auditorías automáticas](#115-monitorización-y-auditorías-automáticas)
  - [11.6. Uso de IA para detectar amenazas internas](#116-uso-de-ia-para-detectar-amenazas-internas)
  - [11.7. Integración con Chronicle Security](#117-integración-con-chronicle-security)
  - [11.8. Casos de uso de IA en ciberseguridad para ITOps/SRE](#118-casos-de-uso-de-ia-en-ciberseguridad-para-itopssre)
  - [11.9. Estrategias de segmentación y roles](#119-estrategias-de-segmentación-y-roles)
  - [11.10. Checklist de seguridad en AIOps](#1110-checklist-de-seguridad-en-aiops)
  - [11.11. Buenas prácticas de compliance en GCP](#1111-buenas-prácticas-de-compliance-en-gcp)

---

## Tema 10 – Gestión de costes con AIOps

### 10.1. Costes como problema de SRE y Operaciones

En un entorno cloud como Google Cloud, **el coste es una métrica operacional más**, igual que la latencia, el error rate o la disponibilidad. Para SRE y equipos de Operaciones, gestionar costes no es solo un tema de finanzas:

- Impacta directamente en las decisiones de capacidad (capacity planning).
- Afecta a los SLO de negocio (por ejemplo, mantener un coste máximo por transacción).
- Puede revelar **ineficiencias operativas**, como exceso de logs, máquinas sobredimensionadas o recursos olvidados.

AIOps introduce la posibilidad de **tratar el coste como un “signal” más de observabilidad**, usando IA para:

- Detectar patrones de gasto inesperados (anomalías de coste).
- Predecir picos de consumo antes de que ocurran.
- Automatizar acciones correctivas (apagado de entornos, cambio de tamaños de máquina, reducción de niveles de logging, etc.).

Vertex AI se convierte aquí en el motor donde entrenamos y desplegamos estos modelos de predicción y detección.

---

### 10.2. Optimización de recursos cloud con IA

La optimización de recursos busca **mantener el equilibrio entre coste y rendimiento**:

- Infraestructura sobredimensionada → coste alto, pero servicios estables.
- Infraestructura infradimensionada → coste bajo, pero riesgo de incumplir SLO.

Con AIOps, podemos usar IA para:

1. **Analizar métricas históricas** (CPU, RAM, conexiones, QPS) desde Cloud Monitoring.
2. **Relacionarlas con eventos operativos** (deploys, incidentes, picos de tráfico).
3. **Recomendar configuraciones óptimas**:
   - Tipo de máquina ideal para un deployment.
   - Número de réplicas mínimo/máximo en un cluster GKE.
   - Niveles de logging o sampling para trazas.

**Ejemplo conceptual**:
- Ingestar métricas de CPU y QPS a BigQuery.
- Entrenar un modelo de regresión en Vertex AI que estime el uso de CPU en función de QPS y hora del día.
- A partir de ese modelo, derivar recomendaciones automáticas de “tamaño mínimo de pool” para un servicio de backend.

El objetivo es que las decisiones de dimensionamiento de recursos **dejen de ser manuales o basadas solo en intuición** y pasen a estar guiadas por modelos.

---

### 10.3. Predicción de costes en Google Cloud

Google Cloud permite exportar la facturación (Billing Export) a BigQuery. A partir de esta tabla, podemos usar AIOps para:

- **Predecir el coste diario/mensual** por:
  - Proyecto.
  - Servicio (Compute Engine, GKE, BigQuery, Cloud Logging, etc.).
  - Etiqueta (equipo, entorno: `env=prod|staging`).

Flujo típico:

1. **Exportar facturación a BigQuery** (Billing Export).
2. Crear **vistas agregadas** (coste diario por proyecto, servicio, equipo).
3. Entrenar un modelo de predicción:
   - En BigQuery ML o en Vertex AI (regresión, modelos de series temporales).
4. Desplegar el modelo como **endpoint en Vertex AI** o como job batch:
   - Endpoint para obtener predicciones “on demand” (por ejemplo, vía Cloud Functions).
   - Batch para generar predicciones diarias en una tabla BigQuery.

Esto permite que el equipo de SRE tenga **paneles de coste futuro** y pueda anticipar:

- Si se va a romper un presupuesto.
- Si el coste por servicio se está disparando comparado con la tendencia esperada.

---

### 10.4. Modelos para estimar consumos futuros

Además del coste, es clave predecir **consumos de recursos**:

- CPU promedio y picos.
- RAM utilizada.
- Almacenamiento (discos, buckets, tablas BigQuery).
- Tráfico de red (ingress/egress).

Tipos de problemas de ML aquí:

- **Series temporales**: predicción del valor futuro de una métrica (por ejemplo, coste o CPU diaria).
- **Regresión multivariable**: estimar recursos en función de señales como QPS, tipo de request, país, etc.

¿Por qué es útil para SRE?

- Mejora el **capacity planning**.
- Permite diseñar **SLO financieros**: coste máximo esperado para una carga específica.
- Ayuda a decidir:
  - Si migrar a otro tipo de máquina.
  - Si dejar de usar un servicio caro a favor de uno más eficiente.

Vertex AI aporta:

- Infraestructura gestionada para entrenar a gran escala.
- Administración de versiones de modelos y datasets.
- Integración con BigQuery y Cloud Storage para manejar grandes volúmenes de datos de métricas y facturación.

---

### 10.5. Automatización de apagado de recursos ociosos

Uno de los casos más directos de AIOps en costes es **detectar y apagar recursos infrautilizados**:

- VMs de test que se quedan encendidas.
- Clusters GKE infrautilizados.
- Instancias de Cloud SQL sin tráfico.
- Jobs de Dataflow sin ejecutar desde hace semanas.

Arquitectura típica:

1. **Ingesta de métricas** (CPU, conexiones, tráfico) desde Cloud Monitoring a BigQuery.
2. Modelo (o reglas + modelo) en Vertex AI que etiqueta recursos como:
   - “Activos”.
   - “Ociosos”.
   - “Riesgo de apagado” (probabilidad de no ser usados en las próximas X horas).
3. Un **pipeline de automatización**:
   - Cloud Scheduler → Pub/Sub → Cloud Function / Cloud Run.
   - Esta función consulta el modelo y, si el recurso se considera ocioso y cumple ciertas políticas, lo apaga o reduce su tamaño.

Es crucial incluir **controles de seguridad y gobernanza**:

- Listas de exclusión (recursos que nunca deben apagarse).
- Ventanas horarias seguras (por ejemplo, noche en horario no productivo).
- Confirmación manual opcional para apagar recursos críticos.

---

### 10.6. Análisis de gasto con BigQuery y Vertex AI

BigQuery es el punto central para:

- **Unificar datos de gasto** (Billing Export).
- Mezclarlos con datos operativos:
  - Métricas de Cloud Monitoring.
  - Logs de Cloud Logging.
  - Información de despliegues (por ejemplo, desde un pipeline de CI/CD exportado a BigQuery).

A partir de ahí, Vertex AI puede aportar:

- **Clustering** de proyectos/servicios según su patrón de consumo:
  - Servicios intensivos en CPU.
  - Servicios intensivos en almacenamiento.
  - Servicios con picos muy estacionales.
- **Detección de anomalías** de coste:
  - Días u horas donde el coste de un servicio se desvía claramente de su comportamiento habitual.

Ejemplo de análisis:

- Detectar que el coste de Cloud Logging sube drásticamente tras un despliegue.
- Correlacionar el aumento con un cambio en el nivel de logging (pasar de `INFO` a `DEBUG`).
- Abrir un incidente de optimización de logs para el equipo responsable.

---

### 10.7. Identificación de ineficiencias en proyectos

Las ineficiencias de coste suelen venir de:

- **Sobredimensionamiento**: máquinas o clusters demasiado grandes.
- **Uso ineficiente de servicios gestionados** (por ejemplo, consultas BigQuery mal diseñadas).
- **Logs excesivos** o sin retención adecuada.
- **Recursos huérfanos** (IP estáticas, discos, buckets, snapshots).

AIOps ayuda a **identificar patrones de ineficiencia**:

- Proyectos en los que la mayoría del coste son logs sin uso.
- Servicios donde el coste de BigQuery se dispara debido a consultas full scan.
- Almacenamiento antiguo que casi no se accede, pero que mantiene un coste alto.

Podemos entrenar modelos para:

- Clasificar proyectos según su “perfil de eficiencia”.
- Recomendar acciones:
  - Ajustar retención de logs.
  - Introducir particionado y clustering en tablas BigQuery.
  - Mover almacenamiento frío a clases de almacenamiento más baratas.

---

### 10.8. Integración con Billing Reports de GCP

Además de Billing Export, GCP ofrece herramientas como:

- **Budgets y alertas estáticas**.
- Informes visuales en la consola de Billing.

AIOps complementa estas herramientas:

- En lugar de usar solo umbrales fijos (“avísame si paso de X €”), usamos:
  - **Umbrales dinámicos basados en modelos** (por ejemplo, 30% por encima de la predicción).
  - Segmentación por etiquetas (equipo, producto).
- El objetivo es pasar de una visión **reactiva** (“este mes se ha disparado el coste”) a una visión **proactiva y predictiva**.

Vertex AI se puede integrar en el flujo:

- Jobs diarios que leen los datos de facturación recientes.
- Generan predicciones y posibles desviaciones.
- Publican resultados a Pub/Sub para disparar workflows de notificación o remediación.

---

### 10.9. Simulaciones de escenarios de costes

Otra aplicación es la **simulación de escenarios ("what-if")**:

- ¿Qué pasaría con el coste si:
  - Migramos de `n2-standard` a `e2-standard`?
  - Movemos un servicio a otra región?
  - Reducimos el factor de replicación de logs o cambiamos las políticas de retención?

La IA puede ayudar a:

- Aprender cómo varía el coste con diferentes configuraciones históricas.
- Generar modelos que respondan a preguntas del tipo:
  - “Si el tráfico aumenta un 50%, ¿qué coste estimado tendré en este servicio manteniendo la configuración actual?”
  - “¿Cómo cambia el coste si introduzco autoescalado agresivo versus estático?”

Estas simulaciones se ejecutan en notebooks, scripts en Vertex AI Workbench o pipelines de Vertex AI, y se integran en dashboards para que los equipos de SRE y FinOps puedan tomar decisiones informadas.

---

### 10.10. Alertas de sobrecostes basadas en IA

En lugar de depender solo de:

- “Si supero 2000 €/mes, mándame un email”

Podemos construir **alertas inteligentes**:

1. Entrenar un modelo que prediga el coste esperado por servicio/proyecto.
2. Calcular un rango de confianza (por ejemplo, percentil 95).
3. Generar una alerta cuando el coste observado:
   - Supere ese rango de confianza.
   - O tenga una pendiente de crecimiento anómala (por ejemplo, duplicar el coste diario habitual en pocas horas).

Ventajas:

- Menos falsos positivos.
- Detección temprana de fugas de coste (por ejemplo, bucles de petición, logs masivos, uso indebido de recursos).

La notificación puede integrarse con:

- Cloud Monitoring (alerting).
- Sistemas de tickets (Jira, ServiceNow).
- Herramientas de chat (Slack, Teams) vía Webhooks.

---

### 10.11. Buenas prácticas en optimización financiera

Algunas buenas prácticas desde el punto de vista de AIOps + FinOps:

- **Etiquetado consistente** (`labels`) en recursos:
  - `team`, `service`, `env`, `cost-center`.
- **Exportar facturación siempre a BigQuery** para análisis avanzado y modelos.
- Definir **SLO relacionados con coste**:
  - Coste máximo por request.
  - Coste máximo por entorno o feature.
- Introducir **bucles de feedback**:
  - Los modelos de predicción y anomalía generan recomendaciones.
  - Los equipos de producto y SRE las revisan, ejecutan acciones y retroalimentan el sistema.
- Revisar y versionar:
  - Modelos de optimización de coste.
  - Reglas de automatización (evitando “automatismos peligrosos” sin controles).
- Alinear AIOps con FinOps:
  - Reuniones periódicas entre SRE/Operaciones y Finanzas.
  - Reportes compartidos basados en los mismos datos y modelos.

---

## Tema 11 – Seguridad y cumplimiento en AIOps

### 11.1. Seguridad como requisito en AIOps

La automatización que propone AIOps implica que **sistemas automáticos ejecutan acciones en producción**:

- Apagar recursos.
- Escalar servicios.
- Modificar configuraciones.
- Acceder a datos operativos sensibles (logs, métricas, auditorías).

Por tanto, la seguridad no es opcional:

- Cualquier error de configuración o brecha de seguridad en estos sistemas puede tener impacto masivo (paradas de servicio, exposición de datos, escaladas de privilegios).
- Los modelos de IA pueden tener acceso a información sensible (por ejemplo, logs con datos personales, IPs, nombres de usuario).

El objetivo del tema 11 es entender **cómo diseñar AIOps seguros** en Google Cloud, usando Vertex AI y herramientas de seguridad como Chronicle Security, IAM y auditorías.

---

### 11.2. Riesgos de seguridad en automatización

Principales riesgos asociados a AIOps:

- **Cuentas de servicio con privilegios excesivos**:
  - Pipelines de Vertex AI o Cloud Functions que pueden borrar o modificar recursos críticos.
- **Automatizaciones sin controles**:
  - Scripts que apagan recursos en producción por falsos positivos.
- **Fuga de información**:
  - Logs con datos sensibles usados para entrenar modelos sin anonimización.
- **Ataques a la cadena de automatización**:
  - Compromiso de la cuenta de servicio de un pipeline para ejecutar acciones maliciosas.

Mitigaciones clave:

- Principio de **mínimo privilegio** (least privilege) para cada pieza de la arquitectura AIOps.
- Validaciones adicionales (aprobaciones humanas) para acciones de alto impacto.
- Anonimización o pseudonimización de datos de entrenamiento.
- Revisión periódica de roles, políticas y cuentas de servicio.

---

### 11.3. Cumplimiento normativo en entornos cloud

Las organizaciones suelen estar sujetas a marcos normativos:

- Privacidad (como GDPR).
- Estándares de seguridad (ISO 27001, SOC 2, etc.).
- Requisitos sectoriales (finanzas, salud, administración pública).

En AIOps esto implica:

- Entender qué datos de observabilidad pueden contener **datos personales o sensibles** (por ejemplo, IDs de usuarios en logs).
- Definir políticas de:
  - Retención y borrado de datos.
  - Localización geográfica de datos (regiones).
  - Acceso a datasets usados para entrenar modelos en Vertex AI.

Operaciones y SRE deben colaborar con seguridad y legal para que los pipelines de AIOps:

- Respeten los requerimientos de retención.
- No saquen datos fuera de las regiones permitidas.
- Tengan auditabilidad total (quién accedió a qué datos y cuándo).

---

### 11.4. Control de accesos en Vertex AI y GCP

El control de accesos se basa principalmente en **IAM (Identity and Access Management)**:

- Roles específicos para:
  - Administrar recursos de Vertex AI (entrenamientos, endpoints, pipelines).
  - Leer datos de BigQuery, Cloud Storage, Cloud Logging.
- Cuentas de servicio separadas:
  - Una para entrenamientos de modelos.
  - Otra para predicción online (endpoint).
  - Otra para pipelines de automatización.

Buenas prácticas:

- No usar cuentas de servicio genéricas con permisos de “Owner” o demasiado amplios.
- Asignar permisos **solo a nivel de recurso necesario**:
  - Dataset concreto.
  - Proyecto específico.
- Revisar periódicamente:
  - Members de IAM (usuarios, grupos, cuentas de servicio).
  - Permisos de acceso a datasets usados por AIOps.
- Integrar con:
  - Identidad corporativa (SSO).
  - Grupos para equipos (SRE, Seguridad, Data).

---

### 11.5. Monitorización y auditorías automáticas

Google Cloud proporciona **Cloud Audit Logs**, donde se registran:

- Operaciones administrativas (creación, borrado, cambios de configuración).
- Accesos a datos (Data Access, si está habilitado).
- Actividad de cuentas de servicio y usuarios.

En AIOps, estos logs son fundamentales para:

- Auditar quién y qué automatización ha ejecutado una acción (por ejemplo, apagado de un cluster).
- Detectar comportamientos sospechosos:
  - Cambios de IAM en horarios no habituales.
  - Creación de cuentas de servicio fuera de proceso.

Flujo típico:

1. Enviar Cloud Audit Logs a BigQuery o Chronicle.
2. Usar Vertex AI para entrenar modelos de:
   - Detección de anomalías en patrones de acceso.
   - Clasificación de eventos sospechosos.
3. Conectar las detecciones con:
   - Cloud Monitoring (alertas).
   - Sistemas de tickets o SOAR.

Así se logra que la propia plataforma AIOps tenga mecanismos para **auto-auditarse y auto-vigilarse**.

---

### 11.6. Uso de IA para detectar amenazas internas

Las amenazas internas pueden ser:

- Usuarios legítimos con intenciones maliciosas.
- Mal uso de credenciales por descuido.
- Automatizaciones mal configuradas que exponen datos.

A partir de logs de:

- Cloud Logging.
- Cloud Audit Logs.
- Sistemas de autenticación y acceso.

Se pueden diseñar modelos que detecten, por ejemplo:

- Accesos a datasets críticos desde ubicaciones o horarios inusuales.
- Incremento repentino en exportaciones de datos.
- Cambios de roles IAM no habituales para un determinado usuario o servicio.

Vertex AI permite:

- Entrenar modelos no supervisados (clustering, autoencoders) para detectar patrones raros.
- Entrenar modelos supervisados si se dispone de datos históricos etiquetados como “incidente” vs “normal”.

---

### 11.7. Integración con Chronicle Security

**Chronicle Security** es la plataforma de seguridad de Google pensada como SIEM/analítica de seguridad a gran escala. En el contexto de AIOps:

- Centraliza eventos de seguridad (logs, telemetría).
- Permite correlacionar información de diferentes fuentes (infraestructura, identidad, red, endpoints).

La integración con AIOps y Vertex AI puede darse en dos direcciones:

1. **Entrada**:
   - Chronicle como fuente de datos enriquecidos de seguridad.
   - Estos datos alimentan modelos de Vertex AI para:
     - Detección avanzada de amenazas.
     - Priorización de incidentes de seguridad.
2. **Salida**:
   - Resultados de modelos de Vertex AI (por ejemplo, riesgo de incidente) enviados de vuelta a Chronicle.
   - Uso de estos resultados para activar playbooks de respuesta automática.

Para SRE e ITOps, esto permite unir la visión de **salud del sistema** (latencia, errores, capacidad) con la visión de **seguridad** (intentos de ataque, accesos sospechosos) en un marco de AIOps unificado.

---

### 11.8. Casos de uso de IA en ciberseguridad para ITOps/SRE

Algunos casos de uso concretos orientados a operaciones:

- **Detección de actividad maliciosa en APIs de observabilidad**:
  - Intentos de listar todos los recursos del proyecto.
  - Accesos masivos a endpoints internos de administración.
- **Anomalías en patrones de despliegue**:
  - Nuevos artefactos desplegados desde repositorios desconocidos.
  - Cambios en pipelines de CI/CD fuera de horario o por usuarios no habituales.
- **Correlación entre incidentes de rendimiento y eventos de seguridad**:
  - Picos de CPU y errores 5xx coincidiendo con aumento de tráfico sospechoso (DDoS, scanning).
  - Uso de modelos que relacionen métricas de infraestructura con señales de seguridad.

Estos modelos ayudan a priorizar la respuesta:

- Si un pico de errores está correlacionado con un ataque, la respuesta será distinta que si se debe a un cambio de configuración interno.

---

### 11.9. Estrategias de segmentación y roles

Para limitar el impacto de incidentes y de automatizaciones maliciosas o erróneas, es clave:

- **Segmentación de redes**:
  - VPC separadas para entornos (`prod`, `staging`, `dev`).
  - VPC Service Controls para proteger datos sensibles.
- **Segmentación lógica por proyecto**:
  - Un proyecto para infraestructura compartida de observabilidad.
  - Proyectos por equipo o producto, con límites de permisos claros.
- **Roles y responsabilidades claramente definidos**:
  - Quién puede:
    - Modificar modelos en Vertex AI.
    - Aprobar automatizaciones de apagado de recursos.
    - Cambiar políticas de IAM.

El diseño de AIOps debe respetar esta segmentación:

- Pipelines con cuentas de servicio específicas para cada entorno.
- Modelos entrenados en datasets de un entorno y desplegados solo en ese entorno, cuando aplique.

---

### 11.10. Checklist de seguridad en AIOps

Un **checklist de referencia** para proyectos de AIOps en GCP:

1. **IAM y cuentas de servicio**
   - ¿Cada pipeline/servicio tiene su propia cuenta de servicio?
   - ¿Se aplican roles mínimos necesarios?
   - ¿Se revisan periódicamente roles y bindings?

2. **Datos de entrenamiento**
   - ¿Los datos de logs/métricas contienen información sensible?
   - ¿Se han anonimizado o eliminado datos personales?
   - ¿Se respeta la retención de datos definida?

3. **Arquitectura de automatización**
   - ¿Existen controles para evitar acciones destructivas por falsos positivos?
   - ¿Hay entornos de prueba para las automatizaciones?
   - ¿Se registran todas las acciones ejecutadas por la automatización?

4. **Auditoría y monitorización**
   - ¿Se están guardando y revisando Cloud Audit Logs?
   - ¿Hay modelos o reglas para detectar anomalías en los accesos?

5. **Seguridad de endpoints de modelos**
   - ¿Quién puede invocar endpoints de Vertex AI?
   - ¿Se usan redes privadas o VPC peering?
   - ¿Se limitan las IPs o identidades que pueden llamar al endpoint?

6. **Respuesta a incidentes**
   - ¿Existe un playbook para incidentes de seguridad relacionados con AIOps?
   - ¿Se prueban periódicamente los procedimientos de respuesta?

---

### 11.11. Buenas prácticas de compliance en GCP

Para cumplir con normativas y buenas prácticas:

- **Uso de regiones adecuadas**:
  - Alojar datos y modelos en regiones permitidas por la organización.
- **Cifrado y claves**:
  - Usar CMEK (Customer-Managed Encryption Keys) cuando sea necesario para datasets sensibles.
- **Data Loss Prevention (DLP)**:
  - Analizar logs y datasets que alimentan a Vertex AI para detectar datos sensibles.
  - Reducir la exposición de esos datos en modelos, dashboards y pipelines.
- **VPC Service Controls**:
  - Proteger perímetros de datos en servicios gestionados (BigQuery, Cloud Storage, Vertex AI).
- **Políticas de organización**:
  - Usar Organization Policy para:
    - Restringir servicios permitidos.
    - Forzar reglas de seguridad (por ejemplo, evitar recursos públicos).
- **Documentación y evidencias**:
  - Documentar flujos de datos de AIOps (de dónde vienen, dónde se almacenan y para qué se usan).
  - Mantener evidencias de:
    - Revisiones de permisos.
    - Evaluaciones de riesgo.
    - Cambios en modelos y automatizaciones.

El objetivo final es que AIOps no solo mejore la eficiencia y la observabilidad, sino que también **cumpla de forma demostrable con los requisitos de seguridad y normativos** de la organización.

---
