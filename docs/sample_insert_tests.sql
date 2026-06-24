-- ============================================================================
-- SQL Script for CDC Data Ingestion Testing
-- Database: insuranceSale (SOURCE DB)
-- Schema: source
-- ============================================================================

-- 1. Switch search path to the source schema
SET search_path TO "source", public;

-- 2. Clean old test data if needed (uncomment to reset test rows)
DELETE FROM "insuranceClaim" WHERE "id" LIKE 'CLM-TEST%';
DELETE FROM "insuranceContractObjectHouse" WHERE "id" LIKE 'OBJ-TEST%';
DELETE FROM "insuranceContractObjectMedicalInsurance" WHERE "contractObjectId" LIKE 'OBJ-TEST%';
DELETE FROM "insuranceContractObjectSocialInsurance" WHERE "contractObjectId" LIKE 'OBJ-TEST%';
DELETE FROM "insuranceContractObjectMoto" WHERE "id" LIKE 'OBJ-TEST%';
DELETE FROM "insuranceContractObjectTravel" WHERE "id" LIKE 'OBJ-TEST%';
DELETE FROM "insuranceContractObjectVehicle" WHERE "contractObjectId" LIKE 'OBJ-TEST%';
DELETE FROM "insuranceContractObject" WHERE "contractObjectId" LIKE 'OBJ-TEST%';
DELETE FROM "insuranceContract" WHERE "contractId" LIKE 'CTR-TEST%';

-- ============================================================================
-- A. INSERT 5 SAMPLE CONTRACTS (insuranceContract)
-- ============================================================================
INSERT INTO "insuranceContract" (
  "contractId", "contractIdDisplay", "customerType", "name", "email", "phone",
  "contractType", "companySale", "companySaleName", "contractObjectType", "source", 
  "amount", "amountPay", "contractStartDate", "contractEndDate", "createdAt", "modifiedAt"
) VALUES 
('CTR-TEST-001', 'CTR-TEST-DISPLAY-001', 1, '  nGuYeN tHi tEsT oNe  ', 'test.one@gmail.com', '0912345678', 1, 'AGENT_A', 'Agent A Company', 1, 1, 15000000.00, 15000000.00, NOW(), NOW() + INTERVAL '1 year', NOW(), NOW()),
('CTR-TEST-002', 'CTR-TEST-DISPLAY-002', 1, '  TrAn VaN tEsT tWo  ', 'test.two@yahoo.com', '0987654321', 1, 'AGENT_B', 'Agent B LLC', 2, 1, 2500000.00, 2250000.00, NOW(), NOW() + INTERVAL '1 year', NOW(), NOW()),
('CTR-TEST-003', 'CTR-TEST-DISPLAY-003', 2, '  cOnG tY tEsT tHrEe  ', 'contact@testthree.vn', '0281234567', 2, 'DIRECT', 'Direct Channel', 3, 1, 45000000.00, 45000000.00, NOW(), NOW() + INTERVAL '6 months', NOW(), NOW()),
('CTR-TEST-004', 'CTR-TEST-DISPLAY-004', 1, '  pHaM mInH tEsT fOuR  ', 'pham.test4@gmail.com', '0901234567', 1, 'AGENT_A', 'Agent A Company', 4, 1, 1200000.00, 1200000.00, NOW(), NOW() + INTERVAL '1 year', NOW(), NOW()),
('CTR-TEST-005', 'CTR-TEST-DISPLAY-005', 1, '  Le hUaN tEsT fIvE  ', 'le.test5@outlook.com', '0933445566', 1, 'AGENT_C', 'Agent C Group', 5, 1, 8000000.00, 7200000.00, NOW(), NOW() + INTERVAL '1 year', NOW(), NOW());


