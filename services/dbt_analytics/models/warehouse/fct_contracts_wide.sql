{{ config(
    materialized='incremental',
    unique_key='contract_object_id'
) }}

WITH contracts AS (
    SELECT * FROM {{ ref('stg_contracts') }}
),

objects AS (
    SELECT * FROM {{ ref('int_contracts_deduped') }}
    
    {% if is_incremental() %}
        -- Only process contract objects that have been modified since the last dbt run
        WHERE modified_at > (SELECT COALESCE(MAX(modified_at), '1970-01-01'::timestamp) FROM {{ this }})
    {% endif %}
),

joined AS (
    SELECT
        o.contract_object_id,
        o.contract_id,
        c.contract_id_display,
        c.buyer_name,
        c.buyer_phone,
        c.buyer_email,
        c.buyer_dob,
        o.people_name AS insured_name,
        o.people_dob AS insured_dob,
        o.people_gender AS insured_gender,
        o.people_phone AS insured_phone,
        o.people_email AS insured_email,
        o.people_address AS insured_address,
        o.people_relationship,
        o.people_city_code,
        o.program_id,
        o.program_name,
        o.insurance_type,
        o.source_type,
        o.major_name,
        o.company_provider_name,
        o.start_date AS contract_start_date,
        o.end_date AS contract_end_date,
        o.fee_insurance,
        c.customer_type,
        c.amount AS contract_amount,
        c.commission AS contract_commission,
        c.amount_pay AS contract_amount_pay,
        c.company_sale_name,
        c.branch_sale_name,
        o.created_at,
        o.modified_at,
        
        -- Customer surrogate key for joining dim_customers
        MD5(COALESCE(o.people_name, '') || '_' || COALESCE(o.people_dob::text, '') || '_' || COALESCE(o.people_phone, '')) AS customer_key
    FROM objects o
    LEFT JOIN contracts c ON o.contract_id = c.contract_id
)

SELECT * FROM joined
