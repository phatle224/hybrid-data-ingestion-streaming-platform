# Tài Liệu Logic Biến Đổi Dữ Liệu Với dbt (dbt Transformation Logic)

Tài liệu này cung cấp cái nhìn tổng quan và chi tiết về luồng biến đổi dữ liệu (Transformation Layer) từ lớp dữ liệu thô **Staging (ODS)** sang lớp báo cáo **Reporting (Data Marts)** bằng cách sử dụng **dbt (Data Build Tool)**.

---

## 🏗️ 1. Mô Hình Luồng Dữ Liệu ELT

Trong kiến trúc Modern Data Stack, quá trình trích xuất và nạp (EL) được thực hiện thời gian thực qua Kafka CDC để đưa vào schema `staging`. dbt sẽ chịu trách nhiệm toàn bộ phần biến đổi dữ liệu (T) sau đó:

```
┌────────────────────────┐       ┌──────────────────────────────────────┐       ┌────────────────────────┐
│      STAGING ODS       │       │             DBT LAYER                │       │    REPORTING LAYER     │
│    (Raw Schemas)       │       │    (Staging ➔ Intermediate ➔ Marts)  │       │     (Data Marts)       │
├────────────────────────┤       ├──────────────────────────────────────┤       ├────────────────────────┤
│ • stgInsuranceContract │ ────► │ • Làm sạch văn bản, chuẩn hóa phone  │ ────► │ • dim_customers        │
│ • stgInsuranceClaim    │       │ • Khử trùng lặp (Online Wins)        │       │ • fct_contracts_wide   │
│ • stgInsuranceObject*  │       │ • Ghép bảng (Join Master/Objects)    │       │ • dm_profiling_analysis│
└────────────────────────┘       └──────────────────────────────────────┘       └────────────────────────┘
```

---

## 📂 2. Cấu Trúc Dự Án dbt Đề Xuất

Dự án dbt sẽ được khởi tạo tại `services/dbt_analytics/` với cấu trúc chuẩn như sau:

```
services/dbt_analytics/
├── dbt_project.yml          # Cấu hình dự án dbt
├── profiles.yml             # Cấu hình kết nối tới PostgreSQL/Snowflake
├── models/
│   ├── staging/             # Lớp 1: Khai báo nguồn và làm sạch thô ban đầu (1:1 với Staging DB)
│   │   ├── src_postgres.yml # Khai báo source tables trong schema staging
│   │   ├── stg_contracts.sql
│   │   ├── stg_claims.sql
│   │   └── stg_contract_objects.sql
│   │
│   ├── intermediate/        # Lớp 2: Ghép nối nghiệp vụ & Khử trùng trùng lặp (Deduplication)
│   │   ├── int_contracts_joined.sql  # Join Master Contract với các đối tượng cụ thể (Vehicle, Moto...)
│   │   └── int_contracts_deduped.sql # Thực hiện logic xử lý trùng lặp "Online Wins"
│   │
│   └── marts/               # Lớp 3: Thiết kế Fact & Dimensions (Dimensional Modeling)
│       ├── dim_customers.sql
│       ├── fct_contracts_wide.sql
│       └── dm_profiling_analysis.sql
```

---

## 🧹 3. Các Quy Tắc Làm Sạch Dữ Liệu (Staging Models)

Lớp `models/staging/` thực hiện ánh xạ trực tiếp từ các bảng nguồn và áp dụng các hàm SQL để xử lý dữ liệu "bẩn" (messy data) được sinh ra từ Mock Generator hoặc quá trình nhập liệu Excel thủ công:

### A. Chuẩn hóa Text & Email
*   **Tên khách hàng / Đối tác:** Sử dụng hàm `TRIM` loại bỏ khoảng trắng thừa và chuẩn hóa sang viết hoa/thường nhất quán.
    ```sql
    TRIM(INITCAP("peopleName")) AS customer_name
    ```
*   **Email:** Chuyển toàn bộ về chữ thường, cắt khoảng trắng.
    ```sql
    TRIM(LOWER(email)) AS clean_email
    ```

### B. Chuẩn hóa Số điện thoại (Phone Numbers)
*   Chuẩn hóa các đầu số khác nhau (`+84`, `84`, `09...`) về một định dạng thống nhất (ví dụ: định dạng quốc tế `+84...` hoặc định dạng nội địa bắt đầu bằng `0`).
    ```sql
    -- Ví dụ chuẩn hóa số điện thoại về định dạng bắt đầu bằng '0'
    CASE 
      WHEN phone LIKE '+84%' THEN '0' || SUBSTRING(phone FROM 4)
      WHEN phone LIKE '84%' THEN '0' || SUBSTRING(phone FROM 3)
      ELSE TRIM(phone)
    END AS clean_phone
    ```

