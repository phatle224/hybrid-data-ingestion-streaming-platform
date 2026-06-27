WITH ranked_contracts AS (
    SELECT 
        contract_object_id,
        contract_id,
        insurance_type,
        source_type,
        people_name,
        people_dob,
        people_gender,
        people_phone,
        people_email,
        people_address,
        people_relationship,
        people_city_code,
        program_id,
        program_name,
        major_name,
        company_provider_name,
        start_date,
        end_date,
        fee_insurance,
        created_at,
        modified_at,
        ROW_NUMBER() OVER (
            PARTITION BY 
                contract_id,
                people_name,
                major_name,
                company_provider_name,
                start_date,
                end_date,
                fee_insurance
            ORDER BY 
                CASE WHEN source_type = 'online' THEN 1 ELSE 2 END ASC, -- Online Wins!
                modified_at DESC                                      -- Mới nhất wins!
        ) as row_num
    FROM "insuranceWarehouse"."intermediate"."int_contracts_joined"
)

SELECT 
    contract_object_id,
    contract_id,
    insurance_type,
    source_type,
    people_name,
    people_dob,
    people_gender,
    people_phone,
    people_email,
    people_address,
    people_relationship,
    people_city_code,
    program_id,
    program_name,
    major_name,
    company_provider_name,
    start_date,
    end_date,
    fee_insurance,
    created_at,
    modified_at
FROM ranked_contracts 
WHERE row_num = 1