#!/usr/bin/env python3
"""Collect reproducible local verification metrics without mutating project data.

Run dbt first so ``target/run_results.json`` represents the command you want to
report, then execute this script from the repository root with the dbt virtual
environment::

    services/dbt_analytics/.venv/Scripts/python scripts/verify_local_metrics.py

The script prints JSON to stdout. It deliberately does not estimate CDC
throughput, end-to-end latency, deduplication rate, or consumer lag: those
metrics require a controlled workload and timestamped event-level measurements.
"""

from __future__ import annotations

import json
import os
import argparse
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_RESULTS = ROOT / "services" / "dbt_analytics" / "target" / "run_results.json"

TABLES = (
    "staging.\"stgInsuranceContract\"",
    "staging.\"stgInsuranceClaim\"",
    "warehouse.dim_customer",
    "warehouse.dim_insured_person",
    "warehouse.dim_product",
    "warehouse.dim_sales_channel",
    "warehouse.fct_contracts",
    "warehouse.fct_claims",
    "mart.dm_contract_summary",
    "mart.dm_profiling_analysis",
)

ENDPOINTS = {
    "portal_frontend": "http://localhost:3010/",
    "portal_backend": "http://localhost:3011/api/health/",
    "kafka_ui": "http://localhost:8080/",
    "debezium_connect": "http://localhost:8083/connectors",
    "debezium_ui": "http://localhost:8084/",
    "prometheus": "http://localhost:9090/-/healthy",
    "grafana": "http://localhost:3030/api/health",
    "kafka_exporter": "http://localhost:9308/metrics",
    "postgres_exporter": "http://localhost:9187/metrics",
}


def load_dotenv(path: Path) -> None:
    """Load simple KEY=VALUE entries without printing secrets."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def dbt_metrics() -> dict[str, object]:
    artifact = json.loads(RUN_RESULTS.read_text(encoding="utf-8"))
    results = artifact.get("results", [])
    statuses = Counter(result.get("status", "unknown") for result in results)
    failures = [
        {
            "unique_id": result.get("unique_id"),
            "status": result.get("status"),
            "failures": result.get("failures"),
        }
        for result in results
        if result.get("status") not in {"pass", "success"}
    ]
    return {
        "generated_at": artifact.get("metadata", {}).get("generated_at"),
        "elapsed_seconds": round(float(artifact.get("elapsed_time", 0)), 3),
        "total": len(results),
        "statuses": dict(sorted(statuses.items())),
        "non_passing": failures,
    }


def database_metrics() -> dict[str, object]:
    try:
        import psycopg2
    except ImportError as exc:  # pragma: no cover - environment-dependent
        return {"error": f"psycopg2 is unavailable: {exc}"}

    host = os.getenv("METRICS_DB_HOST", "localhost")
    database = os.getenv("DB_NAME_STAGING", os.getenv("DB_DATABASE", "insuranceWarehouse"))
    try:
        with psycopg2.connect(
            host=host,
            port=int(os.getenv("DB_PORT", "5432")),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            dbname=database,
            connect_timeout=5,
        ) as connection:
            with connection.cursor() as cursor:
                counts: dict[str, int] = {}
                for table in TABLES:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    counts[table.replace('"', "")] = int(cursor.fetchone()[0])
        return {"database": database, "row_counts": counts}
    except Exception as exc:  # pragma: no cover - environment-dependent
        return {"database": database, "error": f"{type(exc).__name__}: {exc}"}


def endpoint_metrics() -> dict[str, object]:
    checks: dict[str, object] = {}
    for name, url in ENDPOINTS.items():
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                checks[name] = {
                    "status": response.status,
                    "response_ms": round((time.perf_counter() - started) * 1000, 1),
                }
        except (urllib.error.URLError, TimeoutError) as exc:
            checks[name] = {"error": f"{type(exc).__name__}: {exc}"}
    return checks


def run_dbt_test() -> int:
    env = os.environ.copy()
    env["DB_HOST"] = env.get("METRICS_DB_HOST", "localhost")
    env["DB_DATABASE"] = env.get("DB_NAME_STAGING", "insuranceWarehouse")
    command = [
        sys.executable,
        "-c",
        "from dbt.cli.main import cli; cli()",
        "test",
        "--project-dir",
        str(ROOT / "services" / "dbt_analytics"),
        "--profiles-dir",
        str(ROOT / "services" / "dbt_analytics"),
    ]
    result = subprocess.run(command, env=env, check=False)
    return result.returncode


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-dbt-test",
        action="store_true",
        help="run dbt test before reading its artifact (a non-zero result is still reported)",
    )
    args = parser.parse_args()
    load_dotenv(ROOT / ".env")
    dbt_test_exit_code = run_dbt_test() if args.run_dbt_test else None
    report = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "scope": "local demo verification; not a production performance benchmark",
        "dbt": dbt_metrics(),
        "database": database_metrics(),
        "http_health": endpoint_metrics(),
        "not_measured": [
            "CDC throughput",
            "end-to-end CDC latency",
            "offline deduplication rate",
            "maximum Excel batch size",
            "Kafka consumer lag under load",
        ],
    }
    if dbt_test_exit_code is not None:
        report["dbt"]["command_exit_code"] = dbt_test_exit_code
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
