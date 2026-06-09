"""
Bronze Layer — Extract raw data from RDS and upload to S3 as Parquet.
No transformations — raw data exactly as it exists in the database.
"""
import logging
import os
from datetime import datetime
from io import BytesIO

import boto3
import pandas as pd
import psycopg2

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DATABASE_URL = os.environ["DATABASE_URL"]
S3_BUCKET    = os.environ["S3_BUCKET"]
AWS_REGION   = os.environ.get("AWS_DEFAULT_REGION", "eu-north-1")

TABLES = ["users", "products", "product_variants", "carts", "cart_items"]


def s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name=AWS_REGION,
    )


def extract_table(conn, table: str) -> pd.DataFrame:
    logger.info(f"Extracting {table}...")
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    logger.info(f"  {table}: {len(df):,} rows")
    return df


def upload_parquet(client, df: pd.DataFrame, table: str, run_date: str) -> None:
    key = f"bronze/{table}/run_date={run_date}/{table}.parquet"
    buf = BytesIO()
    df.to_parquet(buf, index=False, engine="pyarrow")
    buf.seek(0)
    client.put_object(Bucket=S3_BUCKET, Key=key, Body=buf.getvalue())
    logger.info(f"  Uploaded → s3://{S3_BUCKET}/{key}")


def main():
    run_date = datetime.utcnow().strftime("%Y-%m-%d")
    logger.info(f"=== Bronze extraction started | run_date={run_date} ===")

    client = s3_client()
    conn   = psycopg2.connect(DATABASE_URL)

    try:
        for table in TABLES:
            df = extract_table(conn, table)
            upload_parquet(client, df, table, run_date)
    finally:
        conn.close()

    logger.info("=== Bronze extraction complete ===")


if __name__ == "__main__":
    main()
