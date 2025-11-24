BigQuery ML & Vertex AI CPU Prediction System

This project implements a machine learning pipeline to predict server CPU anomalies ("High CPU" > 80%) using Google Cloud BigQuery ML and Vertex AI.

It supports both Real-Time Alerts (via Vertex AI Endpoints) and Batch Reporting (via BigQuery SQL).

🧠 Strategic Decisions & Best Practices

1. Why NOT Retrain Every Night?

A common misconception is that "fresher is always better." In Machine Learning, retraining every 24 hours is generally discouraged for this use case because:

Model Thrashing: If yesterday was a weird anomaly (e.g., a national holiday or a network outage), retraining immediately makes your model "over-react" to that specific day. The model forgets the general rules and learns the noise.

Stability: You want a predictable alert system. If the model changes logic every night, your operations team cannot trust the alerts (e.g., "Why did this alert today but not yesterday?").

Cost: Training costs money (BigQuery slots). Retraining on 1 day of new data rarely improves accuracy enough to justify the daily cost.

Recommendation: Retrain Monthly or when accuracy explicitly drops (Data Drift). This captures legitimate long-term trend changes without over-reacting to daily noise.

2. Why NOT send server_id to Vertex AI?

When sending requests to the endpoint, we deliberately exclude the server_id.

It's not a predictive feature: A specific ID (like server_99) doesn't cause high CPU. The metrics (Load, Memory, I/O) cause high CPU. If you train on IDs, the model can't generalize to new servers it hasn't seen before.

The "Order Guarantee": Vertex AI endpoints guarantee that the order of the output matches the order of the input.

Input: [Metric A, Metric B, Metric C]

Output: [Prediction A, Prediction B, Prediction C]

The Solution: We keep the server_id in our client application (Python script) and "zip" it back together with the results after the API call returns.



### generate fake data 
```
-- 1. Empty the table first
TRUNCATE TABLE `ml_test.server_metrics`;

-- 2. Insert the new correlated data

INSERT INTO `formacionaiops-476808`.ml_test.server_metrics(server_id, timestamp_col, avg_cpu_last_hour,
  avg_cpu_yesterday, cpu_usage_percent)
WITH
  GENERATOR AS (
    SELECT
      x
    FROM
      UNNEST(GENERATE_ARRAY(1, 1000)) AS x
  ),
  RAW_VALUES AS (
    SELECT
      CONCAT('server_', CAST(FLOOR(1 + RAND() * 5) AS STRING)) AS server_id,
      TIMESTAMP_SUB(`CURRENT_TIMESTAMP`(), INTERVAL CAST(FLOOR(RAND() * 60 * 24) AS INT64) HOUR) AS timestamp_col,
      ROUND(RAND() * 100, 2) AS generated_last_hour,
      ROUND(RAND() * 100, 2) AS generated_yesterday
    FROM
      GENERATOR
  )
SELECT
  server_id,
  timestamp_col,
  generated_last_hour AS avg_cpu_last_hour,
  generated_yesterday AS avg_cpu_yesterday,
  LEAST(100, GREATEST(0, (generated_last_hour + (RAND() * 10 - 5)))) AS cpu_usage_percent
FROM
  RAW_VALUES;
```

###Create the new ML model 
```
CREATE OR REPLACE MODEL `ml_test.cpu_predictor_model`
OPTIONS(
  model_type = 'LOGISTIC_REG',
  input_label_cols = ['is_high_cpu'],
  model_registry = 'vertex_ai',
  vertex_ai_model_id = 'cpu_alert_v1' 
) AS
SELECT
  avg_cpu_last_hour,
  avg_cpu_yesterday,
  -- Re-calculating the label based on the new data
  IF(cpu_usage_percent > 80, 1, 0) AS is_high_cpu
FROM
  `ml_test.server_metrics`


```
Opción 1: Consulta Rápida (Para ver la predicción cruda)
Esta te dirá 1 (Alerta) o 0 (Normal) para cada fila de tu imagen.
``` Predecir valores BQ
SELECT
  server_id,
  timestamp_col,
  avg_cpu_last_hour,
  predicted_is_high_cpu -- 1 = CPU Alta (>80%), 0 = Normal
FROM
  ML.PREDICT(MODEL `ml_test.cpu_predictor_model`,
    (
      SELECT
        server_id,
        timestamp_col,
        avg_cpu_last_hour,
        avg_cpu_yesterday
      FROM
        `ml_test.server_metrics`
    )
  )
ORDER BY timestamp_col DESC;

```

``` Predecir valores BQ

Opción 2: Consulta "Profesional" (Con Probabilidades)
Esta es mejor porque te dice qué tan segura está la IA. Por ejemplo, te dirá: "Creo que es Alerta con un 95% de seguridad".


SELECT
  server_id,
  timestamp_col,
  avg_cpu_last_hour,
  
  -- Traducimos el 1 y 0 a texto
  CASE 
    WHEN predicted_is_high_cpu = 1 THEN '🔴 ALERTA'
    ELSE '🟢 NORMAL'
  END AS estado,

  -- Mostramos la seguridad de la predicción (Probabilidad)
  ROUND(probs.prob * 100, 2) as probabilidad_de_alerta_pct

FROM
  ML.PREDICT(MODEL `ml_test.cpu_predictor_model`,
    (
      SELECT
        server_id,
        timestamp_col,
        avg_cpu_last_hour,
        avg_cpu_yesterday
      FROM
        `ml_test.server_metrics`
    )
  ),
  -- Desempaquetamos el array de probabilidades
  UNNEST(predicted_is_high_cpu_probs) as probs

WHERE probs.label = 1 -- Filtramos para ver la probabilidad de que sea "Alta"
ORDER BY probabilidad_de_alerta_pct DESC;

```

``` JSON
{
  "instances": [
    {
      "avg_cpu_last_hour": 95.5,
      "avg_cpu_yesterday": 88.0
    },
    {
      "avg_cpu_last_hour": 10.2,
      "avg_cpu_yesterday": 12.5
    }
  ]
}

```