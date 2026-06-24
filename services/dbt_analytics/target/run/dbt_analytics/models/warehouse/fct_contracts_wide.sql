
      
        
        
        delete from "insuranceWarehouse"."warehouse"."fct_contracts_wide" as DBT_INTERNAL_DEST
        where (contract_object_id) in (
            select distinct contract_object_id
            from "fct_contracts_wide__dbt_tmp015650929305" as DBT_INTERNAL_SOURCE
        );

    

    insert into "insuranceWarehouse"."warehouse"."fct_contracts_wide" ("contract_object_id", "contract_id", "contract_id_display", "buyer_name", "buyer_phone", "buyer_email", "buyer_dob", "insured_name", "insured_dob", "insured_gender", "insured_phone", "insured_email", "insured_address", "insurance_type", "source_type", "major_name", "company_provider_name", "contract_start_date", "contract_end_date", "fee_insurance", "contract_amount", "contract_commission", "contract_amount_pay", "company_sale_name", "branch_sale_name", "created_at", "modified_at", "customer_key")
    (
        select "contract_object_id", "contract_id", "contract_id_display", "buyer_name", "buyer_phone", "buyer_email", "buyer_dob", "insured_name", "insured_dob", "insured_gender", "insured_phone", "insured_email", "insured_address", "insurance_type", "source_type", "major_name", "company_provider_name", "contract_start_date", "contract_end_date", "fee_insurance", "contract_amount", "contract_commission", "contract_amount_pay", "company_sale_name", "branch_sale_name", "created_at", "modified_at", "customer_key"
        from "fct_contracts_wide__dbt_tmp015650929305"
    )
  