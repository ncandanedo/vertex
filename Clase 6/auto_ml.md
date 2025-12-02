# 🤖 Guía AIOps: Predicción de Capacidad con BigQuery AutoML

Este laboratorio muestra el flujo completo ("End-to-End") para crear un modelo de **Regresión con AutoML** en BigQuery.

El objetivo es predecir un valor numérico (porcentaje de CPU) basándonos en métricas operativas complejas, dejando que Google pruebe y elija automáticamente el mejor algoritmo.

---

## 📖 Entendiendo los Parámetros de Entrenamiento

Cuando usas `AUTOML_REGRESSOR`, no estás eligiendo un algoritmo (como "Árboles" o "Redes Neuronales"). Estás contratando a un "Robot Científico de Datos" para que pruebe muchos por ti.

Aquí explicamos las opciones críticas que usamos en la query `CREATE MODEL`:

### 1. `budget_hours` (Presupuesto de Tiempo)
> **Ejemplo:** `budget_hours = 1.0`

* **¿Qué es?** Es el tiempo máximo (en horas) que le das a Google para entrenar y probar diferentes modelos.
* **¿Cómo funciona?**
    * Google empezará a probar algoritmos (Linear, XGBoost, DNN...).
    * Si pones **1.0**, Google pasará 1 hora probando combinaciones. Al terminar la hora, se quedará con el "Ganador" y descartará el resto.
* **Coste:** Pagas por el tiempo de computación reservado.
* **Recomendación:**
    * Para pruebas/clase: **1.0** (el mínimo suele ser suficiente para datasets pequeños).
    * Para producción crítica: **2.0 - 5.0** (si quieres exprimir un 1-2% extra de precisión).

### 2. `input_label_cols` (La Meta)
> **Ejemplo:** `input_label_cols = ['cpu_usage_pct_target']`

* **¿Qué es?** Es la columna que contiene la **Respuesta Correcta** (el Target).
* **Importante:** Es lo que el modelo intentará adivinar en el futuro.

### 3. `optimization_objective` (Opcional)
> **Ejemplo:** `optimization_objective = 'MINIMIZE_RMSE'`

* **¿Qué es?** Le dice al robot qué métrica usar para decidir quién gana.
    * **RMSE:** (Raíz del Error Cuadrático Medio). Penaliza mucho los errores grandes. Es el estándar.
    * **MAE:** (Error Absoluto Medio). Trata todos los errores por igual.

---

## 🛠️ El Flujo Completo (SQL)

Sigue estos pasos en BigQuery para replicar el experimento.

### Paso 1: Generar Datos de Entrenamiento (Simulación)
Creamos 2,000 minutos de historia de un servidor.
* **Correlación:** Más Tráfico + Más Latencia + Más Errores = **CPU al rojo vivo**.

```sql
CREATE OR REPLACE TABLE `formacionaiops-476808.test.ops_capacity_metrics` AS

WITH GENERATOR AS (
  SELECT x FROM UNNEST(GENERATE_ARRAY(1, 2000)) AS x
),
RAW_DATA AS (
  SELECT
    timestamp_sub(CURRENT_TIMESTAMP(), INTERVAL x MINUTE) as metric_time,
    -- Métricas de entrada (Features)
    CAST(FLOOR(10 + RAND() * 500) AS INT64) as requests_per_sec,
    CAST(FLOOR(20 + RAND() * 2000) AS INT64) as avg_latency_ms,
    CAST(FLOOR(RAND() * 50) AS INT64) as error_log_count,
    IF(RAND() < 0.3, 'TRUE', 'FALSE') as is_backup_running,
    RAND() as ruido
  FROM GENERATOR
)

SELECT
  metric_time,
  requests_per_sec,
  avg_latency_ms,
  error_log_count,
  is_backup_running,
  
  -- Generamos el Target (CPU %) con una fórmula lógica + ruido
  LEAST(100, GREATEST(5, 
    (
      (requests_per_sec * 0.1)      -- Tráfico base
      + (avg_latency_ms * 0.02)     -- Latencia pesa poco
      + (error_log_count * 0.5)     -- Errores pesan mucho
      + CASE WHEN is_backup_running = 'TRUE' THEN 20 ELSE 0 END -- Backup añade carga fija
    ) 
    + (ruido * 5)
  )) AS cpu_usage_pct_target

FROM RAW_DATA;

```

### Paso 2: Entrenar el Modelo (AutoML)
Lanzamos el entrenamiento.

Nota: Esto tardará aproximadamente 1 hora en completarse debido al budget_hours.


```
CREATE OR REPLACE MODEL `formacionaiops-476808.test.cpu_capacity_predictor`
OPTIONS(
  model_type = 'AUTOML_REGRESSOR',
  input_label_cols = ['cpu_usage_pct_target'], -- Queremos predecir % CPU
  budget_hours = 1.0                           -- Tiempo máximo de entrenamiento
) AS
SELECT
  requests_per_sec,
  avg_latency_ms,
  error_log_count,
  is_backup_running,
  cpu_usage_pct_target
FROM
  `formacionaiops-476808.test.ops_capacity_metrics`;
```

### Paso 3: Simular Escenarios (Predicción)

Una vez termine el entrenamiento, usamos ML.PREDICT para preguntar: "¿Qué pasaría sí...?"

```
SELECT
  *
FROM
  ML.PREDICT(MODEL `formacionaiops-476808.test.cpu_capacity_predictor`,
    (
      -- Escenario A: Tráfico Alto pero Sano (Latencia baja, sin errores)
      SELECT 
        'Escenario_A_TraficoSano' as scenario_id, 
        450 as requests_per_sec, 
        30 as avg_latency_ms, 
        0 as error_log_count, 
        'FALSE' as is_backup_running
      
      UNION ALL
      
      -- Escenario B: La "Tormenta Perfecta" (Tráfico medio, pero lento y con errores)
      SELECT 
        'Escenario_B_Incidente' as scenario_id, 
        200 as requests_per_sec, 
        1500 as avg_latency_ms,   -- Latencia alta
        40 as error_log_count,    -- Muchos logs de error
        'FALSE' as is_backup_running

      UNION ALL

      -- Escenario C: Backup Nocturno (Poco tráfico pero backup activo)
      SELECT 
        'Escenario_C_Backup' as scenario_id, 
        50 as requests_per_sec, 
        40 as avg_latency_ms,   
        0 as error_log_count,    
        'TRUE' as is_backup_running
    )
  );
```

###  📊 Interpretación de Resultados
Verás la columna predicted_cpu_usage_pct_target.

Escenario A: Predicción media (~50%). El modelo aprendió que el tráfico puro no es lo único que importa.

Escenario B: Predicción muy alta (~90%). El modelo aprendió que Errores + Latencia es una combinación mortal para la CPU.


### OJOOOOO budget_hours

Lo ponemos por Seguridad Financiera y Operativa. Es tu "cinturón de seguridad".

Control de Costes: Si Google cambiara el defecto mañana a 24 horas y tú lanzas el entrenamiento sin mirar, podrías recibir una factura de cientos de dólares por un experimento. Poner 1.0 te garantiza que nunca pagarás más de 1 hora de computación.

Gestión del Tiempo: Si estás en una clase o tienes prisa, quieres asegurarte de que el modelo no se quede "pensando" durante 6 horas buscando una mejora del 0.001% en precisión.