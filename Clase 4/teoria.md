# Sesión 4  
## Automatización con AIOps en Vertex AI (Tema 4)  
## Análisis predictivo de incidencias (Tema 5)

---

## Agenda de la sesión

- Repaso rápido de lo visto en sesiones anteriores (AIOps, Vertex AI, observabilidad inteligente).  
- **Tema 4:** Automatización con AIOps en Vertex AI.  
- **Tema 5:** Análisis predictivo de incidencias (BigQuery ML + Vertex AI).  
- Preguntas, discusión de casos reales y cierre.

---

## Objetivos de la sesión

Al final de la sesión, el alumno deberá ser capaz de:

- Entender qué es la **automatización inteligente** aplicada a operaciones (AIOps).
- Diseñar flujos de **respuesta automática a incidentes** usando Cloud Monitoring, Pub/Sub, Cloud Functions, Dataflow y Vertex AI.
- Comprender cómo aplicar **modelos de predicción de incidencias** (CPU, RAM, almacenamiento, errores, tickets…) usando **BigQuery ML y Vertex AI**.
- Identificar en qué casos usar **ARIMA_PLUS, LOGISTIC_REG y otros modelos de BigQuery ML** para resolver problemas típicos de AIOps.

---

# Tema 4 – Automatización con AIOps en Vertex AI

Contenido a cubrir:

- Concepto de automatización inteligente  
- Integración con Cloud Functions  
- Uso de Pub/Sub para eventos automáticos  
- Ejecución de pipelines de Vertex AI con Cloud Composer  
- Flujos de trabajo con Dataflow y Vertex AI  
- Automatización de escalado de recursos  
- Casos de respuesta automática a incidentes  
- Diseño de procesos de auto-remediación  
- Validación y control en automatizaciones críticas  
- Buenas prácticas en gobernanza de automatización  

---

## 4.1 Concepto de automatización inteligente

- **De automatización clásica a automatización inteligente**  
  - Automatización clásica: scripts, cron, tareas programadas que reaccionan a reglas simples (if CPU > 80% entonces manda email).  
  - Automatización inteligente (AIOps): decisiones basadas en **datos históricos + modelos de IA**, que aprenden patrones y ajustan la respuesta con el tiempo.  
  - Se busca un ciclo **cerrado**: observar → predecir/decidir → actuar → aprender del resultado.

- **Papel de Vertex AI y BigQuery en la automatización**  
  - BigQuery almacena datos de métricas/logs/histórico de incidencias y entrena modelos con **BigQuery ML**.  
  - Vertex AI orquesta entrenamientos más complejos, despliega modelos y expone **endpoints de predicción**.  
  - La automatización consume las predicciones (por ejemplo, “probabilidad de saturación” o “riesgo de caída”) para decidir acciones.

- **Objetivo principal**  
  - Pasar de un modelo **reactivo** (apagafuegos) a un modelo **proactivo/predictivo** donde el sistema **actúa antes** de que el usuario sufra el problema.

---

## 4.2 Integración con Cloud Functions

- **Cloud Functions como “pegamento” de AIOps**  
  - Cloud Functions permite ejecutar código **sin gestionar servidores**, reaccionando a eventos: Pub/Sub, HTTP, Cloud Storage, Firestore, etc.  
  - En AIOps se usa para automatizar tareas concretas: escalar recursos, reiniciar servicios, crear tickets, notificar por Slack, etc.

- **Flujos típicos en AIOps**  
  - Cloud Monitoring genera una alerta → envía una notificación (Pub/Sub / webhook).  
  - Una Cloud Function recibe el evento → llama a un modelo (Vertex AI o BigQuery ML) para evaluar la gravedad o prever el futuro.  
  - Según el resultado, la función ejecuta acciones:  
    - Ajustar tamaño de un deployment.  
    - Reiniciar una VM o pod.  
    - Abrir un incidente en la herramienta de ITSM.  

- **Ventajas**  
  - Escala automáticamente con el número de eventos.  
  - Bajo coste cuando no hay incidentes (no hay eventos).  
  - Ideal para **acciones pequeñas y acotadas** dentro de un flujo más grande.

---

## 4.3 Uso de Pub/Sub para eventos automáticos

