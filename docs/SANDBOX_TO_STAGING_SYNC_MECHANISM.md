# Cơ Chế Sync Data Sandbox (Source) -> Staging Trong Project `cdc_reporting`

## 1. Trả lời nhanh câu hỏi "có phải bằng Debezium không?"

**Đúng, nhưng chưa đủ.**

Trong project này, cơ chế sync từ sandbox/source sang staging là:

1. **Debezium MySQL Connector** đọc MySQL binlog từ DB source (hiện tại là `insuranceSale`).
2. Debezium đẩy event CDC vào **Kafka topics** (`source.insuranceSale.*`).
3. Service Python **CDC Consumer** đọc các topic đó, transform dữ liệu, rồi ghi vào DB **staging** (`insuranceWarehouse`).

Nói ngắn gọn: **Debezium = capture + publish CDC event**, còn **CDC Consumer = apply vào staging**.

---

## 2. Các thành phần chính trong repo

- Debezium Connect: `docker-compose.debezium.yml`
- Kafka + Zookeeper: `docker-compose.kafka.yml`
- Source connector config: `configs/register-source-connector.json`
- Staging connector config: `configs/register-staging-connector.json`
- CDC consumer service: `docker-compose.consumer.yml`
- Consumer code chính: `services/cdc_consumer/src/cdc_consumer.py`
- Parse/transform Debezium message: `services/shared/shared/debezium.py`
- Build SQL upsert/update/delete: `services/shared/shared/query_builder.py`
- Connection + Kafka factory: `services/shared/shared/connections.py`
- Staging schema: `database/01_staging/01_create_staging_schema.sql`

---

## 3. Luồng dữ liệu thực tế (Source -> Staging)

## 3.1. Source database (sandbox)

- DB source đang capture: `insuranceSale`
- Các bảng được capture (theo `table.include.list`):
  - `contract`
  - `contractObject`
  - `contractObjectVehicle`
  - `contractObjectTravel`
  - `contractObjectMoto`
  - `contractObjectSocialInsurance`
  - `contractObjectmedicalInsurance`
  - `contractObjectHouse`
  - `claim`

## 3.2. Debezium connector đẩy sang Kafka

Connector: `mysql-source-connector`

Các điểm cấu hình quan trọng:

- `connector.class = io.debezium.connector.mysql.MySqlConnector`
- `database.server.id = 184054` (phải unique)
- `topic.prefix = source`
- `database.include.list = insuranceSale`
- `snapshot.mode = when_needed`
- `provide.transaction.metadata = true`
- `heartbeat.interval.ms = 10000`

Khi chạy, Debezium tạo topic dạng:

- `source.insuranceSale.contract`
- `source.insuranceSale.contractObject`
- ...

## 3.3. CDC Consumer đọc Kafka -> ghi Staging

Consumer subscribe prefix:

- `TOPIC_PREFIX=source.insuranceSale`

Topic map sang bảng staging (trong `cdc_consumer.py`):

- `source.insuranceSale.contract` -> `stgContract`
- `source.insuranceSale.contractObject` -> `stgContractObject`
- `source.insuranceSale.contractObjectVehicle` -> `stgContractObjectVehicle`
- `source.insuranceSale.contractObjectTravel` -> `stgContractObjectTravel`
- `source.insuranceSale.contractObjectMoto` -> `stgContractObjectMoto`
- `source.insuranceSale.contractObjectSocialInsurance` -> `stgContractObjectSocialInsurance`
- `source.insuranceSale.contractObjectmedicalInsurance` -> `stgContractObjectMedicalInsurance`
- `source.insuranceSale.contractObjectHouse` -> `stgContractObjectHouse`
- `source.insuranceSale.claim` -> `stgClaim`

---

## 4. Cách xử lý event CDC trong consumer

Consumer parse Debezium payload và xử lý theo operation:

- `c` (create) và `r` (snapshot):
  - Dùng `INSERT ... ON DUPLICATE KEY UPDATE` (upsert)
- `u` (update):
  - Dùng `UPDATE ... WHERE PK = ...` riêng
- `d` (delete):
  - Dùng `DELETE ... WHERE PK = ...`

### 4.1. Transform dữ liệu Debezium

Trong `DebeziumTransformer` có xử lý:

- Epoch milliseconds -> `datetime`
- Days since epoch -> `date`
- Parse date string (`YYYY-MM-DD`, `YYYYMMDD`, `DD/MM/YYYY`)

Mục tiêu: dữ liệu phù hợp kiểu cột MySQL của staging.

### 4.2. Lọc cột theo schema staging

Consumer load schema thật của từng bảng staging bằng `DESCRIBE`.

Khi ghi dữ liệu, chỉ giữ các cột:

