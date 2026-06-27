WITH source AS (
    SELECT * FROM {{ source('staging_db', 'stgInsuranceContractObjectMedicalInsurance') }}
),

cleaned AS (
    SELECT
        "contractObjectId" AS contract_object_id,
        "contractId" AS contract_id,
        'MEDICAL' AS insurance_type,
        'online' AS source_type,
        TRIM(INITCAP("peopleName")) AS people_name,
        "peopleDob" AS people_dob,
        "peopleGender" AS people_gender,
        
        -- Standardize phone numbers
        CASE 
            WHEN "peoplePhone" LIKE '+84%' THEN '0' || SUBSTRING("peoplePhone" FROM 4)
            WHEN "peoplePhone" LIKE '84%' THEN '0' || SUBSTRING("peoplePhone" FROM 3)
            ELSE TRIM("peoplePhone")
        END AS people_phone,
        
        TRIM(LOWER("peopleEmail")) AS people_email,
        "peopleAddress" AS people_address,
        "peopleRelationship" AS people_relationship,
        "peopleCityCode"::text AS people_city_code,
        "programId" AS program_id,
        "programName" AS program_name,
        "majorName" AS major_name,
        "companyProviderName" AS company_provider_name,
        "contractObjectStartDate" AS start_date,
        "contractObjectEndDate" AS end_date,
        "feeInsurance" AS fee_insurance,
        "createdAt" AS created_at,
        
        -- Resolve timestamp anomalies
        CASE 
            WHEN "modifiedAt" IS NULL THEN "createdAt"
            WHEN "modifiedAt" < "createdAt" THEN "createdAt"
            ELSE "modifiedAt"
        END AS modified_at
    FROM source
)

SELECT * FROM cleaned