-- ============================================================================
-- B. INSERT 5 HEALTH OBJECTS (insuranceContractObject)
-- ============================================================================
INSERT INTO "insuranceContractObject" (
  "contractObjectId", "contractId", "programTypeName", "programTypeId", "programId", "programName",
  "packageId", "packageName", "fromAge", "toAge", "feeMainBenefit", "termsId", "majorName", "majorId",
  "productId", "codeFromProvider", "feeInsurance", "maximumAmount", "companyProvider", "companyProviderName",
  "contractObjectType", "peopleLicenseType", "createdBy", "modifiedBy", "peopleName", "peopleDob", "peopleGender"
) VALUES 
('OBJ-TEST-HLT-001', 'CTR-TEST-001', 'Health Care', 'PG-01', 'PR-01', 'Care Premium', 'PK-01', 'Gold Package', 18, 60, 5000000.00, 'T-01', 'Health Major', 'MJ-01', 'PD-01', 'PROV-001', 5000000.00, 100000000.00, 'BAO_VIET', 'Bao Viet Insurance', 1, 1, 'admin', 'admin', 'Nguyen Thi Test One', '1990-05-15', 2),
('OBJ-TEST-HLT-002', 'CTR-TEST-001', 'Health Care', 'PG-01', 'PR-01', 'Care Premium', 'PK-02', 'Silver Package', 18, 60, 3000000.00, 'T-01', 'Health Major', 'MJ-01', 'PD-01', 'PROV-001', 3000000.00, 60000000.00, 'BAO_VIET', 'Bao Viet Insurance', 1, 1, 'admin', 'admin', 'Nguyen Van Test Child', '2015-08-20', 1),
('OBJ-TEST-HLT-003', 'CTR-TEST-002', 'Standard Health', 'PG-02', 'PR-02', 'Care Standard', 'PK-03', 'Bronze Package', 0, 17, 2000000.00, 'T-02', 'Health Major', 'MJ-01', 'PD-01', 'PROV-002', 2000000.00, 40000000.00, 'PVI', 'PVI Insurance', 1, 1, 'admin', 'admin', 'Tran Van Test Two', '1985-12-10', 1),
('OBJ-TEST-HLT-004', 'CTR-TEST-003', 'Corporate Health', 'PG-03', 'PR-03', 'Care Corp', 'PK-01', 'Gold Package', 18, 65, 8000000.00, 'T-01', 'Health Major', 'MJ-01', 'PD-01', 'PROV-001', 8000000.00, 200000000.00, 'BAO_VIET', 'Bao Viet Insurance', 1, 1, 'admin', 'admin', 'Company Director', '1975-01-01', 1),
('OBJ-TEST-HLT-005', 'CTR-TEST-005', 'Health Care', 'PG-01', 'PR-01', 'Care Premium', 'PK-02', 'Silver Package', 18, 60, 3000000.00, 'T-01', 'Health Major', 'MJ-01', 'PD-01', 'PROV-001', 3000000.00, 60000000.00, 'BAO_VIET', 'Bao Viet Insurance', 1, 1, 'admin', 'admin', 'Le Huan Test Five', '1988-11-25', 1);


-- ============================================================================
-- C. INSERT 5 VEHICLE OBJECTS (insuranceContractObjectVehicle)
-- ============================================================================
INSERT INTO "insuranceContractObjectVehicle" (
  "contractObjectId", "contractId", "userId", "programName", "packageName", "feeInsurance", 
  "companyProviderName", "createdAt", "createdBy", "modifiedAt", "modifiedBy"
) VALUES 
('OBJ-TEST-VEH-001', 'CTR-TEST-002', 'USER-002', 'Auto Protect', 'Premium Auto', 4500000.00, 'PVI Insurance', NOW(), 'admin', NOW(), 'admin'),
('OBJ-TEST-VEH-002', 'CTR-TEST-002', 'USER-002', 'Auto Protect', 'Basic Auto', 2000000.00, 'PVI Insurance', NOW(), 'admin', NOW(), 'admin'),
('OBJ-TEST-VEH-003', 'CTR-TEST-003', 'USER-003', 'Fleet Shield', 'Gold Auto', 12000000.00, 'Bao Viet Insurance', NOW(), 'admin', NOW(), 'admin'),
('OBJ-TEST-VEH-004', 'CTR-TEST-004', 'USER-004', 'Auto Protect', 'Basic Auto', 2000000.00, 'Bao Viet Insurance', NOW(), 'admin', NOW(), 'admin'),
('OBJ-TEST-VEH-005', 'CTR-TEST-005', 'USER-005', 'Auto Protect', 'Premium Auto', 4500000.00, 'PVI Insurance', NOW(), 'admin', NOW(), 'admin');