- tồn tại trong bảng staging
- khác `None`
- loại bỏ `modifiedDate` khỏi input vì hệ thống tự set

### 4.3. Đảm bảo tính ổn định khi chạy

- Kafka consumer chạy với `enable_auto_commit=False`
- Offset được `commit()` sau khi xử lý batch
- Retry tối đa `3` lần mỗi message
- Message lỗi liên tục sẽ ghi vào file DLQ jsonl

=> Hành vi thực tế là **at-least-once delivery** (có thể nhận lại message, nên cần upsert/idempotent).

---

## 5. Điều kiện bắt buộc để cơ chế hoạt động

## 5.1. MySQL source phải bật binlog đúng chuẩn

Bắt buộc:

- `log_bin = ON`
- `binlog_format = ROW`
- `binlog_row_image = FULL`
- `server_id != 0`

## 5.2. DB user cho Debezium phải đủ quyền

Tối thiểu:

- `SELECT`
- `RELOAD`
- `SHOW DATABASES`
- `REPLICATION SLAVE`
- `REPLICATION CLIENT`

## 5.3. Staging schema phải tạo trước

Chạy SQL:

- `database/01_staging/01_create_staging_schema.sql`

Nếu staging table chưa có, consumer sẽ không load được schema và sync thất bại.

---

## 6. Quy trình chạy thực tế (runbook nhanh)

## 6.1. Start hạ tầng

```powershell
docker network create cdc-network
docker-compose -f docker-compose.kafka.yml up -d
docker-compose -f docker-compose.debezium.yml up -d
```

## 6.2. Register source connector

```powershell
Invoke-RestMethod -Uri "http://localhost:8083/connectors" `
  -Method Post `
  -ContentType "application/json" `
  -Body (Get-Content configs\register-source-connector.json -Raw)

Invoke-RestMethod -Uri "http://localhost:8083/connectors/mysql-source-connector/status"
```

Trạng thái mong đợi: connector/task đều `RUNNING`.

## 6.3. Start CDC consumer

```powershell
docker-compose -f docker-compose.consumer.yml up -d --build
docker logs cdc_consumer --tail 100 -f
```

## 6.4. (Bổ sung) Register staging connector cho Layer 2

File này không tham gia trực tiếp luồng Source -> Staging, nhưng là connector bắt buộc nếu bạn muốn chạy full pipeline của project (Staging -> Reporting):

```powershell
Invoke-RestMethod -Uri "http://localhost:8083/connectors" `
  -Method Post `
  -ContentType "application/json" `
  -Body (Get-Content configs\register-staging-connector.json -Raw)

Invoke-RestMethod -Uri "http://localhost:8083/connectors/mysql-staging-connector/status"
```

Ý nghĩa của `register-staging-connector.json`:

- Capture CDC từ database `insuranceWarehouse`
- Publish vào topic prefix `staging.*`
- Là input cho Streaming ETL Consumer và Profiling Consumer

---

## 7. Cách verify sync đã đúng

1. Check Debezium connector status = `RUNNING`.
2. Check Kafka topic `source.insuranceSale.*` có message tăng.
3. Check log `cdc_consumer` có dòng `[OK] insert/update/delete`.
4. So sánh row count giữa source và staging cho các bảng chính.
5. Thử một case end-to-end: insert/update/delete ở source rồi xác nhận staging thay đổi tương ứng.

---

## 8. Template áp dụng cho project khác

Khi port cơ chế này sang hệ thống khác, bạn chỉ cần thay đổi đúng 6 nhóm sau:

1. **Source DB info**: host/port/user/password.
2. **Source tables**: `table.include.list` trong connector.
3. **Topic prefix**: ví dụ `source2` thay vì `source`.
4. **Staging schema**: tạo bảng đích + PK rõ ràng để upsert.
5. **Topic -> table mapping + primary key mapping** trong consumer.
6. **Field transform rules** cho date/datetime/decimal theo schema mới.

Khuyến nghị thêm khi triển khai project mới:

- Giữ nguyên pattern upsert + manual commit để an toàn khi retry.
- Dùng DLQ (log hoặc Kafka DLQ topic) để không mất message lỗi.
- Bật metrics/alert cho connector status, lag consumer, và tỉ lệ lỗi.

---

## 9. Kết luận

Project này đang dùng mô hình chuẩn cho bài toán đồng bộ realtime:

- **Debezium + Kafka** để capture và vận chuyển CDC event
- **Python CDC consumer** để apply event vào staging theo logic business

Vì vậy nếu bạn implement cho project khác, hãy giữ nguyên kiến trúc 2 lớp này thay vì chỉ dùng Debezium đơn lẻ.