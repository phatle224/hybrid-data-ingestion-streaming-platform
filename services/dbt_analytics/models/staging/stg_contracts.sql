WITH source AS (
    SELECT * FROM {{ source('staging_db', 'stgInsuranceContract') }}
),

cleaned AS (
    SELECT
        "contractId" AS contract_id,
        "contractIdDisplay" AS contract_id_display,
        TRIM(INITCAP("name")) AS buyer_name,
        "dob" AS buyer_dob,
        "gender" AS buyer_gender,
        
        -- Standardize phone numbers
        CASE 
            WHEN "phone" LIKE '+84%' THEN '0' || SUBSTRING("phone" FROM 4)
            WHEN "phone" LIKE '84%' THEN '0' || SUBSTRING("phone" FROM 3)
            ELSE TRIM("phone")
        END AS buyer_phone,
        
        TRIM(LOWER("email")) AS buyer_email,
        "address" AS buyer_address,
        "contractType" AS contract_type,
        "companySaleName" AS company_sale_name,
        "branchSaleName" AS branch_sale_name,
        "contractStartDate" AS contract_start_date,
        "contractEndDate" AS contract_end_date,
        "contractObjectType" AS contract_object_type,
        "amount" AS amount,
        "commission" AS commission,
        "amountPay" AS amount_pay,
        "source" AS source,
        "createdAt" AS created_at,
        
        -- Resolve timestamp anomalies
        CASE 
            WHEN "modifiedAt" < "createdAt" THEN "createdAt"
            ELSE "modifiedAt"
        END AS modified_at
    FROM source
)

SELECT * FROM cleaned
