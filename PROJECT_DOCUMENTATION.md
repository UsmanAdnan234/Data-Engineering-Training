# Data Engineering Internship — Complete Project Documentation

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Technology Stack](#2-technology-stack)
3. [System Architecture](#3-system-architecture)
4. [Task 1 — Shopping Cart REST API](#4-task-1--shopping-cart-rest-api)
5. [Task 2 — Database Design & Migrations](#5-task-2--database-design--migrations)
6. [Task 3 — Containerization with Docker](#6-task-3--containerization-with-docker)
7. [Task 4 — CI/CD Pipeline with GitHub Actions](#7-task-4--cicd-pipeline-with-github-actions)
8. [Task 5 — AWS Cloud Deployment with Blue-Green Strategy](#8-task-5--aws-cloud-deployment-with-blue-green-strategy)
9. [Task 6 — ETL Pipeline with Medallion Architecture](#9-task-6--etl-pipeline-with-medallion-architecture)
10. [Task 7 — Airflow Orchestration on EC2](#10-task-7--airflow-orchestration-on-ec2)
11. [Task 8 — Data Analytics with AWS Athena](#11-task-8--data-analytics-with-aws-athena)
12. [Task 9 — API Testing & Load Testing](#12-task-9--api-testing--load-testing)
13. [Challenges & How We Solved Them](#13-challenges--how-we-solved-them)
14. [End-to-End Workflow Summary](#14-end-to-end-workflow-summary)

---

## 1. Project Overview

This project is a full end-to-end Data Engineering system built on AWS. It combines a **production-grade REST API** for a shopping cart application with a fully automated **ETL data pipeline** that extracts data from the API's database, transforms it, and loads it into a data lake for analytics.

The project covers the complete lifecycle of data engineering:
- Building and deploying a backend API
- Automated testing and quality gates
- Zero-downtime cloud deployment
- Automated nightly ETL pipeline
- Data lake with analytics queries

**Public API URL:** `http://cart-api-alb-2053330170.eu-north-1.elb.amazonaws.com`

---

## 2. Technology Stack

| Category | Technology |
|---|---|
| **API Framework** | FastAPI (Python 3.12) |
| **Database** | PostgreSQL 16 (AWS RDS) |
| **ORM / Migrations** | Alembic |
| **Containerization** | Docker, Docker Compose |
| **CI/CD** | GitHub Actions |
| **Cloud Provider** | AWS |
| **Compute** | EC2 (t2.micro, Ubuntu) |
| **Load Balancer** | AWS Application Load Balancer (ALB) |
| **ETL Orchestration** | Apache Airflow 2.9.2 |
| **Data Processing** | PySpark 3.5.3 |
| **Data Lake Storage** | AWS S3 |
| **Analytics** | AWS Athena |
| **Code Quality** | Ruff, Bandit, MyPy, pip-audit |
| **Test Coverage** | pytest, pytest-cov (min 70%) |
| **API Testing** | Postman, Newman CLI |

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DEVELOPER LAPTOP                         │
│  Git Push → GitHub → CI (tests/lint) → CD (deploy to AWS)      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          AWS CLOUD                              │
│                                                                 │
│  Internet → ALB (DNS never changes)                             │
│               ├── cart-api-blue  (EC2 t2.micro)  ←→ RDS        │
│               └── cart-api-green (EC2 t2.micro)  ←→ PostgreSQL │
│                                                                 │
│  airflow-etl (EC2 t2.micro, runs 24/7)                         │
│    └── Apache Airflow (Docker) → reads RDS → writes S3         │
│                                                                 │
│  S3 Bucket: cart-api-datalake                                   │
│    ├── bronze/  (raw data)                                      │
│    ├── silver/  (cleaned data)                                  │
│    └── gold/    (aggregated analytics)                          │
│                                                                 │
│  AWS Athena → queries gold/ parquet files                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Task 1 — Shopping Cart REST API

### What We Built

A fully functional shopping cart REST API following clean architecture with three layers:

- **API Layer** (`app/api/cart.py`) — HTTP endpoints, request/response handling
- **Service Layer** (`app/services/cart_service.py`) — Business logic
- **Repository Layer** (`app/repositories/cart_repository.py`) — Database queries

### API Endpoints

| Method | Endpoint | Description | Success Code |
|---|---|---|---|
| `GET` | `/health` | Health check | 200 |
| `POST` | `/carts` | Create a new cart for a user | 201 |
| `POST` | `/carts/{cart_id}/items` | Add item to cart | 201 |
| `DELETE` | `/carts/{cart_id}/items/{item_id}` | Remove item from cart | 200 |
| `DELETE` | `/carts/{cart_id}` | Delete a cart | 200 |
| `POST` | `/carts/{cart_id}/checkout` | Checkout cart (reduces stock) | 200 |

### Business Rules Enforced

- A user can only have one **active** cart at a time
- Cannot add items to a checked-out cart
- Cannot checkout an empty cart
- Stock is reduced atomically on checkout (prevents overselling)
- All integer IDs validated against PostgreSQL INTEGER max (2,147,483,647)

### Error Handling

All errors return structured JSON with a code and message:

```json
{"error": "CART_NOT_FOUND", "message": "Cart not found"}
```

Custom exceptions were defined for each business rule violation:
`UserNotFoundException`, `CartNotFoundException`, `CartAlreadyExistsException`, `InsufficientStockException`, etc.

### Architecture Pattern — Interface + Implementation

Both service and repository layers use Python interfaces (abstract base classes). This makes the code testable — tests can inject a mock repository without touching the real database.

```python
class ICartService(ABC):
    def createCart(self, userId: int) -> dict: ...

class CartService(ICartService):
    def createCart(self, userId: int) -> dict:
        # real implementation
```

### Structured Logging

Every request and error is logged in a structured format for production observability:

```
[createCart] | status_code=201 | event=cart_created | cart_id=42 | user_id=100
[addItem] | status_code=422 | error=INSUFFICIENT_STOCK | cart_id=42 | variant_id=7
```

---

## 5. Task 2 — Database Design & Migrations

### Database Schema

Five tables in PostgreSQL (AWS RDS):

```
users
  user_id (PK) | name | email (UNIQUE) | phone (UNIQUE)

products
  product_id (PK) | name

product_variants
  variant_id (PK) | product_id (FK) | color | size | price (>0) | stock (>=0)

carts
  cart_id (PK) | user_id (FK) | status ('active' | 'checked_out')

cart_items
  item_id (PK) | cart_id (FK) | variant_id (FK) | quantity (>0)
  UNIQUE (cart_id, variant_id)  ← prevents duplicate items in same cart
```

### Alembic Migrations

Database schema is managed with **Alembic** — a migration tool that tracks schema versions. Instead of running raw SQL manually, Alembic:
- Keeps a version history of every schema change
- Runs migrations automatically on container startup
- Can roll back changes if needed

The app's Dockerfile runs `alembic upgrade head` before starting the server, so the schema is always in sync.

### Database Connection Pooling

Used `psycopg2.ThreadedConnectionPool` with 1–10 connections. Instead of opening a new database connection for every HTTP request (expensive), the pool reuses existing connections. FastAPI's `Depends` injection manages connection lifecycle — connections are returned to the pool after each request.

---

## 6. Task 3 — Containerization with Docker

### Why Docker?

Docker packages the application with all its dependencies into an **image** — a portable unit that runs identically on any machine, whether a developer's laptop or a cloud server.

### Multi-Stage Dockerfile

The production Dockerfile uses two stages to keep the final image small and secure:

**Stage 1 (deps):** Install all build tools and Python packages.
**Stage 2 (production):** Copy only the installed packages from Stage 1. No build tools in the final image = smaller and more secure.

Additional security: the app runs as a **non-root user** (`appuser`, UID 1000) inside the container.

### Docker Compose Files

Three different compose files for different environments:

| File | Purpose |
|---|---|
| `docker-compose.yml` | Local development (API + Postgres together) |
| `docker-compose.prod.yml` | Production on EC2 (API only, connects to RDS) |
| `etl/docker-compose.airflow.yml` | Airflow on the 3rd EC2 (4 services) |

### Airflow Docker Setup

Airflow requires 4 containers to work:

| Container | Role |
|---|---|
| `postgres-airflow` | Airflow's internal metadata database |
| `airflow-init` | One-time setup: runs DB migrations, creates admin user |
| `airflow-webserver` | Browser dashboard (port 8080) |
| `airflow-scheduler` | Watches the clock, triggers DAGs on schedule |

The custom `Dockerfile.airflow` extends the official Airflow image to add **Java 17** (required for PySpark) and installs PySpark, boto3, pandas.

---

## 7. Task 4 — CI/CD Pipeline with GitHub Actions

### What is CI/CD?

**CI (Continuous Integration):** Every time code is pushed to GitHub, automated checks run — tests, linting, security scans. If any check fails, the code cannot be deployed.

**CD (Continuous Deployment):** If all CI checks pass on the main branch, the new code is automatically deployed to production — no manual steps.

### CI Pipeline (`.github/workflows/ci.yml`)

Triggered on: push to main, pull requests, manual trigger.

**4 parallel jobs:**

**Job 1 — Static Analysis:**
- `Ruff` — Python linter and formatter (checks code style, import order)
- `Bandit` — Security scanner (finds hardcoded secrets, SQL injection risks, etc.)
- `pip-audit` — Checks all dependencies for known CVEs (security vulnerabilities)
- `MyPy` — Type checker (catches type errors before runtime)

**Job 2 — Tests + Coverage:**
- Spins up a real PostgreSQL 16 service container
- Runs Alembic migrations against it
- Runs pytest across all test cases
- Coverage must be **≥ 70%** or the job fails
- Uploads coverage report as artifact

**Job 3 — SonarCloud Analysis:**
- Sends code + coverage report to SonarCloud for advanced code quality metrics
- Tracks technical debt, code smells, duplications over time

**Job 4 — Docker Build & Push:**
- Runs only on main branch (not on PRs)
- Builds the Docker image
- Pushes to Docker Hub with two tags: `latest` and the git commit SHA
- The SHA tag means every deployment is traceable to an exact commit

### CD Pipeline (`.github/workflows/cd.yml`)

Triggered automatically when CI passes on main (via `workflow_run` trigger).

**Steps:**

1. **Preflight** — Verify all 10 required secrets are set (SSH keys, EC2 IPs, AWS credentials, etc.)
2. **Determine active slot** — Query ALB to find which EC2 is currently serving 100% traffic
3. **Deploy to inactive slot** — SSH into the inactive EC2, pull the new Docker image, restart the container
4. **Health check** — Poll `/docs` endpoint 15 times with 15-second intervals until it returns 200
5. **Smoke test** — Hit `GET /health` and confirm it returns HTTP 200
6. **Switch ALB traffic** — Move 100% of ALB traffic to the newly deployed EC2

This is the **blue-green deployment** strategy.

---

## 8. Task 5 — AWS Cloud Deployment with Blue-Green Strategy

### AWS Services Used

| Service | What It Does in This Project |
|---|---|
| **EC2** | Virtual servers running the API (blue + green) and Airflow |
| **RDS** | Managed PostgreSQL database (always running, not on EC2) |
| **ALB** | Application Load Balancer — single public URL, routes to EC2s |
| **Target Groups** | Two groups: one per EC2, ALB routes between them |
| **S3** | Object storage for the data lake (bronze/silver/gold) |
| **Athena** | Serverless SQL query engine over S3 parquet files |
| **IAM** | Permissions — EC2 instances and users given minimum required access |

### Blue-Green Deployment Explained

The problem with traditional deployment: if you update the app on the running server, there's downtime while the container restarts.

Blue-green solves this:

```
BEFORE DEPLOY:
  ALB → 100% → blue EC2 (current version)
  green EC2 (idle)

DURING DEPLOY:
  Deploy new version to green EC2
  Run health checks on green (users don't see this yet)

AFTER HEALTH CHECK PASSES:
  ALB → 100% → green EC2 (new version)
  blue EC2 (idle, ready for instant rollback)
```

If anything goes wrong with the new version, rollback is instant — just flip the ALB weight back to blue.

### How the ALB Routes Traffic

The ALB has two **Target Groups** — one pointing to blue EC2, one to green EC2. The ALB **Listener Rule** has weights (e.g., blue=100, green=0). The CD pipeline changes these weights using AWS CLI:

```bash
aws elbv2 modify-listener --listener-arn ... --default-actions \
  '[{"Type":"forward","ForwardConfig":{"TargetGroups":[
    {"TargetGroupArn":"...blue...","Weight":0},
    {"TargetGroupArn":"...green...","Weight":100}
  ]}}'
```

### Canary Deployments (Optional)

Instead of flipping 100% instantly, the CD pipeline supports a canary mode — send 10% of traffic to the new version first, monitor, then promote to 100%. This reduces risk for large changes.

### ALB DNS Name

The public URL (`cart-api-alb-2053330170.eu-north-1.elb.amazonaws.com`) **never changes** even when EC2 instances stop/start or their IPs change. The ALB health-checks the EC2s continuously and only routes traffic to healthy instances.

---

## 9. Task 6 — ETL Pipeline with Medallion Architecture

### What is an ETL Pipeline?

**Extract** data from the source (RDS), **Transform** it (clean, aggregate), **Load** it to a destination (S3). This separates the operational database (OLTP) from the analytics data (OLAP).

### Medallion Architecture

A three-layer data architecture in S3:

```
S3 Bucket: cart-api-datalake/
├── bronze/   ← Raw data, exactly as it comes from RDS, no changes
├── silver/   ← Cleaned, deduplicated, validated data
└── gold/     ← Business-ready aggregations for analytics
```

Each layer is stored as **Parquet** files — a columnar format that is much faster and smaller than CSV for analytics queries.

Each run creates a partition folder: `run_date=YYYY-MM-DD/` so historical data is preserved.

### Bronze Layer — Extract (`etl/scripts/bronze_extract.py`)

- Connects to RDS and reads all 5 tables: `users`, `products`, `product_variants`, `carts`, `cart_items`
- No transformations — raw data preserved exactly
- Uploads each table as a parquet file to S3
- Tool used: **pandas + boto3**

```
s3://cart-api-datalake/bronze/users/run_date=2026-06-11/users.parquet
s3://cart-api-datalake/bronze/carts/run_date=2026-06-11/carts.parquet
...
```

### Silver Layer — Transform (`etl/scripts/silver_transform.py`)

- Reads bronze parquet files from S3
- Cleans each table with **PySpark** (distributed processing framework):
  - Drop exact duplicate rows
  - Remove rows with null values in critical columns
  - Validate data types and business constraints (price > 0, stock ≥ 0, valid status values)
  - Normalize text (lowercase email, trim whitespace)
- Writes clean parquet back to S3 silver layer

Why PySpark? Even though this data is small, PySpark is the industry standard for large-scale ETL. It can process terabytes distributed across a cluster — using it here is learning the production-scale tool.

### Gold Layer — Aggregate (`etl/scripts/gold_aggregate.py`)

Creates 4 analytics-ready datasets from silver data:

**1. cart_summary** — Per-cart business view:
- Total cart value (sum of price × quantity)
- Total items count
- Number of unique products
- Cart status, user name

**2. user_activity** — Per-user behavioral metrics:
- Total carts created
- Carts checked out (converted)
- Active carts

**3. product_popularity** — Product performance:
- Total units ordered across all carts
- Times a product was added to any cart
- Total revenue generated

**4. variant_stock_summary** — Inventory analytics:
- Total stock across all variants of a product
- Number of variants
- Average, minimum, maximum price per product

---

## 10. Task 7 — Airflow Orchestration on EC2

### Why Airflow?

We need the ETL to run automatically at 2AM UTC every day, even when the developer's laptop is off. Apache Airflow is an industry-standard workflow orchestration tool — it manages scheduling, retries, dependencies, and monitoring of data pipelines.

### DAG Structure (`etl/dags/etl_pipeline.py`)

A **DAG** (Directed Acyclic Graph) defines the pipeline steps and their order.

```
DAG: etl_pipeline
Schedule: 0 2 * * *  (every day at 2:00 AM UTC)

bronze_extract → silver_transform → gold_aggregate
```

The arrow means silver only starts after bronze succeeds. If bronze fails, silver and gold are skipped. Airflow handles retries automatically.

### Why a Dedicated 3rd EC2?

- The blue/green EC2s run the API — we don't put Airflow there
- Airflow needs to run 24/7 to catch the 2AM schedule
- A 3rd t2.micro EC2 (free tier) was created specifically for Airflow

### Deployment Steps

1. Created a 3rd EC2 instance (`airflow-etl`) in AWS Console
2. Installed Docker and Docker Compose on the EC2 via SSH
3. Copied ETL files from laptop to EC2 using `scp` (secure copy over SSH):
   ```bash
   scp -i key.pem -r ./etl/ ubuntu@<ec2-ip>:~/etl/
   ```
4. Built the Airflow Docker images on the EC2
5. Started all 4 containers with `docker-compose up -d`
6. Containers run persistently — even if you disconnect from SSH

---

## 11. Task 8 — Data Analytics with AWS Athena

### What is Athena?

AWS Athena is a **serverless SQL query engine** that runs SQL directly on files stored in S3. No database server to manage — you just point it at your S3 parquet files and run SQL queries. You pay only per query (per TB scanned).

### Setup

Created a database `datalake` in Athena with 4 external tables pointing to the gold layer in S3:

```sql
CREATE EXTERNAL TABLE gold.cart_summary (
  cart_id INT, user_id INT, user_name STRING, total_value DOUBLE, ...
)
STORED AS PARQUET
LOCATION 's3://cart-api-datalake/gold/cart_summary/'
TBLPROPERTIES ('parquet.compress'='SNAPPY');
```

### Sample Analytics Queries

**Top 10 highest-value carts:**
```sql
SELECT cart_id, user_name, total_value, total_items
FROM gold.cart_summary
ORDER BY total_value DESC
LIMIT 10;
```

**Most popular products:**
```sql
SELECT product_name, total_units_ordered, total_revenue
FROM gold.product_popularity
ORDER BY total_units_ordered DESC
LIMIT 10;
```

**Stock at risk (low stock):**
```sql
SELECT product_name, total_stock, variant_count
FROM gold.variant_stock_summary
WHERE total_stock < 10
ORDER BY total_stock ASC;
```

---

## 12. Task 9 — API Testing & Load Testing

### Functional Tests (pytest)

Located in `tests/` directory. Test cases cover all API endpoints with valid and invalid inputs. Minimum **70% code coverage** enforced — CI fails if coverage drops below this.

Tests use dependency injection to swap the real database with a test database — ensuring tests are isolated and repeatable.

### Postman Collection Tests

`postman/collections/cart_api_tests.postman_collection.json` contains test cases including:

- `TC-01` to `TC-08` — Happy path tests (create cart, add item, checkout, etc.)
- `TC-09` — user_id overflow (exceeds PostgreSQL INTEGER max 2,147,483,647) → expect 422
- Edge cases: duplicate cart, insufficient stock, invalid item IDs

### Load Testing with Newman CLI

`postman/collections/load_test.postman_collection.json` — a stateless load test that simulates real user traffic:

1. Health Check
2. Create Cart (random user_id 1–500,000)
3. Add Item (random variant_id 1–100,000, quantity 1–5)
4. Checkout Cart

Run from laptop against the ALB:
```bash
newman run load_test.postman_collection.json --iteration-count 100 --reporters cli
```

---

## 13. Challenges & How We Solved Them

### Challenge 1 — PySpark Build Failure on Python 3.12

**Problem:** `pip install pyspark==3.5.0` failed inside Docker because the base Airflow 2.9.2 image uses Python 3.12. PySpark's build process uses `pkg_resources` from `setuptools`, which was removed in newer setuptools versions.

**Error:** `pkg_resources is deprecated as an API... ImportError`

**Solution:** Pin `setuptools<67.0.0` before installing PySpark, and upgrade PySpark to 3.5.3:
```dockerfile
RUN pip install --no-cache-dir "setuptools<67.0.0" && \
    pip install --no-cache-dir pyspark==3.5.3 ...
```

---

### Challenge 2 — EC2 Disk Space Full During Docker Build

**Problem:** EC2 t2.micro has only 8GB disk. The PySpark package is 317MB compressed and expands to ~1GB with all Spark jar files. Docker build layers (base image + JDK + PySpark) exceeded the available space.

**Error:** `No space left on device` while downloading pyspark-3.5.3.tar.gz

**Solution (two steps):**
1. Ran `docker system prune -a -f` to free Docker build cache (freed ~4GB)
2. Increased the AWS EBS volume from 8GB to 20GB via AWS Console → EC2 → Volumes → Modify Volume, then extended the filesystem:
```bash
sudo growpart /dev/nvme0n1 1
sudo resize2fs /dev/nvme0n1p1
```
Result: 19GB disk, 12GB free — build succeeded.

---

### Challenge 3 — CD Smoke Test Returning 404

**Problem:** The CD pipeline smoke test was calling `POST /carts` with `user_id: 999999999`. This user doesn't exist in the database, so it returns 404. The smoke test was failing after successful deployments.

**Solution:** Changed the smoke test to call `GET /health` — a simple endpoint that always returns 200 regardless of database state:
```bash
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://$HOST:8000/health")
[ "$STATUS" == "200" ] || exit 1
```

Also added the `/health` endpoint to `app/main.py` which was missing entirely.

---

### Challenge 4 — Wrong Integer Constant (SQLite vs PostgreSQL)

**Problem:** The codebase had `SQLITE_INT_MAX = 9223372036854775807` — the maximum integer for SQLite (64-bit). But the database is PostgreSQL, which uses a 32-bit INTEGER with max value `2,147,483,647`. This meant the API accepted values that PostgreSQL would reject, causing database errors.

**Solution:** Renamed the constant to `PG_INT_MAX = 2147483647` across all files — `app/schemas/cart.py` and `app/api/cart.py`.

---

### Challenge 5 — SSH Connection Disconnecting During Long Operations

**Problem:** When running long Docker build commands (10–15 minutes) over SSH, the connection would time out and disconnect mid-operation.

**Solution:** The `docker-compose up -d` flag (detached mode) means Docker runs in the background. Even if SSH disconnects, the Docker build or containers continue running on the server. Reconnect with SSH and check status.

---

### Challenge 6 — Newman CLI Wrong Flag

**Problem:** Newman load test failed with `error: unknown option '--reporter'`

**Solution:** Newman uses `--reporters` (plural), not `--reporter`.

---

### Challenge 7 — Wrong EBS Volume Selected for Resize

**Problem:** The AWS Console shows all EBS volumes — it's easy to accidentally resize the wrong one. Initially found the `cart-api-green` volume instead of the airflow EC2 volume.

**Solution:** To identify the correct volume: EC2 → Instances → click the specific instance → Storage tab → find the volume ID attached to that instance. Never resize by guessing from the volume list.

---

## 14. End-to-End Workflow Summary

### Daily Automated Flow (No Human Action Required)

```
2:00 AM UTC
    │
    ▼
Airflow Scheduler (EC2 airflow-etl) triggers DAG
    │
    ├─► bronze_extract.py
    │     Reads users, products, variants, carts, cart_items from RDS
    │     Uploads raw parquet to s3://cart-api-datalake/bronze/
    │
    ├─► silver_transform.py  (starts after bronze succeeds)
    │     PySpark reads bronze parquet
    │     Cleans, deduplicates, validates all 5 tables
    │     Uploads clean parquet to s3://cart-api-datalake/silver/
    │
    └─► gold_aggregate.py  (starts after silver succeeds)
          PySpark reads silver parquet
          Computes cart_summary, user_activity, product_popularity, variant_stock_summary
          Uploads analytics parquet to s3://cart-api-datalake/gold/

Next morning: Data is ready in Athena for SQL queries
```

### Developer Workflow (Code Change → Production)

```
Developer writes code on laptop
    │
    ▼
git push origin main
    │
    ▼
GitHub Actions — CI Pipeline starts automatically
    ├─ Ruff lint (code style)
    ├─ Bandit security scan
    ├─ pip-audit CVE check
    ├─ MyPy type check
    ├─ pytest (must pass, coverage ≥ 70%)
    └─ Docker build & push to Docker Hub (tagged with git SHA)
    │
    ▼ (only if ALL CI jobs pass)
GitHub Actions — CD Pipeline starts automatically
    ├─ Check which EC2 is active (blue or green)
    ├─ Deploy new Docker image to INACTIVE EC2
    ├─ Health check /docs (15 retries × 15 seconds)
    ├─ Smoke test GET /health → must return 200
    └─ Switch ALB to send 100% traffic to newly deployed EC2

Total time from git push to live in production: ~5-7 minutes
Zero downtime, instant rollback available
```

### Infrastructure Diagram

```
GitHub Repository
       │ git push
       ▼
GitHub Actions (CI → CD)
       │ deploy via SSH
       ▼
AWS Application Load Balancer (cart-api-alb-*.eu-north-1.elb.amazonaws.com)
       │                    │
       ▼ (active)           ▼ (standby)
cart-api-blue EC2    cart-api-green EC2
  Docker Container     Docker Container
  (FastAPI app)        (FastAPI app)
       │                    │
       └────────┬───────────┘
                │ both connect to
                ▼
        AWS RDS PostgreSQL
        (users, products, carts, cart_items)
                │
                │ ETL reads from RDS
                ▼
        airflow-etl EC2 (3rd instance)
          Apache Airflow (4 Docker containers)
          Runs ETL daily at 2AM UTC
                │
                ▼
        AWS S3: cart-api-datalake
          bronze/ → silver/ → gold/
                │
                ▼
          AWS Athena
          SQL queries on gold parquet files
```

---

*Project completed during Data Engineering Internship — June 2026*
