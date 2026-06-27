{{ config(
    materialized='table',
    schema='warehouse'
) }}

-- ============================================================================
-- Dimension: dim_date
-- Grain: 1 row = 1 ngày dương lịch
-- Source: Generated series (2020-01-01 → 2030-12-31)
-- ============================================================================

WITH date_spine AS (
    SELECT 
        d::date AS full_date
    FROM generate_series(
        '2020-01-01'::date,
        '2030-12-31'::date,
        '1 day'::interval
    ) AS d
)

SELECT
    -- Surrogate key (YYYYMMDD format)
    TO_CHAR(full_date, 'YYYYMMDD')::integer AS date_key,
    
    full_date,
    
    -- Day-level attributes
    EXTRACT(DOW FROM full_date)::integer AS day_of_week,          -- 0=Sun, 6=Sat
    CASE EXTRACT(DOW FROM full_date)
        WHEN 0 THEN 'Chủ Nhật'
        WHEN 1 THEN 'Thứ Hai'
        WHEN 2 THEN 'Thứ Ba'
        WHEN 3 THEN 'Thứ Tư'
        WHEN 4 THEN 'Thứ Năm'
        WHEN 5 THEN 'Thứ Sáu'
        WHEN 6 THEN 'Thứ Bảy'
    END AS day_name,
    EXTRACT(DAY FROM full_date)::integer AS day_of_month,
    
    -- Week-level
    EXTRACT(WEEK FROM full_date)::integer AS week_of_year,
    
    -- Month-level
    EXTRACT(MONTH FROM full_date)::integer AS month_number,
    CASE EXTRACT(MONTH FROM full_date)
        WHEN 1  THEN 'Tháng 1'
        WHEN 2  THEN 'Tháng 2'
        WHEN 3  THEN 'Tháng 3'
        WHEN 4  THEN 'Tháng 4'
        WHEN 5  THEN 'Tháng 5'
        WHEN 6  THEN 'Tháng 6'
        WHEN 7  THEN 'Tháng 7'
        WHEN 8  THEN 'Tháng 8'
        WHEN 9  THEN 'Tháng 9'
        WHEN 10 THEN 'Tháng 10'
        WHEN 11 THEN 'Tháng 11'
        WHEN 12 THEN 'Tháng 12'
    END AS month_name,
    
    -- Quarter & Year
    EXTRACT(QUARTER FROM full_date)::integer AS quarter,
    EXTRACT(YEAR FROM full_date)::integer AS year,
    
    -- Derived flags
    CASE WHEN EXTRACT(DOW FROM full_date) IN (0, 6) THEN TRUE ELSE FALSE END AS is_weekend,
    CASE WHEN full_date = (DATE_TRUNC('month', full_date) + INTERVAL '1 month' - INTERVAL '1 day')::date
         THEN TRUE ELSE FALSE END AS is_month_end

FROM date_spine
