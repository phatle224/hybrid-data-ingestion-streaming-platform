# Đề Xuất Thiết Kế Lại Data Warehouse — Dimensional Modeling Plan

> **Ngày lập:** 2026-06-28  
> **Phiên bản:** v1.0  
> **Trạng thái:** Đề xuất (Pending Review)

---

## 1. Phân Tích Hiện Trạng & Vấn Đề

### 1.1. Cấu Trúc Hiện Tại

```
staging/
  stg_contracts.sql
  stg_contract_objects_health.sql
  stg_contract_objects_vehicle.sql
  stg_contract_objects_travel.sql
  stg_contract_objects_moto.sql
  stg_contract_objects_social.sql
  stg_contract_objects_medical.sql
  stg_contract_objects_house.sql
  stg_contract_objects_offline.sql
  stg_claims.sql

intermediate/
  int_contracts_joined.sql       ← UNION ALL 8 loại đối tượng
  int_contracts_deduped.sql      ← Dedup logic (Online Wins)

warehouse/
  dim_customers.sql              ← 1 Dimension
  fct_contracts_wide.sql         ← 1 Fat Fact (Wide Table)

mart/
  dm_profiling_analysis.sql      ← 1 Data Mart
```

### 1.2. Vấn Đề Tồn Tại

| # | Vấn Đề | Tác Động |
|---|---|---|
| **1** | `fct_contracts_wide.sql` là một **Wide/Fat Fact Table** — chứa hầu hết tất cả các cột, bao gồm cả thông tin người mua (buyer) và người được bảo hiểm (insured) trộn lẫn nhau. | Không phân tách được thực thể nghiệp vụ. JOIN tốn kém và khó mở rộng. |
| **2** | Chỉ có **1 Dimension duy nhất** (`dim_customers`). Thiếu hoàn toàn các dimension: Sản phẩm, Nhà bảo hiểm, Thời gian, Kênh bán hàng. | BI/báo cáo không thể phân tích theo nhiều chiều đánh giá. |
| **3** | `dim_customers` sử dụng `DISTINCT` trực tiếp từ `int_contracts_deduped` → **Khách hàng không có lịch sử thay đổi** (Không hỗ trợ SCD). | Không phân biệt được khách hàng cá nhân vs doanh nghiệp, không theo dõi thay đổi thông tin. |
| **4** | Business Logic như phân nhóm tuổi (age_group), tên tỉnh thành (city mapping), phân loại bệnh án (diagnostic category) được **viết thẳng vào Mart** (`dm_profiling_analysis.sql`). | Logic bị lặp lại, khó bảo trì, không tái sử dụng được. |
| **5** | Không có `dim_date`. Các phân tích theo thời gian phải dùng `EXTRACT(MONTH/YEAR)` trực tiếp trong query. | Không hỗ trợ phân tích theo quý, tuần, ngày trong tuần, ngày lễ... |
| **6** | `fct_contracts_wide` không phân tách thành **nhiều Fact Tables** theo grain (mức độ chi tiết) khác nhau. | Một claim có thể join nhiều hợp đồng, gây ra fan-out. Aggregation bị sai. |

---

## 2. Kiến Trúc Đề Xuất (Target Architecture)

### 2.1. Mô Hình Dữ Liệu — Star Schema / Constellation

```
                    ┌─────────────────┐
                    │   dim_date      │
                    │  (date_key PK)  │
                    └────────┬────────┘
                             │
  ┌──────────────┐           │           ┌──────────────────┐
  │ dim_customer │           │           │  dim_product     │
  │(customer_key)│           │           │ (product_key PK) │
  └──────┬───────┘           │           └────────┬─────────┘
         │                   │                    │
         │          ┌────────▼──────────┐         │
         └──────────►  fct_contracts   ◄──────────┘
                    │  (grain: 1 row =  │
                    │   1 hợp đồng đối  │
                    │   tượng BH)       │
                    └────────┬──────────┘
                             │
         ┌───────────────────┘───────────────────┐
         │                                        │
┌────────▼────────┐                   ┌───────────▼──────────┐
│  fct_claims     │                   │  dim_sales_channel   │
│ (grain: 1 row = │                   │  (channel_key PK)    │
│  1 claim)       │                   └──────────────────────┘
└─────────────────┘
```