- **Pub/Sub como bus de eventos de operaciones**  
  - Pub/Sub permite desacoplar productores (Monitoring, Logging, aplicaciones) y consumidores (Cloud Functions, Dataflow, Vertex AI).  
  - Todo lo que ocurre (alertas, logs enriquecidos, métricas agregadas, cambios de estado) se puede representar como eventos en tópicos.

- **Ejemplos de eventos de AIOps**  
  - “Se ha superado el umbral de latencia en el servicio X”.  
  - “Se ha producido un pico de errores 5xx en el backend Y”.  
  - “Se ha desplegado una nueva versión del servicio Z”.  

- **Patrones comunes**  
  - **Event-driven remediation**:  
    - Evento → Pub/Sub → Cloud Function → acción directa (reiniciar, escalar, etc.).  
  - **Event-driven prediction**:  
    - Evento con métricas recientes → Pub/Sub → función o Dataflow → consulta a modelo (BigQuery ML / Vertex AI) → predicción (“habrá saturación en 30 minutos”) → nueva acción/evento.

---

## 4.4 Ejecución de pipelines de Vertex AI con Cloud Composer

- **Cloud Composer (Airflow gestionado)**  
  - Orquestador de **pipelines complejos**: entrenar modelos, mover datos, ejecutar Dataflow, activar funciones, etc.  
  - En AIOps se usa para tareas periódicas o multi-paso:  
    - Reentrenar modelos de predicción cada X días.  
    - Regenerar features en BigQuery.  
    - Validar modelos y desplegar nuevas versiones si mejoran.

- **Integración con Vertex AI**  
  - Desde un DAG de Airflow (Cloud Composer) se llaman operadores que:  
    - Ejecutan **Vertex AI Pipelines**.  
    - Lanzan entrenamientos de modelos (AutoML, custom).  
    - Actualizan endpoints de predicción.  

- **Ejemplo de flujo AIOps**  
  - Tarea 1: extraer métricas históricas desde BigQuery.  
  - Tarea 2: entrenar/actualizar un modelo de forecasting para CPU.  
  - Tarea 3: evaluar el modelo y registrar métricas.  
  - Tarea 4: si mejora, registrar el modelo en Vertex AI y actualizar endpoint.

---

## 4.5 Flujos de trabajo con Dataflow y Vertex AI

- **Dataflow para procesamiento de streaming/batch**  
  - Dataflow procesa en streaming datos desde Pub/Sub o batch desde BigQuery/Storage.  
  - En AIOps sirve para:  
    - Agregar métricas en ventanas (p.ej., CPU media 1 min / 5 min).  
    - Enriquecer eventos con información adicional (owner del servicio, SLO, etc.).  
    - Generar features para modelos de IA en tiempo real.

- **Interacción con Vertex AI / BigQuery ML**  
  - Dataflow puede escribir datos preparados en BigQuery → BigQuery ML entrena y predice directamente.  
  - En otros casos puede llamar a endpoints de Vertex AI para scoring online.

---

## 4.6 Automatización de escalado de recursos

- **Escalado clásico vs escalado guiado por IA**  
  - Escalado clásico: reglas fijas en GCE/GKE (CPU > 70% durante 5 minutos ⇒ escalar).  
  - Escalado predictivo: modelos de forecasting predicen carga futura y ajustan recursos **antes** del pico.  

- **Implementación típica**  
  - Modelo de forecasting entrenado en BigQuery ML con histórico de QPS, CPU, RAM.  
  - Job periódico o Dataflow que obtiene predicciones para los próximos 30–60 minutos.  
  - Cloud Function que, según la predicción, ajusta automáticamente:  
    - Tamaño mínimo/máximo de un autoscaler.  
    - Número de réplicas de un servicio clave.  

- **Beneficios**  
  - Menos saturaciones durante picos conocidos (campañas, lanzamientos, exámenes online, etc.).  
  - Mejor uso de recursos (escala hacia abajo cuando se prevé baja demanda).

---

## 4.7 Casos de respuesta automática a incidentes

Algunos ejemplos concretos:

- **Reinicio automático de pods/instancias “atascadas”**  
  - Detección de patrones de error (CrashLoopBackOff, alta tasa de errores).  
  - Evento → Cloud Function → reinicio o rollout del deployment.

- **Activación de “modo degradado”**  
  - Modelo detecta / predice saturación inminente.  
  - Acción: reducir features costosas o activar caché agresiva.

