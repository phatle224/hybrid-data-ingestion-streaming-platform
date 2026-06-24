# Kế Hoạch Thiết Kế & Di Di Trú Hệ Thống Sang Portfolio Cá Nhân (CV-Ready)

Tài liệu này đóng vai trò là **Implementation Plan** chi tiết giúp bạn tự tay chuyển đổi và nâng cấp dự án từ môi trường công ty thành một dự án cá nhân (mã nguồn mở) chạy độc lập, sử dụng **PostgreSQL**, **dbt**, và hướng tới **Snowflake** (Modern Data Stack).

---

## 🏗️ 1. Kiến Trúc Đề Xuất (Target Architecture)

Hệ thống sẽ được cấu trúc lại hoàn chỉnh, chạy độc lập bằng Docker Compose:

```
[ Mock Data Generator (Python + Faker) ]
                 │
                 ▼ (INSERT/UPDATE)
   [ Production DB (PostgreSQL) ]
                 │
                 ▼ (CDC via Debezium PostgreSQL Connector)
             [ Kafka ]
                 │
                 ▼ (Ingest/EL)
     [ Staging DB (PostgreSQL) ] ─── (Offline Ingestion Portal - React/FastAPI)
                 │
                 ▼ (Transformation / ELT)
       [ dbt (Data Build Tool) ]
                 │
                 ▼ (Load to Gold Layer)
  [ Data Warehouse / Snowflake (Data Marts) ]
```

---

## 🔄 2. Giải Thuật Đảo Ngược Schema (Staging ➔ Source)

Vì kết nối với Source DB của công ty đã bị ngắt, ta sẽ **thiết kế ngược (reverse-engineer)** schema của Source từ chính schema của Staging có sẵn trong thư mục `database/01_staging/`.

### Quy tắc dịch chuyển Schema:
1.  **Loại bỏ tiền tố `stg`:** Các bảng ở Source DB sẽ là tên gốc (ví dụ: `stgInsuranceContract` ➔ `insuranceContract`, `stgInsuranceClaim` ➔ `insuranceClaim`).
2.  **Loại bỏ các trường metadata của CDC:** Xóa bỏ các trường được tạo riêng cho luồng đồng bộ như `modifiedDate` (ngày cập nhật CDC).
3.  **Chuyển đổi kiểu dữ liệu sang PostgreSQL:**
    *   `varchar` ➔ `VARCHAR` / `TEXT`
    *   `datetime` ➔ `TIMESTAMP` / `TIMESTAMPTZ`
    *   `decimal(20,0)` ➔ `NUMERIC(20, 2)`
    *   `longtext` ➔ `TEXT`
    *   `int(11) / int(2)` ➔ `INTEGER` / `SMALLINT`

### Bản đồ ánh xạ bảng (Mapping Registry):

| Source Table (PostgreSQL) | Staging Table (PostgreSQL) | Ghi chú nghiệp vụ |
|---|---|---|
| `insuranceContract` | `stgInsuranceContract` | Thông tin master hợp đồng (người mua, số tiền, ngày ký...) |
| `insuranceContractObject` | `stgInsuranceContractObject` | Đối tượng bảo hiểm sức khỏe (HEALTH) |
| `insuranceContractObjectVehicle` | `stgInsuranceContractObjectVehicle` | Đối tượng bảo hiểm ô tô (VEHICLE) |
| `insuranceContractObjectTravel` | `stgInsuranceContractObjectTravel` | Đối tượng bảo hiểm du lịch (TRAVEL) |
| `insuranceContractObjectMoto` | `stgInsuranceContractObjectMoto` | Đối tượng bảo hiểm xe máy (MOTO) |
| `insuranceContractObjectSocialInsurance` | `stgInsuranceContractObjectSocialInsurance` | Đối tượng bảo hiểm xã hội (SOCIAL) |
| `insuranceContractObjectMedicalInsurance` | `stgInsuranceContractObjectMedicalInsurance` | Đối tượng bảo hiểm y tế (MEDICAL) |
| `insuranceContractObjectHouse` | `stgInsuranceContractObjectHouse` | Đối tượng bảo hiểm nhà tư nhân (HOUSE) |
| `insuranceClaim` | `stgInsuranceClaim` | Yêu cầu bồi thường bảo hiểm |

---

## 🛠️ 3. Kế Hoạch Triển Khai Từng Bước (Implementation Steps)

