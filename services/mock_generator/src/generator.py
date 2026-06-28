#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mock Data Generator - Generates messy/unclean source data for PostgreSQL to demo CDC + dbt.
"""
import os
import sys
import time
import random
import uuid
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import execute_values
from faker import Faker

# Initialize Faker
fake = Faker('vi_VN')  # Use Vietnamese locale for realistic names and addresses

# Database connection settings from environment
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_USER = os.getenv('DB_USER', 'insure_admin')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'insure_secure_pass')
DB_NAME = os.getenv('DB_DATABASE', 'insure_production')

# Keep track of generated IDs for updates and claim generation
active_contracts = []
active_objects = {}  # contractId -> list of (objectId, type)
active_claims = []

def get_connection():
    """Establish database connection with retry logic."""
    retries = 10
    conn = None
    while retries > 0:
        try:
            print(f"Connecting to production database at {DB_HOST}:{DB_PORT}/{DB_NAME}...")
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                dbname=DB_NAME
            )
            # Set search path to source schema
            with conn.cursor() as cur:
                cur.execute('CREATE SCHEMA IF NOT EXISTS "source";')
                cur.execute('SET search_path TO "source", public;')
                conn.commit()
            print("Successfully connected to production database.")
            return conn
        except Exception as e:
            print(f"Connection failed: {e}. Retries left: {retries - 1}")
            retries -= 1
            time.sleep(3)
    print("Could not connect to database. Exiting.")
    sys.exit(1)

# Helper to generate messy string values
def make_messy_name(name):
    """Adds leading/trailing spaces, mixed case, and duplicate spaces."""
    r = random.random()
    if r < 0.15:
        # ALL CAPS with extra spaces
        return f"   {name.upper()}   "
    elif r < 0.30:
        # lowercase with messy spacing
        return f"  {name.lower().replace(' ', '   ')} "
    elif r < 0.45:
        # Random capitalization inside words
        words = name.split()
        mixed_words = [w[0].upper() + w[1:-1].lower() + w[-1].upper() if len(w) > 1 else w.upper() for w in words]
        return " ".join(mixed_words)
    return name

def make_messy_email(name, domain=None):
    """Generates email with spaces, weird casing, and typos."""
    if not domain:
        domain = random.choice(['gmail.com', 'Gmail.Com', 'GMAIL.COM', 'yahoo.com.vn', 'Yahoo.com', 'hotmail.com', 'outlook.com.vn'])
    
    clean_name = ''.join(c for c in name if c.isalnum()).lower()
    email = f"{clean_name}@{domain}"
    
    r = random.random()
    if r < 0.15:
        # Leading/trailing spaces
        return f"  {email}  "
    elif r < 0.30:
        # Mixed case
        return email.upper()
    elif r < 0.40:
        # Inject string 'null' or 'n/a'
        return random.choice(['n/a', 'none@example.com', 'null'])
    return email

def make_messy_phone():
    """Generates phone number in multiple formats."""
    formats = [
        "09{d1}{d2}{d3}{d4}{d5}{d6}{d7}{d8}",
        "+849{d1}{d2}{d3}{d4}{d5}{d6}{d7}{d8}",
        "84 9{d1} {d2}{d3}{d4} {d5}{d6}{d7}{d8}",
        "09{d1}-{d2}{d3}{d4}-{d5}{d6}{d7}{d8}",
        "09{d1}.{d2}{d3}{d4}.{d5}{d6}{d7}{d8}",
        " 09{d1}{d2}{d3}{d4}{d5}{d6}{d7}{d8}   ",  # whitespace
        "12345",  # Invalid short phone number
        "n/a",    # Null string placeholder
    ]
    fmt = random.choice(formats)
    digits = {f"d{i}": random.randint(0, 9) for i in range(1, 9)}
    return fmt.format(**digits)

def make_messy_voucher():
    """Generates messy promo codes."""
    codes = ['SALE50', 'sale50', '   PROMO100   ', 'NULL', 'none', 'n/a', 'N/A', '', '   ']
    return random.choice(codes)

def make_messy_company_sale():
    """Generates inconsistent company sale names to clean with dbt."""
    companies = [
        'InsuStream Co. Ltd.', 'insustream', 'INSUSTREAM GROUP', 'InsuStream', '  insustream  ',
        'SafeGuard Corp', 'safeguard', 'SafeGuard Co', 'Aegis Insurances', 'aegis'
    ]
    return random.choice(companies)

def make_messy_program_package(major):
    """Generates inconsistent program and package names depending on major."""
    if major == 'HEALTH':
        programs = ['Premium Care', 'premium care', 'PREMIUM_CARE', 'Gói Chăm sóc Vàng', 'Chăm sóc toàn diện']
        packages = ['Sliver Plan', 'Silver Package', 'GOLD CLASS', 'gold', 'Standard']
    elif major in ['VEHICLE', 'MOTO']:
        programs = ['AutoProtect', 'autoprotect', 'Auto Protect Plus', 'Bảo hiểm thân vỏ']
        packages = ['Gói cơ bản', 'Basic Package', 'Super Protect', 'super_protect']
    else:
        programs = ['Global Travel Care', 'Du lịch hoàn hảo', 'TRAVEL_SAFE']
        packages = ['Gói Châu Á', 'Asia Standard', 'Worldwide Premium', 'WORLDWIDE']
    return random.choice(programs), random.choice(packages)

def make_messy_diagnostic():
    """Generates messy diagnostics containing mixed case, spaces, and typos."""
    diagnostics = [
        "Viêm họng cấp J02",
        "viem hong cap",
        "  viêm phế quản cấp  ",
        "Đau răng số 8",
        "dau rang khong buot",
        "Chấn thương do ngã xe máy",
        "chan thuong day chang dau goi",
        "Thai sản - đẻ thường",
        "sản khoa",
        "Đau mắt đỏ",
        "dau mat",
        "Sốt xuất huyết Dengue",
        "sot xuat huyet",
        "unknown",
        "N/A",
        "null"
    ]
    return random.choice(diagnostics)

def make_messy_clinic():
    """Generates inconsistent clinic/hospital names."""
    clinics = [
        "Bệnh viện Bạch Mai", "bv bach mai", "BENH VIEN BACH MAI", "BV Bạch Mai  ",
        "Bệnh Viện Chợ Rẫy", "bv cho ray", "Cho Ray Hospital",
        "Phòng khám Đa khoa Quốc tế", "pk da khoa qte", "PK DKQT",
        "N/A", "unknown", "Tại nhà"
    ]
    return random.choice(clinics)

# ============================================================================
# Generator Logics
# ============================================================================

def generate_contract_and_objects(conn, object_type=None):
    """Inserts a contract and its matching object details."""
    contract_id = f"CTR-{random.randint(100000, 999999)}-{uuid.uuid4().hex[:6].upper()}"
    buyer_id = f"BYR-{random.randint(10000, 99999)}"
    
    # Base metadata
    created_at = datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
    # Messy date anomaly: modifiedAt is earlier than createdAt in 5% of cases!
    if random.random() < 0.05:
        modified_at = created_at - timedelta(hours=2)
    else:
        modified_at = created_at + timedelta(minutes=random.randint(5, 120))
        
    contract_start = created_at + timedelta(days=1)
    contract_end = contract_start + timedelta(days=365)
    
    # Contract Object Type (1: Health, 2: Vehicle, 3: Travel, 4: Moto, 5: Social, 6: Medical, 7: House)
    if object_type is None:
        object_type = random.choice([1, 2, 3, 4, 5, 6, 7])
    major_map = {1: 'HEALTH', 2: 'VEHICLE', 3: 'TRAVEL', 4: 'MOTO', 5: 'SOCIAL', 6: 'MEDICAL', 7: 'HOUSE'}
    major = major_map[object_type]
    
    program_name, package_name = make_messy_program_package(major)
    raw_name = fake.name()
    messy_name = make_messy_name(raw_name)
    
    # Amounts
    amount = float(random.randint(500000, 15000000))
    discount = amount * random.choice([0, 0.05, 0.1, 0.2]) if random.random() < 0.3 else 0.0
    amount_pay = amount - discount
    
    # 1. Insert into insuranceContract
    contract_sql = """
    INSERT INTO "insuranceContract" (
        "contractId", "contractIdDisplay", "contractStatus", "customerType", "name", 
        "phone", "email", "address", "contractType", "companySale", "companySaleName", 
        "contractStartDate", "contractEndDate", "contractObjectType", "voucherCode", 
        "amountDiscount", "amount", "amountPay", "redBill", "paymentMethod", "source", 
        "createdAt", "createdBy", "modifiedAt", "modifiedBy"
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    
    contract_data = (
        contract_id, contract_id, 1, random.choice([1, 2]), messy_name,
        make_messy_phone(), make_messy_email(raw_name), fake.address().replace('\n', ', '),
        random.choice([1, 2]), make_messy_company_sale().lower(), make_messy_company_sale(),
        contract_start, contract_end, object_type, make_messy_voucher(),
        discount, amount, amount_pay, random.choice([0, 1]), random.choice([1, 2, 3]),
        1, created_at, 'admin', modified_at, 'admin'
    )
    
    object_id = f"OBJ-{uuid.uuid4().hex[:10].upper()}"
    
    # Specific object insert queries
    object_sql = ""
    object_data = ()
    
    # Basic shared object attributes
    rel = random.choice([0, 1, 2, 3, 4, 5, 6])
    dob = fake.date_of_birth(minimum_age=18, maximum_age=65)
    gender = random.choice([0, 1, 2, 3]) # 3 is invalid/messy gender
    
    if object_type == 1:  # Health
        object_sql = """
        INSERT INTO "insuranceContractObject" (
            "contractObjectId", "contractId", "programTypeName", "programTypeId", "programId", 
            "programName", "packageId", "packageName", "fromAge", "toAge", "feeMainBenefit", 
            "termsId", "majorName", "majorId", "productId", "codeFromProvider", "feeInsurance", 
            "maximumAmount", "companyProvider", "companyProviderName", "contractObjectType", 
            "peopleRelationship", "peopleName", "peopleDob", "peopleGender", "peoplePhone", 
            "peopleEmail", "peopleAddress", "peopleLicenseType", "createdBy", "modifiedBy"
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        object_data = (
            object_id, contract_id, 'HEALTH', '1', 'PG-HEALTH', program_name, 'PKG-HEALTH', package_name, 
            18, 65, amount_pay, 'TERM-H1', 'HEALTH', '101', 'PROD-HEALTH', 'PROV-HEALTH-CODE', amount, 
            50000000, 'INS-CORP', 'InsureCorp', 1, rel, messy_name, dob, gender, make_messy_phone(), 
            make_messy_email(raw_name), fake.address().replace('\n', ', '), 1, 'admin', 'admin'
        )
        
    elif object_type == 2:  # Vehicle
        object_sql = """
        INSERT INTO "insuranceContractObjectVehicle" (
            "contractObjectId", "contractId", "programTypeName", "programTypeId", "programId", 
            "programName", "packageId", "packageName", "feeMainBenefit", "termsId", "majorName", 
            "majorId", "productId", "feeInsurance", "maximumAmount", "companyProvider", 
            "companyProviderName", "contractObjectType", "peopleRelationship", "peopleName", 
            "peoplePhone", "peopleEmail", "peopleAddress", "createdBy", "modifiedBy"
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        object_data = (
            object_id, contract_id, 'VEHICLE', '2', 'PG-VEHICLE', program_name, 'PKG-VEHICLE', package_name, 
            amount_pay, 'TERM-V1', 'VEHICLE', '102', 'PROD-VEHICLE', amount, amount * 10, 'INS-CORP', 
            'InsureCorp', 2, rel, messy_name, make_messy_phone(), make_messy_email(raw_name), 
            fake.address().replace('\n', ', '), 'admin', 'admin'
        )
        
    elif object_type == 3:  # Travel
        object_sql = """
        INSERT INTO "insuranceContractObjectTravel" (
            "id", "contractId", "userId", "programTypeName", "programTypeId", "programId", 
            "programName", "packageId", "packageName", "feeMainBenefit", "termsId", "majorName", 
            "majorId", "productId", "programObject", "feeInsurance", "companyProvider", 
            "companyProviderName", "name", "dob", "gender", "phone", "email", "address", 
            "licenseType", "domesticOrInternational", "departure", "payerLicenseType", "createdBy", "modifiedBy"
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        object_data = (
            object_id, contract_id, buyer_id, 'TRAVEL', '3', 'PG-TRAVEL', program_name, 'PKG-TRAVEL', package_name, 
            amount_pay, 'TERM-T1', 'TRAVEL', '103', 'PROD-TRAVEL', 1, amount, 'INS-CORP', 'InsureCorp', 
            messy_name, dob, gender, make_messy_phone(), make_messy_email(raw_name), fake.address().replace('\n', ', '), 
            1, random.choice([1, 2]), fake.city(), 1, 'admin', 'admin'
        )
        
    elif object_type == 4:  # Moto
        # Same schema structure for moto (using stgContractObjectMoto logic)
        object_sql = """
        INSERT INTO "insuranceContractObjectMoto" (
            "id", "contractId", "userId", "programTypeName", "programTypeId", "programId", 
            "programName", "packageId", "packageName", "feeMainBenefit", "termsId", "majorName", 
            "majorId", "productId", "feeInsurance", "maximumAmount", "companyProvider", "companyProviderName", 
            "name", "dob", "gender", "phone", "email", "address", "licenseType", "type", "createdBy", "modifiedBy"
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        object_data = (
            object_id, contract_id, buyer_id, 'MOTO', '4', 'PG-MOTO', program_name, 'PKG-MOTO', package_name, 
            amount_pay, 'TERM-M1', 'MOTO', '104', 'PROD-MOTO', amount, amount * 0.8, 'INS-CORP', 'InsureCorp', 
            messy_name, dob, gender, make_messy_phone(), make_messy_email(raw_name), fake.address().replace('\n', ', '), 
            1, random.choice([1, 2]), 'admin', 'admin'
        )
        
    elif object_type == 5:  # Social
        object_sql = """
        INSERT INTO "insuranceContractObjectSocialInsurance" (
            "contractObjectId", "contractId", "programTypeName", "programTypeId", "programId", 
            "programName", "packageId", "packageName", "fromAge", "toAge", "feeMainBenefit", 
            "majorName", "majorId", "productId", "feeInsurance", "maximumAmount", "companyProvider", 
            "companyProviderName", "contractObjectType", "peopleRelationship", "peopleName", 
            "peopleDob", "peopleGender", "peoplePhone", "peopleEmail", "peopleAddress", 
            "peopleLicenseType", "createdBy", "modifiedBy"
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        object_data = (
            object_id, contract_id, 'SOCIAL', '5', 'PG-SOCIAL', program_name, 'PKG-SOCIAL', package_name, 
            18, 65, amount_pay, 'SOCIAL', '105', 'PROD-SOCIAL', amount, amount, 'INS-CORP', 'InsureCorp', 
            5, rel, messy_name, dob, gender, make_messy_phone(), make_messy_email(raw_name), 
            fake.address().replace('\n', ', '), 1, 'admin', 'admin'
        )
        
    elif object_type == 6:  # Medical
        object_sql = """
        INSERT INTO "insuranceContractObjectMedicalInsurance" (
            "contractObjectId", "contractId", "programTypeName", "programTypeId", "programId", 
            "programName", "packageId", "packageName", "feeMainBenefit", "majorName", "majorId", 
            "productId", "feeInsurance", "maximumAmount", "companyProvider", "companyProviderName", 
            "contractObjectType", "peopleRelationship", "peopleName", "peopleDob", "peopleGender", 
            "peoplePhone", "peopleEmail", "peopleAddress", "peopleLicenseType", "createdBy", "modifiedBy"
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        object_data = (
            object_id, contract_id, 'MEDICAL', '6', 'PG-MEDICAL', program_name, 'PKG-MEDICAL', package_name, 
            amount_pay, 'MEDICAL', '106', 'PROD-MEDICAL', amount, amount, 'INS-CORP', 'InsureCorp', 
            6, rel, messy_name, dob, gender, make_messy_phone(), make_messy_email(raw_name), 
            fake.address().replace('\n', ', '), 1, 'admin', 'admin'
        )
        
    elif object_type == 7:  # House
        object_sql = """
        INSERT INTO "insuranceContractObjectHouse" (
            "id", "contractId", "userId", "programTypeName", "programTypeId", "programId", 
            "programName", "packageId", "packageName", "feeMainBenefit", "majorName", "majorId", 
            "productId", "feeInsurance", "maximumAmount", "companyProvider", "companyProviderName", 
            "name", "dob", "gender", "phone", "email", "address", "houseAddress", "houseValue", 
            "houseValueInsured", "createdBy", "modifiedBy"
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        object_data = (
            object_id, contract_id, buyer_id, 'HOUSE', '7', 'PG-HOUSE', program_name, 'PKG-HOUSE', package_name, 
            amount_pay, 'HOUSE', '107', 'PROD-HOUSE', amount, amount * 1.5, 'INS-CORP', 'InsureCorp', 
            messy_name, dob, gender, make_messy_phone(), make_messy_email(raw_name), fake.address().replace('\n', ', '), 
            fake.address().replace('\n', ', '), amount * 2, amount * 1.5, 'admin', 'admin'
        )
        
    # Transactional execution
    try:
        with conn.cursor() as cur:
            cur.execute(contract_sql, contract_data)
            cur.execute(object_sql, object_data)
            conn.commit()
            
        # Append to trackers
        active_contracts.append(contract_id)
        if contract_id not in active_objects:
            active_objects[contract_id] = []
        active_objects[contract_id].append((object_id, object_type))
        
        print(f"Generated new contract: {contract_id} with object {object_id} ({major})")
        
        # Keep lists bounded
        if len(active_contracts) > 200:
            removed = active_contracts.pop(0)
            active_objects.pop(removed, None)
            
    except Exception as e:
        conn.rollback()
        print(f"Failed to generate contract: {e}")

def update_random_contract(conn):
    """Updates contract fields to generate CDC update logs."""
    if not active_contracts:
        return
        
    contract_id = random.choice(active_contracts)
    
    # Randomly toggle status or adjust values
    r = random.random()
    if r < 0.4:
        sql = 'UPDATE "insuranceContract" SET "contractStatus" = %s, "modifiedAt" = %s, "modifiedBy" = %s WHERE "contractId" = %s;'
        new_status = random.choice([2, 3, 4])  # 2: Active, 3: Suspended, 4: Cancelled
        data = (new_status, datetime.now(), 'system_updater', contract_id)
        action = f"status to {new_status}"
    elif r < 0.7:
        sql = 'UPDATE "insuranceContract" SET "note" = %s, "redBill" = %s, "modifiedAt" = %s WHERE "contractId" = %s;'
        data = (f"Updated notes {fake.word()}", random.choice([0, 1]), datetime.now(), contract_id)
        action = "notes and bill status"
    else:
        sql = 'UPDATE "insuranceContract" SET "amountPay" = "amountPay" * 0.9, "modifiedAt" = %s WHERE "contractId" = %s;'
        data = (datetime.now(), contract_id)
        action = "discounted amountPay by 10%"
        
    try:
        with conn.cursor() as cur:
            cur.execute(sql, data)
            conn.commit()
        print(f"Updated contract {contract_id}: Changed {action}.")
    except Exception as e:
        conn.rollback()
        print(f"Failed to update contract {contract_id}: {e}")

def generate_claim(conn):
    """Creates a claim for an existing contract/object."""
    if not active_contracts:
        return
        
    contract_id = random.choice(active_contracts)
    objs = active_objects.get(contract_id, [])
    if not objs:
        return
        
    object_id, object_type = random.choice(objs)
    claim_id = f"CLM-{random.randint(100000, 999999)}-{uuid.uuid4().hex[:6].upper()}"
    
    # Generate amount details
    claim_amount = float(random.randint(100000, 20000000))
    # Unclean data anomaly: compensationAmount > amountClaim in 10% of cases!
    if random.random() < 0.10:
        comp_amount = claim_amount * random.choice([1.2, 1.5, 2.0])
    else:
        comp_amount = claim_amount * random.choice([0.5, 0.7, 0.9, 1.0])
        
    hosp_date = fake.date_between(start_date="-30d", end_date="today")
    discharge_date = hosp_date + timedelta(days=random.randint(1, 14))
    
    # We write dates or timestamps
    created_at = datetime.now()
    modified_at = created_at
    
    claim_sql = """
    INSERT INTO "insuranceClaim" (
        "id", "contractId", "contractObjectId", "amountClaim", "compensationAmount", 
        "note", "bankName", "accountNumberBank", "accountName", "relationship", "claimType", 
        "hospitalizedDate", "hospitalDischargeDate", "placeOfTreatment", "diagnostic", 
        "name", "phone", "email", "status", "createdAt", "createdBy", "modifiedAt", "modifiedBy"
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    
    name = fake.name()
    vietnamese_banks = ['Vietcombank', 'BIDV', 'Techcombank', 'VietinBank', 'Agribank', 'MB Bank', 'VPBank', 'ACB', 'Sacombank', 'TPBank']
    claim_data = (
        claim_id, contract_id, object_id, claim_amount, comp_amount,
        f"Claim note: {fake.sentence()}", random.choice(vietnamese_banks), str(random.randint(1000000000, 999999999999)), name.upper(),
        random.choice([0, 1, 2, 3, 4, 5, 6]), random.choice([1, 2]), hosp_date, discharge_date,
        make_messy_clinic(), make_messy_diagnostic(), make_messy_name(name),
        make_messy_phone(), make_messy_email(name), 1, created_at, 'claim_portal', modified_at, 'claim_portal'
    )
    
    try:
        with conn.cursor() as cur:
            cur.execute(claim_sql, claim_data)
            conn.commit()
            
        active_claims.append(claim_id)
        print(f"Generated new claim: {claim_id} for contract {contract_id} (Claim Amount: {claim_amount})")
        
        if len(active_claims) > 100:
            active_claims.pop(0)
    except Exception as e:
        conn.rollback()
        print(f"Failed to generate claim: {e}")

def update_random_claim(conn):
    """Updates claim status to generate CDC update logs."""
    if not active_claims:
        return
        
    claim_id = random.choice(active_claims)
    
    r = random.random()
    if r < 0.5:
        # Update status
        new_status = random.choice([2, 3, 4])  # 2: Approved, 3: Rejected, 4: Under Review
        sql = 'UPDATE "insuranceClaim" SET "status" = %s, "modifiedAt" = %s, "modifiedBy" = %s WHERE "id" = %s;'
        data = (new_status, datetime.now(), 'claim_verifier', claim_id)
        action = f"status to {new_status}"
    else:
        # Update notes & compensation
        sql = 'UPDATE "insuranceClaim" SET "note" = %s, "compensationAmount" = "compensationAmount" * 1.05, "modifiedAt" = %s WHERE "id" = %s;'
        data = (f"Recalculated compensation {fake.word()}", datetime.now(), claim_id)
        action = "compensation recalculation"
        
    try:
        with conn.cursor() as cur:
            cur.execute(sql, data)
            conn.commit()
        print(f"Updated claim {claim_id}: {action}.")
    except Exception as e:
        conn.rollback()
        print(f"Failed to update claim {claim_id}: {e}")

# ============================================================================
# Main Loop
# ============================================================================

def main():
    print("====================================================================")
    print("INSURANCE MOCK DATA GENERATOR (MESSY DATA EDITION)")
    print("Generating slightly unclean data for CDC & dbt testing...")
    print("====================================================================")
    
    conn = get_connection()
    
    try:
        # Warmup/Seeding Phase: 40 contracts for each of the 7 types (280 total), plus 50 claims
        print("Initial Seeding: Generating 40 contracts for each of the 7 insurance types (280 total)...")
        for obj_type in range(1, 8):
            for _ in range(40):
                generate_contract_and_objects(conn, object_type=obj_type)
        
        print("Initial Seeding: Generating 50 initial claims...")
        for _ in range(50):
            generate_claim(conn)
        print("Initial Seeding completed successfully!")
            
        while True:
            # Random event type selection
            # 55% Insert Contract, 20% Update Contract, 15% Insert Claim, 10% Update Claim
            event_choice = random.random()
            
            if event_choice < 0.55:
                generate_contract_and_objects(conn)
            elif event_choice < 0.75:
                update_random_contract(conn)
            elif event_choice < 0.90:
                generate_claim(conn)
            else:
                update_random_claim(conn)
                
            sleep_time = random.uniform(55.0, 65.0)
            print(f"Sleeping for {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print("\nStopping mock generator.")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    main()
