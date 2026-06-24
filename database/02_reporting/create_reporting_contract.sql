-- ============================================================================
-- FILE: 01_create_reporting_contract.sql  
-- PURPOSE: Tạo schema 'reporting' và các bảng rộng ODS/Reporting trên PostgreSQL
-- DESCRIPTION:
--   - Đã chuyển đổi cú pháp MySQL sang chuẩn PostgreSQL.
--   - Thiết lập schema 'reporting' và cấu hình search_path.
--   - Tạo bảng profiling_analysis và wide table 'contract'.
--   - Thiết lập các indexes tối ưu cho PostgreSQL.
--   - Chuyển đổi Stored Procedure sp_build_profiling_analysis sang PG PL/pgSQL Function.
-- ============================================================================

-- Khởi tạo schema if not exists
CREATE SCHEMA IF NOT EXISTS "reporting";

-- Thiết lập search_path
SET search_path TO "reporting", public;

-- Khởi tạo enum cho data_source nếu chưa tồn tại
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'data_source_type') THEN
        CREATE TYPE data_source_type AS ENUM ('online', 'offline');
    END IF;
END$$;

-- ============================================================================
-- Table: profiling_analysis
-- ============================================================================
CREATE TABLE IF NOT EXISTS profiling_analysis (
    id VARCHAR(64) PRIMARY KEY,
    "contractId" VARCHAR(64),
    "contractObjectId" VARCHAR(64),
    
    -- Thông tin claim & bồi thường
    "amountClaim" DECIMAL(18,2),
    "compensationAmount" DECIMAL(18,2),
    "compensationRate" DECIMAL(10,2),
    
    -- Thời gian điều trị / claim
    "hospitalizedDate" TIMESTAMP,
    clinics VARCHAR(255),
    "contractStartDate" DATE,
    "claimStartDate" DATE,
    "claimMonth" INT,
    "claimYear" INT,
    
    -- Thông tin người được bảo hiểm
    "age_group" VARCHAR(20),
    "relationshipName" VARCHAR(100),
    age INT,
    gender INT,  -- 0 = FEMALE, 1 = MALE
    city VARCHAR(100),
    
    -- Thông tin điều trị & chẩn đoán
    "treatmentType" VARCHAR(50),
    diagnostic TEXT,
    common_diagnostic_category VARCHAR(100),
    
    -- Khoảng thời gian từ hiệu lực HĐ tới ngày claim
    days_from_contract_to_claim INT,
    
    -- Thời gian xuất viện
    "hospitalDischargeDate" TIMESTAMP,
    
    -- Loại khách hàng, sản phẩm
    "customerType" INT,
    "tpaId" VARCHAR(64),
    
    -- Thông tin liên hệ
    name VARCHAR(255),
    phone VARCHAR(50),
    email VARCHAR(255),
    address TEXT,
    
    -- Company/Program
    comp_prog_id VARCHAR(64),
    comp_prog_name VARCHAR(256),
    
    -- ETL metadata
    etl_loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for profiling_analysis
CREATE INDEX IF NOT EXISTS idx_pa_contract_id ON profiling_analysis ("contractId");
CREATE INDEX IF NOT EXISTS idx_pa_contract_object_id ON profiling_analysis ("contractObjectId");
CREATE INDEX IF NOT EXISTS idx_pa_customer_type ON profiling_analysis ("customerType");
CREATE INDEX IF NOT EXISTS idx_pa_city ON profiling_analysis (city);
CREATE INDEX IF NOT EXISTS idx_pa_claim_year ON profiling_analysis ("claimYear");
CREATE INDEX IF NOT EXISTS idx_pa_claim_month ON profiling_analysis ("claimMonth");
CREATE INDEX IF NOT EXISTS idx_pa_age_group ON profiling_analysis ("age_group");
CREATE INDEX IF NOT EXISTS idx_pa_treatment_type ON profiling_analysis ("treatmentType");
CREATE INDEX IF NOT EXISTS idx_pa_diagnostic_category ON profiling_analysis (common_diagnostic_category);
CREATE INDEX IF NOT EXISTS idx_pa_etl_loaded_at ON profiling_analysis (etl_loaded_at);


-- ============================================================================
-- Table: contract (ODS Wide Table)
-- ============================================================================
CREATE TABLE IF NOT EXISTS contract (
  id BIGSERIAL PRIMARY KEY,
  data_source data_source_type NOT NULL,
  "source_table" VARCHAR(100) DEFAULT NULL,
  
  -- PRIMARY KEY & COMMON IDENTIFIERS
  "contractObjectId" VARCHAR(255) DEFAULT NULL,
  "contractObjectIdDisplay" VARCHAR(255) DEFAULT NULL,
  "insuranceType" VARCHAR(50) NOT NULL,
  
  -- CARD & CERTIFICATE INFORMATION
  "cardNumber" VARCHAR(255) DEFAULT NULL,
  "certificateNumberProvider" VARCHAR(255) DEFAULT NULL,
  "accountTPA" VARCHAR(255) DEFAULT NULL,
  
  -- USER & CONTRACT RELATIONSHIP
  "userId" VARCHAR(255) DEFAULT NULL,
  "contractId" VARCHAR(255) DEFAULT NULL,
  "contractIdDisplay" VARCHAR(255) DEFAULT NULL,
  
  -- STATUS & DATES
  "contractStatus" INT DEFAULT NULL,
  "contractObjectSmeStatus" INT DEFAULT NULL,
  "contractIndividualStatus" INT DEFAULT NULL,
  "contractObjectStartDate" TIMESTAMP DEFAULT NULL,
  "contractObjectEndDate" TIMESTAMP DEFAULT NULL,
  "contractObjectIdProvider" VARCHAR(255) DEFAULT NULL,
  "contractObjectUrl" TEXT DEFAULT NULL,
  
  -- PROGRAM & PACKAGE INFORMATION
  "programTypeName" VARCHAR(255) DEFAULT NULL,
  "programTypeId" VARCHAR(255) DEFAULT NULL,
  "programId" VARCHAR(255) DEFAULT NULL,
  "programName" VARCHAR(255) DEFAULT NULL,
  "packageId" VARCHAR(255) DEFAULT NULL,
  "packageName" VARCHAR(255) DEFAULT NULL,
  "packageCodeFromProvider" VARCHAR(255) DEFAULT NULL,
  "programCodeMiningChannel" VARCHAR(255) DEFAULT NULL,
  "programDocument" TEXT DEFAULT '[]',
  
  -- AGE RANGE
  "fromAge" INT DEFAULT NULL,
  "toAge" INT DEFAULT NULL,
  
  -- FEE & AMOUNT INFORMATION
  amount DECIMAL(20,2) DEFAULT NULL,
  "amountPay" DECIMAL(20,2) DEFAULT NULL,
  "feeMainBenefit" DECIMAL(20,2) DEFAULT NULL,
  "feeSideBenefit" DECIMAL(20,2) DEFAULT 0,
  "feeInsurance" DECIMAL(20,2) DEFAULT NULL,
  "maximumAmount" DECIMAL(20,2) DEFAULT NULL,
  
  -- VAT & Pre-VAT Fee breakdown
  "preVatFeeMainBenefit" DECIMAL(20,2) DEFAULT 0,
  "vatFeeMainBenefit" DECIMAL(20,2) DEFAULT 0,
  "preVatFeeSideBenefit" DECIMAL(20,2) DEFAULT 0,
  "vatFeeSideBenefit" DECIMAL(20,2) DEFAULT 0,
  "preVatFeeInsurance" DECIMAL(20,2) DEFAULT 0,
  "vatFeeInsurance" DECIMAL(20,2) DEFAULT 0,
  
  -- TERMS & CONDITIONS
  "termsId" VARCHAR(255) DEFAULT NULL,
  "termsName" VARCHAR(255) DEFAULT NULL,
  "termsUrl" TEXT DEFAULT NULL,
  "termsFeePaymentMethod" VARCHAR(255) DEFAULT NULL,
  
  -- PROVIDER INFORMATION
  "providerId" VARCHAR(255) DEFAULT NULL,
  "providerName" VARCHAR(255) DEFAULT NULL,
  "companyProviderName" VARCHAR(255) DEFAULT NULL,
  "companyProviderId" VARCHAR(255) DEFAULT NULL,
  "companyProviderUrl" TEXT DEFAULT NULL,
  "majorName" VARCHAR(255) DEFAULT NULL,
  "majorId" VARCHAR(255) DEFAULT NULL,
  
  -- PEOPLE INFORMATION
  "peopleName" VARCHAR(255) DEFAULT NULL,
  "peopleDob" DATE DEFAULT NULL,
  "peopleGender" INT DEFAULT NULL,
  "peoplePhone" VARCHAR(255) DEFAULT NULL,
  "peopleEmail" VARCHAR(255) DEFAULT NULL,
  "peopleLicense" VARCHAR(255) DEFAULT NULL,
  "peopleLicenseType" VARCHAR(255) DEFAULT NULL,
  "peopleLicenseFront" TEXT DEFAULT NULL,
  "peopleLicenseBack" TEXT DEFAULT NULL,
  "peopleRelationship" INT DEFAULT NULL,
  
  -- ADDRESS INFORMATION
  "peopleAddress" TEXT DEFAULT NULL,
  "peopleDistrictsCode" VARCHAR(255) DEFAULT NULL,
  "peopleWardsCode" VARCHAR(255) DEFAULT NULL,
  "peopleStreet" TEXT DEFAULT NULL,
  "houseNumber" VARCHAR(255) DEFAULT NULL,
  "cityCode" VARCHAR(255) DEFAULT NULL,
  "customerType" INT DEFAULT NULL,
  upload TEXT DEFAULT NULL,
  note TEXT DEFAULT NULL,
  
  -- AUDIT FIELDS
  "createdAt" TIMESTAMP DEFAULT NULL,
  "createdBy" VARCHAR(255) DEFAULT NULL,
  "modifiedAt" TIMESTAMP DEFAULT NULL,
  "modifiedBy" VARCHAR(255) DEFAULT NULL,
  "modifiedDate" TIMESTAMP DEFAULT NULL,
  
  -- CONTRACT OBJECT METADATA
  "minDate" INT DEFAULT NULL,
  "contractObjectIdPrev" VARCHAR(255) DEFAULT NULL,
  "memberId" VARCHAR(255) DEFAULT NULL,
  "contractObjectCardDocument" TEXT DEFAULT NULL,
  "contractObjectCardImage" TEXT DEFAULT NULL,
  "paymentType" INT DEFAULT NULL,
  document TEXT DEFAULT NULL,
  
  -- VEHICLE SPECIFIC FIELDS
  "vehicleId" VARCHAR(255) DEFAULT NULL,
  "licensePlates" VARCHAR(255) DEFAULT NULL,
  "chassisNumber" VARCHAR(255) DEFAULT NULL,
  "engineNumber" VARCHAR(255) DEFAULT NULL,
  maker VARCHAR(255) DEFAULT NULL,
  type VARCHAR(255) DEFAULT NULL,
  line VARCHAR(255) DEFAULT NULL,
  "seatNumber" INT DEFAULT NULL,
  "programObject" TEXT DEFAULT NULL,
  
  -- HOUSE INSURANCE SPECIFIC FIELDS
  ownership VARCHAR(256) DEFAULT NULL,
  "houseLevelId" VARCHAR(256) DEFAULT NULL,
  "houseProgramObject" INT DEFAULT NULL,
  "houseName" VARCHAR(256) DEFAULT NULL,
  "numberFloors" INT DEFAULT NULL,
  "houseAddress" VARCHAR(256) DEFAULT NULL,
  "houseDistrictsCode" INT DEFAULT NULL,
  "houseWardsCode" INT DEFAULT NULL,
  "houseStreet" VARCHAR(256) DEFAULT NULL,
  "houseHouseNumber" VARCHAR(256) DEFAULT NULL,
  "houseCityCode" INT DEFAULT NULL,
  latitude VARCHAR(256) DEFAULT NULL,
  longitude VARCHAR(256) DEFAULT NULL,
  acreage DOUBLE PRECISION DEFAULT NULL,
  "completionYear" INT DEFAULT NULL,
  "houseValue" DECIMAL(20,2) DEFAULT NULL,
  "houseValueInsured" DECIMAL(20,2) DEFAULT NULL,
  "propertyValue" DECIMAL(20,2) DEFAULT NULL,
  "propertyValueInsured" DECIMAL(20,2) DEFAULT NULL,
  "houseUses" INT DEFAULT NULL,
  business VARCHAR(256) DEFAULT NULL,
  "companyType" VARCHAR(256) DEFAULT NULL,
  "foundingYear" INT DEFAULT NULL,
  "isStone" INT DEFAULT NULL,
  "widthAlley" DOUBLE PRECISION DEFAULT NULL,
  "insuranceDeductible" DECIMAL(20,2) DEFAULT NULL,
  "houseCertificateNumber" VARCHAR(256) DEFAULT NULL,
  "numberInApartment" VARCHAR(256) DEFAULT NULL,
  "apartmentNameOrNumber" VARCHAR(256) DEFAULT NULL,
  "numberUseHouse" DOUBLE PRECISION DEFAULT NULL,
  "rentAmount" DECIMAL(20,2) DEFAULT NULL,
  "housePaymentPeriod" INT DEFAULT NULL,
  "housePaymentPeriodValue" INT DEFAULT NULL,
  "housePaymentNumber" INT DEFAULT NULL,
  "housePaymentRatio" DOUBLE PRECISION DEFAULT NULL,
  "housePaymentType" INT DEFAULT NULL,
  "houseBankName" VARCHAR(256) DEFAULT NULL,
  "houseBankAddress" VARCHAR(256) DEFAULT NULL,
  "houseBankEmail" VARCHAR(256) DEFAULT NULL,
  "houseBankCode" VARCHAR(256) DEFAULT NULL,
  "houseScope" VARCHAR(256) DEFAULT NULL,
  "houseClassificationCode" VARCHAR(256) DEFAULT NULL,
  "partnerHouseId" VARCHAR(256) DEFAULT NULL,
  "partnerAccountId" VARCHAR(256) DEFAULT NULL,
  
  -- TRAVEL SPECIFIC FIELDS
  nationality TEXT DEFAULT NULL,
  "nationalityId" VARCHAR(255) DEFAULT NULL,
  "domesticOrInternational" VARCHAR(255) DEFAULT NULL,
  departure TEXT DEFAULT NULL,
  destination TEXT DEFAULT NULL,
  "destinationDomestic" TEXT DEFAULT NULL,
  journey TEXT DEFAULT NULL,
  "programObjectFromProvider" TEXT DEFAULT NULL,
  "destinationFromProvider" TEXT DEFAULT NULL,
  "codePackageFromProvider" VARCHAR(255) DEFAULT NULL,
  adults INT DEFAULT NULL,
  children INT DEFAULT NULL,
  
  -- PAYER INFORMATION (for TRAVEL)
  "payerUserId" VARCHAR(255) DEFAULT NULL,
  "payerName" VARCHAR(255) DEFAULT NULL,
  "payerDob" DATE DEFAULT NULL,
  "payerGender" INT DEFAULT NULL,
  "payerLicense" VARCHAR(255) DEFAULT NULL,
  "payerLicenseType" VARCHAR(255) DEFAULT NULL,
  "payerLicenseFront" TEXT DEFAULT NULL,
  "payerLicenseBack" TEXT DEFAULT NULL,
  "payerPhone" VARCHAR(255) DEFAULT NULL,
  "payerEmail" VARCHAR(255) DEFAULT NULL,
  "payerAddress" TEXT DEFAULT NULL,
  "payerDistrictsCode" VARCHAR(255) DEFAULT NULL,
  "payerWardsCode" VARCHAR(255) DEFAULT NULL,
  "payerStreet" TEXT DEFAULT NULL,
  "payerHouseNumber" VARCHAR(255) DEFAULT NULL,
  "payerCityCode" VARCHAR(255) DEFAULT NULL,
  "payerNote" TEXT DEFAULT NULL,
  "payerUpload" TEXT DEFAULT NULL,
  "payerCustomerType" INT DEFAULT NULL,
  
  -- SOCIAL INSURANCE SPECIFIC FIELDS
  "declarationType" INT DEFAULT NULL,
  "remunerationType" INT DEFAULT NULL,
  "oldCardStartDate" DATE DEFAULT NULL,
  "oldCardEndDate" DATE DEFAULT NULL,
  renewal BOOLEAN DEFAULT NULL,
  "socialFamilyId" VARCHAR(255) DEFAULT NULL,
  "socialId" VARCHAR(255) DEFAULT NULL,
  "monthlyIncome" DECIMAL(20,2) DEFAULT NULL,
  "paymentPeriod" INT DEFAULT NULL,
  "supportBudget" DECIMAL(20,2) DEFAULT NULL,
  "oldBhxhCodeUnit" VARCHAR(255) DEFAULT NULL,
  "oldRegisterDate" DATE DEFAULT NULL,
  percent DECIMAL(5,2) DEFAULT NULL,
  "discountAmount" DECIMAL(20,2) DEFAULT NULL,
  "fiveYearDate" DATE DEFAULT NULL,
  
  -- MEDICAL INSURANCE SPECIFIC FIELDS
  "medicalId" VARCHAR(255) DEFAULT NULL,
  "hospitalCode" VARCHAR(255) DEFAULT NULL,
  "hospitalName" VARCHAR(255) DEFAULT NULL,
  "hospitalCityRegisteredCode" VARCHAR(255) DEFAULT NULL,
  "hospitalCityRegisteredName" VARCHAR(255) DEFAULT NULL,
  nation VARCHAR(255) DEFAULT NULL,
  ethnicity VARCHAR(255) DEFAULT NULL,
  
  -- THIRD PARTY & PROVIDER INTEGRATION
  "thirdPartyRequestId" VARCHAR(255) DEFAULT NULL,
  "reqCode" VARCHAR(255) DEFAULT NULL,
  "contractIdProvider" VARCHAR(255) DEFAULT NULL,
  
  -- CONTRACT STATUS & TYPE
  "buyHelp" BOOLEAN DEFAULT NULL,
  "buyerId" VARCHAR(255) DEFAULT NULL,
  "contractType" INT DEFAULT NULL,
  "contractIdRoot" VARCHAR(255) DEFAULT NULL,
  
  -- SALES & BRANCH INFORMATION
  "companySale" VARCHAR(255) DEFAULT NULL,
  "branchSale" VARCHAR(255) DEFAULT NULL,
  "branchSaleName" VARCHAR(255) DEFAULT NULL,
  "companySaleName" VARCHAR(255) DEFAULT NULL,
  
  -- CONTRACT PERIOD & DATES
  "contractPeriod" INT DEFAULT NULL,
  "contractPeriodValue" VARCHAR(255) DEFAULT NULL,
  
  -- VOUCHER & DISCOUNT
  "voucherId" VARCHAR(255) DEFAULT NULL,
  "voucherCode" VARCHAR(255) DEFAULT NULL,
  "amountDiscount" DECIMAL(20,2) DEFAULT NULL,
  
  -- PAYMENT INFORMATION
  commission DECIMAL(20,2) DEFAULT NULL,
  "redBill" BOOLEAN DEFAULT NULL,
  "paymentMethod" INT DEFAULT NULL,
  
  -- CANCELLATION & ERROR INFORMATION
  "reasonCancel" TEXT DEFAULT NULL,
  "codeErrorCancel" VARCHAR(255) DEFAULT NULL,
  "messageError" TEXT DEFAULT NULL,
  
  -- REFERRAL & BONUS
  "referralCode" VARCHAR(255) DEFAULT NULL,
  "saleId" VARCHAR(255) DEFAULT NULL,
  "bonusAmount" DECIMAL(20,2) DEFAULT NULL,
  
  -- SOURCE TRACKING
  "fromLead" VARCHAR(50) DEFAULT NULL,
  source VARCHAR(255) DEFAULT NULL,
  "outsideCreatedAt" TIMESTAMP DEFAULT NULL,
  "outsidePaymentAt" TIMESTAMP DEFAULT NULL,
  "outsidePaymentId" VARCHAR(255) DEFAULT NULL,
  "channelId" VARCHAR(255) DEFAULT NULL,
  "levelId" VARCHAR(255) DEFAULT NULL,
  
  -- ADDITIONAL FIELDS
  "certFile" TEXT DEFAULT NULL,
  "orderNumber" VARCHAR(255) DEFAULT NULL,
  
  -- ETL METADATA
  "etl_loaded_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  "etl_batch_id" VARCHAR(50) DEFAULT NULL,
  
  -- UNIQUE CONSTRAINT
  CONSTRAINT uk_contract_object UNIQUE ("contractId", "contractObjectId")
);

-- Indexes for contract table
CREATE INDEX IF NOT EXISTS idx_c_data_source ON contract (data_source);
CREATE INDEX IF NOT EXISTS idx_c_insuranceType ON contract ("insuranceType");
CREATE INDEX IF NOT EXISTS idx_c_contractId ON contract ("contractId");
CREATE INDEX IF NOT EXISTS idx_c_userId ON contract ("userId");
CREATE INDEX IF NOT EXISTS idx_c_modifiedDate ON contract ("modifiedDate");
CREATE INDEX IF NOT EXISTS idx_c_packageName ON contract ("packageName");
CREATE INDEX IF NOT EXISTS idx_c_contractStatus ON contract ("contractStatus");
CREATE INDEX IF NOT EXISTS idx_c_createdAt ON contract ("createdAt");
CREATE INDEX IF NOT EXISTS idx_c_etl_loaded_at ON contract ("etl_loaded_at");
CREATE INDEX IF NOT EXISTS idx_c_business_key ON contract ("contractId", "insuranceType", data_source);
CREATE INDEX IF NOT EXISTS idx_c_houseCityCode ON contract ("houseCityCode");
CREATE INDEX IF NOT EXISTS idx_c_partnerHouseId ON contract ("partnerHouseId");


-- ============================================================================
-- FUNCTION: sp_build_profiling_analysis
-- ============================================================================
CREATE OR REPLACE FUNCTION sp_build_profiling_analysis()
RETURNS void AS $$
BEGIN
    INSERT INTO reporting.profiling_analysis (
        id,
        "contractId",
        "contractObjectId",
        "amountClaim",
        "compensationAmount",
        "compensationRate",
        "hospitalizedDate",
        clinics,
        "contractStartDate",
        "claimStartDate",
        "claimMonth",
        "claimYear",
        "age_group",
        "relationshipName",
        age,
        gender,
        city,
        "treatmentType",
        diagnostic,
        common_diagnostic_category,
        days_from_contract_to_claim,
        "hospitalDischargeDate",
        "customerType",
        "tpaId",
        name,
        phone,
        email,
        address,
        comp_prog_id,
        comp_prog_name,
        etl_loaded_at
    )
    SELECT
        cl.id AS id,
        ct."contractId" AS "contractId",
        co."contractObjectId" AS "contractObjectId",
        cl."amountClaim" AS "amountClaim",
        cl."compensationAmount" AS "compensationAmount",
        (cl."compensationAmount" / NULLIF(cl."amountClaim", 0.0)) * 100.0 AS "compensationRate",
        cl."hospitalizedDate" AS "hospitalizedDate",
        cl."placeOfTreatment" AS clinics,
        DATE(ct."contractStartDate") AS "contractStartDate",
        DATE(cl."createdAt") AS "claimStartDate",
        EXTRACT(MONTH FROM cl."createdAt")::INT AS "claimMonth",
        EXTRACT(YEAR FROM cl."createdAt")::INT AS "claimYear",
        CASE
            WHEN co."peopleDob" IS NOT NULL THEN
                CASE
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, co."peopleDob")) BETWEEN 0 AND 6 THEN '0-6'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, co."peopleDob")) BETWEEN 7 AND 17 THEN '7-17'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, co."peopleDob")) BETWEEN 18 AND 35 THEN '18-35'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, co."peopleDob")) BETWEEN 36 AND 55 THEN '36-55'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, co."peopleDob")) >= 56 THEN '56+'
                    ELSE 'Unknown'
                END
            ELSE 'Unknown'
        END AS "age_group",
        CASE co."peopleRelationship"
            WHEN 0 THEN 'Bản thân'
            WHEN 1 THEN 'Bố/Mẹ đẻ'
            WHEN 2 THEN 'Vợ/Chồng'
            WHEN 3 THEN 'Anh/Chị/Em ruột'
            WHEN 4 THEN 'Con đẻ/nuôi hợp pháp'
            WHEN 5 THEN 'Khác'
            WHEN 6 THEN 'Bố/Mẹ của vợ/chồng'
            ELSE 'Khác'
        END AS "relationshipName",
        CASE
            WHEN co."peopleDob" IS NOT NULL THEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, co."peopleDob"))::INT
            ELSE NULL
        END AS age,
        co."peopleGender" AS gender,
        CASE co."peopleCityCode"
            WHEN '1'  THEN 'Thành phố Hà Nội'
            WHEN '2'  THEN 'Tỉnh Hà Giang'
            WHEN '4'  THEN 'Tỉnh Cao Bằng'
            WHEN '6'  THEN 'Tỉnh Bắc Kạn'
            WHEN '8'  THEN 'Tỉnh Tuyên Quang'
            WHEN '10' THEN 'Tỉnh Lào Cai'
            WHEN '11' THEN 'Tỉnh Điện Biên'
            WHEN '12' THEN 'Tỉnh Lai Châu'
            WHEN '14' THEN 'Tỉnh Sơn La'
            WHEN '15' THEN 'Tỉnh Yên Bái'
            WHEN '17' THEN 'Tỉnh Hoà Bình'
            WHEN '19' THEN 'Tỉnh Thái Nguyên'
            WHEN '20' THEN 'Tỉnh Lạng Sơn'
            WHEN '22' THEN 'Tỉnh Quảng Ninh'
            WHEN '24' THEN 'Tỉnh Bắc Giang'
            WHEN '25' THEN 'Tỉnh Phú Thọ'
            WHEN '26' THEN 'Tỉnh Vĩnh Phúc'
            WHEN '27' THEN 'Tỉnh Bắc Ninh'
            WHEN '30' THEN 'Tỉnh Hải Dương'
            WHEN '31' THEN 'Thành phố Hải Phòng'
            WHEN '33' THEN 'Tỉnh Hưng Yên'
            WHEN '34' THEN 'Tỉnh Thái Bình'
            WHEN '35' THEN 'Tỉnh Hà Nam'
            WHEN '36' THEN 'Tỉnh Nam Định'
            WHEN '37' THEN 'Tỉnh Ninh Bình'
            WHEN '38' THEN 'Tỉnh Thanh Hoá'
            WHEN '40' THEN 'Tỉnh Nghệ An'
            WHEN '42' THEN 'Tỉnh Hà Tĩnh'
            WHEN '44' THEN 'Tỉnh Quảng Bình'
            WHEN '45' THEN 'Tỉnh Quảng Trị'
            WHEN '46' THEN 'Tỉnh Thừa Thiên Huế'
            WHEN '48' THEN 'Thành phố Đà Nẵng'
            WHEN '49' THEN 'Tỉnh Quảng Nam'
            WHEN '51' THEN 'Tỉnh Quảng Ngãi'
            WHEN '52' THEN 'Tỉnh Bình Định'
            WHEN '54' THEN 'Tỉnh Phú Yên'
            WHEN '56' THEN 'Tỉnh Khánh Hoà'
            WHEN '58' THEN 'Tỉnh Ninh Thuận'
            WHEN '60' THEN 'Tỉnh Bình Thuận'
            WHEN '62' THEN 'Tỉnh Kon Tum'
            WHEN '64' THEN 'Tỉnh Gia Lai'
            WHEN '66' THEN 'Tỉnh Đắk Lắk'
            WHEN '67' THEN 'Tỉnh Đắk Nông'
            WHEN '68' THEN 'Tỉnh Lâm Đồng'
            WHEN '70' THEN 'Tỉnh Bình Phước'
            WHEN '72' THEN 'Tỉnh Tây Ninh'
            WHEN '74' THEN 'Tỉnh Bình Dương'
            WHEN '75' THEN 'Tỉnh Đồng Nai'
            WHEN '77' THEN 'Tỉnh Bà Rịa - Vũng Tàu'
            WHEN '79' THEN 'Thành phố Hồ Chí Minh'
            WHEN '80' THEN 'Tỉnh Long An'
            WHEN '82' THEN 'Tỉnh Tiền Giang'
            WHEN '83' THEN 'Tỉnh Bến Tre'
            WHEN '84' THEN 'Tỉnh Trà Vinh'
            WHEN '86' THEN 'Tỉnh Vĩnh Long'
            WHEN '87' THEN 'Tỉnh Đồng Tháp'
            WHEN '89' THEN 'Tỉnh An Giang'
            WHEN '91' THEN 'Tỉnh Kiên Giang'
            WHEN '92' THEN 'Thành phố Cần Thơ'
            WHEN '93' THEN 'Tỉnh Hậu Giang'
            WHEN '94' THEN 'Tỉnh Sóc Trăng'
            WHEN '95' THEN 'Tỉnh Bạc Liêu'
            WHEN '96' THEN 'Tỉnh Cà Mau'
            ELSE 'Không xác định'
        END AS city,
        cl."treatmentType" AS "treatmentType",
        cl.diagnostic AS diagnostic,
        CASE 
            WHEN LOWER(cl.diagnostic) LIKE '%thai%' OR LOWER(cl.diagnostic) LIKE '%sản khoa%' OR LOWER(cl.diagnostic) LIKE '%chửa ngoài tử cung%' THEN 'Thai sản'
            WHEN LOWER(cl.diagnostic) LIKE '%ung thư%' OR LOWER(cl.diagnostic) LIKE '%u ác%' OR LOWER(cl.diagnostic) LIKE '%carcinoma%' THEN 'Ung thư'
            WHEN LOWER(cl.diagnostic) LIKE '%tim%' OR LOWER(cl.diagnostic) LIKE '%mạch%' OR LOWER(cl.diagnostic) LIKE '%huyết áp%' OR LOWER(cl.diagnostic) LIKE '%nhồi máu%' THEN 'Tim mạch & Huyết áp'
            WHEN LOWER(cl.diagnostic) LIKE '%đường%' OR LOWER(cl.diagnostic) LIKE '%đái tháo%' OR LOWER(cl.diagnostic) LIKE '%tiểu đường%' THEN 'Tiểu đường'
            WHEN LOWER(cl.diagnostic) LIKE '%dạ dày%' OR LOWER(cl.diagnostic) LIKE '%tá tràng%' OR LOWER(cl.diagnostic) LIKE '%tiêu hoá%' OR LOWER(cl.diagnostic) LIKE '%ruột%' OR LOWER(cl.diagnostic) LIKE '%trĩ%' THEN 'Tiêu hoá & Dạ dày'
            WHEN LOWER(cl.diagnostic) LIKE '%hô hấp%' OR LOWER(cl.diagnostic) LIKE '%phổi%' OR LOWER(cl.diagnostic) LIKE '%phế quản%' OR LOWER(cl.diagnostic) LIKE '%xoang%' OR LOWER(cl.diagnostic) LIKE '%họng%' OR LOWER(cl.diagnostic) LIKE '%amidan%' THEN 'Hô hấp & Xoang'
            WHEN LOWER(cl.diagnostic) LIKE '%thận%' OR LOWER(cl.diagnostic) LIKE '%tiết niệu%' OR LOWER(cl.diagnostic) LIKE '%bàng quang%' OR LOWER(cl.diagnostic) LIKE '%sỏi%' THEN 'Thận & Tiết niệu'
            WHEN LOWER(cl.diagnostic) LIKE '%xương%' OR LOWER(cl.diagnostic) LIKE '%khớp%' OR LOWER(cl.diagnostic) LIKE '%cột sống%' OR LOWER(cl.diagnostic) LIKE '%thoát vị%' OR LOWER(cl.diagnostic) LIKE '%gút%' THEN 'Cơ xương khớp'
            WHEN LOWER(cl.diagnostic) LIKE '%thần kinh%' OR LOWER(cl.diagnostic) LIKE '%não%' OR LOWER(cl.diagnostic) LIKE '%tiền đình%' OR LOWER(cl.diagnostic) LIKE '%đau đầu%' THEN 'Thần kinh & Tiền đình'
            WHEN LOWER(cl.diagnostic) LIKE '%răng%' OR LOWER(cl.diagnostic) LIKE '%nướu%' OR LOWER(cl.diagnostic) LIKE '%sâu răng%' OR LOWER(cl.diagnostic) LIKE '%khôn%' THEN 'Nha khoa'
            WHEN LOWER(cl.diagnostic) LIKE '%mắt%' OR LOWER(cl.diagnostic) LIKE '%cận thị%' OR LOWER(cl.diagnostic) LIKE '%đục thuỷ tinh%' OR LOWER(cl.diagnostic) LIKE '%giác mạc%' THEN 'Mắt'
            WHEN LOWER(cl.diagnostic) LIKE '%tai%' OR LOWER(cl.diagnostic) LIKE '%viêm tai%' THEN 'Tai'
            WHEN LOWER(cl.diagnostic) LIKE '%da%' OR LOWER(cl.diagnostic) LIKE '%dị ứng%' OR LOWER(cl.diagnostic) LIKE '%chàm%' OR LOWER(cl.diagnostic) LIKE '%mề đay%' THEN 'Da liễu & Dị ứng'
            WHEN LOWER(cl.diagnostic) LIKE '%tai nạn%' OR LOWER(cl.diagnostic) LIKE '%chấn thương%' OR LOWER(cl.diagnostic) LIKE '%gãy%' OR LOWER(cl.diagnostic) LIKE '%vết thương%' OR LOWER(cl.diagnostic) LIKE '%bỏng%' THEN 'Tai nạn & Chấn thương'
            WHEN LOWER(cl.diagnostic) LIKE '%tổng quát%' OR LOWER(cl.diagnostic) LIKE '%kiểm tra%' OR LOWER(cl.diagnostic) LIKE '%tầm soát%' THEN 'Khám tổng quát'
            ELSE 'Khác'
        END AS common_diagnostic_category,
        (cl."createdAt"::date - ct."contractStartDate"::date)::INT AS days_from_contract_to_claim,
        cl."hospitalDischargeDate" AS "hospitalDischargeDate",
        ct."customerType" AS "customerType",
        cl."tpaId" AS "tpaId",
        co."peopleName" AS name,
        co."peoplePhone" AS phone,
        co."peopleEmail" AS email,
        co."peopleAddress" AS address,
        co."programId" AS comp_prog_id,
        co."programName" AS comp_prog_name,
        CURRENT_TIMESTAMP AS etl_loaded_at
    FROM staging."stgInsuranceClaim" cl
    INNER JOIN staging."stgInsuranceContract" ct ON cl."contractId" = ct."contractId"
    INNER JOIN staging."stgInsuranceContractObject" co ON cl."contractObjectId" = co."contractObjectId"
    ON CONFLICT (id) DO UPDATE SET
        "contractId" = EXCLUDED."contractId",
        "contractObjectId" = EXCLUDED."contractObjectId",
        "amountClaim" = EXCLUDED."amountClaim",
        "compensationAmount" = EXCLUDED."compensationAmount",
        "compensationRate" = EXCLUDED."compensationRate",
        "hospitalizedDate" = EXCLUDED."hospitalizedDate",
        clinics = EXCLUDED.clinics,
        "contractStartDate" = EXCLUDED."contractStartDate",
        "claimStartDate" = EXCLUDED."claimStartDate",
        "claimMonth" = EXCLUDED."claimMonth",
        "claimYear" = EXCLUDED."claimYear",
        "age_group" = EXCLUDED."age_group",
        "relationshipName" = EXCLUDED."relationshipName",
        age = EXCLUDED.age,
        gender = EXCLUDED.gender,
        city = EXCLUDED.city,
        "treatmentType" = EXCLUDED."treatmentType",
        diagnostic = EXCLUDED.diagnostic,
        common_diagnostic_category = EXCLUDED.common_diagnostic_category,
        days_from_contract_to_claim = EXCLUDED.days_from_contract_to_claim,
        "hospitalDischargeDate" = EXCLUDED."hospitalDischargeDate",
        "customerType" = EXCLUDED."customerType",
        "tpaId" = EXCLUDED."tpaId",
        name = EXCLUDED.name,
        phone = EXCLUDED.phone,
        email = EXCLUDED.email,
        address = EXCLUDED.address,
        comp_prog_id = EXCLUDED.comp_prog_id,
        comp_prog_name = EXCLUDED.comp_prog_name,
        etl_loaded_at = EXCLUDED.etl_loaded_at;
END;
$$ LANGUAGE plpgsql;
