WITH source AS (
    SELECT * FROM "insuranceWarehouse"."staging"."stgInsuranceContractObjectHouse"
),

cleaned AS (
    SELECT
        "id" AS contract_object_id,
        "contractId" AS contract_id,
        'HOUSE' AS insurance_type,
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
        NULL::integer AS people_relationship,
        "cityCode"::text AS people_city_code,
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