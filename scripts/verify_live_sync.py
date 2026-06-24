import psycopg2

def main():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="Lhp542004@",
            dbname="insuranceWarehouse"
        )
        cur = conn.cursor()
        
        # 1. Staging Count
        cur.execute('SELECT "contractId", name, email FROM staging."stgInsuranceContract" WHERE "contractId" LIKE \'CTR-TEST-LIVE-%\';')
        stg_rows = cur.fetchall()
        print(f"--- Staging: Found {len(stg_rows)} test contracts ---")
        for row in stg_rows:
            print(f"  Staging Row: ID={row[0]}, Name='{row[1]}', Email='{row[2]}'")
            
        # 2. Warehouse Customer Count
        cur.execute("SELECT customer_key, customer_name, customer_email FROM warehouse.dim_customers WHERE customer_email = 'test_live@example.com';")
        wh_custs = cur.fetchall()
        print(f"\n--- Warehouse dim_customers: Found {len(wh_custs)} test customers ---")
        for cust in wh_custs:
            print(f"  Warehouse Cust: Key={cust[0]}, Name='{cust[1]}', Email='{cust[2]}'")
            
        # 3. Warehouse Fact Count
        cur.execute("SELECT contract_id, insured_name, major_name FROM warehouse.fct_contracts_wide WHERE contract_id LIKE 'CTR-TEST-LIVE-%';")
        wh_facts = cur.fetchall()
        print(f"\n--- Warehouse fct_contracts_wide: Found {len(wh_facts)} test contracts ---")
        for fact in wh_facts:
            print(f"  Warehouse Fact: ID={fact[0]}, Insured='{fact[1]}', Major='{fact[2]}'")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