-- ============================================================================
-- D. INSERT 5 TRAVEL OBJECTS (insuranceContractObjectTravel)
-- ============================================================================
INSERT INTO "insuranceContractObjectTravel" (
  "id", "userId", "contractId", "programTypeName", "programTypeId", "programId", "programName",
  "packageId", "packageName", "feeMainBenefit", "termsId", "majorName", "majorId", "productId",
  "programObject", "feeInsurance", "companyProvider", "companyProviderName", "licenseType",
  "domesticOrInternational", "departure", "payerLicenseType", "createdBy", "modifiedBy",
  "name", "dob", "gender", "phone", "email"
) VALUES 
('OBJ-TEST-TVL-001', 'USER-001', 'CTR-TEST-001', 'Travel Safe', 'PG-TVL', 'PR-TVL', 'Travel Care', 'PK-TVL-1', 'Basic Plan', 150000.00, 'T-TVL', 'Travel', 'MJ-TVL', 'PD-TVL', 1, 150000.00, 'PTI', 'PTI Insurance', 1, 1, 'Hanoi', 1, 'admin', 'admin', 'Nguyen Thi Test One', '1990-05-15', 2, '0912345678', 'test.one@gmail.com'),
('OBJ-TEST-TVL-002', 'USER-002', 'CTR-TEST-002', 'Travel Safe', 'PG-TVL', 'PR-TVL', 'Travel Care', 'PK-TVL-2', 'Europe Gold', 500000.00, 'T-TVL', 'Travel', 'MJ-TVL', 'PD-TVL', 1, 500000.00, 'PTI', 'PTI Insurance', 1, 2, 'Saigon', 1, 'admin', 'admin', 'Tran Van Test Two', '1985-12-10', 1, '0987654321', 'test.two@yahoo.com'),
('OBJ-TEST-TVL-003', 'USER-003', 'CTR-TEST-003', 'Travel Safe', 'PG-TVL', 'PR-TVL', 'Travel Care', 'PK-TVL-2', 'Europe Gold', 500000.00, 'T-TVL', 'Travel', 'MJ-TVL', 'PD-TVL', 1, 500000.00, 'Bao Viet', 'Bao Viet Insurance', 1, 2, 'Danang', 1, 'admin', 'admin', 'Company Director', '1975-01-01', 1, '0281234567', 'contact@testthree.vn'),
('OBJ-TEST-TVL-004', 'USER-004', 'CTR-TEST-004', 'Travel Safe', 'PG-TVL', 'PR-TVL', 'Travel Care', 'PK-TVL-1', 'Basic Plan', 150000.00, 'T-TVL', 'Travel', 'MJ-TVL', 'PD-TVL', 1, 150000.00, 'PTI', 'PTI Insurance', 1, 1, 'Hanoi', 1, 'admin', 'admin', 'Pham Minh Test Four', '2000-01-01', 1, '0901234567', 'pham.test4@gmail.com'),
('OBJ-TEST-TVL-005', 'USER-005', 'CTR-TEST-005', 'Travel Safe', 'PG-TVL', 'PR-TVL', 'Travel Care', 'PK-TVL-2', 'Europe Gold', 500000.00, 'T-TVL', 'Travel', 'MJ-TVL', 'PD-TVL', 1, 500000.00, 'PTI', 'PTI Insurance', 1, 2, 'Saigon', 1, 'admin', 'admin', 'Le Huan Test Five', '1988-11-25', 1, '0933445566', 'le.test5@outlook.com');


