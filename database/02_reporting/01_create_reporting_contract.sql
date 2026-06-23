-- ============================================================================
-- FILE: create_profiling_analysis.sql  
-- PURPOSE: Tạo database insuranceReporting với table profiling_analysis
--          và stored procedure (KHÔNG CÒN TRIGGERS - ĐÃ CHUYỂN SANG STREAMING)
-- USAGE: mysql -h <host> -u <user> -p < create_profiling_analysis.sql
-- NOTE: Trigger logic đã được thay thế bởi Profiling Streaming Consumer
--       File này chỉ giữ lại table schema và stored procedure
-- ============================================================================

-- Tạo database insuranceReporting
CREATE DATABASE IF NOT EXISTS `insuranceReporting`
    DEFAULT CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE `insuranceReporting`;

-- Create profiling_analysis table
CREATE TABLE IF NOT EXISTS profiling_analysis (
    -- Khóa & thông tin hợp đồng / đối tượng
    id VARCHAR(64) PRIMARY KEY,
    contractId VARCHAR(64),
    contractObjectId VARCHAR(64),
    
    -- Thông tin claim & bồi thường
    amountClaim DECIMAL(18,2),
    compensationAmount DECIMAL(18,2),
    compensationRate DECIMAL(10,2),
    
    -- Thời gian điều trị / claim
    hospitalizedDate DATETIME,
    clinics VARCHAR(255),
    contractStartDate DATE,
    claimStartDate DATE,
    claimMonth INT,
    claimYear INT,
    
    -- Thông tin người được bảo hiểm
    age_group VARCHAR(20),
    relationshipName VARCHAR(100),
    age INT,
    gender INT,  -- 0 = FEMALE, 1 = MALE
    city VARCHAR(100),
    
    -- Thông tin điều trị & chẩn đoán
    treatmentType VARCHAR(50),
    diagnostic TEXT,
    common_diagnostic_category VARCHAR(100),
    
    -- Khoảng thời gian từ hiệu lực HĐ tới ngày claim
    days_from_contract_to_claim INT,
    
    -- Thời gian xuất viện
    hospitalDischargeDate DATETIME,
    
    -- Loại khách hàng, sản phẩm
    customerType INT(5),
    tpaId VARCHAR(64),
    
    -- Thông tin liên hệ
    name VARCHAR(255),
    phone VARCHAR(50),
    email VARCHAR(255),
    address TEXT,
    
    -- Company/Program
    comp_prog_id VARCHAR(64),
    comp_prog_name VARCHAR(256),
    
    -- ETL metadata
    etl_loaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for better query performance
    INDEX idx_contract_id (contractId),
    INDEX idx_contract_object_id (contractObjectId),
    INDEX idx_customer_type (customerType),
    INDEX idx_city (city),
    INDEX idx_claim_year (claimYear),
    INDEX idx_claim_month (claimMonth),
    INDEX idx_age_group (age_group),
    INDEX idx_treatment_type (treatmentType),
    INDEX idx_diagnostic_category (common_diagnostic_category),
    INDEX idx_etl_loaded_at (etl_loaded_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- STORED PROCEDURE: sp_build_profiling_analysis
-- PURPOSE: Manual rebuild of profiling_analysis from raw data
--          (For disaster recovery or historical data backfill)
-- =====================================================
-- Drop existing procedure
DROP PROCEDURE IF EXISTS sp_build_profiling_analysis;

DELIMITER $$

CREATE PROCEDURE sp_build_profiling_analysis()
BEGIN
    INSERT INTO insuranceReporting.profiling_analysis (
        id,
        contractId,
        contractObjectId,
        amountClaim,
        compensationAmount,
        compensationRate,
        hospitalizedDate,
        clinics,
        contractStartDate,
        claimStartDate,
        claimMonth,
        claimYear,
        age_group,
        relationshipName,
        age,
        gender,
        city,
        treatmentType,
        diagnostic,
        common_diagnostic_category,
        days_from_contract_to_claim,
        hospitalDischargeDate,
        customerType,
        tpaId,
        name,
        phone,
        email,
        address,
        comp_prog_id,
        comp_prog_name,
        etl_loaded_at
    )
    SELECT
        -- Khóa & thông tin hợp đồng / đối tượng
        cl.id AS id,
        ct.contractId AS contractId,
        co.contractObjectId AS contractObjectId,

        -- Thông tin claim & bồi thường
        cl.amountClaim AS amountClaim,
        cl.compensationAmount AS compensationAmount,
        (cl.compensationAmount / NULLIF(cl.amountClaim, 0)) * 100 AS compensationRate,

        -- Thời gian điều trị / claim
        cl.hospitalizedDate AS hospitalizedDate,
        cl.placeOfTreatment AS clinics,
        DATE(ct.contractStartDate) AS contractStartDate,
        DATE(cl.createdAt) AS claimStartDate,
        MONTH(DATE(cl.createdAt)) AS claimMonth,
        YEAR(DATE(cl. createdAt)) AS claimYear,

        -- Thông tin người được bảo hiểm - age_group
        CASE
            WHEN TIMESTAMPDIFF(YEAR, co.peopleDob, CURDATE()) BETWEEN 0 AND 6 THEN '0-6'
            WHEN TIMESTAMPDIFF(YEAR, co.peopleDob, CURDATE()) BETWEEN 7 AND 17 THEN '7-17'
            WHEN TIMESTAMPDIFF(YEAR, co.peopleDob, CURDATE()) BETWEEN 18 AND 35 THEN '18-35'
            WHEN TIMESTAMPDIFF(YEAR, co.peopleDob, CURDATE()) BETWEEN 36 AND 55 THEN '36-55'
            WHEN TIMESTAMPDIFF(YEAR, co.peopleDob, CURDATE()) >= 56 THEN '56+'
            ELSE 'Unknown'
        END AS age_group,
        
        CASE co.peopleRelationship
            WHEN 0 THEN 'Bản thân'
            WHEN 1 THEN 'Bố/Mẹ đẻ'
            WHEN 2 THEN 'Vợ/Chồng'
            WHEN 3 THEN 'Anh/Chị/Em ruột'
            WHEN 4 THEN 'Con đẻ/nuôi hợp pháp'
            WHEN 5 THEN 'Khác'
            WHEN 6 THEN 'Bố/Mẹ của vợ/chồng'
            ELSE 'Khác'
        END AS relationshipName,
        TIMESTAMPDIFF(YEAR, co.peopleDob, CURDATE()) AS age,
        co.peopleGender AS gender,
        
        -- City mapping
        CASE 
            WHEN co.peopleCityCode = 1  THEN 'Thành phố Hà Nội'
            WHEN co.peopleCityCode = 2  THEN 'Tỉnh Hà Giang'
            WHEN co. peopleCityCode = 4  THEN 'Tỉnh Cao Bằng'
            WHEN co.peopleCityCode = 6  THEN 'Tỉnh Bắc Kạn'
            WHEN co.peopleCityCode = 8  THEN 'Tỉnh Tuyên Quang'
            WHEN co.peopleCityCode = 10 THEN 'Tỉnh Lào Cai'
            WHEN co.peopleCityCode = 11 THEN 'Tỉnh Điện Biên'
            WHEN co.peopleCityCode = 12 THEN 'Tỉnh Lai Châu'
            WHEN co. peopleCityCode = 14 THEN 'Tỉnh Sơn La'
            WHEN co.peopleCityCode = 15 THEN 'Tỉnh Yên Bái'
            WHEN co.peopleCityCode = 17 THEN 'Tỉnh Hoà Bình'
            WHEN co.peopleCityCode = 19 THEN 'Tỉnh Thái Nguyên'
            WHEN co.peopleCityCode = 20 THEN 'Tỉnh Lạng Sơn'
            WHEN co.peopleCityCode = 22 THEN 'Tỉnh Quảng Ninh'
            WHEN co.peopleCityCode = 24 THEN 'Tỉnh Bắc Giang'
            WHEN co.peopleCityCode = 25 THEN 'Tỉnh Phú Thọ'
            WHEN co.peopleCityCode = 26 THEN 'Tỉnh Vĩnh Phúc'
            WHEN co.peopleCityCode = 27 THEN 'Tỉnh Bắc Ninh'
            WHEN co.peopleCityCode = 30 THEN 'Tỉnh Hải Dương'
            WHEN co.peopleCityCode = 31 THEN 'Thành phố Hải Phòng'
            WHEN co.peopleCityCode = 33 THEN 'Tỉnh Hưng Yên'
            WHEN co.peopleCityCode = 34 THEN 'Tỉnh Thái Bình'
            WHEN co.peopleCityCode = 35 THEN 'Tỉnh Hà Nam'
            WHEN co.peopleCityCode = 36 THEN 'Tỉnh Nam Định'
            WHEN co.peopleCityCode = 37 THEN 'Tỉnh Ninh Bình'
            WHEN co.peopleCityCode = 38 THEN 'Tỉnh Thanh Hoá'
            WHEN co.peopleCityCode = 40 THEN 'Tỉnh Nghệ An'
            WHEN co.peopleCityCode = 42 THEN 'Tỉnh Hà Tĩnh'
            WHEN co.peopleCityCode = 44 THEN 'Tỉnh Quảng Bình'
            WHEN co. peopleCityCode = 45 THEN 'Tỉnh Quảng Trị'
            WHEN co. peopleCityCode = 46 THEN 'Tỉnh Thừa Thiên Huế'
            WHEN co.peopleCityCode = 48 THEN 'Thành phố Đà Nẵng'
            WHEN co.peopleCityCode = 49 THEN 'Tỉnh Quảng Nam'
            WHEN co.peopleCityCode = 51 THEN 'Tỉnh Quảng Ngãi'
            WHEN co.peopleCityCode = 52 THEN 'Tỉnh Bình Định'
            WHEN co.peopleCityCode = 54 THEN 'Tỉnh Phú Yên'
            WHEN co.peopleCityCode = 56 THEN 'Tỉnh Khánh Hoà'
            WHEN co.peopleCityCode = 58 THEN 'Tỉnh Ninh Thuận'
            WHEN co.peopleCityCode = 60 THEN 'Tỉnh Bình Thuận'
            WHEN co.peopleCityCode = 62 THEN 'Tỉnh Kon Tum'
            WHEN co.peopleCityCode = 64 THEN 'Tỉnh Gia Lai'
            WHEN co.peopleCityCode = 66 THEN 'Tỉnh Đắk Lắk'
            WHEN co.peopleCityCode = 67 THEN 'Tỉnh Đắk Nông'
            WHEN co.peopleCityCode = 68 THEN 'Tỉnh Lâm Đồng'
            WHEN co.peopleCityCode = 70 THEN 'Tỉnh Bình Phước'
            WHEN co.peopleCityCode = 72 THEN 'Tỉnh Tây Ninh'
            WHEN co.peopleCityCode = 74 THEN 'Tỉnh Bình Dương'
            WHEN co.peopleCityCode = 75 THEN 'Tỉnh Đồng Nai'
            WHEN co.peopleCityCode = 77 THEN 'Tỉnh Bà Rịa - Vũng Tàu'
            WHEN co.peopleCityCode = 79 THEN 'Thành phố Hồ Chí Minh'
            WHEN co.peopleCityCode = 80 THEN 'Tỉnh Long An'
            WHEN co.peopleCityCode = 82 THEN 'Tỉnh Tiền Giang'
            WHEN co.peopleCityCode = 83 THEN 'Tỉnh Bến Tre'
            WHEN co.peopleCityCode = 84 THEN 'Tỉnh Trà Vinh'
            WHEN co.peopleCityCode = 86 THEN 'Tỉnh Vĩnh Long'
            WHEN co.peopleCityCode = 87 THEN 'Tỉnh Đồng Tháp'
            WHEN co.peopleCityCode = 89 THEN 'Tỉnh An Giang'
            WHEN co.peopleCityCode = 91 THEN 'Tỉnh Kiên Giang'
            WHEN co.peopleCityCode = 92 THEN 'Thành phố Cần Thơ'
            WHEN co.peopleCityCode = 93 THEN 'Tỉnh Hậu Giang'
            WHEN co.peopleCityCode = 94 THEN 'Tỉnh Sóc Trăng'
            WHEN co.peopleCityCode = 95 THEN 'Tỉnh Bạc Liêu'
            WHEN co.peopleCityCode = 96 THEN 'Tỉnh Cà Mau'
            ELSE 'Không xác định'
        END AS city,

        -- Thông tin điều trị & chẩn đoán
        cl.treatmentType AS treatmentType,
        cl.diagnostic AS diagnostic,
        
        -- Common diagnostic category (với logic mới cập nhật)
        CASE 
            -- 1. Thai sản
            WHEN LOWER(cl.diagnostic) LIKE '%thai%' 
              OR LOWER(cl.diagnostic) LIKE '%sản khoa%' 
              OR LOWER(cl.diagnostic) LIKE '%chửa ngoài tử cung%' 
              THEN 'Thai sản'

            -- 2. Nha khoa
            WHEN LOWER(cl.diagnostic) LIKE '%răng%' 
              OR LOWER(cl.diagnostic) LIKE '%nướu%' 
              OR LOWER(cl.diagnostic) LIKE '%nha chu%' 
              OR LOWER(cl.diagnostic) LIKE '%lợi%' 
              OR LOWER(cl.diagnostic) LIKE '%chỉnh nha%' 
              THEN 'Nha khoa'

            -- 3. Mắt
            WHEN LOWER(cl.diagnostic) LIKE '%mắt%' 
              OR LOWER(cl.diagnostic) LIKE '%kết mạc%' 
              OR LOWER(cl.diagnostic) LIKE '%thủy tinh thể%' 
              OR LOWER(cl.diagnostic) LIKE '%thị lực%' 
              OR LOWER(cl.diagnostic) LIKE '%cận thị%' 
              OR LOWER(cl.diagnostic) LIKE '%loạn thị%' 
              OR LOWER(cl.diagnostic) LIKE '%viễn thị%' 
              OR LOWER(cl.diagnostic) LIKE '%quáng gà%' 
              OR LOWER(cl.diagnostic) LIKE '%lé%' 
              THEN 'Mắt'

            -- 4. Tai Mũi Họng
            WHEN LOWER(cl.diagnostic) LIKE '%tai%' 
              OR LOWER(cl.diagnostic) LIKE '%họng%' 
              OR LOWER(cl.diagnostic) LIKE '%mũi%' 
              OR LOWER(cl.diagnostic) LIKE '%xoang%' 
              OR LOWER(cl.diagnostic) LIKE '%amydan%' 
              OR LOWER(cl.diagnostic) LIKE '%thanh quản%' 
              OR LOWER(cl.diagnostic) LIKE '%lẹo%' 
              OR LOWER(cl.diagnostic) LIKE '%chắp%' 
              THEN 'Tai Mũi Họng'

            -- 5. Thận/Tiết niệu
            WHEN LOWER(cl.diagnostic) LIKE '%thận%' 
              OR LOWER(cl.diagnostic) LIKE '%tiết niệu%' 
              OR LOWER(cl.diagnostic) LIKE '%bàng quang%' 
              THEN 'Thận/Tiết niệu'

            -- 6. Chấn thương/Tai nạn
            WHEN LOWER(cl.diagnostic) LIKE '%chấn thương%' 
              OR LOWER(cl.diagnostic) LIKE '%tai nạn%' 
              OR LOWER(cl.diagnostic) LIKE '%vết thương%' 
              OR LOWER(cl.diagnostic) LIKE '%gãy%' 
              OR LOWER(cl.diagnostic) LIKE '%bong gân%' 
              OR LOWER(cl.diagnostic) LIKE '%trật khớp%' 
              OR LOWER(cl.diagnostic) LIKE '%chật khớp%'
              OR LOWER(cl.diagnostic) LIKE '%rách%' 
              OR LOWER(cl.diagnostic) LIKE '%bỏng%' 
              OR LOWER(cl.diagnostic) LIKE '%ngộ độc%' 
              OR LOWER(cl.diagnostic) LIKE '%đả thương%' 
              OR LOWER(cl.diagnostic) LIKE '%cắn%' 
              OR LOWER(cl.diagnostic) LIKE '%đốt%' 
              OR LOWER(cl.diagnostic) LIKE '%tổn thương%' 
              THEN 'Chấn thương/Tai nạn'

            -- 7. Nội tiết/Chuyển hóa
            WHEN LOWER(cl.diagnostic) LIKE '%tiểu đường%' 
              OR LOWER(cl.diagnostic) LIKE '%đái tháo đường%' 
              OR LOWER(cl.diagnostic) LIKE '%huyết áp%' 
              OR LOWER(cl.diagnostic) LIKE '%chuyển hoá%' 
              OR LOWER(cl.diagnostic) LIKE '%lipid%' 
              OR LOWER(cl.diagnostic) LIKE '%axit uric%' 
              OR LOWER(cl.diagnostic) LIKE '%gout%' 
              OR LOWER(cl.diagnostic) LIKE '%tuyến giáp%' 
              THEN 'Nội tiết/Chuyển hóa'

            -- 8. Tim mạch
            WHEN LOWER(cl.diagnostic) LIKE '%tim%' 
              OR LOWER(cl.diagnostic) LIKE '%mạch vành%' 
              OR LOWER(cl.diagnostic) LIKE '%đau thắt ngực%' 
              OR LOWER(cl.diagnostic) LIKE '%xơ vữa%' 
              OR LOWER(cl.diagnostic) LIKE '%nhồi máu não%' 
              THEN 'Tim mạch'

            -- 9. Hô hấp
            WHEN LOWER(cl.diagnostic) LIKE '%phổi%' 
              OR LOWER(cl.diagnostic) LIKE '%phế quản%' 
              OR LOWER(cl.diagnostic) LIKE '%hen%' 
              OR LOWER(cl.diagnostic) LIKE '%suyễn%' 
              OR LOWER(cl.diagnostic) LIKE '%cảm%' 
              OR LOWER(cl.diagnostic) LIKE '%ho%' 
              OR LOWER(cl.diagnostic) LIKE '%covid%' 
              THEN 'Hô hấp'

            -- 10. Tiêu hóa
            WHEN LOWER(cl.diagnostic) LIKE '%dạ dày%' 
              OR LOWER(cl.diagnostic) LIKE '%tiêu hóa%' 
              OR LOWER(cl.diagnostic) LIKE '%ruột%' 
              OR LOWER(cl.diagnostic) LIKE '%mật%' 
              OR LOWER(cl.diagnostic) LIKE '%gan%' 
              OR LOWER(cl.diagnostic) LIKE '%tụy%' 
              OR LOWER(cl.diagnostic) LIKE '%đại tràng%' 
              OR LOWER(cl.diagnostic) LIKE '%polyp%' 
              OR LOWER(cl.diagnostic) LIKE '%táo bón%' 
              OR LOWER(cl.diagnostic) LIKE '%tiêu chảy%' 
              OR LOWER(cl.diagnostic) LIKE '%trĩ%' 
              OR LOWER(cl.diagnostic) LIKE '%trào ngược%'
              THEN 'Tiêu hóa'

            -- 11. Cơ xương khớp
            WHEN LOWER(cl.diagnostic) LIKE '%xương%' 
              OR LOWER(cl.diagnostic) LIKE '%khớp%' 
              OR LOWER(cl.diagnostic) LIKE '%lưng%' 
              OR LOWER(cl.diagnostic) LIKE '%cột sống%' 
              OR LOWER(cl.diagnostic) LIKE '%gút%' 
              OR LOWER(cl.diagnostic) LIKE '%vai gáy%' 
              OR LOWER(cl.diagnostic) LIKE '%cơ%' 
              OR LOWER(cl.diagnostic) LIKE '%dây chằng%' 
              THEN 'Cơ xương khớp'

            -- 12. Da liễu
            WHEN LOWER(cl.diagnostic) LIKE '%da%' 
              OR LOWER(cl.diagnostic) LIKE '%mày đay%' 
              OR LOWER(cl.diagnostic) LIKE '%dị ứng%' 
              OR LOWER(cl.diagnostic) LIKE '%mụn%' 
              OR LOWER(cl.diagnostic) LIKE '%chàm%' 
              OR LOWER(cl.diagnostic) LIKE '%lang ben%' 
              OR LOWER(cl.diagnostic) LIKE '%nang lông%' 
              OR LOWER(cl.diagnostic) LIKE '%vảy nến%' 
              OR LOWER(cl.diagnostic) LIKE '%zona%' 
              THEN 'Da liễu'

            -- 13. Nhiễm trùng
            WHEN LOWER(cl.diagnostic) LIKE '%nhiễm%' 
              OR LOWER(cl.diagnostic) LIKE '%sốt%' 
              OR LOWER(cl.diagnostic) LIKE '%lao%' 
              OR LOWER(cl.diagnostic) LIKE '%cúm%' 
              OR LOWER(cl.diagnostic) LIKE '%sởi%' 
              OR LOWER(cl.diagnostic) LIKE '%thủy đậu%' 
              OR LOWER(cl.diagnostic) LIKE '%quai bị%' 
              OR LOWER(cl.diagnostic) LIKE '%virus%' 
              OR LOWER(cl.diagnostic) LIKE '%vi khuẩn%' 
              OR LOWER(cl.diagnostic) LIKE '%ký sinh trùng%' 
              OR LOWER(cl.diagnostic) LIKE '%nấm%' 
              THEN 'Nhiễm trùng'

            -- 14. Thần kinh
            WHEN LOWER(cl.diagnostic) LIKE '%thần kinh%' 
              OR LOWER(cl.diagnostic) LIKE '%đau đầu%' 
              OR LOWER(cl.diagnostic) LIKE '%mất ngủ%' 
              OR LOWER(cl.diagnostic) LIKE '%lo âu%' 
              OR LOWER(cl.diagnostic) LIKE '%trầm cảm%' 
              OR LOWER(cl.diagnostic) LIKE '%đột quỵ%' 
              OR LOWER(cl.diagnostic) LIKE '%tiền đình%' 
              OR LOWER(cl.diagnostic) LIKE '%nội sọ%' 
              OR LOWER(cl.diagnostic) LIKE '%động kinh%' 
              OR LOWER(cl.diagnostic) LIKE '%parkinson%' 
              OR LOWER(cl.diagnostic) LIKE '%alzheimer%' 
              THEN 'Thần kinh'

            -- 15. Khám tổng quát
            WHEN LOWER(cl.diagnostic) LIKE '%tổng quát%' 
              OR LOWER(cl.diagnostic) LIKE '%kiểm tra%' 
              OR LOWER(cl.diagnostic) LIKE '%tầm soát%' 
              THEN 'Khám tổng quát'

            ELSE 'Khác'
        END AS common_diagnostic_category,

        -- Khoảng thời gian từ hiệu lực HĐ tới ngày claim
        DATEDIFF(cl.createdAt, ct.contractStartDate) AS days_from_contract_to_claim,

        -- Thời gian xuất viện
        cl.hospitalDischargeDate AS hospitalDischargeDate,

        -- Loại khách hàng, sản phẩm
        ct.customerType AS customerType,
        cl.tpaId AS tpaId,

        -- Thông tin liên hệ
        co.peopleName AS name,
        co.peoplePhone AS phone,
        co.peopleEmail AS email,
        co.peopleAddress AS address,

        -- Company/Program
        co.programId AS comp_prog_id,
        co.programName AS comp_prog_name,
        
        -- ETL timestamp
        NOW() AS etl_loaded_at

    FROM insuranceWarehouse.stgClaim cl
    INNER JOIN insuranceWarehouse.stgContract ct ON cl. contractId = ct.contractId
    INNER JOIN insuranceWarehouse.stgContractObject co ON cl.contractObjectId = co.contractObjectId
    
    ON DUPLICATE KEY UPDATE
        contractId = VALUES(contractId),
        contractObjectId = VALUES(contractObjectId),
        amountClaim = VALUES(amountClaim),
        compensationAmount = VALUES(compensationAmount),
        compensationRate = VALUES(compensationRate),
        hospitalizedDate = VALUES(hospitalizedDate),
        clinics = VALUES(clinics),
        contractStartDate = VALUES(contractStartDate),
        claimStartDate = VALUES(claimStartDate),
        claimMonth = VALUES(claimMonth),
        claimYear = VALUES(claimYear),
        age_group = VALUES(age_group),
        relationshipName = VALUES(relationshipName),
        age = VALUES(age),
        gender = VALUES(gender),
        city = VALUES(city),
        treatmentType = VALUES(treatmentType),
        diagnostic = VALUES(diagnostic),
        common_diagnostic_category = VALUES(common_diagnostic_category),
        days_from_contract_to_claim = VALUES(days_from_contract_to_claim),
        hospitalDischargeDate = VALUES(hospitalDischargeDate),
        customerType = VALUES(customerType),
        tpaId = VALUES(tpaId),
        name = VALUES(name),
        phone = VALUES(phone),
        email = VALUES(email),
        address = VALUES(address),
        comp_prog_id = VALUES(comp_prog_id),
        comp_prog_name = VALUES(comp_prog_name),
        etl_loaded_at = VALUES(etl_loaded_at);
END$$

DELIMITER ;

-- ============================================================================
-- FILE: create_reporting_contract_wide_table.sql
-- PURPOSE: Tạo Wide Table cho ODS/Reporting layer - merge online + offline data
-- DATABASE: insuranceReporting
-- USAGE: mysql -h <host> -u <user> -p < create_reporting_contract_wide_table.sql
-- DESCRIPTION:
--   Bảng này chứa dữ liệu đã được merge từ:
--   1. Online data: CDC staging tables (stgContract + stgContractObject*)
--   2. Offline data: Excel uploads (stgContractObjectOffline) đã qua deduplication
--   
--   Bảng này kết hợp tất cả các field từ 8 loại contractObject:
--   1. ContractObject (BH Sức khỏe - HEALTH)
--   2. ContractObjectVehicle (BH Ô tô - VEHICLE)
--   3. ContractObjectTravel (BH Du lịch - TRAVEL)
--   4. ContractObjectMoto (BH Xe máy - MOTO)
--   5. ContractObjectSocialInsurance (BH Xã hội - SOCIAL)
--   6. ContractObjectMedicalInsurance (BH Y tế - MEDICAL)
--   7. ContractObjectHazard (BH Rủi ro - HAZARD - Offline)
--   8. ContractObjectHouse (BH Nhà ở - HOUSE - Online)
-- ============================================================================

USE `insuranceReporting`;

-- ============================================================================
-- Table: contract
-- Purpose: Wide table chứa dữ liệu merge từ online (CDC) + offline (Excel)
-- ============================================================================
CREATE TABLE IF NOT EXISTS `contract` (
  `id` BIGINT AUTO_INCREMENT COMMENT 'Surrogate key - PK tự tăng (không phải business key)',
  
  -- =========================================================================
  -- DATA SOURCE TRACKING
  -- Phân biệt nguồn dữ liệu: online (CDC) hoặc offline (Excel)
  -- ============================================================================
  `data_source` ENUM('online', 'offline') NOT NULL COMMENT 'Nguồn dữ liệu: online (CDC) hoặc offline (Excel)',
  `source_table` VARCHAR(100) DEFAULT NULL COMMENT 'Tên bảng nguồn gốc',
  
  -- =========================================================================
  -- PRIMARY KEY & COMMON IDENTIFIERS
  -- Dùng cho: ALL (Tất cả 6 loại BH)
  -- =========================================================================
  `contractObjectId` TEXT DEFAULT NULL COMMENT 'ID đối tượng hợp đồng (contract object ID từ business)',
  `contractObjectIdDisplay` TEXT DEFAULT NULL COMMENT 'ID hiển thị - ALL',
  `insuranceType` VARCHAR(50) NOT NULL COMMENT 'Loại BH: HEALTH, VEHICLE, TRAVEL, MOTO, SOCIAL, MEDICAL, HAZARD, HOUSE',
  
  -- =========================================================================
  -- CARD & CERTIFICATE INFORMATION
  -- Dùng cho: ALL
  -- =========================================================================
  `cardNumber` TEXT DEFAULT NULL COMMENT 'Số thẻ - ALL',
  `certificateNumberProvider` TEXT DEFAULT NULL COMMENT 'Số giấy chứng nhận của nhà cung cấp - ALL',
  `accountTPA` TEXT DEFAULT NULL COMMENT 'Tài khoản TPA - ALL',
  
  -- =========================================================================
  -- USER & CONTRACT RELATIONSHIP
  -- Dùng cho: ALL
  -- =========================================================================
  `userId` TEXT DEFAULT NULL COMMENT 'User ID - ALL',
  `contractId` TEXT DEFAULT NULL COMMENT 'Contract ID từ business (đây là ID thật của contract) - ALL',
  `contractIdDisplay` TEXT DEFAULT NULL COMMENT 'Contract ID hiển thị - HEALTH',
  
  -- =========================================================================
  -- STATUS & DATES
  -- Dùng cho: ALL (với tên field khác nhau)
  -- =========================================================================
  `contractStatus` INT(11) DEFAULT NULL COMMENT 'Trạng thái hợp đồng master - ALL',
  `contractObjectSmeStatus` INT(11) DEFAULT NULL COMMENT 'Trạng thái SME - HEALTH, VEHICLE, SOCIAL, MEDICAL',
  `contractIndividualStatus` INT(11) DEFAULT NULL COMMENT 'Trạng thái hợp đồng cá nhân - HEALTH, SOCIAL, MEDICAL',
  `contractObjectStartDate` DATETIME DEFAULT NULL COMMENT 'Ngày bắt đầu - ALL (startDate cho TRAVEL/MOTO)',
  `contractObjectEndDate` DATETIME DEFAULT NULL COMMENT 'Ngày kết thúc - ALL (endDate cho TRAVEL/MOTO)',
  `contractObjectIdProvider` TEXT DEFAULT NULL COMMENT 'Mã chứng nhận nhà BH - ALL (idProvider cho TRAVEL/MOTO)',
  `contractObjectUrl` TEXT DEFAULT NULL COMMENT 'URL đối tượng - ALL (url cho TRAVEL/MOTO)',
  
  -- =========================================================================
  -- PROGRAM & PACKAGE INFORMATION
  -- Dùng cho: ALL
  -- =========================================================================
  `programTypeName` TEXT DEFAULT NULL COMMENT 'Tên loại chương trình - ALL',
  `programTypeId` TEXT DEFAULT NULL COMMENT 'ID loại chương trình - ALL',
  `programId` TEXT DEFAULT NULL COMMENT 'ID chương trình - ALL',
  `programName` TEXT DEFAULT NULL COMMENT 'Tên chương trình - ALL',
  `packageId` TEXT DEFAULT NULL COMMENT 'ID gói - ALL',
  `packageName` TEXT DEFAULT NULL COMMENT 'Tên gói - ALL',
  `packageCodeFromProvider` TEXT DEFAULT NULL COMMENT 'Mã gói từ nhà cung cấp - ALL',
  `programCodeMiningChannel` TEXT DEFAULT NULL COMMENT 'Mã khai thác kênh - ALL',
  `programDocument` LONGTEXT DEFAULT '[]' COMMENT 'Tài liệu chương trình - ALL',
  
  -- =========================================================================
  -- AGE RANGE
  -- Dùng cho: HEALTH, SOCIAL, MEDICAL
  -- =========================================================================
  `fromAge` INT(11) DEFAULT NULL COMMENT 'Tuổi từ - HEALTH, SOCIAL, MEDICAL',
  `toAge` INT(11) DEFAULT NULL COMMENT 'Tuổi đến - HEALTH, SOCIAL, MEDICAL',
  
  -- =========================================================================
  -- FEE & AMOUNT INFORMATION
  -- Dùng cho: ALL
  -- =========================================================================
  `amount` DECIMAL(20,0) DEFAULT NULL COMMENT 'Tổng số tiền hợp đồng master - ALL',
  `amountPay` DECIMAL(20,0) DEFAULT NULL COMMENT 'Số tiền thanh toán hợp đồng master - ALL',
  `feeMainBenefit` DECIMAL(20,0) DEFAULT NULL COMMENT 'Phí quyền lợi chính - ALL',
  `feeSideBenefit` DECIMAL(20,0) DEFAULT 0 COMMENT 'Phí quyền lợi phụ - HEALTH, MOTO, SOCIAL, MEDICAL',
  `feeInsurance` DECIMAL(20,0) DEFAULT NULL COMMENT 'Phí bảo hiểm - ALL',
  `maximumAmount` DECIMAL(20,0) DEFAULT NULL COMMENT 'Số tiền tối đa - ALL',
  
  -- VAT & Pre-VAT Fee breakdown
  `preVatFeeMainBenefit` DECIMAL(20,0) DEFAULT 0 COMMENT 'Phí chính trước VAT - HEALTH, MOTO, SOCIAL, MEDICAL',
  `vatFeeMainBenefit` DECIMAL(20,0) DEFAULT 0 COMMENT 'VAT phí chính - HEALTH, MOTO, SOCIAL, MEDICAL',
  `preVatFeeSideBenefit` DECIMAL(20,0) DEFAULT 0 COMMENT 'Phí phụ trước VAT - HEALTH, MOTO, SOCIAL, MEDICAL',
  `vatFeeSideBenefit` DECIMAL(20,0) DEFAULT 0 COMMENT 'VAT phí phụ - HEALTH, MOTO, SOCIAL, MEDICAL',
  `preVatFeeInsurance` DECIMAL(20,0) DEFAULT 0 COMMENT 'Phí BH trước VAT - HEALTH, MOTO, SOCIAL, MEDICAL',
  `vatFeeInsurance` DECIMAL(20,0) DEFAULT 0 COMMENT 'VAT phí BH - HEALTH, MOTO, SOCIAL, MEDICAL',
  
  -- =========================================================================
  -- TERMS & CONDITIONS
  -- Dùng cho: ALL
  -- =========================================================================
  `termsId` TEXT DEFAULT NULL COMMENT 'ID điều khoản - ALL',
  `termsName` TEXT DEFAULT NULL COMMENT 'Tên điều khoản - ALL',
  `termsUrl` TEXT DEFAULT NULL COMMENT 'URL điều khoản - ALL',
  `termsFeePaymentMethod` TEXT DEFAULT NULL COMMENT 'Phương thức thanh toán phí - ALL',
  
  -- =========================================================================
  -- PROVIDER INFORMATION
  -- Dùng cho: ALL
  -- =========================================================================
  `providerId` TEXT DEFAULT NULL COMMENT 'ID nhà cung cấp - ALL',
  `providerName` TEXT DEFAULT NULL COMMENT 'Tên nhà cung cấp - ALL',
  `companyProviderName` TEXT DEFAULT NULL COMMENT 'Tên công ty nhà cung cấp - ALL',
  `companyProviderId` TEXT DEFAULT NULL COMMENT 'ID công ty nhà cung cấp - ALL',
  `companyProviderUrl` TEXT DEFAULT NULL COMMENT 'URL công ty nhà cung cấp - ALL',
  `majorName` TEXT DEFAULT NULL COMMENT 'Tên sản phẩm chính - ALL',
  `majorId` TEXT DEFAULT NULL COMMENT 'ID sản phẩm chính - ALL',
  
  -- =========================================================================
  -- PEOPLE INFORMATION (for ALL)
  -- Dùng cho: ALL (người được BH)
  -- =========================================================================
  `peopleName` TEXT DEFAULT NULL COMMENT 'Tên người được BH - ALL',
  `peopleDob` DATE DEFAULT NULL COMMENT 'Ngày sinh người được BH - ALL',
  `peopleGender` INT(11) DEFAULT NULL COMMENT 'Giới tính (1=Nam, 0=Nữ) - ALL',
  `peoplePhone` TEXT DEFAULT NULL COMMENT 'Số điện thoại - ALL',
  `peopleEmail` TEXT DEFAULT NULL COMMENT 'Email - ALL',
  `peopleLicense` TEXT DEFAULT NULL COMMENT 'CMND/CCCD - ALL',
  `peopleLicenseType` TEXT DEFAULT NULL COMMENT 'Loại giấy tờ - ALL',
  `peopleLicenseFront` TEXT DEFAULT NULL COMMENT 'Ảnh mặt trước CMND - ALL',
  `peopleLicenseBack` TEXT DEFAULT NULL COMMENT 'Ảnh mặt sau CMND - ALL',
  `peopleRelationship` INT(11) DEFAULT NULL COMMENT 'Quan hệ với người mua (0=Bản thân, 1=Vợ, 2=Chồng, 3=Con, 4=Bố, 5=Mẹ) - ALL',
  
  -- =========================================================================
  -- ADDRESS INFORMATION (for people)
  -- Dùng cho: ALL
  -- =========================================================================
  `peopleAddress` TEXT DEFAULT NULL COMMENT 'Địa chỉ - ALL',
  `peopleDistrictsCode` TEXT DEFAULT NULL COMMENT 'Mã quận/huyện - ALL',
  `peopleWardsCode` TEXT DEFAULT NULL COMMENT 'Mã phường/xã - ALL',
  `peopleStreet` TEXT DEFAULT NULL COMMENT 'Tên đường - ALL',
  `houseNumber` TEXT DEFAULT NULL COMMENT 'Số nhà - ALL',
  `cityCode` TEXT DEFAULT NULL COMMENT 'Mã thành phố - ALL',
  `customerType` INT(11) DEFAULT NULL COMMENT 'Loại khách hàng - ALL',
  `upload` TEXT DEFAULT NULL COMMENT 'File upload - ALL',
  `note` TEXT DEFAULT NULL COMMENT 'Ghi chú - ALL',
  

  
  -- =========================================================================
  -- AUDIT FIELDS
  -- =========================================================================
  `createdAt` DATETIME DEFAULT NULL COMMENT 'Thời gian tạo',
  `createdBy` TEXT DEFAULT NULL COMMENT 'Người tạo',
  `modifiedAt` DATETIME DEFAULT NULL COMMENT 'Thời gian cập nhật',
  `modifiedBy` TEXT DEFAULT NULL COMMENT 'Người cập nhật',
  `modifiedDate` DATETIME DEFAULT NULL COMMENT 'Ngày cập nhật',
  
  -- =========================================================================
  -- CONTRACT OBJECT METADATA
  -- =========================================================================
  `minDate` INT(11) DEFAULT NULL COMMENT 'Ngày tối thiểu - HEALTH',
  `contractObjectIdPrev` TEXT DEFAULT NULL COMMENT 'ID đối tượng trước đó - HEALTH',
  `memberId` TEXT DEFAULT NULL COMMENT 'ID thành viên - HEALTH',
  `contractObjectCardDocument` TEXT DEFAULT NULL COMMENT 'Tài liệu thẻ - HEALTH',
  `contractObjectCardImage` TEXT DEFAULT NULL COMMENT 'Ảnh thẻ - HEALTH',
  `paymentType` INT(11) DEFAULT NULL COMMENT 'Loại thanh toán - HEALTH',
  `document` TEXT DEFAULT NULL COMMENT 'Tài liệu - HEALTH',
  
  -- =========================================================================
  -- VEHICLE SPECIFIC FIELDS
  -- Dùng cho: VEHICLE, MOTO
  -- =========================================================================
  `vehicleId` TEXT DEFAULT NULL COMMENT 'ID xe - VEHICLE',
  `licensePlates` TEXT DEFAULT NULL COMMENT 'Biển số xe - VEHICLE, MOTO',
  `chassisNumber` TEXT DEFAULT NULL COMMENT 'Số khung - VEHICLE, MOTO',
  `engineNumber` TEXT DEFAULT NULL COMMENT 'Số máy - VEHICLE, MOTO',
  `maker` TEXT DEFAULT NULL COMMENT 'Hãng xe - VEHICLE',
  `type` TEXT DEFAULT NULL COMMENT 'Loại xe - VEHICLE, MOTO',
  `line` TEXT DEFAULT NULL COMMENT 'Dòng xe - VEHICLE',
  `seatNumber` INT(11) DEFAULT NULL COMMENT 'Số chỗ ngồi - VEHICLE',
  `programObject` TEXT DEFAULT NULL COMMENT 'Đối tượng chương trình - VEHICLE',
  
  -- =========================================================================
  -- HOUSE INSURANCE SPECIFIC FIELDS
  -- Dùng cho: HOUSE
  -- =========================================================================
  `ownership` VARCHAR(256) DEFAULT NULL COMMENT 'Hình thức sở hữu tài sản - HOUSE',
  `houseLevelId` VARCHAR(256) DEFAULT NULL COMMENT 'Cấp nhà ID - HOUSE',
  `houseProgramObject` INT(11) DEFAULT NULL COMMENT 'Đối tượng ngôi nhà - HOUSE',
  `houseName` VARCHAR(256) DEFAULT NULL COMMENT 'Tên chung cư, khu dân cư - HOUSE',
  `numberFloors` INT(11) DEFAULT NULL COMMENT 'Số tầng - HOUSE',
  `houseAddress` VARCHAR(256) DEFAULT NULL COMMENT 'Địa chỉ căn nhà hoặc căn hộ - HOUSE',
  `houseDistrictsCode` INT(11) DEFAULT NULL COMMENT 'Mã quận huyện căn nhà - HOUSE',
  `houseWardsCode` INT(11) DEFAULT NULL COMMENT 'Mã phường xã căn nhà - HOUSE',
  `houseStreet` VARCHAR(256) DEFAULT NULL COMMENT 'Tên đường căn nhà - HOUSE',
  `houseHouseNumber` VARCHAR(256) DEFAULT NULL COMMENT 'Số nhà căn nhà - HOUSE',
  `houseCityCode` INT(11) DEFAULT NULL COMMENT 'Mã thành phố căn nhà - HOUSE',
  `latitude` VARCHAR(256) DEFAULT NULL COMMENT 'Vĩ độ căn nhà - HOUSE',
  `longitude` VARCHAR(256) DEFAULT NULL COMMENT 'Kinh độ căn nhà - HOUSE',
  `acreage` DOUBLE DEFAULT NULL COMMENT 'Diện tích căn nhà (m2) - HOUSE',
  `completionYear` INT(11) DEFAULT NULL COMMENT 'Năm hoàn thiện xây dựng - HOUSE',
  `houseValue` DECIMAL(20,0) DEFAULT NULL COMMENT 'Giá trị thực tế của ngôi nhà - HOUSE',
  `houseValueInsured` DECIMAL(20,0) DEFAULT NULL COMMENT 'Giá trị tham gia bảo hiểm của nhà - HOUSE',
  `propertyValue` DECIMAL(20,0) DEFAULT NULL COMMENT 'Giá trị tài sản thực tế - HOUSE',
  `propertyValueInsured` DECIMAL(20,0) DEFAULT NULL COMMENT 'Giá trị tài sản tham gia BH - HOUSE',
  `houseUses` INT(11) DEFAULT NULL COMMENT 'Mục đích sử dụng nhà - HOUSE',
  `business` VARCHAR(256) DEFAULT NULL COMMENT 'Ngành kinh doanh - HOUSE',
  `companyType` VARCHAR(256) DEFAULT NULL COMMENT 'Loại công ty - HOUSE',
  `foundingYear` INT(11) DEFAULT NULL COMMENT 'Năm thành lập công ty - HOUSE',
  `isStone` INT(11) DEFAULT NULL COMMENT 'Xây bằng gạch đá - HOUSE',
  `widthAlley` DOUBLE DEFAULT NULL COMMENT 'Chiều rộng ngõ vào nhà - HOUSE',
  `insuranceDeductible` DECIMAL(20,0) DEFAULT NULL COMMENT 'Số tiền miễn thường - HOUSE',
  `houseCertificateNumber` VARCHAR(256) DEFAULT NULL COMMENT 'Số giấy chứng nhận đất - HOUSE',
  `numberInApartment` VARCHAR(256) DEFAULT NULL COMMENT 'Số căn hộ trong chung cư - HOUSE',
  `apartmentNameOrNumber` VARCHAR(256) DEFAULT NULL COMMENT 'Tên hoặc số căn hộ - HOUSE',
  `numberUseHouse` DOUBLE DEFAULT NULL COMMENT 'Số người sử dụng nhà - HOUSE',
  `rentAmount` DECIMAL(20,0) DEFAULT NULL COMMENT 'Số tiền thuê nhà/tháng - HOUSE',
  `housePaymentPeriod` INT(11) DEFAULT NULL COMMENT 'Tần suất thanh toán - HOUSE',
  `housePaymentPeriodValue` INT(11) DEFAULT NULL COMMENT 'Khoảng cách thanh toán - HOUSE',
  `housePaymentNumber` INT(11) DEFAULT NULL COMMENT 'Số kỳ thanh toán - HOUSE',
  `housePaymentRatio` DOUBLE DEFAULT NULL COMMENT 'Tỉ lệ % thanh toán - HOUSE',
  `housePaymentType` INT(11) DEFAULT NULL COMMENT 'Loại thanh toán - HOUSE',
  `houseBankName` VARCHAR(256) DEFAULT NULL COMMENT 'Tên ngân hàng thế chấp - HOUSE',
  `houseBankAddress` VARCHAR(256) DEFAULT NULL COMMENT 'Địa chỉ ngân hàng - HOUSE',
  `houseBankEmail` VARCHAR(256) DEFAULT NULL COMMENT 'Email ngân hàng - HOUSE',
  `houseBankCode` VARCHAR(256) DEFAULT NULL COMMENT 'Mã ngân hàng - HOUSE',
  `houseScope` VARCHAR(256) DEFAULT NULL COMMENT 'Phạm vi địa lý - HOUSE',
  `houseClassificationCode` VARCHAR(256) DEFAULT NULL COMMENT 'Mã phân loại ngôi nhà - HOUSE',
  `partnerHouseId` VARCHAR(256) DEFAULT NULL COMMENT 'Mã nhà từ đối tác - HOUSE',
  `partnerAccountId` VARCHAR(256) DEFAULT NULL COMMENT 'Mã tài khoản đối tác - HOUSE',
  
  -- =========================================================================
  -- TRAVEL SPECIFIC FIELDS
  -- Dùng cho: TRAVEL
  -- =========================================================================
  `nationality` TEXT DEFAULT NULL COMMENT 'Quốc tịch - TRAVEL',
  `nationalityId` TEXT DEFAULT NULL COMMENT 'ID quốc tịch - TRAVEL',
  `domesticOrInternational` TEXT DEFAULT NULL COMMENT 'Trong nước/Quốc tế - TRAVEL',
  `departure` TEXT DEFAULT NULL COMMENT 'Điểm khởi hành - TRAVEL',
  `destination` TEXT DEFAULT NULL COMMENT 'Điểm đến - TRAVEL',
  `destinationDomestic` TEXT DEFAULT NULL COMMENT 'Điểm đến trong nước - TRAVEL',
  `journey` TEXT DEFAULT NULL COMMENT 'Hành trình - TRAVEL',
  `programObjectFromProvider` TEXT DEFAULT NULL COMMENT 'Đối tượng từ nhà cung cấp - TRAVEL',
  `destinationFromProvider` TEXT DEFAULT NULL COMMENT 'Điểm đến từ nhà cung cấp - TRAVEL',
  `codePackageFromProvider` TEXT DEFAULT NULL COMMENT 'Mã gói từ nhà cung cấp - TRAVEL',
  `adults` INT(11) DEFAULT NULL COMMENT 'Số người lớn - TRAVEL',
  `children` INT(11) DEFAULT NULL COMMENT 'Số trẻ em - TRAVEL',
  
  -- =========================================================================
  -- PAYER INFORMATION (for TRAVEL)
  -- Dùng cho: TRAVEL
  -- =========================================================================
  `payerUserId` TEXT DEFAULT NULL COMMENT 'User ID người thanh toán - TRAVEL',
  `payerName` TEXT DEFAULT NULL COMMENT 'Tên người thanh toán - TRAVEL',
  `payerDob` DATE DEFAULT NULL COMMENT 'Ngày sinh người thanh toán - TRAVEL',
  `payerGender` INT(11) DEFAULT NULL COMMENT 'Giới tính người thanh toán - TRAVEL',
  `payerLicense` TEXT DEFAULT NULL COMMENT 'CMND người thanh toán - TRAVEL',
  `payerLicenseType` TEXT DEFAULT NULL COMMENT 'Loại giấy tờ người thanh toán - TRAVEL',
  `payerLicenseFront` TEXT DEFAULT NULL COMMENT 'Ảnh mặt trước CMND người thanh toán - TRAVEL',
  `payerLicenseBack` TEXT DEFAULT NULL COMMENT 'Ảnh mặt sau CMND người thanh toán - TRAVEL',
  `payerPhone` TEXT DEFAULT NULL COMMENT 'Số điện thoại người thanh toán - TRAVEL',
  `payerEmail` TEXT DEFAULT NULL COMMENT 'Email người thanh toán - TRAVEL',
  `payerAddress` TEXT DEFAULT NULL COMMENT 'Địa chỉ người thanh toán - TRAVEL',
  `payerDistrictsCode` TEXT DEFAULT NULL COMMENT 'Mã quận/huyện người thanh toán - TRAVEL',
  `payerWardsCode` TEXT DEFAULT NULL COMMENT 'Mã phường/xã người thanh toán - TRAVEL',
  `payerStreet` TEXT DEFAULT NULL COMMENT 'Tên đường người thanh toán - TRAVEL',
  `payerHouseNumber` TEXT DEFAULT NULL COMMENT 'Số nhà người thanh toán - TRAVEL',
  `payerCityCode` TEXT DEFAULT NULL COMMENT 'Mã thành phố người thanh toán - TRAVEL',
  `payerNote` TEXT DEFAULT NULL COMMENT 'Ghi chú người thanh toán - TRAVEL',
  `payerUpload` TEXT DEFAULT NULL COMMENT 'File upload người thanh toán - TRAVEL',
  `payerCustomerType` INT(11) DEFAULT NULL COMMENT 'Loại khách hàng người thanh toán - TRAVEL',
  
  -- =========================================================================
  -- SOCIAL INSURANCE SPECIFIC FIELDS
  -- Dùng cho: SOCIAL
  -- =========================================================================
  `declarationType` INT(11) DEFAULT NULL COMMENT 'Loại khai báo - SOCIAL',
  `remunerationType` INT(11) DEFAULT NULL COMMENT 'Loại thù lao - SOCIAL',
  `oldCardStartDate` DATE DEFAULT NULL COMMENT 'Ngày bắt đầu thẻ cũ - SOCIAL',
  `oldCardEndDate` DATE DEFAULT NULL COMMENT 'Ngày kết thúc thẻ cũ - SOCIAL',
  `renewal` TINYINT(1) DEFAULT NULL COMMENT 'Gia hạn - SOCIAL',
  `socialFamilyId` TEXT DEFAULT NULL COMMENT 'ID gia đình BHXH - SOCIAL',
  `socialId` TEXT DEFAULT NULL COMMENT 'ID BHXH - SOCIAL',
  `monthlyIncome` DECIMAL(20,0) DEFAULT NULL COMMENT 'Thu nhập hàng tháng - SOCIAL',
  `paymentPeriod` INT(11) DEFAULT NULL COMMENT 'Kỳ thanh toán - SOCIAL',
  `supportBudget` DECIMAL(20,0) DEFAULT NULL COMMENT 'Ngân sách hỗ trợ - SOCIAL',
  `oldBhxhCodeUnit` TEXT DEFAULT NULL COMMENT 'Mã đơn vị BHXH cũ - SOCIAL',
  `oldRegisterDate` DATE DEFAULT NULL COMMENT 'Ngày đăng ký cũ - SOCIAL',
  `percent` DECIMAL(5,2) DEFAULT NULL COMMENT 'Phần trăm - SOCIAL',
  `discountAmount` DECIMAL(20,0) DEFAULT NULL COMMENT 'Số tiền giảm - SOCIAL',
  `fiveYearDate` DATE DEFAULT NULL COMMENT 'Ngày 5 năm - SOCIAL',
  
  -- =========================================================================
  -- MEDICAL INSURANCE SPECIFIC FIELDS
  -- Dùng cho: MEDICAL
  -- =========================================================================
  `medicalId` TEXT DEFAULT NULL COMMENT 'ID BHYT - MEDICAL',
  `hospitalCode` TEXT DEFAULT NULL COMMENT 'Mã bệnh viện - MEDICAL',
  `hospitalName` TEXT DEFAULT NULL COMMENT 'Tên bệnh viện - MEDICAL',
  `hospitalCityRegisteredCode` TEXT DEFAULT NULL COMMENT 'Mã thành phố đăng ký BV - MEDICAL',
  `hospitalCityRegisteredName` TEXT DEFAULT NULL COMMENT 'Tên thành phố đăng ký BV - MEDICAL',
  `nation` TEXT DEFAULT NULL COMMENT 'Dân tộc - MEDICAL',
  `ethnicity` TEXT DEFAULT NULL COMMENT 'Sắc tộc - MEDICAL',
  
  -- =========================================================================
  -- THIRD PARTY & PROVIDER INTEGRATION
  -- Dùng cho: HEALTH
  -- =========================================================================
  `thirdPartyRequestId` TEXT DEFAULT NULL COMMENT 'ID yêu cầu bên thứ ba - HEALTH',
  `reqCode` TEXT DEFAULT NULL COMMENT 'Mã yêu cầu - HEALTH',
  `contractIdProvider` TEXT DEFAULT NULL COMMENT 'ID hợp đồng nhà cung cấp - HEALTH',
  
  -- =========================================================================
  -- CONTRACT STATUS & TYPE
  -- Dùng cho: HEALTH
  -- =========================================================================
  `buyHelp` TINYINT(1) DEFAULT NULL COMMENT 'Mua hộ - HEALTH',
  `buyerId` TEXT DEFAULT NULL COMMENT 'ID người mua - HEALTH',
  `contractType` INT(11) DEFAULT NULL COMMENT 'Loại hợp đồng - HEALTH',
  `contractIdRoot` TEXT DEFAULT NULL COMMENT 'ID hợp đồng gốc - HEALTH',
  
  -- =========================================================================
  -- SALES & BRANCH INFORMATION
  -- Dùng cho: HEALTH
  -- =========================================================================
  `companySale` TEXT DEFAULT NULL COMMENT 'Công ty bán hàng - HEALTH',
  `branchSale` TEXT DEFAULT NULL COMMENT 'Chi nhánh bán hàng - HEALTH',
  `branchSaleName` TEXT DEFAULT NULL COMMENT 'Tên chi nhánh bán hàng - HEALTH',
  `companySaleName` TEXT DEFAULT NULL COMMENT 'Tên công ty bán hàng - HEALTH',
  
  -- =========================================================================
  -- CONTRACT PERIOD & DATES
  -- Dùng cho: HEALTH
  -- =========================================================================
  `contractPeriod` INT(11) DEFAULT NULL COMMENT 'Thời hạn hợp đồng - HEALTH',
  `contractPeriodValue` TEXT DEFAULT NULL COMMENT 'Giá trị thời hạn - HEALTH',
  
  -- =========================================================================
  -- VOUCHER & DISCOUNT
  -- Dùng cho: HEALTH
  -- =========================================================================
  `voucherId` TEXT DEFAULT NULL COMMENT 'ID voucher - HEALTH',
  `voucherCode` TEXT DEFAULT NULL COMMENT 'Mã voucher - HEALTH',
  `amountDiscount` DECIMAL(20,0) DEFAULT NULL COMMENT 'Số tiền giảm giá - HEALTH',
  
  -- =========================================================================
  -- PAYMENT INFORMATION
  -- Dùng cho: HEALTH
  -- =========================================================================
  `commission` DECIMAL(20,0) DEFAULT NULL COMMENT 'Hoa hồng - HEALTH',
  `paymentDueDate` DATE DEFAULT NULL COMMENT 'Ngày đến hạn thanh toán - HAZARD',
  `paymentDate` DATE DEFAULT NULL COMMENT 'Ngày thanh toán thực tế - HAZARD',
  `redBill` TINYINT(1) DEFAULT NULL COMMENT 'Hóa đơn đỏ - HEALTH',
  `paymentMethod` INT(11) DEFAULT NULL COMMENT 'Phương thức thanh toán - HEALTH',
  
  -- =========================================================================
  -- CANCELLATION & ERROR INFORMATION
  -- Dùng cho: HEALTH
  -- =========================================================================
  `reasonCancel` TEXT DEFAULT NULL COMMENT 'Lý do hủy - HEALTH',
  `codeErrorCancel` TEXT DEFAULT NULL COMMENT 'Mã lỗi hủy - HEALTH',
  `messageError` TEXT DEFAULT NULL COMMENT 'Thông báo lỗi - HEALTH',
  
  -- =========================================================================
  -- REFERRAL & BONUS
  -- Dùng cho: HEALTH
  -- =========================================================================
  `referralCode` TEXT DEFAULT NULL COMMENT 'Mã giới thiệu - HEALTH',
  `saleId` TEXT DEFAULT NULL COMMENT 'ID nhân viên bán hàng - HEALTH',
  `bonusAmount` DECIMAL(20,0) DEFAULT NULL COMMENT 'Số tiền thưởng - HEALTH',
  
  -- =========================================================================
  -- SOURCE TRACKING
  -- Dùng cho: HEALTH
  -- =========================================================================
  `fromLead` VARCHAR(50) DEFAULT NULL COMMENT 'Từ lead - HEALTH',
  `source` TEXT DEFAULT NULL COMMENT 'Nguồn - HEALTH',
  `outsideCreatedAt` DATETIME DEFAULT NULL COMMENT 'Thời gian tạo bên ngoài - HEALTH',
  `outsidePaymentAt` DATETIME DEFAULT NULL COMMENT 'Thời gian thanh toán bên ngoài - HEALTH',
  `outsidePaymentId` TEXT DEFAULT NULL COMMENT 'ID thanh toán bên ngoài - HEALTH',
  `channelId` TEXT DEFAULT NULL COMMENT 'ID kênh - HEALTH',
  `levelId` TEXT DEFAULT NULL COMMENT 'ID cấp độ - HEALTH',
  
  -- =========================================================================
  -- ADDITIONAL FIELDS
  -- Dùng cho: HEALTH
  -- =========================================================================
  `certFile` TEXT DEFAULT NULL COMMENT 'File chứng chỉ - HEALTH',
  `orderNumber` TEXT DEFAULT NULL COMMENT 'Số thứ tự - HEALTH',
  
  -- =========================================================================
  -- ETL METADATA
  -- Tracking thông tin ETL process
  -- =========================================================================
  `etl_loaded_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Thời gian load vào ODS',
  `etl_batch_id` VARCHAR(50) DEFAULT NULL COMMENT 'Batch ID của ETL process',
  
  -- =========================================================================
  -- INDEXES & CONSTRAINTS
  -- =========================================================================
  PRIMARY KEY (`id`),
  
  -- UNIQUE constraint for idempotent ETL (prevent duplicate inserts)
  -- Allows: 1 contractId → multiple contractObjectId (many beneficiaries)
  -- Blocks: duplicate (contractId + contractObjectId) pairs
  -- Note: Offline records with NULL contractObjectId can still duplicate
  UNIQUE KEY `uk_contract_object` (`contractId`(100), `contractObjectId`(100)),
  
  INDEX `idx_data_source` (`data_source`),
  INDEX `idx_insuranceType` (`insuranceType`),
  INDEX `idx_contractId` (`contractId`(50)),
  INDEX `idx_userId` (`userId`(50)),
  INDEX `idx_modifiedDate` (`modifiedDate`),
  INDEX `idx_packageName` (`packageName`(100)),
  INDEX `idx_contractStatus` (`contractStatus`),
  INDEX `idx_createdAt` (`createdAt`),
  INDEX `idx_etl_loaded_at` (`etl_loaded_at`),
  INDEX `idx_business_key` (`contractId`(50), `insuranceType`, `data_source`),
  INDEX `idx_paymentDate` (`paymentDate`),
  INDEX `idx_houseCityCode` (`houseCityCode`),
  INDEX `idx_partnerHouseId` (`partnerHouseId`(100))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='ODS Wide table - merge online (CDC) + offline (Excel) data - 8 insurance types';

-- ============================================================================
-- NOTES:
-- ============================================================================
-- 1. Field `insuranceType` dùng để phân biệt loại bảo hiểm:
--    - 'HEALTH': BH Sức khỏe (stgContractObject)
--    - 'VEHICLE': BH Ô tô (stgContractObjectVehicle)
--    - 'TRAVEL': BH Du lịch (stgContractObjectTravel)
--    - 'MOTO': BH Xe máy (stgContractObjectMoto)
--    - 'SOCIAL': BH Xã hội (stgContractObjectSocialInsurance)
--    - 'MEDICAL': BH Y tế (stgContractObjectMedicalInsurance)
--    - 'HAZARD': BH Rủi ro (stgContractObjectHazard - Offline Excel)
--    - 'HOUSE': BH Nhà ở (stgContractObjectHouse - Online CDC)
--
-- 2. Field `data_source` dùng để phân biệt nguồn dữ liệu:
--    - 'online': Dữ liệu từ CDC staging (production database)
--    - 'offline': Dữ liệu từ Excel upload (stgContractObjectOffline)
--
-- 3. Business Key cho deduplication:
--    - contractId + name/peopleName + majorName + companyProviderName
--    - Được sử dụng bởi Redis cache để detect duplicates
--    - "Online wins" policy: Nếu trùng, ưu tiên giữ data online
--
-- 4. Các field có comment "ALL" được sử dụng bởi tất cả 6 loại BH
--
-- 5. TRAVEL và MOTO có 2 bộ field cho người được BH:
--    - Các field `people*` (dùng cho HEALTH, SOCIAL, MEDICAL, VEHICLE)
--    - Các field không prefix (name, dob, gender...) dùng cho TRAVEL, MOTO
--
-- 6. HEALTH có rất nhiều field từ contract (các field liên quan đến sale, payment, etc.)
--    mà các loại BH khác không có
--
-- 7. ETL Process:
--    - Merge data từ stgContract + stgContractObject* (online) với stgContractObjectOffline (offline)
--    - Redis cache được build từ online data để detect duplicates
--    - Offline data sẽ skip nếu trùng với online data (checked via Redis)
--    - Mỗi lần chạy ETL tạo một etl_batch_id mới
--
-- 8. Khuyến nghị khi query:
--    - Luôn filter theo `insuranceType` để improve performance
--    - Sử dụng index `idx_business_key` khi cần tìm duplicate
--    - Filter theo `data_source` nếu chỉ muốn xem online hoặc offline data
--
-- ============================================================================
-- END OF FILE
-- ============================================================================
