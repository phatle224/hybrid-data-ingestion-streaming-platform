import psycopg2

def check_db(dbname, prefix, tables, is_source=True):
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="${DB_PASSWORD}",
        dbname=dbname
    )
    cur = conn.cursor()
    schema = "source" if is_source else "staging"
    cur.execute(f"SET search_path TO {schema}, public;")
    
    print(f"\nRecord Counts in {dbname} ({schema.upper()} DB):")
    print("-" * 50)
    
    total = 0
    for name, table in tables.items():
        try:
            cur.execute(f'SELECT count(*) FROM "{table}";')
            count = cur.fetchone()[0]
            total += count
            print(f" - {name} ({table}): {count} records")
        except Exception as e:
            print(f" - {name} ({table}): ERROR: {e}")
            conn.rollback()
            
    print(f"Total: {total}")
    cur.close()
    conn.close()

def main():
    source_tables = {
        'Master Contract': 'insuranceContract',
        'HEALTH Object': 'insuranceContractObject',
        'VEHICLE Object': 'insuranceContractObjectVehicle',
        'TRAVEL Object': 'insuranceContractObjectTravel',
        'MOTO Object': 'insuranceContractObjectMoto',
        'SOCIAL Object': 'insuranceContractObjectSocialInsurance',
        'MEDICAL Object': 'insuranceContractObjectMedicalInsurance',
        'HOUSE Object': 'insuranceContractObjectHouse',
        'Claims': 'insuranceClaim'
    }
    
    staging_tables = {
        'Master Contract': 'stgInsuranceContract',
        'HEALTH Object': 'stgInsuranceContractObject',
        'VEHICLE Object': 'stgInsuranceContractObjectVehicle',
        'TRAVEL Object': 'stgInsuranceContractObjectTravel',
        'MOTO Object': 'stgInsuranceContractObjectMoto',
        'SOCIAL Object': 'stgInsuranceContractObjectSocialInsurance',
        'MEDICAL Object': 'stgInsuranceContractObjectMedicalInsurance',
        'HOUSE Object': 'stgInsuranceContractObjectHouse',
        'Claims': 'stgInsuranceClaim'
    }
    
    check_db("insuranceSale", "source", source_tables, is_source=True)
    check_db("insuranceStaging", "staging", staging_tables, is_source=False)

if __name__ == '__main__':
    main()
