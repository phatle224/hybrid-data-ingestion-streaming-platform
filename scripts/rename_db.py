import psycopg2

def main():
    try:
        # Connect to 'postgres' database to perform administrative tasks
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="${DB_PASSWORD}",
            dbname="postgres"
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        print("Terminating existing connections to insuranceStaging...")
        cur.execute("""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = 'insuranceStaging'
              AND pid <> pg_backend_pid();
        """)
        
        print("Renaming database from insuranceStaging to insuranceWarehouse...")
        cur.execute('ALTER DATABASE "insuranceStaging" RENAME TO "insuranceWarehouse";')
        print("Database renamed successfully!")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error during database rename: {e}")

if __name__ == '__main__':
    main()
