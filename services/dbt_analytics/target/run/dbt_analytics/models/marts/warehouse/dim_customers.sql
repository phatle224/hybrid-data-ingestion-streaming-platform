
      
        
        
        delete from "insuranceWarehouse"."warehouse"."dim_customers" as DBT_INTERNAL_DEST
        where (customer_key) in (
            select distinct customer_key
            from "dim_customers__dbt_tmp010907400378" as DBT_INTERNAL_SOURCE
        );

    

    insert into "insuranceWarehouse"."warehouse"."dim_customers" ("customer_key", "customer_name", "customer_dob", "customer_gender", "customer_phone", "customer_email", "customer_address", "age", "age_group", "modified_at")
    (
        select "customer_key", "customer_name", "customer_dob", "customer_gender", "customer_phone", "customer_email", "customer_address", "age", "age_group", "modified_at"
        from "dim_customers__dbt_tmp010907400378"
    )
  