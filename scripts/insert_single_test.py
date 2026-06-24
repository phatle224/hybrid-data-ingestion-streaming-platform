import psycopg2
from datetime import datetime

def main():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="Lhp542004@",
            dbname="insuranceSale"
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # Unique contract ID for test
        contract_id = f"CTR-TEST-LIVE-{int(datetime.now().timestamp())}"
        object_id = f"OBJ-TEST-LIVE-{int(datetime.now().timestamp())}"
        
        print(f"Inserting test contract {contract_id} and object {object_id} to source DB...")
        
        # 1. Insert contract
        cur.execute(f"""
            INSERT INTO source."insuranceContract" (
                "contractId", "contractIdDisplay", "contractStatus", "customerType", "name", 
                "phone", "email", "address", "contractType", "companySale", "companySaleName", 
                "contractStartDate", "contractEndDate", "contractObjectType", "voucherCode", 
                "amountDiscount", "amount", "amountPay", "redBill", "paymentMethod", "source", 
                "createdAt", "createdBy", "modifiedAt", "modifiedBy"
            ) VALUES (
                '{contract_id}', '{contract_id}', 1, 1, '  ngUYEn VaN TEST LIVE  ', 
                '0911222333', 'test_live@example.com', '123 Test Street, Hanoi', 1, 
                'affina', 'Affina Group', '2026-06-25', '2027-06-25', 3, 'SALE50', 
                0.0, 1000000.0, 1000000.0, 0, 1, 1, 
                NOW(), 'test_user', NOW(), 'test_user'
            );
        """)
        
        # 2. Insert travel object (type 3)
        cur.execute(f"""
            INSERT INTO source."insuranceContractObjectTravel" (
                "id", "contractId", "userId", "programTypeName", "programTypeId", "programId", 
                "programName", "packageId", "packageName", "feeMainBenefit", "termsId", "majorName", 
                "majorId", "productId", "programObject", "feeInsurance", "companyProvider", 
                "companyProviderName", "name", "dob", "gender", "phone", "email", "address", 
                "licenseType", "domesticOrInternational", "departure", "payerLicenseType", 
                "createdBy", "modifiedBy"
            ) VALUES (
                '{object_id}', '{contract_id}', 'USR-999', 'TRAVEL', '3', 'PG-TRAVEL', 
                'Global Travel Protect', 'PKG-TRAVEL-BASIC', 'Basic Plan', 1000000.0, 'TERM-T1', 
                'TRAVEL', '103', 'PROD-TRAVEL', 1, 1000000.0, 'INS-CORP', 'InsureCorp', 
                '  ngUYEn VaN TEST LIVE  ', '1990-01-01', 1, '0911222333', 'test_live@example.com', 
                '123 Test Street, Hanoi', 1, 1, 'Hanoi', 1, 'test_user', 'test_user'
            );
        """)
        
        print("Insert successful!")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
