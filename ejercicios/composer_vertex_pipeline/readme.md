# Guía rápida: ARIMA+ (BQML) para detectar anomalías en *requests*

> **Proyecto:** `formacionaiops-476808` · **Dataset:** `clasificador_logs_flask` · **Ubicación BigQuery:** `EU` (multi-región)  
> Ejecuta todas las consultas en BigQuery con **Job location = EU**.

---

## 1) Crear la tabla `logs_minutely` con datos sintéticos (2 días, 3 servicios)

```sql
-- (Opcional) Crea el dataset si no existe (en EU)
CREATE SCHEMA IF NOT EXISTS `formacionaiops-476808.clasificador_logs_flask`
OPTIONS(location = 'EU');

-- Tabla particionada por fecha(ts) y clusterizada por service
CREATE OR REPLACE TABLE `formacionaiops-476808.clasificador_logs_flask.logs_minutely`
PARTITION BY DATE(ts)
CLUSTER BY service AS
WITH minutes AS (
  SELECT TIMESTAMP_ADD(TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), MINUTE),
         INTERVAL -2880 + n MINUTE) AS ts          -- 2 días (2880 min)
  FROM UNNEST(GENERATE_ARRAY(0, 2879)) AS n
),
svc AS (SELECT service FROM UNNEST(['auth','checkout','search']) AS service),
grid AS (SELECT m.ts, s.service FROM minutes m CROSS JOIN svc s),
baseline AS (
  SELECT
    ts, service,
    CASE service WHEN 'auth' THEN 140 WHEN 'checkout' THEN 220 ELSE 300 END
    + 45 * SIN(2 * 3.1415926 * EXTRACT(HOUR FROM ts)/24.0)   -- patrón diario
    + 18 * COS(2 * 3.1415926 * EXTRACT(HOUR FROM ts)/12.0)   -- semidiario
    + 0.02 * TIMESTAMP_DIFF(ts, (SELECT MIN(ts) FROM grid), MINUTE) -- ligera tendencia
    + (RAND()*12 - 6) AS req_raw
  FROM grid
),
base_clipped AS (
  SELECT
    ts, service,
    CAST(GREATEST(0, ROUND(req_raw)) AS INT64) AS requests_base,
    CASE service
      WHEN 'auth' THEN 0.012 + (RAND()*0.010 - 0.005)
      WHEN 'checkout' THEN 0.018 + (RAND()*0.012 - 0.006)
      ELSE 0.010 + (RAND()*0.010 - 0.005)
    END AS err_base,
    CASE service
      WHEN 'auth' THEN 110 + RAND()*20
      WHEN 'checkout' THEN 140 + RAND()*30
      ELSE 95 + RAND()*15
    END AS lat_base
  FROM baseline
),
injected AS (
  SELECT
    ts, service,
    IF(RAND() < 0.004, requests_base + CAST(100 + RAND()*180 AS INT64), requests_base) AS requests,
    IF(RAND() < 0.004, LEAST(1.0, 0.03 + RAND()*0.25), GREATEST(0.0, err_base)) AS error_rate,
    IF(RAND() < 0.004, lat_base + 80 + RAND()*120,
       lat_base + (SIN(2 * 3.1415926 * EXTRACT(MINUTE FROM ts)/60.0)*5)) AS latency_ms
  FROM base_clipped
)
SELECT
  ts,
  service,
  requests,
  ROUND(error_rate, 4) AS error_rate,
  ROUND(latency_ms, 2) AS latency_ms,
  CAST(ROUND(requests * error_rate) AS INT64) AS errors_5xx
FROM injected;
```