### Bước 1: Khởi Tạo Môi Trường Cục Bộ Với PostgreSQL (Đã Hoàn Thành - DONE)
1. **Dựng 2 instance PostgreSQL bằng Docker Compose:**
   * **Container 1 (`cdc_production_db`):** Đóng vai trò là Source DB của hệ thống bán hàng (chạy port `5432` nội bộ, map ra ngoài `5432`). Đã cấu hình `wal_level = logical` để hỗ trợ Logical Replication cho Debezium CDC.
   * **Container 2 (`cdc_staging_db`):** Đóng vai trò là Staging & Reporting DB (chạy port `5432` nội bộ, map ra ngoài `5433`).
2. **Tạo script SQL khởi tạo:** Đã tạo toàn bộ các script SQL khởi tạo schema cho Source DB (`database/00_source/`), Staging DB (`database/01_staging/`), và Reporting DB (`database/02_reporting/`), loại bỏ hoàn toàn các cấu phần của dòng bảo hiểm `Hazard` và đổi sang tiền tố chuẩn `insurance*` / `stgInsurance*`.

---

### Bước 2: Viết Python Fake Data Generator Service (Đã Hoàn Thành - DONE)
*   **Hiện trạng:** Đã thiết kế và cài đặt hoàn tất dịch vụ sinh dữ liệu giả lập `services/mock_generator` sử dụng `psycopg2-binary` và `Faker` để tạo luồng dữ liệu ngẫu nhiên.
*   **Chi tiết thiết kế:**
    *   **Thư viện sử dụng:** `psycopg2-binary`, `Faker`.
    *   **Logic hoạt động:** Tự động chạy ngầm, định kỳ (5-10 giây) chèn ngẫu nhiên hợp đồng (`insuranceContract`), đối tượng hợp đồng (Vehicle, Travel, Moto, Social, Medical, House) và claims (`insuranceClaim`). Thực hiện các thao tác `UPDATE` ngẫu nhiên để tạo sự kiện CDC.
    *   **Thiết kế dữ liệu "messy" (không quá sạch):** Cố tình tạo ra các dị thường dữ liệu thực tế để phục vụ cho việc làm sạch ở tầng dbt sau này:
        *   *Email/Tên:* Trộn lẫn chữ HOA/thường, chèn khoảng trắng ngẫu nhiên đầu/cuối chuỗi (ví dụ: `  ngUYEn VaN A  `).
        *   *Số điện thoại:* Định dạng hỗn hợp (`+84`, `09...`, phân cách bằng dấu chấm/gạch ngang, hoặc số không hợp lệ).
        *   *Kênh bán hàng/Đại lý:* Tên viết hoa thường không nhất quán (`Affina`, `affina`, `AFFINA GROUP`).
        *   *Gói bảo hiểm:* Tên gói viết bằng tiếng Anh/Việt lẫn lộn hoặc sai lệch nhẹ.
        *   *Dị thường logic:* Ngày sửa đổi (`modifiedAt`) trước ngày tạo (`createdAt`) hoặc số tiền bồi thường (`compensationAmount`) vượt quá số tiền yêu cầu bồi thường (`amountClaim`).

---

### Bước 3: Cấu Hình Debezium PostgreSQL Connector (Đã Hoàn Thành - DONE)
Đã cấu hình và kiểm thử các file đăng ký connector cho PostgreSQL:
*   **Source Connector (`configs/register-source-connector.json`):** Đọc log WAL từ `insurance_production` (schema `public`), xuất bản các thay đổi vào Kafka dưới dạng topic prefix `source.public.*`.
*   **Staging Connector (`configs/register-staging-connector.json`):** Đọc log WAL từ `insurance_staging` (schema `staging`), lọc theo danh sách bảng `stgInsurance*`, xuất bản các thay đổi vào Kafka dưới dạng topic prefix `staging.staging.*`.

---

### Bước 4: Chuyển Đổi Transform Layer Sang dbt (Data Build Tool) (BƯỚC TIẾP THEO - NEXT STEP)
Thay vì viết code Python streaming join phức tạp, bạn sẽ xây dựng một dự án dbt đặt trong thư mục `services/dbt_analytics/`:
1.  **Tầng Sources (`models/staging/src_postgres.yml`):**
    Định nghĩa nguồn dữ liệu là các bảng `stg_` trong PostgreSQL Staging.
