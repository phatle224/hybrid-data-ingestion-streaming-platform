# Airflow Migration Guide

This document outlines how to migrate the current custom dbt Scheduler Daemon into a production-grade **Apache Airflow DAG**, complete with retry logic, failure notifications, and SLA monitoring.

---

## 1. Current Architecture: Custom Scheduler Daemon

The project currently uses a lightweight Python daemon (`dbt_scheduler.py`) that triggers `dbt run` on a fixed interval (every 5 minutes). It runs inside a Docker container alongside the dbt project files.

### Trade-offs

| Aspect | Custom Daemon (Current) | Apache Airflow (Target) |
|--------|------------------------|------------------------|
| Memory footprint | ~10 MB | ~2-4 GB (Webserver + Scheduler + Worker) |
| Retry logic | None (crashes silently) | Built-in exponential backoff retries |
| Failure visibility | Logs only | Web UI + Email/Slack alerts |
| Task dependencies | Sequential only | Full DAG dependency graphs |
| Execution history | Log file rotation | Persistent database with full audit trail |
| Setup complexity | Single Dockerfile | Requires Airflow infra (PostgreSQL metadata DB, Redis for Celery) |

**Why the custom daemon was chosen**: For a local development and demo environment, a custom scheduler keeps the total Docker footprint under 1 GB RAM. Airflow's full stack introduces significant overhead that is unnecessary for a single-pipeline demo.

---

## 2. Target Architecture: Airflow DAG

### Prerequisites

- Apache Airflow 2.7+ installed (via `docker-compose` or `pip install apache-airflow`)
- Airflow PostgreSQL metadata database configured
- dbt CLI available in the Airflow worker environment

### DAG File: `dbt_etl_dag.py`

Place this file in your Airflow `dags/` directory:

```python
"""
dbt ELT Pipeline DAG
====================
Orchestrates the dbt transformation pipeline with proper retry logic,
SLA monitoring, and failure alerting.

Schedule: Every 5 minutes (matching current daemon behavior)
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DBT_PROJECT_DIR = "/opt/dbt/dbt_analytics"
DBT_PROFILES_DIR = "/opt/dbt/dbt_analytics"

default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email": ["data-alerts@company.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=1),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=10),
    "execution_timeout": timedelta(minutes=15),
    "sla": timedelta(minutes=8),
}

# ---------------------------------------------------------------------------
# DAG Definition
# ---------------------------------------------------------------------------
with DAG(
    dag_id="dbt_etl_pipeline",
    default_args=default_args,
    description="Incremental dbt ELT: Staging -> Warehouse -> Mart",
    schedule_interval="*/5 * * * *",
    start_date=days_ago(1),
    catchup=False,
    max_active_runs=1,
    tags=["dbt", "etl", "data-warehouse"],
) as dag:

    # Step 1: Validate dbt project compiles without errors
    dbt_debug = BashOperator(
        task_id="dbt_debug",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt debug --profiles-dir {DBT_PROFILES_DIR}",
    )

    # Step 2: Run staging models (views — lightweight, always full-refresh)
    dbt_run_staging = BashOperator(
        task_id="dbt_run_staging",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && "
            f"dbt run --profiles-dir {DBT_PROFILES_DIR} "
            f"--select staging --full-refresh"
        ),
    )

    # Step 3: Run intermediate models (deduplication logic)
    dbt_run_intermediate = BashOperator(
        task_id="dbt_run_intermediate",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && "
            f"dbt run --profiles-dir {DBT_PROFILES_DIR} "
            f"--select intermediate"
        ),
    )

    # Step 4: Run warehouse models (incremental dimensions + facts)
    dbt_run_warehouse = BashOperator(
        task_id="dbt_run_warehouse",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && "
            f"dbt run --profiles-dir {DBT_PROFILES_DIR} "
            f"--select warehouse"
        ),
    )

    # Step 5: Run data mart models (incremental aggregations)
    dbt_run_marts = BashOperator(
        task_id="dbt_run_marts",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && "
            f"dbt run --profiles-dir {DBT_PROFILES_DIR} "
            f"--select mart"
        ),
    )

    # Step 6: Execute all dbt tests for data quality validation
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && "
            f"dbt test --profiles-dir {DBT_PROFILES_DIR}"
        ),
    )

    # Step 7: Generate dbt documentation
    dbt_docs_generate = BashOperator(
        task_id="dbt_docs_generate",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && "
            f"dbt docs generate --profiles-dir {DBT_PROFILES_DIR}"
        ),
    )

    # -----------------------------------------------------------------------
    # Task Dependencies (DAG Graph)
    # -----------------------------------------------------------------------
    # dbt_debug -> staging -> intermediate -> warehouse -> marts -> test -> docs
    (
        dbt_debug
        >> dbt_run_staging
        >> dbt_run_intermediate
        >> dbt_run_warehouse
        >> dbt_run_marts
        >> dbt_test
        >> dbt_docs_generate
    )
```

