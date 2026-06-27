{{ config(
    materialized='incremental',
    unique_key='contract_object_id'
) }}

-- ============================================================================
-- Fact: fct_contracts (Hợp Đồng Bảo Hiểm)
-- Grain: 1 row = 1 đối tượng bảo hiểm (contract object) duy nhất
-- Design: Slim fact with FK keys → Star Schema joins to Dimensions
-- Replaces: fct_contracts_wide.sql (Fat Table approach)
-- ============================================================================

WITH contracts AS (
    SELECT * FROM {{ ref('stg_contracts') }}
),

objects AS (
    SELECT * FROM {{ ref('int_contracts_deduped') }}

    {% if is_incremental() %}
        WHERE modified_at > (SELECT COALESCE(MAX(modified_at), '1970-01-01'::timestamp) FROM {{ this }})
    {% endif %}
)

SELECT
    -- ====== Natural Key ======
    o.contract_object_id,
    o.contract_id,

    -- ====== Dimension Foreign Keys (Star Schema) ======
    -- FK → dim_customer (người mua bảo hiểm)
    MD5(
        COALESCE(c.buyer_name, '') || '||' ||
        COALESCE(c.buyer_dob::text, '') || '||' ||
        COALESCE(c.buyer_phone, '')
    ) AS customer_key,

    -- FK → dim_insured_person (người được bảo hiểm)
    MD5(
        COALESCE(o.people_name, '') || '||' ||
        COALESCE(o.people_dob::text, '') || '||' ||
        COALESCE(o.people_phone, '')
    ) AS insured_person_key,

    -- FK → dim_product (sản phẩm bảo hiểm)
    MD5(
        COALESCE(o.insurance_type, '') || '||' ||
        COALESCE(o.major_name, '') || '||' ||
        COALESCE(o.program_name, '') || '||' ||
        COALESCE(o.company_provider_name, '')
    ) AS product_key,

    -- FK → dim_sales_channel (kênh bán hàng)
    MD5(
        COALESCE(c.company_sale_name, '') || '||' ||
        COALESCE(c.branch_sale_name, '')
    ) AS channel_key,

    -- FK → dim_date (ngày hiệu lực / kết thúc / tạo hợp đồng)
    TO_CHAR(o.start_date::date, 'YYYYMMDD')::integer AS start_date_key,
    TO_CHAR(o.end_date::date, 'YYYYMMDD')::integer AS end_date_key,
    TO_CHAR(o.created_at::date, 'YYYYMMDD')::integer AS created_date_key,

    -- ====== Measures (số liệu đo lường) ======
    o.fee_insurance,
    c.amount AS contract_amount,
    c.commission AS contract_commission,
    c.amount_pay AS contract_amount_pay,

    -- ====== Degenerate Dimensions (attributes quá chi tiết, không cần bảng riêng) ======
    o.source_type,
    o.insurance_type,
    c.contract_id_display,

    -- ====== Audit / Metadata ======
    o.created_at,
    o.modified_at,
    CURRENT_TIMESTAMP AS etl_loaded_at

FROM objects o
LEFT JOIN contracts c ON o.contract_id = c.contract_id
