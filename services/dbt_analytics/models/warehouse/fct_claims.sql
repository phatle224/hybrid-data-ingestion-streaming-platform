{{ config(
    materialized='incremental',
    unique_key='claim_id'
) }}

-- ============================================================================
-- Fact: fct_claims (Yêu Cầu Bồi Thường Bảo Hiểm)
-- Grain: 1 row = 1 yêu cầu bồi thường (claim) duy nhất
-- Design: Separated from dm_profiling_analysis; diagnostic category computed here
-- ============================================================================

WITH claims AS (
    SELECT * FROM {{ ref('stg_claims') }}

    {% if is_incremental() %}
        WHERE modified_at > (SELECT COALESCE(MAX(modified_at), '1970-01-01'::timestamp) FROM {{ this }})
    {% endif %}
),

contracts AS (
    SELECT * FROM {{ ref('fct_contracts') }}
)

SELECT
    -- ====== Natural Key ======
    cl.claim_id,

    -- ====== Foreign Keys ======
    cl.contract_object_id,
    co.contract_id,
    co.customer_key,
    co.insured_person_key,
    co.product_key,

    -- FK → dim_date
    TO_CHAR(cl.created_at::date, 'YYYYMMDD')::integer AS claim_date_key,
    CASE
        WHEN cl.hospitalized_date IS NOT NULL
        THEN TO_CHAR(cl.hospitalized_date::date, 'YYYYMMDD')::integer
        ELSE NULL
    END AS hospitalized_date_key,

    -- ====== Measures ======
    cl.amount_claim,
    cl.compensation_amount,

    -- Tỉ lệ bồi thường (%)
    CASE
        WHEN cl.amount_claim IS NOT NULL AND cl.amount_claim > 0
        THEN ROUND((cl.compensation_amount / cl.amount_claim) * 100, 2)
        ELSE 0.00
    END AS compensation_rate,

    -- Số ngày nằm viện
    CASE
        WHEN cl.hospital_discharge_date IS NOT NULL AND cl.hospitalized_date IS NOT NULL
        THEN (cl.hospital_discharge_date::date - cl.hospitalized_date::date)
        ELSE NULL
    END AS days_hospitalized,

    -- Số ngày từ hiệu lực HĐ → ngày claim
    CASE
        WHEN co.start_date_key IS NOT NULL AND cl.created_at IS NOT NULL
        THEN (cl.created_at::date - TO_DATE(co.start_date_key::text, 'YYYYMMDD'))
        ELSE NULL
    END AS days_from_contract_to_claim,

    -- ====== Claim Attributes ======
    cl.claim_type,
    cl.treatment_type,
    cl.diagnostic,
    cl.place_of_treatment,
    cl.hospitalized_date,
    cl.hospital_discharge_date,
    cl.status AS claim_status,
    cl.tpa_id,

    -- ====================================================================
    -- DIAGNOSTIC CATEGORY (business logic tập trung tại Fact Claims)
    -- ====================================================================
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

    -- ====== Time Attributes (denormalized for convenience) ======
    EXTRACT(MONTH FROM cl.created_at)::integer AS claim_month,
    EXTRACT(YEAR FROM cl.created_at)::integer AS claim_year,

    -- ====== Audit ======
    cl.created_at,
    cl.modified_at,
    CURRENT_TIMESTAMP AS etl_loaded_at

FROM claims cl
INNER JOIN contracts co ON cl.contract_object_id = co.contract_object_id
