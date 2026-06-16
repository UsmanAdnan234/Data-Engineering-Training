"""
Gold Layer — Business metrics aggregated from silver data using PySpark.
Produces 4 analytical datasets ready for reporting.
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
        .appName("GoldAggregate")
        .master("local[1]")
        .config("spark.driver.memory", "1g")
        .config("spark.driver.maxResultSize", "512m")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.executor.memory", "1g")
        .getOrCreate()
    )

def load_silver(client, spark: SparkSession, table: str, run_date: str) -> DataFrame:
    key  = f"silver/{table}/run_date={run_date}/{table}.parquet"
    resp = client.get_object(Bucket=S3_BUCKET, Key=key)
    df   = spark.createDataFrame(pd.read_parquet(BytesIO(resp["Body"].read())))
    logger.info(f"  Loaded silver/{table}: {df.count():,} rows")
    return df


def upload_gold(client, df: DataFrame, name: str, run_date: str) -> None:
    key = f"gold/{name}/run_date={run_date}/{name}.parquet"
    with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tmp:
        path = tmp.name
    df.toPandas().to_parquet(path, index=False, engine="pyarrow")
    with open(path, "rb") as f:
        client.put_object(Bucket=S3_BUCKET, Key=key, Body=f.read())
    os.unlink(path)
    logger.info(f"  Uploaded gold/{name} → s3://{S3_BUCKET}/{key}  ({df.count():,} rows)")


def main():
    run_date = datetime.utcnow().strftime("%Y-%m-%d")
    logger.info(f"=== Gold aggregation started | run_date={run_date} ===")

    client = s3_client()
    spark  = get_spark()

    
    users      = load_silver(client, spark, "users",            run_date)
    products   = load_silver(client, spark, "products",         run_date)
    variants   = load_silver(client, spark, "product_variants", run_date)
    carts      = load_silver(client, spark, "carts",            run_date)
    cart_items = load_silver(client, spark, "cart_items",       run_date)


    cart_summary = (
        cart_items
        .join(variants, "variant_id")
        .withColumn("line_total", F.col("quantity") * F.col("price"))
        .groupBy("cart_id")
        .agg(
            F.round(F.sum("line_total"), 2).alias("total_value"),
            F.sum("quantity").alias("total_items"),
            F.countDistinct("variant_id").alias("unique_products"),
        )
        .join(carts, "cart_id")
        .join(users.select("user_id", "name", "email"), "user_id")
    )
    upload_gold(client, cart_summary, "cart_summary", run_date)

    
    user_activity = (
        carts
        .groupBy("user_id")
        .agg(
            F.count("cart_id").alias("total_carts"),
            F.sum(F.when(F.col("status") == "checked_out", 1).otherwise(0)).alias("checked_out_carts"),
            F.sum(F.when(F.col("status") == "active",      1).otherwise(0)).alias("active_carts"),
        )
        .join(users.select("user_id", "name", "email"), "user_id")
    )
    upload_gold(client, user_activity, "user_activity", run_date)

    
    product_popularity = (
        cart_items
        .join(variants, "variant_id")
        .join(products, "product_id")
        .groupBy("product_id", "name")
        .agg(
            F.sum("quantity").alias("total_units_ordered"),
            F.countDistinct("cart_id").alias("times_added_to_cart"),
            F.round(F.sum(F.col("quantity") * F.col("price")), 2).alias("total_revenue"),
        )
        .orderBy(F.col("total_units_ordered").desc())
    )
    upload_gold(client, product_popularity, "product_popularity", run_date)

    variant_stock = (
        variants
        .join(products, "product_id")
        .groupBy("product_id", "name")
        .agg(
            F.sum("stock").alias("total_stock"),
            F.count("variant_id").alias("variant_count"),
            F.round(F.avg("price"), 2).alias("avg_price"),
            F.min("price").alias("min_price"),
            F.max("price").alias("max_price"),
        )
    )
    upload_gold(client, variant_stock, "variant_stock_summary", run_date)

    spark.stop()
    logger.info("=== Gold aggregation complete ===")


if __name__ == "__main__":
    main()
