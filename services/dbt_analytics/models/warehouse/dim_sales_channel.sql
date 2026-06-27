{{ config(
    materialized='table',
    schema='warehouse'
) }}

-- ============================================================================
-- Dimension: dim_sales_channel (Kênh Bán Hàng)
-- Grain: 1 row = 1 kênh bán hàng duy nhất
-- Source: stg_contracts (DISTINCT channels)
-- ============================================================================

WITH distinct_channels AS (
    SELECT DISTINCT
        company_sale_name,
        branch_sale_name
    FROM {{ ref('stg_contracts') }}
    WHERE company_sale_name IS NOT NULL
       OR branch_sale_name IS NOT NULL
)

SELECT
    MD5(
        COALESCE(company_sale_name, '') || '||' ||
        COALESCE(branch_sale_name, '')
    ) AS channel_key,

    COALESCE(company_sale_name, 'Không xác định') AS company_sale_name,
    COALESCE(branch_sale_name, 'Không xác định') AS branch_sale_name

FROM distinct_channels