- **Creación automática de tickets enriquecidos**  
  - Ante ciertos patrones, se abre ticket en la herramienta de soporte (Jira, ServiceNow) con:  
    - contexto técnico,  
    - métricas relevantes,  
    - sugerencia de causa probable (vía modelo de clasificación).

---

## 4.8 Diseño de procesos de auto-remediación

- **Fases de diseño**  
  1. Identificar incidentes frecuentes y repetitivos (runbooks).  
  2. Definir qué pasos del runbook son automatizables sin riesgo.  
  3. Modelar la lógica: reglas + modelos de ML (detección/predicción).  
  4. Implementar prototipos “en modo solo observación” (no tocan producción, solo recomiendan).  
  5. Progresar a acciones automáticas con salvavidas y límites.

- **Buenas prácticas**  
  - Empezar con acciones no destructivas (abrir ticket, mandar alerta adicional).  
  - Medir impacto: cuántos incidentes evita, cuántas veces se equivoca.  
  - Documentar el flujo y mantener un runbook actualizado.

---

## 4.9 Validación y control en automatizaciones críticas

- **Riesgos**  
  - Loops de automatización mal diseñada (acción genera más eventos que vuelven a disparar la misma acción).  
  - Cambios automáticos en sistemas sensibles (base de datos, redes, seguridad).

- **Mecanismos de control**  
  - Guardrails:  
    - Limitar frecuencia y número de veces que una acción se puede ejecutar en un intervalo.  
    - Requerir aprobación humana para acciones de alto impacto.  
  - Feature flags para apagar rápidamente una automatización problemática.  
  - Logs y auditoría claros: cada acción automática debe dejar trazabilidad.

---

## 4.10 Buenas prácticas en gobernanza de automatización

- Definir propietario claro de cada automatización (squad, equipo de SRE).  
- Mantener el código de automatización en repositorios versionados con revisiones de código.  
- Establecer un proceso de cambios controlados (pull requests, tests, entornos de staging).  
- Revisar periódicamente métricas:  
  - ¿Cuántos incidentes ha mitigado?  
  - ¿Cuántos falsos positivos ha generado?  
- Documentar en la wiki interna y enlazar desde los paneles de observabilidad.

---

# Tema 5 – Análisis predictivo de incidencias

Contenido a cubrir:

- Importancia del análisis predictivo en operaciones  
- Modelos de predicción de fallos en Vertex AI  
- Identificación de patrones en métricas históricas  
- Prevención de saturación en recursos cloud  
- Predicción de consumo de CPU, RAM y almacenamiento  
- Análisis de logs para detectar problemas futuros  
- Creación de modelos de predicción en BigQuery ML  
- Validación de predicciones en entornos reales  
- Integración de alertas predictivas con Monitoring  
- Casos de éxito en predicción de incidencias  

---

## 5.1 Importancia del análisis predictivo en operaciones

- Operaciones reactivas vs predictivas:  
  - Reactivo: se actúa cuando ya hay alarma roja o el usuario se queja.  
  - Predictivo: se analizan tendencias y patrones históricos para anticipar incidentes (fallos de hardware, saturación, picos de tráfico).  

- Beneficios:  
  - Menos downtime, mejor experiencia de usuario.  
  - Mejor planificación de capacidad y costes.  
  - Menos estrés en el equipo de operaciones.

---

## 5.2 Modelos de predicción de fallos en Vertex AI

- **Tipos de problemas típicos en AIOps**  
  - Clasificación: “¿Este servidor/servicio va a fallar en las próximas N horas? (sí/no)”.  
  - Regresión: “¿Cuántos errores tendré en la siguiente ventana de tiempo?”.  
  - Series temporales: “¿Cuál será el uso de CPU/QPS la próxima hora?”.

- **Dónde entrenar los modelos**  
  - Para datos tabulares y time series que ya están en BigQuery, es muy natural usar **BigQuery ML** (entrenas con SQL).  
  - Vertex AI entra en juego cuando:  
    - Necesitas modelos más complejos (redes neuronales avanzadas, AutoML, etc.).  
    - Quieres desplegar como endpoint online con SLA de predicción.

---

## 5.3 Identificación de patrones en métricas históricas