### 2.2. Nguyên Tắc Thiết Kế

1. **Tách biệt Fact và Dimension rõ ràng** — Fact chứa foreign key + measure, Dimension chứa attributes.
2. **Grain rõ ràng** — Mỗi Fact Table phải có grain (đơn vị đo) được định nghĩa cụ thể.
3. **Business Logic vào Dimension** — Các phân nhóm (age_group, city_name, relationship_name) chuyển sang Dimension tương ứng thay vì viết CASE trực tiếp trong Fact.
4. **Surrogate Keys** — Dùng MD5 hoặc sequence key làm khóa kết nối Fact-Dimension, không dùng natural key.

---

## 3. Danh Sách Các Models Cần Tạo Mới / Tái Cấu Trúc

### 3.1. Intermediate Layer (Mới)

| Model | Mô Tả | Mức Ưu Tiên |
|---|---|---|
| `int_contracts_enriched.sql` | Join contract master với contract objects; tính toán các trường phái sinh (age, age_group, city_name, relationship_name) tại tầng Intermediate thay vì Mart. | 🔴 Cao |

### 3.2. Dimension Layer (Warehouse) — Tái Cấu Trúc & Thêm Mới

| Model | Grain | Trạng Thái | Mức Ưu Tiên |
|---|---|---|---|
| `dim_date.sql` | 1 row = 1 ngày (từ 2020 đến 2030) | 🆕 Tạo mới | 🔴 Cao |
| `dim_customer.sql` | 1 row = 1 khách hàng duy nhất (Buyer) | 🔄 Tái cấu trúc từ `dim_customers.sql` | 🔴 Cao |
| `dim_insured_person.sql` | 1 row = 1 người được bảo hiểm | 🆕 Tạo mới | 🔴 Cao |
| `dim_product.sql` | 1 row = 1 sản phẩm/gói bảo hiểm | 🆕 Tạo mới | 🔴 Cao |
| `dim_insurance_provider.sql` | 1 row = 1 nhà bảo hiểm (BHV, LIBERTY, PVI...) | 🆕 Tạo mới | 🟡 Trung Bình |
| `dim_sales_channel.sql` | 1 row = 1 kênh bán hàng (companySaleName, branchSaleName) | 🆕 Tạo mới | 🟡 Trung Bình |

### 3.3. Fact Layer (Warehouse) — Tái Cấu Trúc & Thêm Mới

| Model | Grain | Foreign Keys | Measures | Trạng Thái |
|---|---|---|---|---|
| `fct_contracts.sql` | 1 row = 1 đối tượng bảo hiểm (contract object) | `customer_key`, `insured_person_key`, `product_key`, `provider_key`, `channel_key`, `date_key` (start) | `fee_insurance`, `contract_amount`, `commission` | 🔄 Tái cấu trúc |
| `fct_claims.sql` | 1 row = 1 yêu cầu bồi thường (claim) | `contract_object_id`, `customer_key`, `date_key` (claim date) | `amount_claim`, `compensation_amount`, `compensation_rate`, `days_hospitalized` | 🆕 Tách từ `dm_profiling_analysis` |

### 3.4. Data Mart Layer — Tái Cấu Trúc

| Model | Mô Tả | Trạng Thái |
|---|---|---|
| `dm_profiling_analysis.sql` | Tái cấu trúc để JOIN từ `fct_claims` + Dimensions thay vì tính toán trực tiếp. Business logic di chuyển sang Intermediate. | 🔄 Tái cấu trúc |
| `dm_contract_summary.sql` | Data Mart tổng hợp hợp đồng: phân tích theo loại bảo hiểm, nhà cung cấp, kênh bán hàng. | 🆕 Tạo mới |

