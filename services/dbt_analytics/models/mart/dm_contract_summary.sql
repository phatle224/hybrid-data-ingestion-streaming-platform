{{ config(
    materialized='incremental',
    unique_key='contract_object_id'
) }}

-- ============================================================================
-- Data Mart: dm_contract_summary (Tổng Hợp Hợp Đồng Bảo Hiểm)
-- Grain: 1 row = 1 contract object (hợp đồng bảo hiểm chi tiết)
-- Purpose: Phân tích hợp đồng theo loại sản phẩm, nhà cung cấp, kênh bán hàng,
--          khu vực địa lý, thời gian — sẵn sàng cho BI dashboards.
-- ============================================================================

WITH contracts AS (
    SELECT * FROM {{ ref('fct_contracts') }}

    {% if is_incremental() %}
        WHERE modified_at > (SELECT COALESCE(MAX(contract_modified_at), '1970-01-01'::timestamp) FROM {{ this }})
    {% endif %}
),

customers AS (
    SELECT * FROM {{ ref('dim_customer') }}
),

insured AS (
    SELECT * FROM {{ ref('dim_insured_person') }}
),

products AS (
    SELECT * FROM {{ ref('dim_product') }}
),

channels AS (
    SELECT * FROM {{ ref('dim_sales_channel') }}
),

dates AS (
    SELECT * FROM {{ ref('dim_date') }}
)

SELECT
    -- ====== Identifiers ======
    co.contract_object_id,
    co.contract_id,
    co.contract_id_display,

    -- ====== Customer Info (Buyer) ======
    cust.buyer_name,
    cust.buyer_phone,
    cust.buyer_email,
    cust.customer_type,
    cust.buyer_age_group,

    -- ====== Insured Person Info ======
    ip.insured_name,
    ip.insured_age,
    ip.insured_age_group,
    ip.insured_gender,
    ip.relationship_name,
    ip.city_name,

    -- ====== Product Info ======
    p.insurance_type,
    p.insurance_category,
    p.major_name,
    p.program_name,
    p.company_provider_name,

    -- ====== Sales Channel Info ======
    ch.company_sale_name,
    ch.branch_sale_name,

    -- ====== Time Info (contract start date) ======
    d.full_date AS contract_start_date,
    d.month_name AS contract_month,
    d.quarter AS contract_quarter,
    d.year AS contract_year,

    -- ====== Measures ======
    co.fee_insurance,
    co.contract_amount,
    co.contract_commission,
    co.contract_amount_pay,

    -- ====== Source ======
    co.source_type,

    -- ====== Audit ======
    co.created_at AS contract_created_at,
    co.modified_at AS contract_modified_at,
    CURRENT_TIMESTAMP AS etl_loaded_at

FROM contracts co
LEFT JOIN customers cust ON co.customer_key = cust.customer_key
LEFT JOIN insured ip ON co.insured_person_key = ip.insured_person_key
LEFT JOIN products p ON co.product_key = p.product_key
LEFT JOIN channels ch ON co.channel_key = ch.channel_key
LEFT JOIN dates d ON co.start_date_key = d.date_key
