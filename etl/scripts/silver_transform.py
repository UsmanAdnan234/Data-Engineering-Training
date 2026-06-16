"""
Silver Layer — Clean and validate bronze data using pandas.
Removes nulls, deduplicates, standardises formats.
"""
import logging
import os
import tempfile
from datetime import datetime
from io import BytesIO

import boto3
import pandas as pd

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


def download_bronze(client, table: str, run_date: str) -> pd.DataFrame:
    key  = f"bronze/{table}/run_date={run_date}/{table}.parquet"
    resp = client.get_object(Bucket=S3_BUCKET, Key=key)
    df   = pd.read_parquet(BytesIO(resp["Body"].read()))
    logger.info(f"  {table} bronze rows: {len(df):,}")
    return df


def upload_silver(client, df: pd.DataFrame, table: str, run_date: str) -> None:
    key = f"silver/{table}/run_date={run_date}/{table}.parquet"
    with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tmp:
        path = tmp.name
    df.to_parquet(path, index=False, engine="pyarrow")
    with open(path, "rb") as f:
        client.put_object(Bucket=S3_BUCKET, Key=key, Body=f.read())
    os.unlink(path)
    logger.info(f"  Uploaded → s3://{S3_BUCKET}/{key}")


def clean_users(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(subset=["user_id"])
    df = df.dropna(subset=["name", "email", "phone"])
    df["email"] = df["email"].str.lower().str.strip()
    df["name"]  = df["name"].str.strip()
    return df


def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(subset=["product_id"])
    df = df.dropna(subset=["name"])
    df["name"] = df["name"].str.strip()
    return df


def clean_product_variants(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(subset=["variant_id"])
    df = df.dropna(subset=["price", "stock"])
    df = df[(df["price"] > 0) & (df["stock"] >= 0)]
    return df


def clean_carts(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(subset=["cart_id"])
    df = df[df["status"].isin(["active", "checked_out"])]
    return df


def clean_cart_items(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(subset=["item_id"])
    df = df.dropna(subset=["quantity"])
    df = df[df["quantity"] > 0]
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

    for table, transform_fn in TRANSFORMS.items():
        logger.info(f"Transforming: {table}")
        raw = download_bronze(client, table, run_date)
        if raw.empty:
            logger.warning(f"  {table} bronze is empty — skipping")
            continue
        df_clean = transform_fn(raw)
        logger.info(f"  {table} silver rows: {len(df_clean):,}")
        upload_silver(client, df_clean, table, run_date)

    logger.info("=== Silver transformation complete ===")


if __name__ == "__main__":
    main()
