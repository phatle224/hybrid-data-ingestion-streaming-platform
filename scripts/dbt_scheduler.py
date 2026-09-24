#!/usr/bin/env python3
"""Run the dbt models on a fixed interval inside the scheduler container."""

from __future__ import annotations

import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


INTERVAL_SECONDS = int(os.getenv("SCHEDULER_INTERVAL", "300"))
DBT_DIR = Path(os.getenv("DBT_DIR", "/usr/app/dbt_analytics"))
LOG_FILE = Path(os.getenv("LOG_FILE", DBT_DIR / "logs" / "dbt_scheduler.log"))


def log(message: str) -> None:
    line = f"[{datetime.now(timezone.utc).isoformat()}] {message}"
    print(line, flush=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(f"{line}\n")


def run_dbt() -> None:
    log("Starting scheduled dbt run")
    result = subprocess.run(
        ["dbt", "run", "--profiles-dir", "."],
        cwd=DBT_DIR,
        capture_output=True,
        text=True,
        check=False,
    )
    for output_line in result.stdout.splitlines():
        if output_line.strip():
            log(output_line)
    if result.stderr:
        for output_line in result.stderr.splitlines():
            if output_line.strip():
                log(f"stderr: {output_line}")
    log(f"Scheduled dbt run finished with exit code {result.returncode}")


def main() -> None:
    if INTERVAL_SECONDS <= 0:
        raise ValueError("SCHEDULER_INTERVAL must be greater than zero")
    log(f"dbt scheduler started; interval={INTERVAL_SECONDS}s; project={DBT_DIR}")
    while True:
        run_dbt()
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
