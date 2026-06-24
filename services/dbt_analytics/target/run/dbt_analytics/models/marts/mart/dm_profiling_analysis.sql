
      
        
        
        delete from "insuranceWarehouse"."mart"."dm_profiling_analysis" as DBT_INTERNAL_DEST
        where (claim_id) in (
            select distinct claim_id
            from "dm_profiling_analysis__dbt_tmp010907668808" as DBT_INTERNAL_SOURCE
        );

    

    insert into "insuranceWarehouse"."mart"."dm_profiling_analysis" ("claim_id", "contract_id", "contract_object_id", "amount_claim", "compensation_amount", "compensation_rate", "hospitalized_date", "hospital_discharge_date", "days_hospitalized", "place_of_treatment", "diagnostic", "common_diagnostic_category", "days_from_contract_to_claim", "name", "phone", "email", "address", "gender", "age", "age_group", "comp_prog_name", "source_type", "claim_created_at", "claim_modified_at")
    (
        select "claim_id", "contract_id", "contract_object_id", "amount_claim", "compensation_amount", "compensation_rate", "hospitalized_date", "hospital_discharge_date", "days_hospitalized", "place_of_treatment", "diagnostic", "common_diagnostic_category", "days_from_contract_to_claim", "name", "phone", "email", "address", "gender", "age", "age_group", "comp_prog_name", "source_type", "claim_created_at", "claim_modified_at"
        from "dm_profiling_analysis__dbt_tmp010907668808"
    )
  