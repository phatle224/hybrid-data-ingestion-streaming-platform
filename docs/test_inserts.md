# Tài Liệu Hướng Dẫn & Kịch Bản Kiểm Thử Dữ Liệu CDC (Staging & Warehouse Sync)

Tài liệu này cung cấp kịch bản kiểm thử (Test Scripts) với dữ liệu thực tế cho 9 bảng nghiệp vụ tại database **Source** (`insuranceSale`). Mục tiêu là kiểm chứng xem dữ liệu thêm mới có tự động đồng bộ (stream) qua Debezium & Kafka vào các bảng **Staging** tương ứng và các schema khác (`warehouse`, `mart`) của database **Warehouse** (`insuranceWarehouse`) hay không.

File SQL script đầy đủ đã được lưu tại: [sample_insert_tests.sql](file:///d:/affina/phase_cdc\cdc_reporting\docs\sample_insert_tests.sql)

---

## 📋 1. Danh Sách Bản Ghi Tạo Mới (5 Rows/Table)

Các bản ghi kiểm thử dưới đây được liên kết logic với nhau thông qua `contractId` và `contractObjectId` để đảm bảo dữ liệu có thể tham chiếu và thực hiện JOIN thành công trong dbt:

1. **`insuranceContract` (Hợp đồng gốc):** Tạo 5 hợp đồng có ID từ `CTR-TEST-001` đến `CTR-TEST-005` với tên khách hàng cố tình chứa khoảng trắng và viết hoa thường không nhất quán để test logic dọn dẹp dữ liệu của dbt (ví dụ: `  nGuYeN tHi tEsT oNe  `).
2. **`insuranceContractObject` (Đối tượng bảo hiểm sức khỏe - HEALTH):** 5 bản ghi liên kết tới các hợp đồng trên.
3. **`insuranceContractObjectVehicle` (Ô tô):** 5 bản ghi.
4. **`insuranceContractObjectTravel` (Du lịch):** 5 bản ghi.
5. **`insuranceContractObjectMoto` (Xe máy):** 5 bản ghi.
6. **`insuranceContractObjectSocialInsurance` (Bảo hiểm xã hội):** 5 bản ghi.
7. **`insuranceContractObjectMedicalInsurance` (Bảo hiểm y tế):** 5 bản ghi.
8. **`insuranceContractObjectHouse` (Nhà tư nhân):** 5 bản ghi.
9. **`insuranceClaim` (Yêu cầu bồi thường):** 5 bản ghi bồi thường liên quan trực tiếp đến các hợp đồng sức khỏe trên.

---

## 🛠️ 2. Các Bước Thực Hiện Kiểm Thử

### Bước 1: Thực thi lệnh INSERT vào Database Source (`insuranceSale`)

Sử dụng công cụ quản lý Database (như DBeaver, pgAdmin) hoặc chạy qua PowerShell để thực hiện script:

```powershell
# Chạy trực tiếp qua psql vào database insuranceSale
psql -h localhost -p 5432 -U postgres -d insuranceSale -f docs/sample_insert_tests.sql
```

*(Nhập mật khẩu của bạn là `${DB_PASSWORD}` khi được yêu cầu)*

### Bước 2: Kiểm tra dữ liệu được nạp vào Staging (`insuranceWarehouse`)

Do hệ thống CDC Debezium hoạt động thời gian thực (Real-time), dữ liệu sẽ được chuyển sang các bảng staging trong vòng dưới 2 giây. Chạy script đếm số dòng staging để kiểm tra:

```powershell
python scripts/check_staging_counts.py
```

Bạn sẽ thấy số lượng dòng của các bảng `stgInsurance*` tăng lên 5 bản ghi so với ban đầu. Bạn cũng có thể truy cập Database `insuranceWarehouse` chạy truy vấn sau để xem dữ liệu thô đã được Debezium bắt và biến đổi:

```sql
SET search_path TO staging;
SELECT "contractId", "name", "email" FROM "stgInsuranceContract" WHERE "contractId" LIKE 'CTR-TEST%';
```

### Bước 3: Chạy biến đổi tầng dbt (ELT Pipeline)

Sau khi dữ liệu thô đã nằm ở schema `staging` của database `insuranceWarehouse`, chạy dbt để thực hiện biến đổi sang các schema phân tích:

```powershell
cd services/dbt_analytics
dbt run --profiles-dir .
```

dbt sẽ thực hiện:
* Làm sạch tên (loại bỏ khoảng trắng, viết hoa chuẩn: `Nguyen Thi Test One`).
* Chuẩn hóa email, số điện thoại.
* Ghép nối (Union) các đối tượng bảo hiểm khác nhau vào `int_contracts_joined`.
* Khử trùng và đưa vào Fact Table `warehouse.fct_contracts_wide` và Dimension Table `warehouse.dim_customers`.
* Tính toán các chỉ số phân tích rủi ro bồi thường đưa vào Data Mart `mart.dm_profiling_analysis`.

### Bước 4: Kiểm tra kết quả tại Data Warehouse và Data Mart

Chạy truy vấn để xác nhận các bản ghi kiểm thử đã qua xử lý dbt:

```sql
-- Kiểm tra dữ liệu khách hàng đã chuẩn hóa trong Warehouse
SELECT "customer_key", "customer_name", "customer_email" 
FROM "insuranceWarehouse"."warehouse"."dim_customers" 
WHERE "customer_email" LIKE '%test%';

-- Kiểm tra dữ liệu wide fact table
SELECT "contract_id", "insured_name", "fee_insurance", "insurance_type"
FROM "insuranceWarehouse"."warehouse"."fct_contracts_wide"
WHERE "contract_id" LIKE 'CTR-TEST%';

-- Kiểm tra phân tích bồi thường trong Data Mart
SELECT "contract_id", "diagnostic", "amount_claim", "compensation_amount", "compensation_rate"
FROM "insuranceWarehouse"."mart"."dm_profiling_analysis"
WHERE "contract_id" LIKE 'CTR-TEST%';
```

---

## ⚡ 3. Cách Chạy Tự Động Toàn Bộ Kịch Bản Kiểm Thử Qua Python

Để thuận tiện nhất cho việc kiểm thử, một script Python tự động hóa toàn bộ quy trình đã được viết tại [run_insert_test.py](file:///d:/affina\phase_cdc\cdc_reporting\scripts\run_insert_test.py). Script này sẽ tự động:
1. Kết nối DB Source (`insuranceSale`) và chạy chèn 35 bản ghi thử nghiệm.
2. Đợi 10 giây để Debezium bắt sự thay đổi và đồng bộ sang Kafka -> Staging DB.
3. Chạy `dbt run` để biến đổi dữ liệu.
4. Truy vấn đếm số lượng dòng bản ghi thử nghiệm trong Staging, Warehouse Fact/Dimension, và Data Mart để xác nhận thành công.

Để chạy script tự động:
```powershell
python scripts/run_insert_test.py
```

---

## 🗑️ 4. Dọn dẹp dữ liệu kiểm thử (Rollback)

Sau khi kết thúc quá trình kiểm thử, để đưa cơ sở dữ liệu về trạng thái sạch sẽ trước đó, hãy thực thi đoạn lệnh sau trên cả DB Source và DB Warehouse:

```sql
-- Chạy trên DB Source: insuranceSale
SET search_path TO "source", public;
DELETE FROM "insuranceClaim" WHERE "id" LIKE 'CLM-TEST%';
DELETE FROM "insuranceContractObjectHouse" WHERE "id" LIKE 'OBJ-TEST%';
DELETE FROM "insuranceContractObjectMedicalInsurance" WHERE "contractObjectId" LIKE 'OBJ-TEST%';
DELETE FROM "insuranceContractObjectSocialInsurance" WHERE "contractObjectId" LIKE 'OBJ-TEST%';
DELETE FROM "insuranceContractObjectMoto" WHERE "id" LIKE 'OBJ-TEST%';
DELETE FROM "insuranceContractObjectTravel" WHERE "id" LIKE 'OBJ-TEST%';
DELETE FROM "insuranceContractObjectVehicle" WHERE "contractObjectId" LIKE 'OBJ-TEST%';
DELETE FROM "insuranceContractObject" WHERE "contractObjectId" LIKE 'OBJ-TEST%';
DELETE FROM "insuranceContract" WHERE "contractId" LIKE 'CTR-TEST%';
```