- Usamos métricas como CPU, RAM, latencia, errores 4xx/5xx, QPS, número de conexiones, etc.  
- Pasos típicos:  
  1. Agregar métricas en ventanas (1 min, 5 min, 1 hora).  
  2. Añadir contexto (día de la semana, hora, eventos especiales, despliegues).  
  3. Explorar correlaciones: qué suele pasar antes de un fallo; patrones de “pre-falla”.  

---

## 5.4 Prevención de saturación en recursos cloud

- Pregunta típica: “¿Se va a saturar este servicio si sigue la tendencia actual?”  
- Estrategia:  
  - Entrenar modelos con histórico de uso de recursos + incidencias.  
  - Predecir:  
    - Próximos valores de CPU/RAM/QPS.  
    - Probabilidad de estar por encima de un umbral crítico.  
  - Integrar estas predicciones en la lógica de autoscalado y alertas.

---

## 5.5 Predicción de consumo de CPU, RAM y almacenamiento

- Series temporales con ARIMA_PLUS / ARIMA_PLUS_XREG:  
  - Modelos de forecasting de BigQuery ML para series temporales univariantes y multivariantes, usados junto con ML.FORECAST.  
  - Casos típicos:  
    - Predicción de uso de CPU de un servicio.  
    - Predicción de espacio en disco en una base de datos.  
    - Predicción de tráfico HTTP diario.  

---

## 5.6 Análisis de logs para detectar problemas futuros

- De logs crudos a señales de predicción:  
  - A partir de Cloud Logging se extraen:  
    - Frecuencia de ciertos errores.  
    - Patrones de mensajes (regex, códigos, servicios afectados).  
    - Usuarios/tenants afectados.  
  - Se agregan en BigQuery y se crean features: conteos, ratios, flags de “error raro”, etc.

- Modelos posibles:  
  - Clasificación (LOGISTIC_REG, BOOSTED_TREE_CLASSIFIER, DNN_CLASSIFIER…) que predicen:  
    - “¿Este patrón de logs termina en un incidente crítico?”.  
  - Autoencoder/PCA para detectar logs con patrones raros (anomalías).

---

## 5.7 Creación de modelos de predicción en BigQuery ML

Pasos genéricos con BigQuery ML:

1. **Preparar datos**  
   - Tabla en BigQuery con columnas de features + etiqueta (label) si es supervisado.  

2. **Crear el modelo con CREATE MODEL**  

   ```sql
   CREATE OR REPLACE MODEL `aiops_demo.incidentes_sla_model`
   OPTIONS(
     MODEL_TYPE = 'LOGISTIC_REG',
     INPUT_LABEL_COLS = ['incumple_sla']
   ) AS
   SELECT
     incumple_sla,          -- 0/1
     cpu_media_5m,
     errores_5xx_5m,
     hora_del_dia,
     dia_semana,
     tipo_servicio
   FROM `aiops_demo.incidentes_historico`;
   ```

3. **Evaluar el modelo (ML.EVALUATE)**  
   - Métricas según el tipo de modelo (ROC_AUC, accuracy, RMSE, etc.).  

4. **Obtener predicciones (ML.PREDICT o ML.FORECAST)**  
   - Se aplican a datos recientes o futuros (en el caso de forecasting).

---

## 5.8 Tabla de modelos de BigQuery ML y preguntas que responden

A continuación, una tabla con modelos de BigQuery ML relevantes para AIOps (nombre de MODEL_TYPE) y ejemplos de preguntas para las que son adecuados.

