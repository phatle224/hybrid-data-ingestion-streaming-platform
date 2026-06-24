#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dbt Scheduler - Runs dbt run in incremental mode every 5 minutes.
Logs output to logs/dbt_scheduler.log.
"""
import os
import sys
import time
import subprocess
from datetime import datetime

# Configurations
INTERVAL_SECONDS = 300  # 5 minutes
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DBT_DIR = os.path.join(WORKSPACE_DIR, 'services', 'dbt_analytics')
LOG_FILE = os.path.join(WORKSPACE_DIR, 'logs', 'dbt_scheduler.log')

# Ensure logs directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log_message(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
    except Exception as e:
        print(f"Failed to write to log file: {e}")

def run_dbt():
    log_message("Starting scheduled dbt run...")
    
    # Resolve dbt executable path
    if sys.platform == 'win32':
        dbt_exe = os.path.join(DBT_DIR, '.venv', 'Scripts', 'dbt.exe')
    else:
        dbt_exe = os.path.join(DBT_DIR, '.venv', 'bin', 'dbt')
        
    if not os.path.exists(dbt_exe):
        log_message(f"Error: dbt executable not found at {dbt_exe}. Fallback to global 'dbt'")
        dbt_exe = 'dbt'

    cmd = [dbt_exe, 'run', '--profiles-dir', '.']
    
    try:
        # Run process and capture output
        result = subprocess.run(
            cmd,
            cwd=DBT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False
        )
        
        # Log result
        if result.returncode == 0:
            log_message("dbt run completed successfully.")
            # Log summary of output (success lines)
            success_lines = [line for line in result.stdout.split('\n') if 'OK created' in line or 'Finished running' in line or 'Completed successfully' in line]
            for line in success_lines:
                log_message(f"  > {line}")
        else:
            log_message(f"dbt run failed with exit code {result.returncode}.")
            # Log output to log file
            log_message("=== DBT RUN ERROR OUTPUT ===")
            for line in result.stdout.split('\n'):
                if line.strip():
                    log_message(f"  ERROR: {line}")
            log_message("============================")
            
    except Exception as e:
        log_message(f"Exception raised while running dbt: {e}")

def main():
    log_message("=========================================================")
    log_message(f"dbt scheduler daemon initialized. Interval: {INTERVAL_SECONDS}s")
    log_message(f"dbt directory: {DBT_DIR}")
    log_message("=========================================================")
    
    # Run immediately on startup
    run_dbt()
    
    try:
        while True:
            log_message(f"Sleeping for {INTERVAL_SECONDS} seconds until next run...")
            time.sleep(INTERVAL_SECONDS)
            run_dbt()
    except KeyboardInterrupt:
        log_message("dbt scheduler stopped by user.")

if __name__ == '__main__':
    main()
