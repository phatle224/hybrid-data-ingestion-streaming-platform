WITH source AS (
    SELECT * FROM {{ source('staging_db', 'stgInsuranceContractObjectMoto') }}
),

cleaned AS (
    SELECT
        "id" AS contract_object_id,
        "contractId" AS contract_id,
        'MOTO' AS insurance_type,
        'online' AS source_type,
        TRIM(INITCAP("name")) AS people_name,
        "dob" AS people_dob,
        "gender" AS people_gender,
        
        -- Standardize phone numbers
        CASE 
            WHEN "phone" LIKE '+84%' THEN '0' || SUBSTRING("phone" FROM 4)
            WHEN "phone" LIKE '84%' THEN '0' || SUBSTRING("phone" FROM 3)
            ELSE TRIM("phone")
        END AS people_phone,
        
        TRIM(LOWER("email")) AS people_email,
        "address" AS people_address,
        "majorName" AS major_name,
        "companyProviderName" AS company_provider_name,
        "startDate" AS start_date,
        "endDate" AS end_date,
        "feeInsurance" AS fee_insurance,
        "createdAt" AS created_at,
        
        -- Resolve timestamp anomalies
        CASE 
            WHEN "modifiedAt" < "createdAt" THEN "createdAt"
            ELSE "modifiedAt"
        END AS modified_at
    FROM source
)

SELECT * FROM cleaned
