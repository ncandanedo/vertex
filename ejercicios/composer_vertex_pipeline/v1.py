from datetime import datetime
from airflow import DAG
from airflow.providers.google.cloud.operators.vertex_ai.pipeline_job import RunPipelineJobOperator

PROJECT = "formacionaiops-476808"
VERTEX_REGION = "europe-west1"   # región de Vertex/Composer
BQ_LOCATION  = "EU"              # tu dataset está en EU
BUCKET = "europe-west1-test-57b1047f-bucket"
PIPELINE_ROOT = f"gs://{BUCKET}/vertex-pipelines"

CREATE_SPEC = "https://us-kfp.pkg.dev/ml-pipeline/google-cloud-registry/bigquery-create-model-job/sha256:cca23c8174ddcc6c9ddc4fdf5611ae6418708d8216327368d61ac3b409ce4348"

DATASET = "clasificador_logs_flask"
TABLE = f"{PROJECT}.{DATASET}.logs_minutely"
MODEL_ID = "mdl_requests_arima"

SQL_CREATE_MODEL = f"""
CREATE OR REPLACE MODEL `{PROJECT}.{DATASET}.{MODEL_ID}`
OPTIONS(
  MODEL_TYPE='ARIMA_PLUS',
  TIME_SERIES_TIMESTAMP_COL='ts',
  TIME_SERIES_DATA_COL='requests',
  TIME_SERIES_ID_COL='service'
) AS
SELECT ts, requests, service
FROM `{TABLE}`;
"""

with DAG(
    dag_id="vertex_create_bqml_model",
    start_date=datetime(2025, 11, 22),
    schedule_interval=None,
    catchup=False,
    tags=["vertex","bqml","create-model"],
) as dag:

    create_model = RunPipelineJobOperator(
        task_id="create_bqml_model",
        project_id=PROJECT,
        region=VERTEX_REGION,
        template_path=CREATE_SPEC,
        pipeline_root=PIPELINE_ROOT,
        display_name="bqml-create-model-arima",
        parameter_values={
            "project": PROJECT,
            "location": BQ_LOCATION,               # ⚠️ BigQuery en EU
            "labels": {"owner":"rafa","purpose":"create-bqml-model"},
            "job_configuration_query": {"useLegacySql": False},
            "query_parameters": [],
            "query": SQL_CREATE_MODEL,
        },
        enable_caching=False,
    )