-- ============================================================================
-- E. INSERT 5 MOTO OBJECTS (insuranceContractObjectMoto)
-- ============================================================================
INSERT INTO "insuranceContractObjectMoto" (
  "id", "userId", "contractId", "programTypeName", "programTypeId", "programId", "programName",
  "packageId", "packageName", "feeMainBenefit", "termsId", "majorName", "majorId", "productId",
  "feeInsurance", "maximumAmount", "companyProvider", "companyProviderName", "type", 
  "createdBy", "modifiedBy", "name", "phone"
) VALUES 
('OBJ-TEST-MTO-001', 'USER-004', 'CTR-TEST-004', 'Moto Protect', 'PG-MTO', 'PR-MTO', '2-Wheel Safe', 'PK-MTO-1', 'Mandatory Plan', 66000.00, 'T-MTO', 'Moto', 'MJ-MTO', 'PD-MTO', 66000.00, 100000000.00, 'PVI', 'PVI Insurance', 1, 'admin', 'admin', 'Pham Minh Test Four', '0901234567'),
('OBJ-TEST-MTO-002', 'USER-004', 'CTR-TEST-004', 'Moto Protect', 'PG-MTO', 'PR-MTO', '2-Wheel Safe', 'PK-MTO-2', 'Comprehensive Plan', 150000.00, 'T-MTO', 'Moto', 'MJ-MTO', 'PD-MTO', 150000.00, 150000000.00, 'PVI', 'PVI Insurance', 2, 'admin', 'admin', 'Pham Minh Moto 2', '0901234567'),
('OBJ-TEST-MTO-003', 'USER-001', 'CTR-TEST-001', 'Moto Protect', 'PG-MTO', 'PR-MTO', '2-Wheel Safe', 'PK-MTO-1', 'Mandatory Plan', 66000.00, 'T-MTO', 'Moto', 'MJ-MTO', 'PD-MTO', 66000.00, 100000000.00, 'Bao Viet', 'Bao Viet Insurance', 1, 'admin', 'admin', 'Nguyen Thi Test One', '0912345678'),
('OBJ-TEST-MTO-004', 'USER-002', 'CTR-TEST-002', 'Moto Protect', 'PG-MTO', 'PR-MTO', '2-Wheel Safe', 'PK-MTO-1', 'Mandatory Plan', 66000.00, 'T-MTO', 'Moto', 'MJ-MTO', 'PD-MTO', 66000.00, 100000000.00, 'PVI', 'PVI Insurance', 1, 'admin', 'admin', 'Tran Van Test Two', '0987654321'),
('OBJ-TEST-MTO-005', 'USER-005', 'CTR-TEST-005', 'Moto Protect', 'PG-MTO', 'PR-MTO', '2-Wheel Safe', 'PK-MTO-2', 'Comprehensive Plan', 150000.00, 'T-MTO', 'Moto', 'MJ-MTO', 'PD-MTO', 150000.00, 150000000.00, 'PVI', 'PVI Insurance', 2, 'admin', 'admin', 'Le Huan Test Five', '0933445566');


