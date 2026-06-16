"""
Gold Layer — Business metrics aggregated from silver data using pandas.
Produces 4 analytical datasets ready for reporting.
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


def load_silver(client, table: str, run_date: str) -> pd.DataFrame:
    key  = f"silver/{table}/run_date={run_date}/{table}.parquet"
    resp = client.get_object(Bucket=S3_BUCKET, Key=key)
    df   = pd.read_parquet(BytesIO(resp["Body"].read()))
    logger.info(f"  Loaded silver/{table}: {len(df):,} rows")
    return df


def upload_gold(client, df: pd.DataFrame, name: str, run_date: str) -> None:
    key = f"gold/{name}/run_date={run_date}/{name}.parquet"
    with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tmp:
        path = tmp.name
    df.to_parquet(path, index=False, engine="pyarrow")
    with open(path, "rb") as f:
        client.put_object(Bucket=S3_BUCKET, Key=key, Body=f.read())
    os.unlink(path)
    logger.info(f"  Uploaded gold/{name} → s3://{S3_BUCKET}/{key}  ({len(df):,} rows)")


def main():
    run_date = datetime.utcnow().strftime("%Y-%m-%d")
    logger.info(f"=== Gold aggregation started | run_date={run_date} ===")

    client   = s3_client()
    users    = load_silver(client, "users",            run_date)
    products = load_silver(client, "products",         run_date)
    variants = load_silver(client, "product_variants", run_date)
    carts    = load_silver(client, "carts",            run_date)
    items    = load_silver(client, "cart_items",       run_date)

    # cart_summary
    merged = items.merge(variants[["variant_id", "price"]], on="variant_id")
    merged["line_total"] = merged["quantity"] * merged["price"]
    cart_summary = (
        merged.groupby("cart_id")
        .agg(
            total_value=("line_total", "sum"),
            total_items=("quantity",   "sum"),
            unique_products=("variant_id", "nunique"),
        )
        .reset_index()
    )
    cart_summary["total_value"] = cart_summary["total_value"].round(2)
    cart_summary = cart_summary.merge(carts[["cart_id", "user_id", "status"]], on="cart_id")
    cart_summary = cart_summary.merge(users[["user_id", "name", "email"]], on="user_id")
    upload_gold(client, cart_summary, "cart_summary", run_date)

    # user_activity
    user_activity = (
        carts.groupby("user_id")
        .agg(
            total_carts=("cart_id", "count"),
            checked_out_carts=("status", lambda x: (x == "checked_out").sum()),
            active_carts=("status",      lambda x: (x == "active").sum()),
        )
        .reset_index()
    )
    user_activity = user_activity.merge(users[["user_id", "name", "email"]], on="user_id")
    upload_gold(client, user_activity, "user_activity", run_date)

    # product_popularity
    merged2 = items.merge(variants[["variant_id", "product_id", "price"]], on="variant_id")
    merged2 = merged2.merge(products[["product_id", "name"]], on="product_id")
    merged2["revenue"] = merged2["quantity"] * merged2["price"]
    product_popularity = (
        merged2.groupby(["product_id", "name"])
        .agg(
            total_units_ordered=("quantity",  "sum"),
            times_added_to_cart=("cart_id",   "nunique"),
            total_revenue=("revenue",         "sum"),
        )
        .reset_index()
        .sort_values("total_units_ordered", ascending=False)
    )
    product_popularity["total_revenue"] = product_popularity["total_revenue"].round(2)
    upload_gold(client, product_popularity, "product_popularity", run_date)

    # variant_stock_summary
    merged3 = variants.merge(products[["product_id", "name"]], on="product_id")
    variant_stock = (
        merged3.groupby(["product_id", "name"])
        .agg(
            total_stock=("stock",      "sum"),
            variant_count=("variant_id", "count"),
            avg_price=("price",        "mean"),
            min_price=("price",        "min"),
            max_price=("price",        "max"),
        )
        .reset_index()
    )
    variant_stock["avg_price"] = variant_stock["avg_price"].round(2)
    upload_gold(client, variant_stock, "variant_stock_summary", run_date)

    logger.info("=== Gold aggregation complete ===")


if __name__ == "__main__":
    main()