### C. Xử lý Dị Thường Thời Gian & Logic Nghiệp Vụ
*   **Lỗi logic ngày tháng:** Nếu phát hiện `modifiedAt` trước `createdAt` do lỗi hệ thống nguồn:
    ```sql
    CASE 
      WHEN "modifiedAt" < "createdAt" THEN "createdAt"
      ELSE "modifiedAt"
    END AS modified_at
    ```
*   **Null Handling:** Ép các trường ghi chú hoặc tài liệu bị trống (`NULL`) về giá trị mặc định để tránh lỗi khi báo cáo.
    ```sql
    COALESCE(note, 'No note provided') AS note
    ```

---

## 🔄 4. Logic Khử Trùng Lặp & Quy Tắc "Online Wins" (Intermediate Models)

Đây là **chìa khóa cốt lõi** để xử lý bài toán dữ liệu lai (Hybrid Data Ingestion) – kết hợp giữa CDC thời gian thực (Online) và Tải file Excel thủ công (Offline):

### A. Business Key 7 thành phần (7-field Business Key)
Để xác định hai hợp đồng từ hai nguồn khác nhau có thực chất là một hay không, hệ thống dựa vào Business Key gồm 7 trường nghiệp vụ:
1.  `contractId` hoặc `contractObjectId` (Mã định danh)
2.  `peopleName` (Tên người được bảo hiểm)
3.  `majorName` (Loại nghiệp vụ bảo hiểm)
4.  `companyProviderName` (Nhà bảo hiểm cung cấp)
5.  `contractObjectStartDate` (Ngày bắt đầu hiệu lực)
6.  `contractObjectEndDate` (Ngày kết thúc hiệu lực)
7.  `feeInsurance` (Phí bảo hiểm)

### B. Logic ưu tiên "Online Wins" (Online Priority)
Nếu xảy ra trùng lặp Business Key giữa bản ghi **Online (CDC)** và **Offline (Excel Upload)**:
*   Bản ghi **Online (CDC)** được cấu hình có độ ưu tiên cao nhất (`source_type_priority = 1`).
*   Bản ghi **Offline (Excel)** có độ ưu tiên thấp hơn (`source_type_priority = 2`).
*   Nếu cùng một nguồn, bản ghi có ngày sửa đổi muộn nhất (`modifiedAt` DESC) sẽ chiến thắng.

### C. Cú pháp dbt SQL ứng dụng `ROW_NUMBER()`:
```sql
-- models/intermediate/int_contracts_deduped.sql
WITH ranked_contracts AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (
            PARTITION BY 
                contract_id,
                customer_name,
                major_name,
                company_provider_name,
                start_date,
                end_date,
                fee_insurance
            ORDER BY 
                CASE WHEN source_type = 'online' THEN 1 ELSE 2 END ASC, -- Online Wins
                modified_at DESC                                      -- Mới nhất wins
        ) as row_num
    FROM {{ ref('int_contracts_joined') }}
)

SELECT * 
FROM ranked_contracts 
WHERE row_num = 1
```

---

## 📊 5. Cấu Trúc Lớp Data Marts (Reporting Models)

Sau khi dữ liệu đã được làm sạch và khử trùng lặp ở lớp Intermediate, dbt sẽ tổng hợp thành các mô hình phân tích tối ưu ở lớp Marts:

### 1. `dim_customers` (Bảng chiều khách hàng)
*   **Nội dung:** Tổng hợp thông tin duy nhất của khách hàng dựa trên định danh cá nhân hoặc tổ chức.
*   **Ứng dụng:** Phân tích chân dung khách hàng (Age, Gender, Location).

### 2. `fct_contracts_wide` (Bảng Wide Table hợp đồng)
*   **Nội dung:** Join phẳng toàn bộ thông tin từ hợp đồng master (`stg_contracts`), đối tượng bảo hiểm cụ thể, và thông tin làm sạch.
*   **Mục đích:** Thay thế hoàn toàn bảng rộng cũ, hỗ trợ các truy vấn BI/Dashboard tốc độ cao mà không cần thực hiện nhiều phép JOIN phức tạp ở runtime.

### 3. `dm_profiling_analysis` (Bảng Mart phân tích hồ sơ rủi ro claims)
*   **Nội dung:** Kết hợp dữ liệu hợp đồng đã khử trùng và dữ liệu claim (`stg_claims`).
*   **Chỉ số tính toán sẵn (Pre-calculated metrics):**
    *   Tỷ lệ bồi thường: `compensationAmount / amountClaim AS compensation_rate`
    *   Thời gian từ lúc mua hợp đồng đến khi xảy ra sự cố: `claim_date - contract_start_date AS days_to_claim`
    *   Nhóm tuổi của khách hàng: `age_group` (dưới 18, 18-35, 36-50, trên 50)
    *   Phân loại bệnh lý: `common_diagnostic_category` (Dịch từ diagnostic sang nhóm bệnh phổ biến)
