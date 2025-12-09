# Curso: AIOps con Vertex AI en Google Cloud  
## Teoría Tema 8 y Tema 9  
**Aplicaciones de Machine Learning en Operaciones e Integración con DevOps y SRE** 

---

## Índice

- [Introducción general](#introducción-general)
- [Tema 8: Aplicaciones de Machine Learning en Operaciones](#tema-8-aplicaciones-de-machine-learning-en-operaciones)
  - [8.1. Modelos supervisados aplicados a incidencias](#81-modelos-supervisados-aplicados-a-incidencias)
  - [8.2. Aprendizaje no supervisado en detección de fallos](#82-aprendizaje-no-supervisado-en-detección-de-fallos)
  - [8.3. Aplicaciones de clustering en métricas de sistemas](#83-aplicaciones-de-clustering-en-métricas-de-sistemas)
  - [8.4. Modelos de clasificación de errores](#84-modelos-de-clasificación-de-errores)
  - [8.5. Predicción de disponibilidad de servicios](#85-predicción-de-disponibilidad-de-servicios)
  - [8.6. Modelos de regresión para tiempos de respuesta](#86-modelos-de-regresión-para-tiempos-de-respuesta)
  - [8.7. Detección de correlaciones entre métricas](#87-detección-de-correlaciones-entre-métricas)
  - [8.8. Validación cruzada de modelos de ML](#88-validación-cruzada-de-modelos-de-ml)
  - [8.9. Uso de Vertex Pipelines para ML Ops](#89-uso-de-vertex-pipelines-para-ml-ops)
  - [8.10. Casos de ML aplicado a operaciones en producción](#810-casos-de-ml-aplicado-a-operaciones-en-producción)
- [Tema 9: Integración con DevOps y SRE](#tema-9-integración-con-devops-y-sre)
  - [9.1. Qué significa AIOps para DevOps y SRE](#91-qué-significa-aiops-para-devops-y-sre)
  - [9.2. Integración en pipelines de CI/CD](#92-integración-en-pipelines-de-cicd)
  - [9.3. Uso de alertas inteligentes en despliegues](#93-uso-de-alertas-inteligentes-en-despliegues)
  - [9.4. Automatización de validaciones post-deploy](#94-automatización-de-validaciones-post-deploy)
  - [9.5. Retroalimentación continua con observabilidad](#95-retroalimentación-continua-con-observabilidad)
  - [9.6. Integración de Vertex AI en prácticas SRE](#96-integración-de-vertex-ai-en-prácticas-sre)
  - [9.7. Balance entre automatización y control humano](#97-balance-entre-automatización-y-control-humano)
  - [9.8. Detección temprana de fallos en despliegues](#98-detección-temprana-de-fallos-en-despliegues)
  - [9.9. Casos prácticos en SRE con AIOps](#99-casos-prácticos-en-sre-con-aiops)
  - [9.10. Beneficios para la cultura DevOps](#910-beneficios-para-la-cultura-devops)

---

## Introducción general

En los temas 8 y 9 pasamos de “entender” AIOps a **usar Machine Learning de forma concreta** sobre logs, métricas e incidencias; y después a **integrar esos modelos en la práctica diaria de DevOps y SRE**.

- El **Tema 8** se centra en los tipos de modelos de ML que aplicamos en Operaciones: clasificación de errores, detección de anomalías, predicción de disponibilidad, tiempos de respuesta, etc.
- El **Tema 9** explica cómo encajar estos modelos en el ciclo de vida real de software y operaciones: CI/CD, SRE, SLOs, alertas inteligentes y automatizaciones controladas.

En ambos temas, Vertex AI actúa como **plataforma central** para entrenar, desplegar y operar los modelos, mientras que Cloud Logging, Cloud Monitoring, Pub/Sub y BigQuery proporcionan los datos que alimentan las soluciones AIOps.

---

## Tema 8: Aplicaciones de Machine Learning en Operaciones

### 8.1. Modelos supervisados aplicados a incidencias

Un modelo supervisado aprende a partir de ejemplos históricos **etiquetados**.  
En AIOps, esto significa usar datos como:

- **Features (entradas)**:  
  - Métricas de infraestructura: CPU, RAM, I/O, conexiones, latencia, colas de mensajes.  
  - Métricas de aplicación: tasa de errores HTTP, tiempos de respuesta p95/p99, throughput.  
  - Metadatos de despliegues: versión de servicio, fecha/hora del release, región, clúster.  
  - Información de logs agregada: conteo de ciertos patrones de error, códigos 5xx, etc.

- **Labels (salidas)**:  
  - “Incidente crítico / incidente menor / sin incidente”.  
  - “Tipo de incidente”: red, base de datos, aplicación, almacenamiento, seguridad.  
  - “Severidad”: SEV1, SEV2, SEV3, etc.

**¿Por qué es útil en Operaciones?**

- Permite **predecir si un patrón actual de métricas** terminará en incidente crítico en los próximos X minutos.  
- Ayuda a **priorizar** qué señales merecen atención inmediata.
- Automatiza parte del **triage** inicial, reduciendo el tiempo hasta el diagnóstico inicial.

**En Vertex AI**:

1. Almacenamos histórico de métricas/logs e incidentes en **BigQuery**.  
2. Creamos un **dataset supervisado** (ej. `<features de métricas y logs>, label_incidente`).  
3. Entrenamos un modelo (AutoML Tabular o Custom Training) para clasificar el riesgo de incidente.  
4. Desplegamos el modelo como **Vertex AI Endpoint** para consultas online o usamos **batch prediction** para análisis horarios.

El objetivo SRE: **detectar de forma temprana patrones de degradación** antes de que los usuarios sufran el problema.

---

### 8.2. Aprendizaje no supervisado en detección de fallos

Cuando no tenemos etiquetas claras de “hubo/no hubo incidente”, usamos **aprendizaje no supervisado** para encontrar patrones raros:

- Detectar **comportamientos anómalos** en el uso de CPU, latencias, errores, etc.
- Encontrar **patrones de logs inusuales** que suelen aparecer cerca de un fallo.

Técnicas típicas:

- **Clustering** (ej.: K-means, DBSCAN) para agrupar puntos de datos “normales” y marcar los que quedan lejos del grupo como posibles anomalías.
- **Modelos de detección de anomalías** (Isolation Forest, autoencoders) que aprenden qué es “normal” y asignan una puntuación de rareza.

En AIOps:

- Entrenamos modelos con datos históricos de periodos considerados “normales”.
- Usamos el modelo sobre streams de métricas (Cloud Monitoring) o logs (Cloud Logging exportados via Pub/Sub + Dataflow) para marcar en tiempo casi real comportamientos inusuales.

**Por qué es importante**: muchas veces el fallo que realmente nos interesa **nunca ha ocurrido exactamente igual antes**. El aprendizaje no supervisado nos da capacidad de detección temprana sin necesidad de tener miles de ejemplos etiquetados.

---

### 8.3. Aplicaciones de clustering en métricas de sistemas

El **clustering** agrupa elementos similares. En Operaciones, se puede aplicar en:

1. **Agrupación de máquinas/servicios por comportamiento**  
   - Agrupar pods o VMs según su uso de CPU, memoria, disco y latencia.  
   - Detectar nodos “raros” que no encajan en el resto del clúster (posible mala configuración o hardware defectuoso).

2. **Análisis de patrones temporales**  
   - Agrupar franjas horarias o días de la semana según patrones de carga.  
   - Extraer grupos tipo:
     - “Tráfico de oficina (9:00–18:00)”.
     - “Tráfico nocturno”.
     - “Picos de fin de semana”.

3. **Segmentación de tipos de incidencias**  
   - Agrupar incidentes según métricas asociadas para descubrir “familias de problemas”:
     - Incidentes de saturación de CPU.
     - Incidentes de latencia de base de datos.
     - Incidentes de red intermitente.

**En Vertex AI / BigQuery:**

- Exportamos métricas de Cloud Monitoring a BigQuery.  
- Ejecutamos clustering con **BigQuery ML** o entrenamos un modelo de clustering con Vertex AI.  
- Usamos los resultados para diseñar políticas de **autoscaling específicas por tipo de servicio** y detectar comportamientos anómalos en un grupo.

---

### 8.4. Modelos de clasificación de errores

La clasificación de errores busca que el modelo reciba:

- Texto de logs (mensajes, stacktraces).
- Códigos de error (HTTP 4xx/5xx, errores de base de datos, timeouts).
- Métricas asociadas (picos de CPU, saturación de conexiones).

Y devuelva etiquetas tipo:

- “Error de red”, “Error de base de datos”, “Bug en aplicación”, “Timeout externo”.
- “Transitorio” vs “persistente”.
- “Relacionado con despliegue reciente” vs “sin relación”.

**Ventajas para SRE / Operaciones:**

- El **triage automático** mejora:  
  - Se enruta más rápido el incidente al equipo adecuado (DBA, Networking, Backend).  
  - Se priorizan errores de alto impacto.

- Se puede construir un **clasificador de tickets**:
  - A partir de historiales de tickets de soporte (Jira, ServiceNow) exportados a BigQuery.
  - Vertex AI entrena un modelo de NLP que sugiere categoría y prioridad.

En Vertex AI:

1. Preparar dataset con columnas: `texto_error`, `features_métricas`, `label_tipo_error`.  
2. Usar modelos de texto (AutoML Text o modelos personalizados) para clasificación.  
3. Desplegar como endpoint e integrarlo con:
   - Flujos de ingestión de logs.  
   - Sistemas de ticketing (vía Cloud Functions o Cloud Run).

---

### 8.5. Predicción de disponibilidad de servicios

La **disponibilidad** suele expresarse como un porcentaje (ej.: 99,9%).  
Con ML podemos pasar de observar disponibilidad _a posteriori_ a **predecir el riesgo de incumplir el SLO**.

Entradas típicas:

- Historial de uptime/downtime por servicio.  
- Node/pod health, reinicios, errores 5xx, saturación de colas.  
- Información de despliegues, cambios de configuración, ventanas de mantenimiento.  

Salidas posibles:

- Probabilidad de que el servicio incumpla el SLO mensual.  
- Predicción de minutos de downtime esperados en la próxima semana.

¿Para qué sirve?

- Planificar **capacidades y refuerzos** en fechas críticas (ej.: campaña, exámenes online, lanzamientos).  
- Ajustar **estrategias de despliegue** (usar canary, blue/green) cuando el riesgo es alto.  
- Ayudar a decidir si el SLO actual es realista o se debe renegociar con el negocio.

En Vertex AI:

- Se entrena un modelo supervisado (clasificación o regresión) con datos históricos de disponibilidad y métricas.  
- Se programan predicciones periódicas (ej.: job en Cloud Scheduler + Cloud Run que llama al endpoint de Vertex AI) y se guardan en BigQuery o Cloud Monitoring para visualización.

---

### 8.6. Modelos de regresión para tiempos de respuesta

La **regresión** predice valores numéricos, por ejemplo:

- Latencia media, p95, p99 de un servicio.  
- Número de peticiones atendidas por segundo (QPS) que soportará una configuración.  

Ejemplos de uso:

- Predecir el p95 de latencia de un microservicio en función de:
  - QPS esperado.  
  - Número de pods.  
  - Tipo de máquina.  
  - Tamaño del pool de conexiones a base de datos.

- Estimar el impacto de:
  - Añadir un nuevo cliente grande.  
  - Cambiar un límite de recursos en Kubernetes.

Beneficios:

- Permite hacer **“what-if” simulations** antes de cambios importantes.  
- Ayuda a diseñar **estrategias de autoscaling más inteligentes** (no solo basadas en CPU, sino en el impacto en la latencia).

En Vertex AI:

- Se entrena un modelo de regresión (AutoML Tabular o modelo custom) con datos de carga y resultado de rendimiento.  
- Se integra en pipelines de pruebas de rendimiento (por ejemplo, tests con Locust/JMeter que alimentan datos al modelo y validan la latencia esperada).

---

### 8.7. Detección de correlaciones entre métricas

En sistemas complejos, la cantidad de métricas es enorme. El ML ayuda a identificar:

- Qué métricas están **más correlacionadas** con:
  - Latencia.  
  - Tasa de errores.  
  - Consumo de recursos.  
  - Incumplimientos de SLO.

- Qué **combinaciones de métricas** suelen darse antes de un incidente:
  - “CPU alta + GC frecuente + aumento de errores 5xx”.  
  - “Latencia de base de datos alta + saturación de conexiones”.

Técnicas:

- Análisis de correlación clásico (Pearson, Spearman) sobre datos en BigQuery.  
- **Feature importance** en modelos supervisados (ej.: XGBoost en Vertex AI) para ver qué features influyen más en la predicción.  
- Métodos de interpretabilidad (SHAP, LIME) para modelos complejos.

Impacto en SRE:

- Mejora el **diagnóstico**: se sabe rápidamente qué métricas mirar cuando algo se rompe.  
- Ayuda a mejorar los **dashboards**: se incluye lo realmente relevante para el SLO, no todo lo que “podría ser útil”.

---

### 8.8. Validación cruzada de modelos de ML

Un modelo AIOps malo puede generar:

- Demasiado ruido (falsos positivos).
- Riesgo operacional (falsos negativos en incidencias críticas).
- Automatizaciones peligrosas.

Por eso es clave la **validación cruzada**:

- Dividir los datos de entrenamiento en varias particiones y evaluar el modelo en datos no vistos.  
- En series temporales, respetar siempre el orden del tiempo (no usar “datos futuros” para predecir el pasado).

Métricas de evaluación:

- **Clasificación**: precisión, recall, F1, AUC, especialmente:
  - Falsos positivos (alertas innecesarias).  
  - Falsos negativos (incidentes no detectados).

- **Regresión**: MAE, RMSE, R², y sobre todo:
  - Errores máximos tolerables para el negocio (por ejemplo, cuánta desviación de latencia p95 es aceptable).

En Vertex AI:

- Los jobs de entrenamiento permiten separar train/validation/test, y obtener métricas en cada uno.  
- En Vertex Pipelines se puede automatizar la comparación entre la versión de modelo actual y una nueva, y decidir si se promueve o no.

---

### 8.9. Uso de Vertex Pipelines para ML Ops

**Vertex Pipelines** permite construir flujos reproducibles de ML, muy alineados con la filosofía DevOps/SRE:

Pasos típicos de un pipeline de AIOps:

1. **Ingesta de datos**  
   - Leer métricas exportadas a BigQuery desde Cloud Monitoring.  
   - Leer logs procesados por Dataflow desde Cloud Storage.

2. **Preprocesamiento y feature engineering**  
   - Agregar métricas por ventanas de tiempo (1 min, 5 min, 1 h).  
   - Extraer features de logs (conteo de ciertos errores, n-grams de texto, etc.).  

3. **Entrenamiento del modelo**  
   - Ejecutar entrenamiento con AutoML o entrenamiento custom (containers propios).  

4. **Evaluación y comparación de versiones**  
   - Calcular métricas de calidad.  
   - Comparar con el modelo actualmente en producción (versionado de modelos).

5. **Despliegue controlado**  
   - Si el nuevo modelo mejora los KPIs definidos, se despliega automáticamente a un endpoint.  
   - Si no, el pipeline terminará sin actualizar producción.

**¿Por qué usar Pipelines en AIOps?**

- Estandariza y automatiza el ciclo de vida de los modelos (entrenar → evaluar → desplegar).  
- Permite **re-entrenos periódicos** (ej.: diarias o semanales) sin intervención manual.  
- Proporciona trazabilidad, historiales de ejecuciones y reproducibilidad, aspectos clave para SRE y gobernanza.

---

### 8.10. Casos de ML aplicado a operaciones en producción

Ejemplos típicos en entornos reales:

1. **Autoscaling predictivo**  
   - Modelo que predice la carga futura (QPS, CPU) a partir del histórico.  
   - Vertex AI genera previsiones que se usan para ajustar límites de autoscaling antes de que llegue el pico.

2. **Detección de anomalías en logs**  
   - Pipeline que lee logs en tiempo real, los pasa por un modelo de anomalías y envía alertas a Cloud Monitoring o abre tickets automáticamente.

3. **Clasificación y priorización de tickets**  
   - Modelo entrenado con tickets históricos que sugiere tipo, prioridad y equipo asignado.

4. **Alertas inteligentes**  
   - En lugar de umbrales fijos (CPU > 80%), usar modelos que entienden qué es “normal” para cada servicio, reduciendo falsos positivos.

5. **Recomendaciones de runbooks**  
   - A partir de patrones de métricas y logs, sugerir los runbooks más relevantes según incidentes similares del pasado.

---

## Tema 9: Integración con DevOps y SRE

### 9.1. Qué significa AIOps para DevOps y SRE

- **DevOps**: automatización de despliegues, integración continua, colaboración entre desarrollo y operaciones.
- **SRE**: foco en fiabilidad, SLOs, error budgets, reducción de toil y mejora continua.
- **AIOps**: aplicar modelos de ML sobre métricas, logs, trazas y eventos para:
  - Detectar problemas antes de que sean incidentes graves.  
  - Automatizar parte del diagnóstico y la respuesta.  
  - Reducir ruido de alertas y tareas manuales.

Para un equipo SRE, AIOps no reemplaza las prácticas de SRE, sino que las **potencia**:

- Los SLOs siguen siendo el centro.
- AIOps añade “ojos extra” para leer y entender miles de métricas y logs de forma automática.

---

### 9.2. Integración en pipelines de CI/CD

Los modelos de AIOps también necesitan **ciclo de vida y disciplina**, igual que el código:

- Repositorios de código para:
  - Configuración de Vertex Pipelines.  
  - Código de entrenamiento y preprocesado.  
  - Definición de features y esquemas de datos.

- Pipelines CI/CD (Cloud Build, GitHub Actions, GitLab CI, etc.) que:
  - Ejecutan tests del código de entrenamiento y pipelines.  
  - Verifican que el esquema de datos no ha roto el modelo.  
  - Lanzan entrenamientos en Vertex AI cuando se hace un merge en `main` o cuando se actualizan datos.

Recomendaciones:

- Tratar modelos y pipelines de ML como **artefactos versionados**.  
- Integrar la comprobación de métricas del modelo (AUC, F1, MAE…) como **“gates” de despliegue**, igual que los tests unitarios.

---

### 9.3. Uso de alertas inteligentes en despliegues

En un despliegue moderno no basta con mirar si el pod está “Running”; hay que observar:

- Latencias (p95, p99).  
- Errores 5xx.  
- Métricas de saturación (CPU, memoria, conexiones).  
- Cambios en patrones de logs.

Con AIOps:

- Alimentamos un modelo con métricas de los primeros minutos tras un despliegue (canary o post-rollout).  
- El modelo decide si el comportamiento es:
  - “Normal para una versión nueva”.  
  - “Anómalo” y potencialmente peligroso.

Esto permite construir **alertas inteligentes**:

- Se activan solo cuando hay una degradación significativa estadísticamente.  
- Reducen falsos positivos (por ejemplo, pequeños spikes de CPU que siempre se han dado en cada release).

---

### 9.4. Automatización de validaciones post-deploy

Después de cada deploy, podemos seguir un flujo automatizado:

1. **Smoke tests automáticos**  
   - Se ejecutan tests básicos para comprobar endpoints críticos.

2. **Comparación de métricas pre/post**  
   - Se analizan las métricas de los últimos X minutos antes del despliegue vs. después.  
   - Un modelo de AIOps evalúa si el cambio es aceptable.

3. **Decisión automática o semi-automática**  
   - Si el modelo detecta degradación fuerte, se ejecuta un **rollback automático** (mediante Cloud Deploy, GitOps, etc.).  
   - En casos menos claros, se envía una alerta a SRE para decisión manual.

¿Por qué es importante?

- Reduce el **tiempo que una versión defectuosa está en producción**.  
- Estandariza la validación post-deploy más allá de la simple verificación de “pod ready”.

---

### 9.5. Retroalimentación continua con observabilidad

La observabilidad es el **combustible** de AIOps:

- Métricas, logs, trazas y eventos se almacenan (Cloud Monitoring + Cloud Logging + BigQuery).  
- Esos datos se utilizan para entrenar y mejorar modelos de AIOps.

Y AIOps, a su vez, **retroalimenta la observabilidad**:

- Los modelos generan nuevas métricas:
  - “Riesgo de incidencia en los próximos 30 minutos”.  
  - “Probabilidad de violar el SLO mensual”.  
  - “Score de anomalía de este servicio”.

Estas métricas se vuelcan de nuevo a Cloud Monitoring y dashboards, creando un **ciclo de feedback continuo**:

1. Operación real de sistemas.  
2. Observabilidad agrega y almacena datos.  
3. Modelos AIOps se re-entrenan y mejoran.  
4. Nuevas predicciones y alertas inteligentes.  
5. SRE y DevOps ajustan arquitectura, SLOs y procesos.

---

### 9.6. Integración de Vertex AI en prácticas SRE

Vertex AI se integra con SRE en varias dimensiones:

- **Gestión de SLOs**  
  - Modelos que predicen si se va a consumir el error budget antes de fin de periodo.  
  - Métricas derivadas de los modelos visibles en dashboards SRE.

- **Planificación de capacidad**  
  - Modelos de forecasting de carga que ayudan a dimensionar clusters, tamaños de nodos y políticas de autoscaling.

- **Gestión de incidentes**  
  - Clasificación automática de incidentes y sugerencia de runbooks.  
  - Agrupación de alertas relacionadas para evitar “alert storms”.

A nivel práctico:

- Vertex AI produce endpoints y batch jobs.  
- SRE integra esos endpoints en:
  - Cloud Functions / Cloud Run para automatizaciones.  
  - Alertas en Cloud Monitoring que se apoyan en predicciones, no solo en umbrales fijos.

---

### 9.7. Balance entre automatización y control humano

AIOps permite automatizar, pero SRE debe decidir:

- **Qué acciones son seguras de automatizar**:
  - Reinicios de pods.  
  - Regeneración de certificados.  
  - Escalado de réplicas.

- **Qué acciones requieren revisión humana**:
  - Rollbacks a versiones anteriores.  
  - Cambios de configuración de red crítica.  
  - Escalados de capacidad con coste elevado.

Buenas prácticas:

- Empezar con **automatizaciones no destructivas** (añadir recursos, reintentos, avisos).  
- Añadir **“circuit breakers” y límites** en las automatizaciones (máximo número de rollbacks, máximo número de incrementos de recursos al día).  
- Mantener siempre la posibilidad de **override manual**.

El objetivo es reducir toil, no perder el control operativo.

---

### 9.8. Detección temprana de fallos en despliegues

La fase de “early life” de una nueva versión es crítica. Con AIOps y DevOps:

- Se monitoriza la nueva versión con métricas detalladas desde el primer minuto.
- Se compara su comportamiento con la versión anterior (canary analysis):
  - Latencia, errores, consumo de recursos, patrones de logs.

Un modelo de AIOps puede:

- Calcular un **“canary score”** que indica si la nueva versión se comporta mejor, igual o peor.  
- Recomendar:
  - Continuar el rollout.  
  - Pausar.  
  - Hacer rollback.

SRE se beneficia porque:

- Reduce el tiempo de detección de regresiones.  
- Disminuye la necesidad de inspección manual continua durante cada despliegue.

---

### 9.9. Casos prácticos en SRE con AIOps

Algunos ejemplos combinando SRE + AIOps:

1. **Alertas basadas en error budget**  
   - Modelo que predice cuánto error budget se consumirá si continúa la tasa de errores actual.  
   - Se disparan alertas cuando el modelo indica que se agotará el budget en pocas horas.

2. **Priorización de incidentes**  
   - Incidentes se clasifican según:
     - Impacto esperado en SLOs.  
     - Impacto en negocio (número de usuarios afectados, volumen de transacciones).

3. **Runbooks sugeridos automáticamente**  
   - Según el patrón de métricas/logs, el sistema sugiere runbooks que funcionaron en incidentes similares pasados.  
   - SRE sólo tiene que revisar y ejecutar, reduciendo MTTR.

4. **Agrupación de alertas correlacionadas**  
   - Un modelo agrupa múltiples alertas relacionadas (por ejemplo, varias alertas de microservicios que dependen de la misma base de datos caída) en **un único incidente raíz**.

---

### 9.10. Beneficios para la cultura DevOps

Integrar AIOps con DevOps y SRE no es solo un cambio técnico, también cultural:

- Más **decisiones basadas en datos**:
  - Predicciones de capacidad.  
  - Análisis de impacto de cambios.  
  - Medición objetiva de mejoras.

- Menos **toil y trabajo repetitivo**:
  - Se automatizan tareas de triage, clasificación y respuesta básica.

- Mejor **colaboración entre equipos**:
  - Desarrollo entiende mejor el impacto de sus cambios gracias a métricas y modelos.  
  - SRE dispone de herramientas más potentes para asegurar la fiabilidad.

En resumen, AIOps, soportado por Vertex AI y las herramientas de observabilidad de GCP, se convierte en un **acelerador de la cultura DevOps/SRE**, alineando automatización, fiabilidad e inteligencia en la operación diaria de sistemas.

---

## FIN

Examen: (https://forms.gle/nJBRQWfxHeaQatSn6)
FeedBack: (https://imagina-formacion.typeform.com/to/IkO83DnN)

SER Book: (https://sre.google/books/)