---

## 3. DAG Execution Flow

```mermaid
graph LR
    A["dbt debug"] --> B["dbt run staging"]
    B --> C["dbt run intermediate"]
    C --> D["dbt run warehouse"]
    D --> E["dbt run marts"]
    E --> F["dbt test"]
    F --> G["dbt docs generate"]
```

Each task runs in sequence. If any step fails:
1. Airflow retries up to **3 times** with exponential backoff (1 min, 2 min, 4 min).
2. If all retries are exhausted, an **email alert** is sent to `data-alerts@company.com`.
3. The DAG run is marked as `failed`, and subsequent scheduled runs will still proceed (no `depends_on_past`).

---

## 4. Deployment with Docker Compose

To run Airflow alongside the existing CDC infrastructure, add the following to a new `docker-compose.airflow.yml`:

```yaml
version: '3.8'

x-airflow-common: &airflow-common
  image: apache/airflow:2.7.3-python3.11
  environment:
    AIRFLOW__CORE__EXECUTOR: LocalExecutor
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@airflow-postgres:5432/airflow
    AIRFLOW__CORE__FERNET_KEY: ''
    AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
    AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
    # Pass dbt database connection as env vars
    DB_HOST: ${DB_HOST:-host.docker.internal}
    DB_PORT: ${DB_PORT:-5432}
    DB_USER: ${DB_USER:-postgres}
    DB_PASSWORD: ${DB_PASSWORD}
    DB_DATABASE: ${DB_NAME_STAGING:-insuranceWarehouse}
  volumes:
    - ./dags:/opt/airflow/dags
    - ./services/dbt_analytics:/opt/dbt/dbt_analytics
    - ./logs/airflow:/opt/airflow/logs
  extra_hosts:
    - "host.docker.internal:host-gateway"
  networks:
    - cdc-network

services:
  airflow-postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - airflow-db-data:/var/lib/postgresql/data
    networks:
      - cdc-network

  airflow-init:
    <<: *airflow-common
    entrypoint: /bin/bash
    command:
      - -c
      - |
        airflow db init
        airflow users create \
          --username admin \
          --password admin \
          --firstname Admin \
          --lastname User \
          --role Admin \
          --email admin@example.com
    depends_on:
      - airflow-postgres

  airflow-webserver:
    <<: *airflow-common
    command: webserver
    ports:
      - "8088:8080"
    depends_on:
      - airflow-init
    restart: always

  airflow-scheduler:
    <<: *airflow-common
    command: scheduler
    depends_on:
      - airflow-init
    restart: always

volumes:
  airflow-db-data:

networks:
  cdc-network:
    name: cdc-network
    external: true
```

### Startup Commands

```bash
# 1. Initialize Airflow metadata database and admin user
docker compose -f docker-compose.airflow.yml run --rm airflow-init

# 2. Start Airflow webserver and scheduler
docker compose -f docker-compose.airflow.yml up -d airflow-webserver airflow-scheduler

# 3. Access Airflow UI
# http://localhost:8088 (user: admin, password: admin)
```

---

## 5. Monitoring & Alerting Extensions

### Slack Notifications (Optional)

Install the Slack provider and add a callback to the DAG:

```python
from airflow.providers.slack.notifications.slack import send_slack_notification

# Add to default_args:
default_args["on_failure_callback"] = send_slack_notification(
    text="dbt ELT Pipeline FAILED: {{ dag_run.dag_id }}",
    channel="#data-alerts",
    slack_conn_id="slack_webhook",
)
```

### SLA Monitoring

The DAG is configured with an **8-minute SLA**. If any task exceeds this, Airflow logs an SLA miss event and sends an email notification. This ensures the data warehouse is refreshed within acceptable latency bounds.