| MODEL_TYPE (BigQuery ML) | Ejemplos de preguntas que responde / Para qué es bueno en AIOps |
|--------------------------|------------------------------------------------------------------|
| `LINEAR_REG` | ¿Cuántos errores 5xx esperamos en la próxima hora? ¿Cuál será la duración media de los tickets mañana? Bueno para predecir valores numéricos simples (regresión) a partir de features tabulares. |
| `LOGISTIC_REG` | ¿Este incidente va a incumplir el SLA (sí/no)? ¿Este patrón de métricas indica fallo inminente (sí/no)? Bueno como modelo de clasificación binaria/multiclase sencillo, rápido y explicable. |
| `BOOSTED_TREE_CLASSIFIER` | ¿Cuál es la probabilidad de que un pod entre en CrashLoopBackOff en la próxima hora? ¿A qué categoría pertenece este incidente (red, app, DB…)? Bueno para clasificación tabular con relaciones no lineales y alta capacidad predictiva. |
| `BOOSTED_TREE_REGRESSOR` | ¿Cuántas peticiones por segundo tendrá este servicio en la próxima ventana de tiempo? ¿Cuál será la latencia media dentro de 15 minutos? Bueno para regresión con datos tabulares complejos. |
| `RANDOM_FOREST_CLASSIFIER` | ¿Este usuario/tenant tiene alta probabilidad de disparar una incidencia de rendimiento? Bueno para clasificación cuando quieres modelos robustos y con buena interpretación de importancia de variables. |
| `DNN_CLASSIFIER` | Dado un gran conjunto de métricas y señales, ¿el servicio está en estado “saludable”, “degradado” o “crítico”? Bueno para problemas complejos de clasificación con muchos features (deep learning tabular). |
| `DNN_REGRESSOR` | ¿Cuál será la latencia P95 de este endpoint en función de múltiples señales (tráfico, región, tipo de cliente)? Bueno para regresión compleja con relaciones no lineales. |
| `KMEANS` | ¿Qué grupos de servicios comparten patrones de uso similares? ¿Qué hosts tienen comportamientos de métricas parecidos? Bueno para segmentación y clustering de servicios/hosts; también útil como base para detección de anomalías por cluster. |
| `AUTOENCODER` | ¿Qué puntos de datos de métricas/logs son “raros” comparados con el comportamiento normal? Bueno para detección de anomalías no supervisada y para generar embeddings para búsquedas de similitud. |
| `PCA` | ¿Qué combinaciones de métricas explican la mayor parte de la variación del sistema? ¿Cómo reduzco la dimensionalidad de cientos de métricas sin perder demasiada información? Bueno para reducción de dimensionalidad y también se puede usar para anomalías. |
| `MATRIX_FACTORIZATION` | ¿Qué combinación de servicio/componente es más probable que esté implicada en la próxima incidencia, dado el histórico? Bueno para recomendación (por ejemplo, sugerir causa probable o componente a revisar) usando patrones de co-ocurrencia entre incidentes y servicios. |
| `ARIMA_PLUS` | ¿Cómo evolucionará el uso de CPU/latencia/tráfico en las próximas horas para un servicio concreto? Bueno para forecasting univariante y detección de anomalías en series temporales. |
| `ARIMA_PLUS_XREG` | ¿Cómo evolucionará la carga de un sistema considerando factores externos (día de la semana, campañas, lanzamientos)? Bueno para forecasting multivariante con regresores externos, útil en capacity planning y planificación de eventos. |
| `AUTOML_CLASSIFIER` | ¿Qué tipo de incidente es este ticket de texto (red, app, seguridad…)? ¿Este patrón de uso de la plataforma es normal o sospechoso? Bueno cuando quieres un modelo de clasificación potente y no quieres diseñar a mano el algoritmo. |
| `AUTOML_REGRESSOR` | ¿Cuánto tardará en resolverse un ticket con estas características? ¿Cuántas incidencias de cierto tipo esperamos la semana que viene? Bueno para regresión automática sin tener que elegir el algoritmo concreto. |

---

## 5.9 Validación de predicciones en entornos reales

- Comparar predicciones con lo que realmente ocurrió (backtesting).  
- Medir métricas de negocio y operativas:  
  - ¿Cuántos incidentes evitamos gracias al modelo?  
  - ¿Cuántos falsos positivos/falsos negativos genera?  
- Ajustar umbrales y lógica de automatización según resultados reales.

---

## 5.10 Integración de alertas predictivas con Monitoring

- Las predicciones (probabilidad de fallo, forecasting de CPU, etc.) se pueden escribir de vuelta a BigQuery o a Cloud Monitoring.  
- Desde Monitoring se crean alertas basadas en valores predichos, no solo medidos.  
  - Ejemplo: alerta si la predicción de CPU para los próximos 30 minutos supera el 80%.  
- Se integran con los canales habituales (email, PagerDuty, Slack, etc.) y con los flujos automáticos del Tema 4.

---

## 5.11 Casos de éxito en predicción de incidencias

- Prevención de saturación en exámenes online:  
  - Modelo de forecasting predice picos de tráfico.  
  - Se escala la infraestructura antes del examen para evitar caídas.  