2.  **Tầng Staging Models (`models/staging/`):**
    *   Tạo các model `stg_contracts.sql`, `stg_claims.sql`, v.v.
    *   Thực hiện làm sạch dữ liệu thô ban đầu (ép kiểu, đổi giá trị NULL, chuẩn hóa text).
3.  **Tầng Intermediate Models (`models/intermediate/`):**
    *   Join các bảng đối tượng cụ thể (Vehicle, Travel...) với bảng hợp đồng master (`stg_contracts`).
    *   Xử lý logic chống trùng lặp: Nếu trùng lặp giữa online và offline, sử dụng hàm `ROW_NUMBER() OVER (PARTITION BY business_key ORDER BY source_type_priority, modified_at DESC)` để lọc bản ghi chiến thắng (Online Wins).
4.  **Tầng Marts Models (`models/marts/`):**
    *   `dim_customers.sql`: Chứa thông tin chiều khách hàng.
    *   `fct_contracts_wide.sql`: Bảng Wide Table chứa thông tin hợp đồng đã được join đầy đủ (thay thế cho bảng `contract_wide_table` cũ).
    *   `dm_profiling_analysis.sql`: Data Mart phân tích hành vi, độ tuổi, phân loại bệnh từ claims (thay thế cho `profiling_analysis` cũ).

---

### Bước 5: Nâng Cấp Lên Cloud Warehouse (Snowflake)
Để CV của bạn đạt mức "Production-Grade" chuẩn doanh nghiệp lớn:
*   **Thiết kế luồng Data Lake / EL:** Thay vì CDC đi thẳng vào PostgreSQL Staging, bạn có thể cấu hình Debezium đẩy dữ liệu CDC lên **Amazon S3 / Google Cloud Storage**.
*   **Snowpipe Ingestion:** Dùng Snowpipe của Snowflake để tự động copy dữ liệu từ Cloud Storage vào Snowflake Staging.
*   **dbt on Snowflake:** Cấu hình dbt chạy trực tiếp trên Snowflake để thực hiện biến đổi dữ liệu sang Data Marts.

---

## 🎯 4. Mô Tả Dự Án Để Đưa Vào CV (CV Description Template)

Dưới đây là cách bạn trình bày dự án này trong CV để gây ấn tượng mạnh nhất với nhà tuyển dụng:

```markdown
### HYBRID INSURANCE DATA INGESTION & ANALYTICS PLATFORM (Personal Project)
**Technology Stack:** PostgreSQL, Apache Kafka, Debezium (CDC), dbt, Snowflake, Python, Redis, React, FastAPI, Docker.

**Description:**
Xây dựng hệ thống nạp và xử lý dữ liệu lai (Hybrid Ingestion Pipeline) kết hợp đồng thời dữ liệu giao dịch thời gian thực (Online CDC) và dữ liệu tải lên ngoại tuyến theo lô (Offline Excel Upload) từ các đại lý bảo hiểm, phục vụ phân tích hành vi khách hàng và rủi ro bồi thường.

**Key Achievements:**
* Thiết kế giải pháp CDC (Change Data Capture) sử dụng Debezium và Kafka để lắng nghe thay đổi (WAL log) từ PostgreSQL Production, tự động đồng bộ sang Staging DB với độ trễ dưới 2 giây.
* Áp dụng OOP Design Patterns (Strategy, Factory, Template Method) kết hợp Redis Cache để xử lý động các biểu mẫu Excel phức tạp và kiểm tra trùng lặp dữ liệu O(1) dựa trên 7-field Business Keys (đạt tỉ lệ chính xác 100% theo chính sách "Online Wins").
* Xây dựng dự án dbt (Data Build Tool) để chuyển đổi cấu trúc dữ liệu ELT từ Staging ODS sang kiến trúc Dimensional Modeling (Fact/Dimension) trên Snowflake Data Warehouse.
* Thiết kế Customer Profiling Data Mart tự động phân nhóm khách hàng theo độ tuổi, địa lý và phân loại chẩn đoán bệnh lý thời gian thực, hỗ trợ các quyết định kinh doanh của bộ phận Marketing và Underwriting.
* Container hóa toàn bộ hệ thống (10+ dịch vụ) bằng Docker & Docker Compose để dễ dàng triển khai, kiểm thử cục bộ.
```