-- ============================================================================
-- F. INSERT 5 SOCIAL INSURANCE OBJECTS (insuranceContractObjectSocialInsurance)
-- ============================================================================
INSERT INTO "insuranceContractObjectSocialInsurance" (
  "contractObjectId", "contractId", "programTypeName", "programTypeId", "programId", "programName",
  "packageId", "packageName", "fromAge", "toAge", "feeMainBenefit", "majorName", "majorId", "productId",
  "feeInsurance", "maximumAmount", "companyProvider", "companyProviderName", "contractObjectType",
  "peopleLicenseType", "createdBy", "modifiedBy", "peopleName", "peopleDob", "peopleGender"
) VALUES 
('OBJ-TEST-SOC-001', 'CTR-TEST-005', 'Social Care', 'PG-SOC', 'PR-SOC', 'VSS Standard', 'PK-SOC-1', 'Basic Support', 18, 60, 2000000.00, 'Social Major', 'MJ-SOC', 'PD-SOC', 2000000.00, 50000000.00, 'BHXH_VN', 'Vietnam Social Security', 5, 1, 'admin', 'admin', 'Le Huan Test Five', '1988-11-25', 1),
('OBJ-TEST-SOC-002', 'CTR-TEST-005', 'Social Care', 'PG-SOC', 'PR-SOC', 'VSS Standard', 'PK-SOC-1', 'Basic Support', 18, 60, 2000000.00, 'Social Major', 'MJ-SOC', 'PD-SOC', 2000000.00, 50000000.00, 'BHXH_VN', 'Vietnam Social Security', 5, 1, 'admin', 'admin', 'Le Huan Wife', '1990-02-12', 2),
('OBJ-TEST-SOC-003', 'CTR-TEST-001', 'Social Care', 'PG-SOC', 'PR-SOC', 'VSS Standard', 'PK-SOC-1', 'Basic Support', 18, 60, 2000000.00, 'Social Major', 'MJ-SOC', 'PD-SOC', 2000000.00, 50000000.00, 'BHXH_VN', 'Vietnam Social Security', 5, 1, 'admin', 'admin', 'Nguyen Thi Test One', '1990-05-15', 2),
('OBJ-TEST-SOC-004', 'CTR-TEST-002', 'Social Care', 'PG-SOC', 'PR-SOC', 'VSS Standard', 'PK-SOC-1', 'Basic Support', 18, 60, 2000000.00, 'Social Major', 'MJ-SOC', 'PD-SOC', 2000000.00, 50000000.00, 'BHXH_VN', 'Vietnam Social Security', 5, 1, 'admin', 'admin', 'Tran Van Test Two', '1985-12-10', 1),
('OBJ-TEST-SOC-005', 'CTR-TEST-004', 'Social Care', 'PG-SOC', 'PR-SOC', 'VSS Standard', 'PK-SOC-1', 'Basic Support', 18, 60, 2000000.00, 'Social Major', 'MJ-SOC', 'PD-SOC', 2000000.00, 50000000.00, 'BHXH_VN', 'Vietnam Social Security', 5, 1, 'admin', 'admin', 'Pham Minh Test Four', '2000-01-01', 1);


-- ============================================================================
-- G. INSERT 5 MEDICAL INSURANCE OBJECTS (insuranceContractObjectMedicalInsurance)
-- ============================================================================
INSERT INTO "insuranceContractObjectMedicalInsurance" (
  "contractObjectId", "contractId", "programTypeName", "programTypeId", "programId", "programName",
  "packageId", "packageName", "feeMainBenefit", "majorName", "majorId", "productId",
  "feeInsurance", "maximumAmount", "companyProvider", "companyProviderName", "contractObjectType",
  "peopleLicenseType", "createdBy", "modifiedBy", "peopleName", "peopleDob", "peopleGender"
) VALUES 
('OBJ-TEST-MED-001', 'CTR-TEST-001', 'Medical Care', 'PG-MED', 'PR-MED', 'VSS Medical', 'PK-MED-1', 'National Health', 800000.00, 'Medical Major', 'MJ-MED', 'PD-MED', 800000.00, 200000000.00, 'BYT_VN', 'Ministry of Health VN', 4, 1, 'admin', 'admin', 'Nguyen Thi Test One', '1990-05-15', 2),
('OBJ-TEST-MED-002', 'CTR-TEST-002', 'Medical Care', 'PG-MED', 'PR-MED', 'VSS Medical', 'PK-MED-1', 'National Health', 800000.00, 'Medical Major', 'MJ-MED', 'PD-MED', 800000.00, 200000000.00, 'BYT_VN', 'Ministry of Health VN', 4, 1, 'admin', 'admin', 'Tran Van Test Two', '1985-12-10', 1),
('OBJ-TEST-MED-003', 'CTR-TEST-003', 'Medical Care', 'PG-MED', 'PR-MED', 'VSS Medical', 'PK-MED-1', 'National Health', 800000.00, 'Medical Major', 'MJ-MED', 'PD-MED', 800000.00, 200000000.00, 'BYT_VN', 'Ministry of Health VN', 4, 1, 'admin', 'admin', 'Company Director', '1975-01-01', 1),
('OBJ-TEST-MED-004', 'CTR-TEST-004', 'Medical Care', 'PG-MED', 'PR-MED', 'VSS Medical', 'PK-MED-1', 'National Health', 800000.00, 'Medical Major', 'MJ-MED', 'PD-MED', 800000.00, 200000000.00, 'BYT_VN', 'Ministry of Health VN', 4, 1, 'admin', 'admin', 'Pham Minh Test Four', '2000-01-01', 1),
('OBJ-TEST-MED-005', 'CTR-TEST-005', 'Medical Care', 'PG-MED', 'PR-MED', 'VSS Medical', 'PK-MED-1', 'National Health', 800000.00, 'Medical Major', 'MJ-MED', 'PD-MED', 800000.00, 200000000.00, 'BYT_VN', 'Ministry of Health VN', 4, 1, 'admin', 'admin', 'Le Huan Test Five', '1988-11-25', 1);