---

## 4. Thiết Kế Chi Tiết Từng Model

### 4.1. `dim_date` (Dimension Thời Gian)

```sql
-- Grain: 1 row = 1 ngày
-- Columns:
date_key          INTEGER        -- Surrogate key (YYYYMMDD)
full_date         DATE           -- Ngày đầy đủ
day_of_week       INTEGER        -- 1 (Mon) → 7 (Sun)
day_name          VARCHAR        -- 'Thứ Hai', 'Thứ Ba'...
day_of_month      INTEGER        -- 1 → 31
week_of_year      INTEGER        -- 1 → 53
month_number      INTEGER        -- 1 → 12
month_name        VARCHAR        -- 'Tháng 1', 'Tháng 2'...
quarter           INTEGER        -- 1 → 4
year              INTEGER        -- 2020, 2021...
is_weekend        BOOLEAN        -- TRUE nếu T7/CN
is_month_end      BOOLEAN        -- TRUE nếu ngày cuối tháng
```

> **Lưu ý thiết kế:** `dim_date` nên được tạo bằng cách generate series ngày (không cần source data), và nên được tạo trước khi các Fact Tables tham chiếu đến nó.

### 4.2. `dim_customer` (Người Mua Bảo Hiểm)

```sql
-- Grain: 1 row = 1 người mua bảo hiểm duy nhất
-- Tách biệt khỏi Insured Person (người được bảo hiểm)
-- Columns:
customer_key      VARCHAR        -- Surrogate key MD5
contract_id       VARCHAR        -- FK → contract master
buyer_name        VARCHAR        -- Tên chuẩn hóa (INITCAP + TRIM)
buyer_dob         DATE
buyer_gender      INTEGER
buyer_phone       VARCHAR        -- Chuẩn hóa format 0xx
buyer_email       VARCHAR        -- Lowercase
buyer_address     TEXT
customer_type     INTEGER        -- 0 = Cá nhân, 1 = Doanh nghiệp
company_sale_name VARCHAR
branch_sale_name  VARCHAR
created_at        TIMESTAMP
modified_at       TIMESTAMP
```

### 4.3. `dim_insured_person` (Người Được Bảo Hiểm)

```sql
-- Grain: 1 row = 1 người được bảo hiểm duy nhất
-- Columns:
insured_person_key VARCHAR       -- Surrogate key MD5
insured_name      VARCHAR        -- Chuẩn hóa
insured_dob       DATE
insured_age       INTEGER        -- Tính tại thời điểm load
insured_age_group VARCHAR        -- '0-6', '7-17', '18-35', '36-55', '56+'
insured_gender    INTEGER        -- 0 = Nữ, 1 = Nam
insured_phone     VARCHAR
insured_email     VARCHAR
insured_address   TEXT
people_city_code  VARCHAR
city_name         VARCHAR        -- ← Decode từ city_code TẠI ĐÂY (thay vì ở Mart)
people_relationship INTEGER
relationship_name VARCHAR        -- ← Decode tại đây: 'Bản thân', 'Bố/Mẹ'...
source_type       VARCHAR        -- 'online' / 'offline'
```

> **Điểm khác biệt quan trọng:** Toàn bộ logic CASE giải mã `city_code` (63 tỉnh thành) và `relationship` được đặt **tại Dimension này**, không còn trong Mart.

### 4.4. `dim_product` (Sản Phẩm Bảo Hiểm)

```sql
-- Grain: 1 row = 1 gói sản phẩm bảo hiểm
-- Columns:
product_key           VARCHAR    -- Surrogate key MD5(major_name + program_name + company_provider)
insurance_type        VARCHAR    -- 'HEALTH', 'VEHICLE', 'TRAVEL', 'MOTO', 'SOCIAL', 'MEDICAL', 'HOUSE'
major_name            VARCHAR    -- Tên ngành bảo hiểm: 'Sức khỏe', 'Xe cơ giới'
program_id            VARCHAR
program_name          VARCHAR    -- Tên chương trình: 'Zuellig_2025'
company_provider_name VARCHAR    -- Tên nhà bảo hiểm: 'BHV', 'LIBERTY', 'PVI'
```

