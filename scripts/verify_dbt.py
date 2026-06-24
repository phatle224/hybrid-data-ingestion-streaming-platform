import psycopg2

def main():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="${DB_PASSWORD}",
            dbname="insuranceWarehouse"
        )
        cur = conn.cursor()
        
        # Check schemas
        cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name IN ('staging', 'intermediate', 'warehouse', 'mart');")
        schemas = [row[0] for row in cur.fetchall()]
        print(f"Active Schemas: {schemas}")
        
        # Check records in reporting models
        tables = {
            'warehouse.dim_customers': ('warehouse', 'dim_customers'),
            'warehouse.fct_contracts_wide': ('warehouse', 'fct_contracts_wide'),
            'mart.dm_profiling_analysis': ('mart', 'dm_profiling_analysis')
        }
        
        print("\nRecord Counts in Reporting Layer (DBT Marts):")
        print("-" * 50)
        for label, (schema, table) in tables.items():
            try:
                cur.execute(f'SELECT count(*) FROM "{schema}"."{table}";')
                count = cur.fetchone()[0]
                print(f" - {label}: {count} records")
            except Exception as e:
                print(f" - {label}: ERROR: {e}")
                conn.rollback()
                
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == '__main__':
    main()
