{{ config(
    materialized='table',
    schema='warehouse'
) }}

-- ============================================================================
-- Dimension: dim_product (Sản Phẩm Bảo Hiểm)
-- Grain: 1 row = 1 sản phẩm/gói bảo hiểm duy nhất
-- Source: int_contracts_deduped (DISTINCT product attributes)
-- Materialized as TABLE (low cardinality, full refresh mỗi lần run)
-- ============================================================================

WITH distinct_products AS (
    SELECT DISTINCT
        insurance_type,
        major_name,
        program_id,
        program_name,
        company_provider_name
    FROM {{ ref('int_contracts_deduped') }}
    WHERE major_name IS NOT NULL
       OR insurance_type IS NOT NULL
)

SELECT
    -- Surrogate key
    MD5(
        COALESCE(insurance_type, '') || '||' ||
        COALESCE(major_name, '') || '||' ||
        COALESCE(program_name, '') || '||' ||
        COALESCE(company_provider_name, '')
    ) AS product_key,

    insurance_type,
    major_name,
    program_id,
    program_name,
    company_provider_name,

    -- Insurance category (group level)
    CASE insurance_type
        WHEN 'HEALTH'  THEN 'Sức khỏe'
        WHEN 'VEHICLE' THEN 'Xe ô tô'
        WHEN 'TRAVEL'  THEN 'Du lịch'
        WHEN 'MOTO'    THEN 'Xe máy'
        WHEN 'SOCIAL'  THEN 'Bảo hiểm xã hội'
        WHEN 'MEDICAL' THEN 'Bảo hiểm y tế'
        WHEN 'HOUSE'   THEN 'Nhà tư nhân'
        ELSE COALESCE(insurance_type, 'Không xác định')
    END AS insurance_category

FROM distinct_products
