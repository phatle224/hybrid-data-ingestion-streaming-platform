

-- ============================================================================
-- Data Mart: dm_profiling_analysis (Phân Tích Hồ Sơ Bồi Thường)
-- Grain: 1 row = 1 claim
-- Design: JOIN fct_claims + Dimensions (Star Schema query pattern)
--         NO business logic computation here — all decoded from Dimensions
-- ============================================================================

WITH claims AS (
    SELECT * FROM "insuranceWarehouse"."warehouse"."fct_claims"

    
),

insured AS (
    SELECT * FROM "insuranceWarehouse"."warehouse"."dim_insured_person"
),

products AS (
    SELECT * FROM "insuranceWarehouse"."warehouse"."dim_product"
),

dates AS (
    SELECT * FROM "insuranceWarehouse"."warehouse"."dim_date"
)

SELECT
    -- ====== Identifiers ======
    cl.claim_id,
    cl.contract_id,
    cl.contract_object_id,

    -- ====== Claim Measures ======
    cl.amount_claim,
    cl.compensation_amount,
    cl.compensation_rate,
    cl.days_hospitalized,
    cl.days_from_contract_to_claim,

    -- ====== Time Attributes (from dim_date) ======
    cl.hospitalized_date,
    cl.hospital_discharge_date,
    cl.place_of_treatment AS clinics,
    d.full_date AS claim_start_date,
    cl.claim_month,
    cl.claim_year,
    d.quarter AS claim_quarter,
    d.day_name AS claim_day_name,

    -- ====== Insured Person Attributes (from dim_insured_person) ======
    ip.insured_name AS name,
    ip.insured_age AS age,
    ip.insured_age_group AS age_group,
    ip.insured_gender AS gender,
    ip.relationship_name,
    ip.city_name AS city,
    ip.insured_phone AS phone,
    ip.insured_email AS email,
    ip.insured_address AS address,

    -- ====== Diagnostic Attributes ======
    cl.treatment_type,
    cl.diagnostic,
    cl.common_diagnostic_category,

    -- ====== Product Attributes (from dim_product) ======
    p.insurance_type,
    p.insurance_category,
    p.major_name,
    p.program_id AS comp_prog_id,
    p.program_name AS comp_prog_name,
    p.company_provider_name,

    -- ====== Other ======
    cl.tpa_id,
    cl.claim_status,

    -- ====== Audit ======
    cl.created_at AS claim_created_at,
    cl.modified_at AS claim_modified_at,
    CURRENT_TIMESTAMP AS etl_loaded_at

FROM claims cl
LEFT JOIN insured ip ON cl.insured_person_key = ip.insured_person_key
LEFT JOIN products p ON cl.product_key = p.product_key
LEFT JOIN dates d ON cl.claim_date_key = d.date_key