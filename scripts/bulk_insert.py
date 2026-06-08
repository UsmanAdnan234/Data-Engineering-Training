#!/usr/bin/env python3
"""
Bulk Insert Script — insert millions of records into cart_db using Faker + execute_values.

Usage:
    python scripts/bulk_insert.py --table users   --count 1000000
    python scripts/bulk_insert.py --table all     --count 500000 --batch-size 5000
    python scripts/bulk_insert.py --table variants --count 100000 --db-url postgresql://...

Tables: users | products | variants | all
"""

import argparse
import os
import sys
import time

import psycopg2
from faker import Faker
from psycopg2.extras import execute_values

fake = Faker()


def connect(db_url: str):
    try:
        return psycopg2.connect(db_url)
    except psycopg2.OperationalError as e:
        print(f"ERROR: Cannot connect to database.\n{e}")
        sys.exit(1)


def bulk_insert_users(conn, total: int, batch_size: int) -> None:
    print(f"\n[users] Inserting {total:,} rows in batches of {batch_size:,}...")
    inserted = 0
    start = time.perf_counter()

    with conn.cursor() as cur:
        while inserted < total:
            n = min(batch_size, total - inserted)
            rows = [
                (
                    fake.name(),
                    fake.unique.email(),
                    fake.numerify("03#########"),
                )
                for _ in range(n)
            ]
            execute_values(
                cur,
                "INSERT INTO users (name, email, phone) VALUES %s ON CONFLICT DO NOTHING",
                rows,
            )
            inserted += n
            elapsed = time.perf_counter() - start
            rate = inserted / elapsed if elapsed > 0 else 0
            print(f"  {inserted:>10,} / {total:,}   ({rate:,.0f} rows/s)", end="\r")

    conn.commit()
    elapsed = time.perf_counter() - start
    print(f"\n[users] Done. {inserted:,} rows in {elapsed:.1f}s  ({inserted/elapsed:,.0f} rows/s)")


def bulk_insert_products(conn, total: int, batch_size: int) -> None:
    print(f"\n[products] Inserting {total:,} rows in batches of {batch_size:,}...")
    inserted = 0
    start = time.perf_counter()

    categories = ["T-Shirt", "Jeans", "Sneakers", "Hoodie", "Cap", "Jacket", "Shorts",
                  "Dress", "Skirt", "Coat", "Vest", "Blouse", "Sweater", "Sandals", "Boots"]

    with conn.cursor() as cur:
        while inserted < total:
            n = min(batch_size, total - inserted)
            rows = [
                (f"{fake.random_element(categories)} — {fake.word().capitalize()} Edition",)
                for _ in range(n)
            ]
            execute_values(
                cur,
                "INSERT INTO products (name) VALUES %s",
                rows,
            )
            inserted += n
            elapsed = time.perf_counter() - start
            rate = inserted / elapsed if elapsed > 0 else 0
            print(f"  {inserted:>10,} / {total:,}   ({rate:,.0f} rows/s)", end="\r")

    conn.commit()
    elapsed = time.perf_counter() - start
    print(f"\n[products] Done. {inserted:,} rows in {elapsed:.1f}s  ({inserted/elapsed:,.0f} rows/s)")


def bulk_insert_variants(conn, total: int, batch_size: int) -> None:
    print(f"\n[product_variants] Inserting {total:,} rows in batches of {batch_size:,}...")

    with conn.cursor() as cur:
        cur.execute("SELECT product_id FROM products ORDER BY product_id")
        product_ids = [row[0] for row in cur.fetchall()]

    if not product_ids:
        print("  ERROR: No products found. Insert products first (--table products).")
        return

    colors = ["White", "Black", "Red", "Blue", "Green", "Gray", "Navy", "Beige", "Brown", "Pink"]
    sizes  = ["XS", "S", "M", "L", "XL", "XXL", "28", "30", "32", "34", "36", "38", "40", "42", "44", "Free"]

    inserted = 0
    start = time.perf_counter()

    with conn.cursor() as cur:
        while inserted < total:
            n = min(batch_size, total - inserted)
            rows = [
                (
                    fake.random_element(product_ids),
                    fake.random_element(colors),
                    fake.random_element(sizes),
                    round(fake.pyfloat(min_value=100, max_value=10000, right_digits=2), 2),
                    fake.random_int(min=0, max=500),
                )
                for _ in range(n)
            ]
            execute_values(
                cur,
                "INSERT INTO product_variants (product_id, color, size, price, stock) VALUES %s",
                rows,
            )
            inserted += n
            elapsed = time.perf_counter() - start
            rate = inserted / elapsed if elapsed > 0 else 0
            print(f"  {inserted:>10,} / {total:,}   ({rate:,.0f} rows/s)", end="\r")

    conn.commit()
    elapsed = time.perf_counter() - start
    print(f"\n[product_variants] Done. {inserted:,} rows in {elapsed:.1f}s  ({inserted/elapsed:,.0f} rows/s)")


def main():
    parser = argparse.ArgumentParser(description="Bulk insert fake records into cart_db.")
    parser.add_argument(
        "--table",
        choices=["users", "products", "variants", "all"],
        required=True,
        help="Which table(s) to populate",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1_000_000,
        help="Number of rows to insert (default: 1,000,000)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10_000,
        help="Rows per INSERT batch (default: 10,000)",
    )
    parser.add_argument(
        "--db-url",
        default=os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/cart_db"),
        help="PostgreSQL connection URL",
    )
    args = parser.parse_args()

    print("=" * 60)
    print(f"  Bulk Insert  |  table={args.table}  |  count={args.count:,}")
    print(f"  DB: {args.db_url[:50]}...")
    print("=" * 60)

    conn = connect(args.db_url)

    total_start = time.perf_counter()

    if args.table in ("users", "all"):
        bulk_insert_users(conn, args.count, args.batch_size)

    if args.table in ("products", "all"):
        bulk_insert_products(conn, args.count, args.batch_size)

    if args.table in ("variants", "all"):
        bulk_insert_variants(conn, args.count, args.batch_size)

    conn.close()

    total_elapsed = time.perf_counter() - total_start
    print(f"\n{'='*60}")
    print(f"  All done in {total_elapsed:.1f}s total")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
