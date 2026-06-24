WITH distinct_customers AS (
    SELECT DISTINCT
        people_name AS customer_name,
        people_dob AS customer_dob,
        people_gender AS customer_gender,
        people_phone AS customer_phone,
        people_email AS customer_email,
        people_address AS customer_address
    FROM {{ ref('int_contracts_deduped') }}
    WHERE people_name IS NOT NULL
)

SELECT
    MD5(COALESCE(customer_name, '') || '_' || COALESCE(customer_dob::text, '') || '_' || COALESCE(customer_phone, '')) AS customer_key,
    customer_name,
    customer_dob,
    customer_gender,
    customer_phone,
    customer_email,
    customer_address,
    -- Calculate customer age groups
    EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM customer_dob) AS age,
    CASE 
        WHEN EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM customer_dob) < 18 THEN 'Under 18'
        WHEN EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM customer_dob) BETWEEN 18 AND 35 THEN '18-35'
        WHEN EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM customer_dob) BETWEEN 36 AND 50 THEN '36-50'
        ELSE 'Over 50'
    END AS age_group
FROM distinct_customers
