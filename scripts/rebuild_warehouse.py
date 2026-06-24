import os
import psycopg2

DB_HOST = "localhost"
DB_PORT = "5432"
DB_USER = "postgres"
DB_PASSWORD = "${DB_PASSWORD}"
DB_NAME = "insuranceWarehouse"

SQL_STAGING_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../database/01_staging/01_create_staging_schema.sql"))

def main():
    print(f"Connecting to database '{DB_NAME}' to drop and recreate schemas...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # 1. Drop old schemas
        schemas_to_drop = ["staging", "intermediate", "reporting", "warehouse", "mart"]
        for schema in schemas_to_drop:
            print(f"Dropping schema '{schema}' (CASCADE)...")
            cur.execute(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE;')
            
        print("All old schemas dropped successfully.")
        
        # 2. Run DDL script to recreate staging tables
        print(f"Reading staging DDL from {SQL_STAGING_PATH}...")
        with open(SQL_STAGING_PATH, 'r', encoding='utf-8') as f:
            sql_script = f.read()
            
        print("Executing staging DDL script...")
        cur.execute(sql_script)
        print("Raw staging tables recreated successfully.")
        
        cur.close()
        conn.close()
        print("Rebuild finished successfully!")
    except Exception as e:
        print(f"Error during schema rebuild: {e}")

if __name__ == '__main__':
    main()
