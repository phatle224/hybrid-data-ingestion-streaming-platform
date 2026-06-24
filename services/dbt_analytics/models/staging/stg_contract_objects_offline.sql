WITH source AS (
    SELECT * FROM {{ source('staging_db', 'stgInsuranceContractObjectOffline') }}
),

cleaned AS (
    SELECT
        "contractObjectId" AS contract_object_id,
        "contractId" AS contract_id,
        "insuranceType" AS insurance_type,
        'offline' AS source_type,
        
        -- Use COALESCE to fallback to name/dob/phone/email if people fields are null
        TRIM(INITCAP(COALESCE("peopleName", "name"))) AS people_name,
        COALESCE("peopleDob", "dob"::date) AS people_dob,
        COALESCE("peopleGender", "gender") AS people_gender,
        
        -- Standardize phone numbers
        CASE 
            WHEN COALESCE("peoplePhone", "phone") LIKE '+84%' THEN '0' || SUBSTRING(COALESCE("peoplePhone", "phone") FROM 4)
            WHEN COALESCE("peoplePhone", "phone") LIKE '84%' THEN '0' || SUBSTRING(COALESCE("peoplePhone", "phone") FROM 3)
            ELSE TRIM(COALESCE("peoplePhone", "phone"))
        END AS people_phone,
        
        TRIM(LOWER(COALESCE("peopleEmail", "email"))) AS people_email,
        COALESCE("peopleAddress", "address") AS people_address,
        "majorName" AS major_name,
        "companyProviderName" AS company_provider_name,
        "contractObjectStartDate" AS start_date,
        "contractObjectEndDate" AS end_date,
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
