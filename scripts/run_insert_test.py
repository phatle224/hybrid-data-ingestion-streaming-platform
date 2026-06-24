import psycopg2
import time
import subprocess
import os

def run_sql_file(dbname, file_path):
    print(f"Connecting to {dbname} and running {file_path}...")
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="${DB_PASSWORD}",
        dbname=dbname
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        sql = f.read()
        
    # Execute the file contents
    cur.execute(sql)
    print("SQL execution complete.")
    cur.close()
    conn.close()

def run_dbt():
    print("Running dbt pipeline...")
    dbt_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../services/dbt_analytics"))
    dbt_path = os.path.abspath(os.path.join(dbt_dir, ".venv/Scripts/dbt.exe"))
    
    res = subprocess.run([dbt_path, "run", "--profiles-dir", "."], cwd=dbt_dir, capture_output=True, text=True)
    if res.returncode == 0:
        print("dbt run successful!")
    else:
        print("dbt run failed!")
        print(res.stdout)
        print(res.stderr)

def verify_results():
    print("\nVerifying test records in staging and warehouse schemas...")
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="${DB_PASSWORD}",
        dbname="insuranceWarehouse"
    )
    cur = conn.cursor()
    
    # 1. Check staging table
    cur.execute("SELECT count(*) FROM staging.\"stgInsuranceContract\" WHERE \"contractId\" LIKE 'CTR-TEST%';")
    stg_count = cur.fetchone()[0]
    print(f" - stgInsuranceContract test rows: {stg_count}")
    
    # 2. Check warehouse dim_customers table
    cur.execute("SELECT count(*) FROM warehouse.dim_customers WHERE customer_email LIKE '%test%';")
    cust_count = cur.fetchone()[0]
    print(f" - warehouse.dim_customers test rows: {cust_count}")
    
    # 3. Check warehouse fct_contracts_wide table
    cur.execute("SELECT count(*) FROM warehouse.fct_contracts_wide WHERE contract_id LIKE 'CTR-TEST%';")
    fct_count = cur.fetchone()[0]
    print(f" - warehouse.fct_contracts_wide test rows: {fct_count}")
    
    # 4. Check mart dm_profiling_analysis table
    cur.execute("SELECT count(*) FROM mart.dm_profiling_analysis WHERE contract_id LIKE 'CTR-TEST%';")
    mart_count = cur.fetchone()[0]
    print(f" - mart.dm_profiling_analysis test rows: {mart_count}")
    
    cur.close()
    conn.close()

def main():
    sql_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../docs/sample_insert_tests.sql"))
    
    # 1. Run the inserts on source db
    run_sql_file("insuranceSale", sql_file)
    
    # 2. Sleep for Debezium to stream
    print("Waiting 10 seconds for Debezium logical replication and Kafka streaming...")
    time.sleep(10)
    
    # 3. Run dbt to process the new data
    run_dbt()
    
    # 4. Verify results in warehouse
    verify_results()

if __name__ == '__main__':
    main()
