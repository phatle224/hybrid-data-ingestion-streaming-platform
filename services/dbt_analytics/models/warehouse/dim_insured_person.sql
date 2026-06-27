{{ config(
    materialized='incremental',
    unique_key='insured_person_key'
) }}

-- ============================================================================
-- Dimension: dim_insured_person (Người Được Bảo Hiểm)
-- Grain: 1 row = 1 người được bảo hiểm duy nhất
-- Source: int_contracts_deduped
-- Business logic: City decode (63 tỉnh thành) + Relationship decode tập trung tại đây
-- ============================================================================

WITH source_persons AS (
    SELECT
        people_name,
        people_dob,
        people_gender,
        people_phone,
        people_email,
        people_address,
        people_city_code,
        people_relationship,
        source_type,
        MAX(modified_at) AS modified_at
    FROM {{ ref('int_contracts_deduped') }}
    WHERE people_name IS NOT NULL

    {% if is_incremental() %}
        AND modified_at > (SELECT COALESCE(MAX(modified_at), '1970-01-01'::timestamp) FROM {{ this }})
    {% endif %}

    GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9
)

SELECT
    -- Surrogate key
    MD5(
        COALESCE(people_name, '') || '||' ||
        COALESCE(people_dob::text, '') || '||' ||
        COALESCE(people_phone, '')
    ) AS insured_person_key,

    people_name AS insured_name,
    people_dob AS insured_dob,
    people_gender AS insured_gender,
    people_phone AS insured_phone,
    people_email AS insured_email,
    people_address AS insured_address,
    people_city_code,
    people_relationship,
    source_type,

    -- ====================================================================
    -- AGE CALCULATION (tập trung tại Dimension, không lặp ở Mart)
    -- ====================================================================
    CASE
        WHEN people_dob IS NOT NULL
        THEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, people_dob))::integer
        ELSE NULL
    END AS insured_age,

    CASE
        WHEN people_dob IS NULL THEN 'Unknown'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, people_dob)) BETWEEN 0 AND 6 THEN '0-6'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, people_dob)) BETWEEN 7 AND 17 THEN '7-17'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, people_dob)) BETWEEN 18 AND 35 THEN '18-35'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, people_dob)) BETWEEN 36 AND 55 THEN '36-55'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, people_dob)) >= 56 THEN '56+'
        ELSE 'Unknown'
    END AS insured_age_group,

    -- ====================================================================
    -- RELATIONSHIP DECODE (từ int code → tên tiếng Việt)
    -- ====================================================================
    CASE people_relationship
        WHEN 0 THEN 'Bản thân'
        WHEN 1 THEN 'Bố/Mẹ đẻ'
        WHEN 2 THEN 'Vợ/Chồng'
        WHEN 3 THEN 'Anh/Chị/Em ruột'
        WHEN 4 THEN 'Con đẻ/nuôi hợp pháp'
        WHEN 5 THEN 'Khác'
        WHEN 6 THEN 'Bố/Mẹ của vợ/chồng'
        ELSE 'Khác'
    END AS relationship_name,

    -- ====================================================================
    -- CITY DECODE (63 tỉnh thành Việt Nam — tập trung tại đây)
    -- ====================================================================
    CASE people_city_code
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
    END AS city_name,

    modified_at

FROM source_persons
