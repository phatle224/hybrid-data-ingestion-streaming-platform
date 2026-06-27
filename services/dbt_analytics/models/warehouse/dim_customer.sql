{{ config(
    materialized='incremental',
    unique_key='customer_key'
) }}

-- ============================================================================
-- Dimension: dim_customer (Người Mua Bảo Hiểm / Buyer)
-- Grain: 1 row = 1 khách hàng mua bảo hiểm duy nhất
-- Source: stg_contracts
-- SCD Type: 1 (Overwrite)
-- ============================================================================

WITH source_customers AS (
    SELECT
        contract_id,
        buyer_name,
        buyer_dob,
        buyer_gender,
        buyer_phone,
        buyer_email,
        buyer_address,
        customer_type,
        company_sale_name,
        branch_sale_name,
        created_at,
        modified_at
    FROM {{ ref('stg_contracts') }}
    WHERE buyer_name IS NOT NULL

    {% if is_incremental() %}
        AND modified_at > (SELECT COALESCE(MAX(modified_at), '1970-01-01'::timestamp) FROM {{ this }})
    {% endif %}
),

-- Deduplicate: keep the most recently modified record per customer
ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY buyer_name, buyer_dob, buyer_phone
            ORDER BY modified_at DESC
        ) AS rn
    FROM source_customers
)

SELECT
    -- Surrogate key
    MD5(
        COALESCE(buyer_name, '') || '||' ||
        COALESCE(buyer_dob::text, '') || '||' ||
        COALESCE(buyer_phone, '')
    ) AS customer_key,

    buyer_name,
    buyer_dob,
    buyer_gender,
    buyer_phone,
    buyer_email,
    buyer_address,
    customer_type,
    company_sale_name,
    branch_sale_name,

    -- Age calculation
    CASE
        WHEN buyer_dob IS NOT NULL
        THEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, buyer_dob))::integer
        ELSE NULL
    END AS buyer_age,

    -- Age group
    CASE
        WHEN buyer_dob IS NULL THEN 'Unknown'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, buyer_dob)) BETWEEN 0 AND 17 THEN '0-17'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, buyer_dob)) BETWEEN 18 AND 35 THEN '18-35'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, buyer_dob)) BETWEEN 36 AND 55 THEN '36-55'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, buyer_dob)) >= 56 THEN '56+'
        ELSE 'Unknown'
    END AS buyer_age_group,

    created_at,
    modified_at

FROM ranked
WHERE rn = 1
