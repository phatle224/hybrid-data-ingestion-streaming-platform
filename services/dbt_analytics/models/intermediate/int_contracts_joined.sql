WITH unioned_objects AS (
    SELECT * FROM {{ ref('stg_contract_objects_vehicle') }}
    UNION ALL
    SELECT * FROM {{ ref('stg_contract_objects_travel') }}
    UNION ALL
    SELECT * FROM {{ ref('stg_contract_objects_moto') }}
    UNION ALL
    SELECT * FROM {{ ref('stg_contract_objects_social') }}
    UNION ALL
    SELECT * FROM {{ ref('stg_contract_objects_medical') }}
    UNION ALL
    SELECT * FROM {{ ref('stg_contract_objects_house') }}
    UNION ALL
    SELECT * FROM {{ ref('stg_contract_objects_health') }}
    UNION ALL
    SELECT * FROM {{ ref('stg_contract_objects_offline') }}
)

SELECT * FROM unioned_objects