> **Nota:** No uses `ORDER BY` dentro del `CREATE TABLE AS SELECT` cuando hay **PARTITION BY**/**CLUSTER BY**.

---

## 2) Crear el modelo ARIMA\_PLUS (multi-serie por `service`)

Entrenamos con un **holdout de 60 min** para poder detectar cambios recientes como “novedad”.

```sql
CREATE OR REPLACE MODEL `formacionaiops-476808.clasificador_logs_flask.mdl_requests_arima`
OPTIONS(
  MODEL_TYPE = 'ARIMA_PLUS',
  TIME_SERIES_TIMESTAMP_COL = 'ts',
  TIME_SERIES_DATA_COL = 'requests',
  TIME_SERIES_ID_COL = 'service'
) AS
SELECT ts, requests, service
FROM `formacionaiops-476808.clasificador_logs_flask.logs_minutely`
WHERE ts < TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 60 MINUTE);
```

---

## 3) Insertar una **anomalía controlada**

Insertamos un pico muy alto en `checkout` **en el minuto actual** para forzar una detección.

```sql
INSERT INTO `formacionaiops-476808.clasificador_logs_flask.logs_minutely`
(ts, service, requests, error_rate, latency_ms, errors_5xx)
VALUES (
  TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), MINUTE),  -- ahora, al minuto
  'checkout',
  20000,     -- pico artificial
  0.02,
  120.0,
  400
);
```

---

## 4) Detectar la nueva anomalía

### 4.1) Consulta ad‑hoc (sin escribir tabla)
```sql
SELECT *
FROM ML.DETECT_ANOMALIES(
  MODEL `formacionaiops-476808.clasificador_logs_flask.mdl_requests_arima`,
  STRUCT(0.90 AS anomaly_prob_threshold),   -- más sensible que 0.95
  (
    SELECT ts, requests, service
    FROM `formacionaiops-476808.clasificador_logs_flask.logs_minutely`
    WHERE ts >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 2 HOUR)
  )
)
WHERE is_anomaly = TRUE
ORDER BY anomaly_probability DESC
LIMIT 50;
```

### 4.2) Persistir resultados en una tabla particionada (opcional)
```sql
CREATE OR REPLACE TABLE `formacionaiops-476808.clasificador_logs_flask.anomalies_requests_pipeline`
PARTITION BY DATE(ts)
CLUSTER BY service AS
SELECT *
FROM ML.DETECT_ANOMALIES(
  MODEL `formacionaiops-476808.clasificador_logs_flask.mdl_requests_arima`,
  STRUCT(0.90 AS anomaly_prob_threshold),
  TABLE `formacionaiops-476808.clasificador_logs_flask.logs_minutely`
);
```

---

## ¿Para qué es bueno ARIMA\_PLUS aquí?

- **Picos en una métrica temporal univariante** (`requests`) por **servicio**.  
- Captura **estacionalidad** (horas punta vs valles) y **tendencias**; señala lo **atípico** de verdad.  
- Fácil de **interpretar** y rápido de ejecutar en BigQuery (sin infra extra).

**Cuándo considerar otra cosa:**  
- Si quieres anomalías **multivariantes** (combinando `requests`, `error_rate`, `latency_ms`) o patrones no estacionales → prueba **AUTOENCODER** de BQML.  
- Si hay **cambios de nivel** bruscos y permanentes (shift), re‑entrena o usa ventanas de entrenamiento más recientes.

---

## Verificación rápida

```sql
-- ¿Hay filas en la tabla de anomalías?
SELECT COUNT(*) FROM `formacionaiops-476808.clasificador_logs_flask.anomalies_requests_pipeline`;

-- Últimas anomalías
SELECT ts, service, requests, anomaly_probability
FROM `formacionaiops-476808.clasificador_logs_flask.anomalies_requests_pipeline`
WHERE is_anomaly = TRUE
ORDER BY ts DESC
LIMIT 50;
```

> Si no ves nada, baja el umbral a **0.85–0.90** o amplía la ventana del subquery (p.ej. 6–24 h).


### Query para ver que va a crear el FORECAST mañana con la capacidad

```
-- Crea/actualiza una tabla con el forecast SOLO para mañana (UTC)
CREATE OR REPLACE TABLE `formacionaiops-476808.clasificador_logs_flask.forecast_requests_tomorrow` AS
WITH fc AS (
  -- 1000 pasos (= 2 días a nivel minutely) para asegurarnos de cubrir mañana completo
  SELECT *
  FROM ML.FORECAST(
    MODEL `formacionaiops-476808.clasificador_logs_flask.mdl_requests_arima`,
    STRUCT(1000 AS horizon, 0.95 AS confidence_level)
  )
)
SELECT *
FROM fc
WHERE DATE(forecast_timestamp) = DATE_ADD(CURRENT_DATE(), INTERVAL 1 DAY)
ORDER BY service, forecast_timestamp;

```
### Query para ver que va a pasar mañana con la capacidad


```
-- Resumen de forecast para mañana (por servicio)
WITH base AS (
  SELECT
    service,
    forecast_timestamp,
    forecast_value,
    prediction_interval_lower_bound,
    prediction_interval_upper_bound
  FROM `formacionaiops-476808.clasificador_logs_flask.forecast_requests_tomorrow`
),

-- 1) Métricas agregadas por servicio
agg AS (
  SELECT
    service,
    MIN(forecast_timestamp) AS start_ts,
    MAX(forecast_timestamp) AS end_ts,
    AVG(forecast_value) AS avg_forecast,
    SUM(forecast_value) AS total_forecast_day,
    -- p95 aproximado
    APPROX_QUANTILES(forecast_value, 101)[OFFSET(95)] AS p95_forecast,
    AVG(prediction_interval_upper_bound - prediction_interval_lower_bound) AS avg_bandwidth
  FROM base
  GROUP BY service
),

-- 2) Pico (minuto con mayor forecast) por servicio
peak AS (
  SELECT
    service,
    (ARRAY_AGG(STRUCT(
        forecast_value AS peak_value,
        forecast_timestamp AS peak_ts,
        prediction_interval_lower_bound AS peak_pi_lower,
        prediction_interval_upper_bound AS peak_pi_upper
      )
      ORDER BY forecast_value DESC LIMIT 1))[OFFSET(0)] AS p
  FROM base
  GROUP BY service
),

-- 3) Hora más cargada (suma de 60 min) por servicio
hourly AS (
  SELECT
    service,
    TIMESTAMP_TRUNC(forecast_timestamp, HOUR) AS hour,
    SUM(forecast_value) AS sum_forecast,
    SUM(prediction_interval_lower_bound) AS sum_lower,
    SUM(prediction_interval_upper_bound) AS sum_upper
  FROM base
  GROUP BY service, hour
),
hour_top AS (
  SELECT * EXCEPT(rn) FROM (
    SELECT h.*,
           ROW_NUMBER() OVER (PARTITION BY service ORDER BY sum_forecast DESC) AS rn
    FROM hourly h
  )
  WHERE rn = 1
)

SELECT
  a.service,
  a.start_ts,
  a.end_ts,
  ROUND(a.avg_forecast, 2)         AS avg_forecast_min,
  ROUND(a.total_forecast_day, 2)   AS total_forecast_day,
  ROUND(a.p95_forecast, 2)         AS p95_forecast_min,
  ROUND(a.avg_bandwidth, 2)        AS avg_pi_width_min,
  -- Pico del día
  ROUND(p.p.peak_value, 2)         AS peak_value_min,
  p.p.peak_ts                      AS peak_ts,
  ROUND(p.p.peak_pi_lower, 2)      AS peak_pi_lower_min,
  ROUND(p.p.peak_pi_upper, 2)      AS peak_pi_upper_min,
  -- Hora más cargada
  hour_top.hour                    AS busiest_hour,
  ROUND(hour_top.sum_forecast, 2)  AS busiest_hour_sum_forecast,
  ROUND(hour_top.sum_lower, 2)     AS busiest_hour_sum_lower,
  ROUND(hour_top.sum_upper, 2)     AS busiest_hour_sum_upper
FROM agg a
JOIN peak p   USING (service)
JOIN hour_top USING (service)
ORDER BY a.service;
```

Para cada servicio, el modelo (ARIMA_PLUS) está pronosticando valores bastante planos en la ventana que alcanzaste (desde 00:00 hasta ~06:47 UTC):

auth

Promedio por minuto: ~187 req/min (igual al pico → plano).

Banda de incertidumbre media: ±~42 (ancho ~83.6).

Límite superior típico por minuto: ~223.

Hora más cargada: 00:00–01:00 con ~11.2k req/h (banda ~9.0k–13.4k).

checkout

Promedio por minuto: ~267 req/min (plano).

Banda de incertidumbre media: ±~41 (ancho ~82.4).

Límite superior típico por minuto: ~303.

Hora más cargada: 00:00–01:00 con ~16.0k req/h (banda 13.8k–18.2k).

search

Promedio por minuto: ~347 req/min (plano).

Banda de incertidumbre media: ±~44 (ancho ~88.0).

Límite superior típico por minuto: ~385.

Hora más cargada: 00:00–01:00 con ~20.8k req/h (banda 18.5k–23.2k).