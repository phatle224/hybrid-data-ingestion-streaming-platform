

WITH contracts AS (
    SELECT * FROM "insuranceWarehouse"."warehouse"."fct_contracts_wide"
),

claims AS (
    SELECT * FROM "insuranceWarehouse"."staging"."stg_claims"
    
    
),

joined AS (
    SELECT
        cl.claim_id,
        co.contract_id,
        co.contract_object_id,
        cl.amount_claim,
        cl.compensation_amount,
        
        -- Calculated Claim metrics
        CASE 
            WHEN cl.amount_claim IS NOT NULL AND cl.amount_claim > 0 
            THEN ROUND((cl.compensation_amount / cl.amount_claim) * 100, 2)
            ELSE 0.00
        END AS compensation_rate,
        
        cl.hospitalized_date,
        cl.hospital_discharge_date,
        
        -- Length of hospitalization (days)
        CASE 
            WHEN cl.hospital_discharge_date IS NOT NULL AND cl.hospitalized_date IS NOT NULL 
            THEN cl.hospital_discharge_date - cl.hospitalized_date
            ELSE NULL
        END AS days_hospitalized,
        
        cl.place_of_treatment AS clinics,
        co.contract_start_date::date AS contract_start_date,
        cl.created_at::date AS claim_start_date,
        EXTRACT(MONTH FROM cl.created_at)::int AS claim_month,
        EXTRACT(YEAR FROM cl.created_at)::int AS claim_year,
        
        -- Age groups based on old rules
        CASE
            WHEN co.insured_dob IS NOT NULL THEN
                CASE
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, co.insured_dob)) BETWEEN 0 AND 6 THEN '0-6'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, co.insured_dob)) BETWEEN 7 AND 17 THEN '7-17'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, co.insured_dob)) BETWEEN 18 AND 35 THEN '18-35'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, co.insured_dob)) BETWEEN 36 AND 55 THEN '36-55'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, co.insured_dob)) >= 56 THEN '56+'
                    ELSE 'Unknown'
                END
            ELSE 'Unknown'
        END AS age_group,
        
        -- Relationship Name based on old rules
        CASE co.people_relationship
            WHEN 0 THEN 'Bản thân'
            WHEN 1 THEN 'Bố/Mẹ đẻ'
            WHEN 2 THEN 'Vợ/Chồng'
            WHEN 3 THEN 'Anh/Chị/Em ruột'
            WHEN 4 THEN 'Con đẻ/nuôi hợp pháp'
            WHEN 5 THEN 'Khác'
            WHEN 6 THEN 'Bố/Mẹ của vợ/chồng'
            ELSE 'Khác'
        END AS relationship_name,
        
        -- Age based on old rules
        CASE
            WHEN co.insured_dob IS NOT NULL THEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, co.insured_dob))::int
            ELSE NULL
        END AS age,
        
        co.insured_gender AS gender,
        
        -- City based on old rules
        CASE co.people_city_code
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
        
        cl.treatment_type,
        cl.diagnostic,
        
        -- Diagnostic categorization based on old rules
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
        
        -- Days from contract effect to claim
        (cl.created_at::date - co.contract_start_date::date)::int AS days_from_contract_to_claim,
        
        co.customer_type,
        cl.tpa_id,
        co.insured_name AS name,
        co.insured_phone AS phone,
        co.insured_email AS email,
        co.insured_address AS address,
        co.program_id AS comp_prog_id,
        co.program_name AS comp_prog_name,
        co.source_type,
        cl.created_at AS claim_created_at,
        cl.modified_at AS claim_modified_at,
        CURRENT_TIMESTAMP AS etl_loaded_at
    FROM claims cl
    INNER JOIN contracts co ON cl.contract_object_id = co.contract_object_id
)

SELECT * FROM joined