### 4.5. `fct_contracts` (Fact Hợp Đồng — Grain: 1 Contract Object)

```sql
-- Grain: 1 row = 1 đối tượng bảo hiểm (contract object) duy nhất
-- Columns:
contract_object_id    VARCHAR    -- Natural key
contract_id           VARCHAR    -- FK → Hợp đồng master
customer_key          VARCHAR    -- FK → dim_customer (người mua)
insured_person_key    VARCHAR    -- FK → dim_insured_person (người được BH)
product_key           VARCHAR    -- FK → dim_product
provider_key          VARCHAR    -- FK → dim_insurance_provider
channel_key           VARCHAR    -- FK → dim_sales_channel
start_date_key        INTEGER    -- FK → dim_date (ngày hiệu lực)
end_date_key          INTEGER    -- FK → dim_date (ngày hết hạn)
created_date_key      INTEGER    -- FK → dim_date (ngày tạo hợp đồng)

-- Measures
fee_insurance         DECIMAL    -- Phí bảo hiểm của đối tượng
contract_amount       DECIMAL    -- Tổng giá trị hợp đồng
contract_commission   DECIMAL    -- Hoa hồng
contract_amount_pay   DECIMAL    -- Số tiền đã thanh toán
source_type           VARCHAR    -- 'online' / 'offline'
created_at            TIMESTAMP
modified_at           TIMESTAMP
```

### 4.6. `fct_claims` (Fact Bồi Thường — Grain: 1 Claim)

```sql
-- Grain: 1 row = 1 yêu cầu bồi thường (claim)
-- Columns:
claim_id              VARCHAR    -- Natural key
contract_object_id    VARCHAR    -- FK → fct_contracts
customer_key          VARCHAR    -- FK → dim_customer (Denormalized để query nhanh)
insured_person_key    VARCHAR    -- FK → dim_insured_person
product_key           VARCHAR    -- FK → dim_product
claim_date_key        INTEGER    -- FK → dim_date (ngày claim)
hospitalized_date_key INTEGER    -- FK → dim_date (ngày nhập viện)

-- Measures
amount_claim          DECIMAL    -- Số tiền yêu cầu BT
compensation_amount   DECIMAL    -- Số tiền được BT
compensation_rate     DECIMAL    -- Tỉ lệ BT (%)
days_hospitalized     INTEGER    -- Số ngày điều trị
days_from_contract_to_claim INTEGER  -- Số ngày từ HĐ → claim

-- Attributes (không normalize được / cardinality thấp)
claim_type            VARCHAR
treatment_type        VARCHAR
diagnostic            TEXT       -- Raw text chẩn đoán
common_diagnostic_category VARCHAR  -- Phân loại bệnh (tính ở Intermediate)
tpa_id                VARCHAR
place_of_treatment    VARCHAR
claim_status          VARCHAR
created_at            TIMESTAMP
modified_at           TIMESTAMP
```

---

## 5. Lộ Trình Thực Hiện (Implementation Roadmap)

### Giai Đoạn 1 — Xây Dựng Foundation (Tuần 1-2)

- [ ] Tạo `dim_date.sql` (generate series 2020–2030)
- [ ] Tái cấu trúc `dim_customer.sql` (tách người mua khỏi người được BH)
- [ ] Tạo `dim_insured_person.sql` (di chuyển logic decode city/relationship vào đây)
- [ ] Tạo `dim_product.sql` (normalize danh mục sản phẩm)

### Giai Đoạn 2 — Tái Cấu Trúc Facts (Tuần 2-3)

