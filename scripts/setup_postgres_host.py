#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Initialization Script for local Windows Host PostgreSQL.
Creates the databases 'insuranceSale' and 'insuranceStaging' if they don't exist,
and runs the schema SQL scripts to set up all tables and schemas.
"""
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Default configurations (can override from environment)
DB_HOST = "localhost"
DB_PORT = "5432"
DB_USER = "postgres"
DB_PASSWORD = "${DB_PASSWORD}"

# Database names
DB_SOURCE = "insuranceSale"
DB_STAGING = "insuranceWarehouse"

# SQL files to run
SQL_SOURCE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../database/00_source/create_source_schema.sql"))
SQL_STAGING = os.path.abspath(os.path.join(os.path.dirname(__file__), "../database/01_staging/01_create_staging_schema.sql"))
SQL_REPORTING = os.path.abspath(os.path.join(os.path.dirname(__file__), "../database/02_reporting/01_create_reporting_contract.sql"))

def execute_sql_file(conn, file_path):
    """Executes a multi-statement SQL script file."""
    print(f"Running SQL script: {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        with conn.cursor() as cur:
            cur.execute(sql_script)
        conn.commit()
        print(f"Successfully executed {file_path}")
    except Exception as e:
        conn.rollback()
        print(f"Error executing {file_path}: {e}")
        # Print error details
        if hasattr(e, 'pgerror'):
            print(f"PgError: {e.pgerror}")

def main():
    print("====================================================================")
    print("POSTGRESQL HOST INITIALIZATION SCRIPT")
    print("====================================================================")
    
    # 1. Connect to postgres database to check/create databases
    try:
        print(f"Connecting to host postgresql on {DB_HOST}:{DB_PORT} as {DB_USER}...")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    except Exception as e:
        print(f"Failed to connect to host PostgreSQL: {e}")
        print("Please check that PostgreSQL is running, port 5432 is correct, and credentials are valid.")
        sys.exit(1)
        
    with conn.cursor() as cur:
        # Check source database
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (DB_SOURCE,))
        if not cur.fetchone():
            print(f"Database '{DB_SOURCE}' does not exist. Creating...")
            cur.execute(f'CREATE DATABASE "{DB_SOURCE}";')
            print(f"Database '{DB_SOURCE}' created.")
        else:
            print(f"Database '{DB_SOURCE}' already exists.")
            
        # Check staging database
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (DB_STAGING,))
        if not cur.fetchone():
            print(f"Database '{DB_STAGING}' does not exist. Creating...")
            cur.execute(f'CREATE DATABASE "{DB_STAGING}";')
            print(f"Database '{DB_STAGING}' created.")
        else:
            print(f"Database '{DB_STAGING}' already exists.")
            
    conn.close()
    
    # 2. Apply DDL script to Source Database
    print(f"\nInitializing Source DB: {DB_SOURCE}...")
    try:
        conn_source = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_SOURCE
        )
        execute_sql_file(conn_source, SQL_SOURCE)
        conn_source.close()
    except Exception as e:
        print(f"Failed to initialize source DB: {e}")
        
    # 3. Apply DDL scripts to Staging Database
    print(f"\nInitializing Staging DB: {DB_STAGING}...")
    try:
        conn_staging = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_STAGING
        )
        execute_sql_file(conn_staging, SQL_STAGING)
        execute_sql_file(conn_staging, SQL_REPORTING)
        conn_staging.close()
    except Exception as e:
        print(f"Failed to initialize staging DB: {e}")

    print("\nInitialization finished!")

if __name__ == '__main__':
    main()
