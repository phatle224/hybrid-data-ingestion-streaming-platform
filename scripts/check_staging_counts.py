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
        
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='staging' AND table_name LIKE 'stgInsurance%';")
        tables = [row[0] for row in cur.fetchall()]
        
        print("Row counts for staging tables:")
        print("-" * 50)
        for t in sorted(tables):
            cur.execute(f'SELECT count(*) FROM "staging"."{t}";')
            count = cur.fetchone()[0]
            print(f" - {t}: {count} rows")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == '__main__':
    main()