-- ============================================================================
-- H. INSERT 5 HOUSE OBJECTS (insuranceContractObjectHouse)
-- ============================================================================
INSERT INTO "insuranceContractObjectHouse" (
  "id", "contractId", "programName", "packageName", "feeMainBenefit", "feeInsurance", 
  "companyProviderName", "createdAt", "createdBy", "modifiedAt", "modifiedBy", "houseName", "houseAddress"
) VALUES 
('OBJ-TEST-HSE-001', 'CTR-TEST-003', 'House Shield', 'Gold House', 1500000.00, 1500000.00, 'Bao Viet Insurance', NOW(), 'admin', NOW(), 'admin', 'Test Villa A', '123 Villa Street, Dist 2, HCM'),
('OBJ-TEST-HSE-002', 'CTR-TEST-003', 'House Shield', 'Bronze House', 600000.00, 600000.00, 'Bao Viet Insurance', NOW(), 'admin', NOW(), 'admin', 'Test Apartment B', 'Room 501, Sunshine Block, Dist 7, HCM'),
('OBJ-TEST-HSE-003', 'CTR-TEST-002', 'House Shield', 'Gold House', 1500000.00, 1500000.00, 'PVI Insurance', NOW(), 'admin', NOW(), 'admin', 'Test House C', '456 Townhouse Lane, Hanoi'),
('OBJ-TEST-HSE-004', 'CTR-TEST-004', 'House Shield', 'Bronze House', 600000.00, 600000.00, 'Bao Viet Insurance', NOW(), 'admin', NOW(), 'admin', 'Test House D', '789 Alley Rd, Danang'),
('OBJ-TEST-HSE-005', 'CTR-TEST-005', 'House Shield', 'Gold House', 1500000.00, 1500000.00, 'PVI Insurance', NOW(), 'admin', NOW(), 'admin', 'Test House E', '999 Highrise Ave, Can Tho');


-- ============================================================================
-- I. INSERT 5 CLAIMS (insuranceClaim)
-- ============================================================================
INSERT INTO "insuranceClaim" (
  "id", "contractId", "contractObjectId", "amountClaim", "compensationAmount", "claimType", "status",
  "createdAt", "createdBy", "modifiedAt", "modifiedBy", "diagnostic", "placeOfTreatment"
) VALUES 
('CLM-TEST-001', 'CTR-TEST-001', 'OBJ-TEST-HLT-001', 5000000.00, 4500000.00, 1, 3, NOW(), 'admin', NOW(), 'admin', 'Acute appendicitis surgery', 'Bao Son General Hospital'),
('CLM-TEST-002', 'CTR-TEST-001', 'OBJ-TEST-HLT-002', 1200000.00, 1200000.00, 1, 3, NOW(), 'admin', NOW(), 'admin', 'Pediatric bronchitis consultation', 'Vinmec International Hospital'),
('CLM-TEST-003', 'CTR-TEST-002', 'OBJ-TEST-HLT-003', 2500000.00, 2000000.00, 1, 3, NOW(), 'admin', NOW(), 'admin', 'Dental root canal treatment', 'Saigon International Dental Center'),
('CLM-TEST-004', 'CTR-TEST-003', 'OBJ-TEST-HLT-004', 15000000.00, 15000000.00, 2, 3, NOW(), 'admin', NOW(), 'admin', 'Gastritis inpatient treatment (3 days)', 'Cho Ray Hospital'),
('CLM-TEST-005', 'CTR-TEST-005', 'OBJ-TEST-HLT-005', 3000000.00, 0.00, 1, 4, NOW(), 'admin', NOW(), 'admin', 'Regular health checkup (Non-claimable under terms)', 'Columbia Asia Clinic');
