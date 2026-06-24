{{ config(
    materialized='incremental',
    unique_key='claim_id'
) }}

WITH contracts AS (
    SELECT * FROM {{ ref('fct_contracts_wide') }}
),

customers AS (
    SELECT * FROM {{ ref('dim_customers') }}
),

claims AS (
    SELECT * FROM {{ ref('stg_claims') }}
    
    {% if is_incremental() %}
        -- Only process claims that have been modified since the last dbt run
        WHERE modified_at > (SELECT COALESCE(MAX(claim_modified_at), '1970-01-01'::timestamp) FROM {{ this }})
    {% endif %}
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
        
        cl.place_of_treatment,
        cl.diagnostic,
        
        -- Diagnostic categorization (Standard logic)
        CASE 
            WHEN cl.diagnostic ILIKE '%cancer%' OR cl.diagnostic ILIKE '%ung thư%' THEN 'Cancer / Oncology'
            WHEN cl.diagnostic ILIKE '%flu%' OR cl.diagnostic ILIKE '%cúm%' OR cl.diagnostic ILIKE '%sốt%' THEN 'Infectious Disease / Flu'
            WHEN cl.diagnostic ILIKE '%heart%' OR cl.diagnostic ILIKE '%tim%' THEN 'Cardiovascular'
            WHEN cl.diagnostic ILIKE '%fracture%' OR cl.diagnostic ILIKE '%gãy%' OR cl.diagnostic ILIKE '%tai nạn%' THEN 'Injury / Trauma'
            WHEN cl.diagnostic IS NULL THEN 'Unknown'
            ELSE 'Other General Treatment'
        END AS common_diagnostic_category,
        
        -- Days from contract effect to claim
        CASE 
            WHEN cl.hospitalized_date IS NOT NULL AND co.contract_start_date IS NOT NULL 
            THEN cl.hospitalized_date::date - co.contract_start_date::date
            ELSE NULL
        END AS days_from_contract_to_claim,
        
        -- Demographics from dimension customer
        cu.customer_name AS name,
        cu.customer_phone AS phone,
        cu.customer_email AS email,
        cu.customer_address AS address,
        cu.customer_gender AS gender,
        cu.age,
        cu.age_group,
        
        -- Company / Program info
        co.company_provider_name AS comp_prog_name,
        co.source_type,
        cl.created_at AS claim_created_at,
        cl.modified_at AS claim_modified_at
    FROM claims cl
    INNER JOIN contracts co ON cl.contract_object_id = co.contract_object_id
    LEFT JOIN customers cu ON co.customer_key = cu.customer_key
)

SELECT * FROM joined
