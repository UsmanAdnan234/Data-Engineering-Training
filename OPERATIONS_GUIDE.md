# Operations Guide — Cart API Data Engineering Project

**Project:** Cart API — Medallion Architecture ETL Pipeline  
**Author:** Data Engineering Team  
**Date:** June 2026  

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Will Data Be Lost When Stopped?](#2-will-data-be-lost-when-stopped)
3. [How to Stop Everything](#3-how-to-stop-everything)
4. [How to Restart Everything](#4-how-to-restart-everything)
5. [Quick Command Reference](#5-quick-command-reference)

---

## 1. Project Overview

This project consists of the following components:

| Component | What It Does | Where It Runs |
|-----------|-------------|---------------|
| **Cart API (FastAPI)** | REST API for cart management | Blue + Green EC2 on AWS |
| **PostgreSQL (RDS)** | Stores all cart, user, product data | AWS RDS |
| **ALB (Load Balancer)** | Routes traffic between blue and green | AWS ALB |
| **CI Pipeline** | Runs lint and tests on every push | GitHub Actions |
| **CD Pipeline** | Deploys app using blue-green strategy | GitHub Actions → EC2 |
| **Airflow + PySpark** | Runs ETL pipeline (Bronze→Silver→Gold) | Your Laptop (Docker) |
| **S3 Data Lake** | Stores parquet files (bronze/silver/gold) | AWS S3 |
| **Athena** | SQL queries on S3 parquet data | AWS Console |

### Architecture Flow

```
GitHub Push
    │
    ▼
CI (lint + tests)
    │
    ▼
CD (blue-green deploy)
    │
    ▼
EC2 Blue / EC2 Green ──── ALB ──── Users
    │
    ▼
RDS PostgreSQL
    │
    ▼
Airflow DAG (laptop)
    ├── Bronze: RDS → S3 raw parquet
    ├── Silver: clean + validate → S3
    └── Gold: aggregate metrics → S3
                │
                ▼
            AWS Athena (SQL queries)
```

---

## 2. Will Data Be Lost When Stopped?

**Short answer: NO. Stopping is like pausing. Nothing is deleted.**

| Component | Data Lost When Stopped? | Explanation |
|-----------|------------------------|-------------|
| **RDS (PostgreSQL)** | ❌ No | Data stored on EBS disk, persists forever |
| **EC2 (blue + green)** | ❌ No | App code on EBS disk, persists when stopped |
| **S3 (parquet files)** | ❌ No | S3 has no concept of stopping, always persists |
| **Athena table definitions** | ❌ No | Stored in AWS Glue catalog, always available |
| **Airflow DAG history** | ❌ No | Stored in Docker volume on laptop |
| **GitHub code** | ❌ No | Always available on GitHub |

> **Important:** Stopping ≠ Deleting. Only if you click **Terminate** (EC2) or **Delete** (RDS) will data be lost.

---

## 3. How to Stop Everything

Stop in this order to avoid errors.

---

### Step 1 — Stop Airflow

**Where:** Your laptop — PowerShell

```powershell
cd "C:\Users\HP 840 G7\OneDrive\Desktop\DE-internship\Data-Engineering-Training\etl"
docker-compose -f docker-compose.airflow.yml down
```

**Verify:** Docker Desktop shows no running Airflow containers.

---

### Step 2 — Stop EC2 Instances (Blue and Green)

**Where:** AWS Console in browser

```
1. Go to: AWS Console → EC2 → Instances
2. Tick the checkbox next to the BLUE instance
3. Click: Actions → Instance State → Stop
4. Click: Stop (confirm)
5. Repeat for the GREEN instance
6. Wait until both show status: "Stopped"
```

---

### Step 3 — Stop RDS Database

**Where:** AWS Console in browser

```
1. Go to: AWS Console → RDS → Databases
2. Click on your database (cart-db)
3. Click: Actions → Stop temporarily
4. Click: Stop (confirm)
5. Wait until status shows: "Stopped"
```

> **Note:** AWS automatically restarts RDS after 7 days. If you see it running again after a week, just stop it again.

---

### Step 4 — Nothing else to stop

| Component | Action |
|-----------|--------|
| ALB | Leave it — tiny cost, no concept of stopping |
| S3 | Leave it — always on, no cost unless data is read |
| Athena | Leave it — serverless, only charges when you run queries |
| GitHub Actions | Leave it — only runs when you push code |

---

## 4. How to Restart Everything

Restart in this exact order — each step depends on the previous one.

---

### Step 1 — Start RDS Database

**Where:** AWS Console in browser

```
1. Go to: AWS Console → RDS → Databases
2. Click on your database (cart-db)
3. Click: Actions → Start
4. Wait 3-5 minutes until status shows: "Available"
```

> **Do not proceed to Step 2 until RDS is Available.** The app needs the database.

---

### Step 2 — Start EC2 Instances (Blue and Green)

**Where:** AWS Console in browser

```
1. Go to: AWS Console → EC2 → Instances
2. Tick the checkbox next to the BLUE instance
3. Click: Actions → Instance State → Start
4. Repeat for the GREEN instance
5. Wait until both show:
   - Status: "Running"
   - Status checks: "2/2 checks passed"
```

> **Note:** After starting, EC2 instances get a NEW public IP address. But the ALB URL stays the same — always use the ALB URL, not the EC2 IP directly.

---

### Step 3 — Deploy App via CI/CD

**Where:** Your laptop — PowerShell

```powershell
cd "C:\Users\HP 840 G7\OneDrive\Desktop\DE-internship\Data-Engineering-Training"
git commit --allow-empty -m "chore: trigger deploy"
git push origin main
```

**Then monitor on GitHub:**
```
GitHub → your repo → Actions tab
→ Wait for CI to pass (2-3 minutes)
→ CD will auto-trigger after CI passes
→ Wait for CD to pass (3-5 minutes)
```

**Verify app is running:**
```powershell
curl http://cart-api-alb-2053330170.eu-north-1.elb.amazonaws.com/health
```
Expected response: `{"status": "ok"}`

---

### Step 4 — Start Airflow

**Where:** Your laptop — PowerShell

```powershell
cd "C:\Users\HP 840 G7\OneDrive\Desktop\DE-internship\Data-Engineering-Training\etl"
docker-compose -f docker-compose.airflow.yml up -d
```

Wait 1-2 minutes, then open in browser:
```
http://localhost:8080
```
Login credentials:
- Username: `admin`
- Password: `admin`

---

### Step 5 — Run ETL Pipeline

**Where:** Airflow browser UI at `http://localhost:8080`

```
1. Click on "DAGs" in the top menu
2. Find "etl_pipeline" in the list
3. Click the toggle to enable it (if it shows paused)
4. Click the ▶ (Trigger DAG) button on the right
5. Click "Trigger" to confirm
```

**Monitor progress:**
```
Click on "etl_pipeline" → click the latest run → Graph view
```

Tasks run in order:
- `bronze_extract` → copies RDS data to S3 (~2-3 mins)
- `silver_transform` → cleans data, saves to S3 (~3-5 mins)  
- `gold_aggregate` → creates business metrics, saves to S3 (~3-5 mins)

All 3 tasks should turn **green**.

---

### Step 6 — Run Load Test

**Where:** Your laptop — PowerShell

```powershell
cd "C:\Users\HP 840 G7\OneDrive\Desktop\DE-internship\Data-Engineering-Training"
newman run "postman/collections/load_test.postman_collection.json" --iteration-count 9999 --delay-request 100 --reporters cli
```

This runs ~10 minutes of requests against the ALB to test performance.

To stop early: press `Ctrl + C`

---

### Step 7 — Check Data in Athena

**Where:** AWS Console in browser

```
1. Go to: AWS Console → Athena → Query editor
2. Make sure database is set to "datalake" (left sidebar)
```

Run these queries to verify data is present:

```sql
-- Check cart summaries
SELECT * FROM datalake.gold_cart_summary LIMIT 20;

-- Top 10 best selling products
SELECT name, total_units_ordered, total_revenue
FROM datalake.gold_product_popularity
ORDER BY total_units_ordered DESC
LIMIT 10;

-- Most active users
SELECT name, email, total_carts, checked_out_carts
FROM datalake.gold_user_activity
ORDER BY total_carts DESC
LIMIT 10;

-- Stock levels per product
SELECT name, total_stock, variant_count, avg_price
FROM datalake.gold_variant_stock_summary
ORDER BY total_stock DESC
LIMIT 10;
```

---

## 5. Quick Command Reference

### Laptop PowerShell Commands

| Action | Command |
|--------|---------|
| Start Airflow | `cd ...\etl` then `docker-compose -f docker-compose.airflow.yml up -d` |
| Stop Airflow | `cd ...\etl` then `docker-compose -f docker-compose.airflow.yml down` |
| Trigger CI/CD deploy | `git commit --allow-empty -m "chore: trigger" && git push origin main` |
| Run load test | `newman run "postman/collections/load_test.postman_collection.json" --iteration-count 9999 --delay-request 100 --reporters cli` |
| Check app health | `curl http://cart-api-alb-2053330170.eu-north-1.elb.amazonaws.com/health` |

### AWS Console Actions (browser)

| Action | Path |
|--------|------|
| Start/Stop EC2 | EC2 → Instances → select → Actions → Instance State |
| Start/Stop RDS | RDS → Databases → select → Actions → Start/Stop |
| View CI/CD runs | GitHub → repo → Actions tab |
| Query data | Athena → Query editor |
| View S3 files | S3 → cart-api-datalake |

### Important URLs

| Service | URL |
|---------|-----|
| Live API | `http://cart-api-alb-2053330170.eu-north-1.elb.amazonaws.com` |
| API Docs | `http://cart-api-alb-2053330170.eu-north-1.elb.amazonaws.com/docs` |
| Airflow UI | `http://localhost:8080` (only when Airflow is running on laptop) |
| GitHub Actions | `https://github.com/<your-username>/<your-repo>/actions` |

---

## Free Tier Usage Warning

| Service | Free Tier Limit | Tip |
|---------|----------------|-----|
| EC2 | 750 hrs/month per instance | You have 2 instances = 375 hrs each. Stop when not using. |
| RDS | 750 hrs/month | Stop when not using. |
| S3 | 5 GB storage | You have small parquet files, well within limits. |
| Athena | 1 TB queries/month | You're well within limits. |
| ALB | **Not free tier** | Costs ~$16-20/month. Biggest cost item. |

> **Always stop EC2 and RDS when not actively working on the project.**
