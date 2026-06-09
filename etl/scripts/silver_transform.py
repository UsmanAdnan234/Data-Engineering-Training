"""
Silver Layer — Clean and validate bronze data using PySpark.
Removes nulls, deduplicates, standardises formats.
"""
import logging
import os
import tempfile
from datetime import datetime
from io import BytesIO

import boto3
import pandas as pd
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

S3_BUCKET  = os.environ["S3_BUCKET"]
AWS_REGION = os.environ.get("AWS_DEFAULT_REGION", "eu-north-1")


def s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name=AWS_REGION,
    )


def get_spark() -> SparkSession:
    return (
        SparkSession.builder
        .appName("SilverTransform")
        .master("local[*]")
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )


def download_bronze(client, table: str, run_date: str) -> pd.DataFrame:
    key = f"bronze/{table}/run_date={run_date}/{table}.parquet"
    resp = client.get_object(Bucket=S3_BUCKET, Key=key)
    df   = pd.read_parquet(BytesIO(resp["Body"].read()))
    logger.info(f"  {table} bronze rows: {len(df):,}")
    return df


def upload_silver(client, df_spark: DataFrame, table: str, run_date: str) -> None:
    key = f"silver/{table}/run_date={run_date}/{table}.parquet"
    with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tmp:
        path = tmp.name
    df_spark.toPandas().to_parquet(path, index=False, engine="pyarrow")
    with open(path, "rb") as f:
        client.put_object(Bucket=S3_BUCKET, Key=key, Body=f.read())
    os.unlink(path)
    logger.info(f"  Uploaded → s3://{S3_BUCKET}/{key}")


# ── Per-table transformations ────────────────────────────────────────────────

def clean_users(spark: SparkSession, raw: pd.DataFrame) -> DataFrame:
    df = spark.createDataFrame(raw)
    df = df.dropDuplicates(["user_id"])
    df = df.filter(
        F.col("name").isNotNull() &
        F.col("email").isNotNull() &
        F.col("phone").isNotNull()
    )
    df = df.withColumn("email", F.lower(F.trim(F.col("email"))))
    df = df.withColumn("name",  F.trim(F.col("name")))
    return df


def clean_products(spark: SparkSession, raw: pd.DataFrame) -> DataFrame:
    df = spark.createDataFrame(raw)
    df = df.dropDuplicates(["product_id"])
    df = df.filter(F.col("name").isNotNull())
    df = df.withColumn("name", F.trim(F.col("name")))
    return df


def clean_product_variants(spark: SparkSession, raw: pd.DataFrame) -> DataFrame:
    df = spark.createDataFrame(raw)
    df = df.dropDuplicates(["variant_id"])
    df = df.filter(
        F.col("price").isNotNull() & (F.col("price") > 0) &
        F.col("stock").isNotNull() & (F.col("stock") >= 0)
    )
    return df


def clean_carts(spark: SparkSession, raw: pd.DataFrame) -> DataFrame:
    df = spark.createDataFrame(raw)
    df = df.dropDuplicates(["cart_id"])
    df = df.filter(F.col("status").isin("active", "checked_out"))
    return df


def clean_cart_items(spark: SparkSession, raw: pd.DataFrame) -> DataFrame:
    df = spark.createDataFrame(raw)
    df = df.dropDuplicates(["item_id"])
    df = df.filter(F.col("quantity").isNotNull() & (F.col("quantity") > 0))
    return df


TRANSFORMS = {
    "users":            clean_users,
    "products":         clean_products,
    "product_variants": clean_product_variants,
    "carts":            clean_carts,
    "cart_items":       clean_cart_items,
}


def main():
    run_date = datetime.utcnow().strftime("%Y-%m-%d")
    logger.info(f"=== Silver transformation started | run_date={run_date} ===")

    client = s3_client()
    spark  = get_spark()

    for table, transform_fn in TRANSFORMS.items():
        logger.info(f"Transforming: {table}")
        raw = download_bronze(client, table, run_date)
        if raw.empty:
            logger.warning(f"  {table} bronze is empty — skipping")
            continue
        df_clean = transform_fn(spark, raw)
        logger.info(f"  {table} silver rows: {df_clean.count():,}")
        upload_silver(client, df_clean, table, run_date)

    spark.stop()
    logger.info("=== Silver transformation complete ===")


if __name__ == "__main__":
    main()
