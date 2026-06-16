"""
ETL Pipeline DAG — Medallion Architecture: Bronze → Silver → Gold

Schedule: daily at 02:00 UTC
Bronze: extract raw tables from RDS → S3
Silver: clean and validate with PySpark → S3
Gold:   aggregate business metrics with PySpark → S3
"""
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta

sys.path.insert(0, "/opt/airflow")

from airflow import DAG
from airflow.operators.python import PythonOperator
from notifications.slack_notifier import notify_failure, notify_retry, notify_success

default_args = {
    "owner":          "data-team",
    "retries":        0,
    "retry_delay":    timedelta(minutes=5),
    "email_on_retry": False,
}

MAX_RETRIES = 3


def run_script(script_name: str, stage: str) -> None:
    script_path = f"/opt/airflow/scripts/{script_name}"
    pipeline_name = f"etl_pipeline → {stage}"

    for attempt in range(1, MAX_RETRIES + 1):
        start = time.time()
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            env=os.environ.copy(),
        )
        print(result.stdout)
        duration = time.time() - start

        if result.returncode == 0:
            notify_success(pipeline_name=pipeline_name, duration_sec=duration)
            return

        error = RuntimeError(
            f"{script_name} failed (exit {result.returncode})\n{result.stderr}"
        )
        print("STDERR:", result.stderr)

        if attempt < MAX_RETRIES:
            notify_retry(pipeline_name=pipeline_name, attempt=attempt, max_attempts=MAX_RETRIES, error=error)
            time.sleep(10 * attempt)
        else:
            notify_failure(pipeline_name=pipeline_name, error=error, stage=stage)
            raise error


with DAG(
    dag_id="etl_pipeline",
    description="RDS → Bronze → Silver → Gold (Medallion Architecture)",
    default_args=default_args,
    start_date=datetime(2026, 6, 1),
    schedule="0 2 * * *",
    catchup=False,
    tags=["etl", "medallion", "s3"],
) as dag:

    bronze_task = PythonOperator(
        task_id="bronze_extract",
        python_callable=lambda: run_script("bronze_extract.py", stage="Bronze"),
    )

    silver_task = PythonOperator(
        task_id="silver_transform",
        python_callable=lambda: run_script("silver_transform.py", stage="Silver"),
    )

    gold_task = PythonOperator(
        task_id="gold_aggregate",
        python_callable=lambda: run_script("gold_aggregate.py", stage="Gold"),
    )

    bronze_task >> silver_task >> gold_task