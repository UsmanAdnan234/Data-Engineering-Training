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
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner":          "data-team",
    "retries":        1,
    "retry_delay":    timedelta(minutes=5),
    "email_on_retry": False,
}


def run_script(script_name: str) -> None:
    script_path = f"/opt/airflow/scripts/{script_name}"
    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True,
        env=os.environ.copy(),
    )
    print(result.stdout)
    if result.returncode != 0:
        print("STDERR:", result.stderr)
        raise RuntimeError(f"{script_name} failed (exit {result.returncode})")


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
        python_callable=lambda: run_script("bronze_extract.py"),
    )

    silver_task = PythonOperator(
        task_id="silver_transform",
        python_callable=lambda: run_script("silver_transform.py"),
    )

    gold_task = PythonOperator(
        task_id="gold_aggregate",
        python_callable=lambda: run_script("gold_aggregate.py"),
    )

    bronze_task >> silver_task >> gold_task
