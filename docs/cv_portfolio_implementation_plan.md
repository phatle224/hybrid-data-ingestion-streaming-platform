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
1.  **Loại bỏ tiền tố `stg`:** Các bảng ở Source DB sẽ là tên gốc (ví dụ: `stgContract` ➔ `contract`, `stgClaim` ➔ `claim`).
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
| `contract` | `stgContract` | Thông tin master hợp đồng (người mua, số tiền, ngày ký...) |
| `contract_object` | `stgContractObject` | Đối tượng bảo hiểm sức khỏe (HEALTH) |
| `contract_object_vehicle` | `stgContractObjectVehicle` | Đối tượng bảo hiểm ô tô (VEHICLE) |
| `contract_object_travel` | `stgContractObjectTravel` | Đối tượng bảo hiểm du lịch (TRAVEL) |
| `contract_object_moto` | `stgContractObjectMoto` | Đối tượng bảo hiểm xe máy (MOTO) |
| `contract_object_social_insurance` | `stgContractObjectSocialInsurance` | Đối tượng bảo hiểm xã hội (SOCIAL) |
| `contract_object_medical_insurance` | `stgContractObjectMedicalInsurance` | Đối tượng bảo hiểm y tế (MEDICAL) |
| `claim` | `stgClaim` | Yêu cầu bồi thường bảo hiểm |

---

## 🛠️ 3. Kế Hoạch Triển Khai Từng Bước (Implementation Steps)

### Bước 1: Khởi Tạo Môi Trường Cục Bộ Với PostgreSQL
1. Dựng 2 instance PostgreSQL bằng Docker Compose:
   * **Container 1:** `production_db` (Port 5432) - DB chính của hệ thống bán hàng. Cần cấu hình `wal_level = logical` để Debezium có thể cào log CDC qua cơ chế Logical Replication của Postgres.
   * **Container 2:** `staging_db` (Port 5433) - DB trung gian nhận dữ liệu CDC và offline portal.
2. Tạo script SQL khởi tạo schema cho `production_db` bằng cách áp dụng quy tắc đảo ngược ở mục 2.

---

### Bước 2: Viết Python Fake Data Generator Service
Tạo một service Python nhỏ (`services/mock_generator`) chạy ngầm trong Docker:
*   **Thư viện sử dụng:** `psycopg2-binary`, `Faker`.
*   **Logic hoạt động:**
    1. Chạy một vòng lặp vô hạn (với thời gian chờ ngẫu nhiên từ 5-10 giây).
    2. Mỗi vòng lặp, sinh ngẫu nhiên một hợp đồng mới (`contract`), chọn ngẫu nhiên loại bảo hiểm (Health, Vehicle, Travel...) để chèn vào bảng đối tượng tương ứng.
    3. Ngẫu nhiên sinh sự kiện yêu cầu bồi thường (`claim`) cho các hợp đồng đã có hiệu lực.
    4. Thỉnh thoảng chạy lệnh `UPDATE` cập nhật trạng thái hợp đồng hoặc số tiền claims để tạo event cập nhật cho CDC.

---

### Bước 3: Cấu Hình Debezium PostgreSQL Connector
Vì chuyển từ MySQL sang PostgreSQL, ta cần đổi connector của Debezium:
*   Tạo file cấu hình `register-postgres-source.json`.
*   Sử dụng lớp connector `"io.debezium.connector.postgresql.PostgresConnector"`.
*   Cấu hình plugin đồng bộ (thường dùng `pgoutput` có sẵn trong Postgres).
*   Đăng ký connector thông qua API của Debezium Connect (Port 8083).

---

### Bước 4: Chuyển Đổi Transform Layer Sang dbt (Data Build Tool)
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
