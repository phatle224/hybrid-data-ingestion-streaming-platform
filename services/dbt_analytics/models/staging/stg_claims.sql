WITH source AS (
    SELECT * FROM {{ source('staging_db', 'stgInsuranceClaim') }}
),

cleaned AS (
    SELECT
        "id" AS claim_id,
        "contractId" AS contract_id,
        "contractObjectId" AS contract_object_id,
        "amountClaim" AS amount_claim,
        "compensationAmount" AS compensation_amount,
        COALESCE("note", 'No note') AS note,
        "claimType" AS claim_type,
        "hospitalizedDate" AS hospitalized_date,
        "hospitalDischargeDate" AS hospital_discharge_date,
        "placeOfTreatment" AS place_of_treatment,
        TRIM("diagnostic") AS diagnostic,
        TRIM(INITCAP("name")) AS claimant_name,
        
        -- Standardize phone numbers
        CASE 
            WHEN "phone" LIKE '+84%' THEN '0' || SUBSTRING("phone" FROM 4)
            WHEN "phone" LIKE '84%' THEN '0' || SUBSTRING("phone" FROM 3)
            ELSE TRIM("phone")
        END AS claimant_phone,
        
        TRIM(LOWER("email")) AS claimant_email,
        "status" AS status,
        "tpaId" AS tpa_id,
        "createdAt" AS created_at,
        
        -- Resolve timestamp anomalies
        CASE 
            WHEN "modifiedAt" < "createdAt" THEN "createdAt"
            ELSE "modifiedAt"
        END AS modified_at
    FROM source
)

SELECT * FROM cleaned