- Predicción de tickets de soporte:  
  - Modelo de regresión predice volumen de tickets por día.  
  - El equipo ajusta recursos humanos y SLAs en función de la carga esperada.  

- Detección temprana de patrones de fallo:  
  - Modelos de clasificación y autoencoder detectan patrones de logs/metrics que suelen preceder a fallos graves.  
  - Se actúa antes de que impacte al usuario.


### Documentación
- https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-create

### Analogias de los aprendizajes

1. Aprendizaje Supervisado (Supervised Learning)
La Analogía: Es como un alumno que estudia con exámenes anteriores resueltos. Tiene la pregunta y la respuesta correcta. Aprende la relación entre ambas para poder responder preguntas nuevas en el futuro.

Clave: Tienes datos históricos etiquetados (sabes qué pasó).

Se divide en dos tipos principales:

A. Regresión (Predecir un Número)
El objetivo es adivinar un valor numérico infinito (precio, temperatura, porcentaje).

Caso de Uso: Predecir el porcentaje de CPU (0% a 100%) que tendrá un servidor, predecir el precio de una casa o las ventas totales ($).

Algoritmos BigQuery:

LINEAR_REG: El básico y rápido.

BOOSTED_TREE_REGRESSOR: (XGBoost) El más preciso para tablas.

DNN_REGRESSOR: Redes neuronales profundas (para datos muy complejos).

B. Clasificación (Predecir una Etiqueta)
El objetivo es meter el dato en una "caja" o categoría cerrada.

Caso de Uso: Detectar si un log es ERROR o INFO, detectar si un correo es SPAM o NO SPAM, predecir si un cliente se IRÁ (Churn) o se QUEDARÁ.

Algoritmos BigQuery:

LOGISTIC_REG: El estándar para Sí/No (Binario).

BOOSTED_TREE_CLASSIFIER: El más potente para múltiples categorías.

AUTOML_CLASSIFIER: Deja que Google elija el mejor por ti.

2. Aprendizaje No Supervisado (Unsupervised Learning)
La Analogía: Es como un detective que entra en una habitación llena de pruebas desordenadas sin saber qué crimen se cometió. Su trabajo es encontrar patrones, agrupar pistas y ver qué cosas "no encajan".

Clave: NO tienes etiquetas. No sabes qué es "bueno" o "malo" de antemano.

A. Clustering (Agrupamiento)
El objetivo es encontrar grupos naturales en los datos.

Caso de Uso: Tu ejercicio de los servidores (agruparlos en Zombies, Calculadoras, etc.), segmentar clientes (VIPs, Ahorradores, Nuevos).

Algoritmos BigQuery:

KMEANS: El rey del agrupamiento. Crea "K" grupos basándose en cercanía.

B. Detección de Anomalías
El objetivo es aprender qué es "lo normal" para señalar lo que es "raro".

Caso de Uso: Detectar fraude en tarjetas de crédito (un gasto raro en otro país), detectar un ciberataque (tráfico inusual).

Algoritmos BigQuery:

AUTOENCODER: Red neuronal que aprende a comprimir tus datos. Si no puede comprimir un dato bien, es que es una anomalía.

PCA: Reducción de dimensionalidad (también sirve para ver datos raros).

3. Series Temporales (Time Series Forecasting)
La Analogía: Es el hombre del tiempo. Mira lo que pasó ayer, anteayer y la semana pasada para dibujar una línea hacia el futuro.

Clave: El orden del tiempo es lo único que importa.

Caso de Uso: Predecir la carga de CPU hora a hora para mañana, predecir stock de inventario, demanda eléctrica.

Algoritmos BigQuery:

ARIMA_PLUS: El motor estándar de Google para forecasting. Maneja festivos y tendencias automáticamente.

4. Sistemas de Recomendación
La Analogía: Es el algoritmo de Netflix. "A usuarios como tú, les gustó esto".

Caso de Uso: Recomendar productos en un e-commerce, recomendar canciones.

Algoritmos BigQuery:

MATRIX_FACTORIZATION: Crea un mapa gigante de Usuarios vs Productos para rellenar los huecos vacíos.

### FIN


Examen: https://forms.gle/a45asjaLCVHx9NYCA
FeedBack: (https://imagina-formacion.typeform.com/to/IkO83DnN)