- [ ] Tái cấu trúc `fct_contracts.sql` (thay `fct_contracts_wide.sql`; slim down, thêm FK keys)
- [ ] Tạo `fct_claims.sql` (tách claim ra khỏi `dm_profiling_analysis`)
- [ ] Tạo `int_contracts_enriched.sql` (consolidate business logic decode ở Intermediate)

### Giai Đoạn 3 — Tái Cấu Trúc Marts (Tuần 3-4)

- [ ] Tái cấu trúc `dm_profiling_analysis.sql` (JOIN từ `fct_claims` + Dimensions)
- [ ] Tạo `dm_contract_summary.sql` (tổng hợp hợp đồng theo loại, nhà cung cấp, kênh)

### Giai Đoạn 4 — Kiểm Thử & Tối Ưu (Tuần 4)

- [ ] Viết dbt tests (`not_null`, `unique`, `accepted_values`, `relationships`) cho tất cả models mới
- [ ] Benchmark query performance trước và sau tái cấu trúc
- [ ] Cập nhật `dbt_project.yml` và `src_postgres.yml`

---

## 6. Sơ Đồ Lineage Sau Tái Cấu Trúc

```
[Staging Sources]
    stg_contracts          ─────────────────────────────────► dim_customer
    stg_contract_objects_* ─► int_contracts_joined            
                                        │
                                        ▼
                            int_contracts_deduped
                                        │
                                        ▼
                            int_contracts_enriched ──────────► dim_insured_person
                                        │                ────► dim_product
                                        │
                                        ▼
                                  fct_contracts ──────────────► dm_contract_summary
                                        │
    stg_claims ─────────────────────────▼
                                  fct_claims ────────────────► dm_profiling_analysis
                                        │
                               dim_date (FK)
```

---

## 7. Ghi Chú Kỹ Thuật

### 7.1. Chiến Lược Incremental Load

| Model | Incremental Key | Filter Column |
|---|---|---|
| `dim_date` | `date_key` | N/A (Static table, full refresh) |
| `dim_customer` | `customer_key` | `modified_at` |
| `dim_insured_person` | `insured_person_key` | `modified_at` |
| `dim_product` | `product_key` | N/A (thường ít thay đổi, full refresh định kỳ) |
| `fct_contracts` | `contract_object_id` | `modified_at` |
| `fct_claims` | `claim_id` | `modified_at` |

### 7.2. Xử Lý SCD (Slowly Changing Dimension)

Hiện tại tất cả Dimension dùng SCD Type 1 (Overwrite). Nếu cần lịch sử thay đổi thông tin khách hàng/sản phẩm, có thể nâng cấp lên **SCD Type 2** bằng cách thêm các cột:
```sql
valid_from     TIMESTAMP
valid_to       TIMESTAMP
is_current     BOOLEAN
```

### 7.3. Các dbt Packages Nên Dùng

| Package | Mục Đích |
|---|---|
| `dbt-utils` | `generate_surrogate_key`, `date_spine` (tạo dim_date) |
| `dbt-expectations` | Test data quality nâng cao |

Cài đặt thông qua `packages.yml`:
```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: [">=1.0.0"]
```

---

## 8. Tóm Tắt Lợi Ích Sau Khi Tái Cấu Trúc

| Tiêu Chí | Trước | Sau |
|---|---|---|
| Số Dimensions | 1 (`dim_customers`) | 6 (`date`, `customer`, `insured_person`, `product`, `provider`, `channel`) |
| Số Fact Tables | 1 (Wide Table) | 2 (`fct_contracts`, `fct_claims`) |
| Business Logic | Nằm trong Mart SQL | Tập trung tại Intermediate & Dimension |
| Query Performance | Full join Wide Table | Star Join — truy vấn theo dimension |
| Khả năng mở rộng | Thấp (thêm cột = thay đổi tất cả) | Cao (thêm Dimension mới độc lập) |
| Tái sử dụng Logic | Không (duplicate CASE statements) | Có (decode logic trong Dimension) |
| BI Reporting | Hạn chế (1 chiều) | Đa chiều (thời gian, sản phẩm, kênh, địa lý) |
