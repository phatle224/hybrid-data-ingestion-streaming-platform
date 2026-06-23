# CDC SERVER - HƯỚNG DẪN TRIỂN KHAI

**Ngày:** 27 tháng 11, 2025  
**Dự án:** Affina CDC Pipeline - Đồng bộ dữ liệu thời gian thực

---

## MỤC LỤC

1. [Mô tả chung về hệ thống](#mô-tả-chung-về-hệ-thống)
2. [Lưu ý quan trọng](#lưu-ý-quan-trọng)
3. [Danh sách kiểm tra trước triển khai](#danh-sách-kiểm-tra-trước-triển-khai)
4. [Cấu hình MySQL Binlog (QUAN TRỌNG)](#cấu-hình-mysql-binlog)
5. [Các bước triển khai (QUAN TRỌNG)](#các-bước-triển-khai-quan-trọng)


---

## MÔ TẢ CHUNG VỀ HỆ THỐNG
Hệ thống CDC Server sử dụng Debezium để theo dõi các thay đổi (INSERT, UPDATE, DELETE) trên các bảng trong MySQL database nguồn `insuranceSale`, sau đó đẩy các thay đổi này vào Kafka topics. Một consumer Python sẽ đọc các messages từ Kafka topics và đồng bộ dữ liệu vào database staging `insuranceWarehouse`. Cuối cùng, các triggers trong database staging sẽ tự động cập nhật dữ liệu vào database reporting `insuranceReporting` để phục vụ cho mục đích phân tích và báo cáo

Như chị Mai đã mail cho anh thì sau khi anh triển khai hệ thống này xong và được anh cung cấp tài khoản để vào database insuranceReporting thì team BI sẽ dùng tool metabase kết nối vào database này thực hiện các báo cáo phân tích dữ liệu ạ

---

## LƯU Ý QUAN TRỌNG

### Yêu cầu hệ thống

#### Hạ tầng cơ sở
- **Docker:** Phiên bản 20.10 trở lên
- **Docker Compose:** Phiên bản 2.0 trở lên
- **MySQL Server:** Phiên bản 8.0 trở lên (Database nguồn)
- **MySQL Binlog:** PHẢI được bật với format ROW (xem [Cấu hình MySQL Binlog](#cấu-hình-mysql-binlog))

### Cấu hình Production

**KHI TRIỂN KHAI LÊN PRODUCTION, BẮT BUỘC PHẢI THAY ĐỔI:**

#### 1. `docker-compose.yml`: 

**QUAN TRỌNG:** Trên môi trường Production, anh có thể thay đổi external ports để tránh xung đột với các dịch vụ khác, nếu không có thì anh có thể giữ nguyên giống config có sẵn trong file docker-compose của em luôn ạ, còn bên dưới là ví dụ anh có thể tham khảo để thay đổi ports:

```yaml
services:
  zookeeper:
    ports:
      - "12181:2181"  # Thay vì 2181:2181

  kafka:
    ports:
      - "19092:9092"  # Thay vì 9092:9092
      - "19093:9093"  # Thay vì 9093:9093
    environment:
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9093,PLAINTEXT_HOST://localhost:19092

  debezium-connect:
    ports:
      - "18083:8083"  # Thay vì 8083:8083

  kafka-ui:
    ports:
      - "19999:8080"  # Thay vì 9999:8080
```

#### 2. `consumer/.env`: thay đổi Database Credentials trong 

**QUAN TRỌNG:** Production PHẢI sử dụng password riêng biệt và bảo mật:

```dotenv
# MySQL Production Database
MYSQL_HOST=192.168.1.100                    # Thay thành IP Production MySQL
MYSQL_PORT=3306
MYSQL_USER=synthetic_cdc_user                    # User Production (do DBA tạo)
MYSQL_PASSWORD=<PRODUCTION_PASSWORD>        # Password Production (do DBA cung cấp)
MYSQL_DATABASE=insuranceWarehouse

# Kafka Production Config
KAFKA_BOOTSTRAP_SERVERS=kafka:9093          # Không đổi (internal Docker)
KAFKA_GROUP_ID=prod-consumer-v1             # Đổi tên consumer group

# Topic Prefix
TOPIC_PREFIX=prod.insuranceSale               # Nên đổi prefix cho Production
```

#### 3. `register-mysql-final.json`: cần cập nhật lại config theo Production

```json
{
  "name": "mysql-server-connector",
  "config": {
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "tasks.max": "1",
    "database.hostname": "PRODUCTION_MYSQL_IP", // Thay thành IP Production MySQL
    "database.port": "3306",
    "database.user": "PRODUCTION_CDC_USER", // Thay thành user Production
    "database.password": "PRODUCTION_PASSWORD", // Thay thành password Production 
    "database.server.id": "184054",
    "topic.prefix": "server",
    "database.include.list": "insuranceSale",
    "table.include.list": "insuranceSale.contractObject,insuranceSale.claim,insuranceSale.contract",
    ...
  }
}
```

#### 4. Thông tin về SQL Scripts

Dự án sử dụng 2 SQL scripts để tạo database schemas:

**`sql/create_staging_schema.sql`:**
- Tạo database `insuranceWarehouse`
- Tạo các bảng staging: `stgContract`, `stgContractObject`, `stgClaim`
- Không cần thay đổi cấu hình, chỉ cần chạy trực tiếp với user có quyền tạo database

**`sql/create_reporting_schema.sql`:**
- Tạo database `insuranceReporting`
- Tạo bảng `profiling_analysis` và stored procedure
- Tạo 9 triggers tự động đồng bộ từ staging sang reporting
- Không cần thay đổi cấu hình, chỉ cần chạy trực tiếp với user có quyền tạo database và trigger

**Lưu ý:** Cả 2 file SQL đều được thiết kế để chạy trực tiếp trên MySQL Production server, không cần chỉnh sửa cấu hình.

#### 5. Checklist Production Deployment

- [ ] **Đã tạo Docker network**: `docker network create cdc-network`
- [ ] **Đã thay đổi ports** trong `docker-compose.kafka.yml`, `docker-compose.debezium.yml`, `docker-compose.consumer.yml` nếu cần
- [ ] **Đã cập nhật MYSQL_HOST** trong `consumer/.env` thành Production MySQL IP
- [ ] **Đã cập nhật MYSQL_USER** và **MYSQL_PASSWORD** (do DBA cung cấp)
- [ ] **Đã đổi KAFKA_GROUP_ID** thành tên Production (ví dụ: `prod-consumer-v1`)
- [ ] **Đã cập nhật topic.prefix** trong `register-mysql-final.json` (ví dụ: `prod`)
- [ ] **Đã test kết nối** từ Docker host đến Production MySQL
- [ ] **Đã xác minh binlog** đã bật trên Production MySQL
- [ ] **Đã tạo user** với đầy đủ quyền REPLICATION trên Production MySQL

---

## DANH SÁCH KIỂM TRA TRƯỚC TRIỂN KHAI

### 1. Kiểm tra MySQL Source Database

Xác minh database nguồn tồn tại:
```sql
-- Kết nối đến MySQL
mysql -h localhost -u synthetic_db_user -p

-- Kiểm tra database nguồn tồn tại
SHOW DATABASES LIKE 'insuranceSale'; -- Database chứa 3 bảng cần CDC

-- Kiểm tra các bảng cần thiết
USE insuranceSale;
SHOW TABLES;  -- Phải có: contract, contractObject, claim


### 2. Kiểm tra quyền MySQL User

Xác minh user có đầy đủ quyền:
```sql
-- Kiểm tra quyền của synthetic_db_user
SHOW GRANTS FOR 'synthetic_db_user'@'%';

-- Các quyền bắt buộc:
-- SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT trên *.*
-- ALL PRIVILEGES trên insuranceWarehouse.* và insuranceReporting.*
```

Nếu thiếu quyền, cấp quyền như sau:
```sql
GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'synthetic_db_user'@'%';
GRANT ALL PRIVILEGES ON insuranceWarehouse.* TO 'synthetic_db_user'@'%';
GRANT ALL PRIVILEGES ON insuranceReporting.* TO 'synthetic_db_user'@'%';
FLUSH PRIVILEGES;
```

---

## CẤU HÌNH MYSQL BINLOG (CẦN BẮT BUỘC BẬT ĐỂ CDC HOẠT ĐỘNG)

### 1. Kiểm tra trạng thái Binlog

```sql
-- Kiểm tra binlog có được bật không
SHOW VARIABLES LIKE 'log_bin';
-- Kết quả mong đợi: ON

-- Kiểm tra định dạng binlog
SHOW VARIABLES LIKE 'binlog_format';
-- Kết quả mong đợi: ROW

-- Kiểm tra binlog row image
SHOW VARIABLES LIKE 'binlog_row_image';
-- Kết quả mong đợi: FULL

-- Kiểm tra server_id
SHOW VARIABLES LIKE 'server_id';
-- Phải khác 0 (ví dụ: 1, 100, etc.)
```

### 2. Bật Binlog (Nếu chưa được bật)

**CẢNH BÁO:** Thao tác này yêu cầu restart MySQL và phải thực hiện trong khung giờ bảo trì.

#### Bước 1: Chỉnh sửa file cấu hình MySQL

Chỉnh sửa file `/etc/my.cnf` hoặc `/etc/mysql/my.cnf`:

```ini
[mysqld]
# Server ID (duy nhất cho mỗi MySQL server)
server-id = 1

# Bật binary log
log-bin = mysql-bin
binlog_format = ROW
binlog_row_image = FULL

```

#### Bước 2: Khởi động lại MySQL

```bash
# Với systemd
sudo systemctl restart mysql

# HOẶC với service command
sudo service mysql restart
```

#### Bước 3: Xác minh cấu hình

```sql
SHOW VARIABLES LIKE 'log_bin';
SHOW VARIABLES LIKE 'binlog_format';
SHOW VARIABLES LIKE 'binlog_row_image';
SHOW VARIABLES LIKE 'server_id';
```

Với kết quả mong đợi như sau:
```
+------------------+-------+
| Variable_name    | Value |
+------------------+-------+
| log_bin          | ON    |
+------------------+-------+
+------------------+-------+
| Variable_name    | Value |
+------------------+-------+
| binlog_format    | ROW   |
+------------------+-------+
+------------------+-------+
| Variable_name    | Value |
+------------------+-------+
| binlog_row_image | FULL  |
+------------------+-------+
+------------------+-------+
| Variable_name    | Value |
+------------------+-------+
| server_id        | 1     |
+------------------+-------+
```
---

## CÁC BƯỚC TRIỂN KHAI (QUAN TRỌNG)

### Bước 0: Cấu hình biến môi trường

Consumer cần file cấu hình môi trường. Template được cung cấp trong `consumer/.env.example`.

#### Tạo file .env:

```bash
cd consumer
cp .env.example .env
```

#### Chỉnh sửa file .env:

```bash
# Sử dụng editor bạn thích
nano .env
# HOẶC
vim .env
```

#### Cấu hình bắt buộc (Development/Staging):

```dotenv
# Cấu hình Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9093          # Mạng nội bộ Docker
KAFKA_GROUP_ID=server-consumer-v14          # ID consumer group

# MySQL Staging Database
MYSQL_HOST=localhost                     # MySQL server (Dev/Staging)
MYSQL_PORT=3306
MYSQL_USER=synthetic_db_user                        # Database user
MYSQL_PASSWORD=REDACTED_PASSWORD           # Database password
MYSQL_DATABASE=insuranceWarehouse               # Tên staging database

# Topic Prefix (phải khớp với Debezium connector)
TOPIC_PREFIX=server.insuranceSale             # Từ register-mysql-final.json

# Cài đặt Consumer
LOG_LEVEL=INFO                              # DEBUG để troubleshoot
CONSUMER_TIMEOUT_MS=1000
MAX_POLL_INTERVAL_MS=300000
MAX_POLL_RECORDS=500
AUTO_OFFSET_RESET=earliest
```


**ĐỐI VỚI PRODUCTION:**
- Thay đổi `MYSQL_HOST` thành IP/hostname của Production MySQL server
- Thay đổi `MYSQL_PASSWORD` thành password Production (được cung cấp bởi DBA)
- Thay đổi `KAFKA_GROUP_ID` thành tên khác (ví dụ: `prod-consumer-v1`)
- Xem thêm chi tiết tại [Cấu hình Production](#cấu-hình-production)

**Xác minh cấu hình:**
```bash
# Kiểm tra file .env tồn tại và có giá trị đúng
cat consumer/.env | grep -E "MYSQL_HOST|TOPIC_PREFIX|KAFKA_GROUP_ID"

# Trên Windows PowerShell:
Get-Content consumer\.env | Select-String "MYSQL_HOST|TOPIC_PREFIX|KAFKA_GROUP_ID"
```

---

### Bước 1: Tạo Staging Database Schema

**Chạy SQL script để tạo staging schema:**

```bash
# Cách 1: Chạy từ command line (Linux/Mac)
mysql -h localhost -u synthetic_db_user -p < sql/create_staging_schema.sql

# Cách 2: Chạy từ command line (Windows PowerShell)
Get-Content sql\create_staging_schema.sql | mysql -h localhost -u synthetic_db_user -p

# Cách 3: Chạy trong MySQL client
mysql -h localhost -u synthetic_db_user -p
mysql> source /path/to/sql/create_staging_schema.sql;
# Hoặc trên Windows:
mysql> source d:\affina\phase_cdc\cdc_production_deploy\sql\create_staging_schema.sql;
```

**Kết quả mong đợi:**
```
Database 'insuranceWarehouse' created
Table 'stgContract' created successfully (93 columns)
Table 'stgContractObject' created successfully (134 columns)
Table 'stgClaim' created successfully (47 columns)
```

**Xác minh:**
```sql
USChạy SQL script để tạo reporting schema:**

```bash
# Cách 1: Chạy từ command line (Linux/Mac)
mysql -h localhost -u synthetic_db_user -p < sql/create_reporting_schema.sql

# Cách 2: Chạy từ command line (Windows PowerShell)
Get-Content sql\create_reporting_schema.sql | mysql -h localhost -u synthetic_db_user -p

# Cách 3: Chạy trong MySQL client
mysql -h localhost -u synthetic_db_user -p
mysql> source /path/to/sql/create_reporting_schema.sql;
# Hoặc trên Windows:
mysql> source d:\affina\phase_cdc\cdc_production_deploy\sql\ file SQL
mysql -h localhost -u synthetic_db_user -p < sql/create_reporting_schema.sql
```

**Hoặc chạy từng lệnh SQL trong file:**

```bash
# Mở MySQL client
mysql -h localhost -u synthetic_db_user -p

# Trong MySQL prompt
mysql> source /path/to/sql/create_reporting_schema.sql;
```

**Kết quả mong đợi:**
```
Database 'insuranceReporting' created
Table 'profiling_analysis' created (29 columns)
Stored procedure 'sp_build_profiling_analysis' created
9 triggers created successfully on insuranceWarehouse tables
```

**Xác minh:**
```sql
-- Kiểm tra database và table
USE insuranceReporting;
SHOW TABLES;
DESC profiling_analysis;

-- Kiểm tra stored procedure
SHOW PROCEDURE STATUS WHERE Db = 'insuranceReporting';

-- Kiểm tra triggers
USE insuranceWarehouse;
SHOW TRIGGERS;
-- Phải hiển thị 9 triggers:
-- - trg_stgClaim_after_insert, trg_stgClaim_after_update, trg_stgClaim_after_delete
-- - trg_stgContract_after_insert, trg_stgContract_after_update, trg_stgContract_after_delete
-- - trg_stgContractObject_after_insert, trg_stgContractObject_after_update, trg_stgContractObject_after_delete
```

---

### Bước 3: Khởi động hạ tầng

**Option 1: Deploy từng service riêng lẻ (Khuyến nghị)**

```bash
# Tạo Docker network
docker network create cdc-network

# 1. Deploy Kafka Infrastructure (Zookeeper, Kafka, Kafka-UI)
docker-compose -f docker-compose.kafka.yml up -d

# Đợi 30 giây để Kafka khởi động hoàn toàn
sleep 30

# 2. Deploy Debezium Connect
docker-compose -f docker-compose.debezium.yml up -d

# Đợi 30 giây để Debezium Connect khởi động
sleep 30

# 3. Deploy Python Consumer
docker-compose -f docker-compose.consumer.yml up -d
```

**Option 2: Deploy tất cả cùng lúc (Không khuyến nghị cho Production)**

```bash
# Tạo Docker network
docker network create cdc-network

# Deploy tất cả services
docker-compose up -d
```


**Xác minh Containers:**
```bash
# Kiểm tra tất cả containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Hoặc kiểm tra từng service
docker-compose -f docker-compose.kafka.yml ps
docker-compose -f docker-compose.debezium.yml ps
docker-compose -f docker-compose.consumer.yml ps

# Tất cả containers phải ở trạng thái "Up" hoặc "Running"
```
docker-compose ps
# Tất cả containers phải ở trạng thái "Up" hoặc "Running"
```

**Kiểm tra Logs:**
```bash
# Kiểm tra Kafka đã sẵn sàng
docker logs server_kafka --tail 50

# Kiểm tra Debezium Connect đã sẵn sàng
docker logs server_connect --tail 50
# Tìm dòng: "Kafka Connect started"
```

### Bước 4: Đăng ký Debezium Connector

Đợi 30 giây để Kafka Connect khởi động hoàn toàn, sau đó:

```bash
# Đăng ký connector (Linux/Mac)
curl -X POST http://localhost:8083/connectors -H "Content-Type: application/json" -d @register-mysql-final.json

# HOẶC sử dụng PowerShell (Windows)
Invoke-RestMethod -Uri "http://localhost:8083/connectors" -Method Post -ContentType "application/json" -Body (Get-Content register-mysql-final.json -Raw)
```

**Xác minh Connector:**
```bash
# Kiểm tra trạng thái connector, không dùng lệnh này được thì dùng lệnh bên dưới
curl http://localhost:8083/connectors/mysql-server-connector/status

# PowerShell:
Invoke-RestMethod -Uri "http://localhost:8083/connectors/mysql-server-connector/status"

# Kết quả mong đợi:
{
  "name": "mysql-server-connector",
  "connector": {"state": "RUNNING"},
  "tasks": [{"id": 0, "state": "RUNNING"}]
}
```

**Kiểm tra Topics đã được tạo:**
```bash
docker exec server_kafka kafka-topics --bootstrap-server localhost:9093 --list
# Các topics mong đợi:
# - server.insuranceSale.contract
# - server.insuranceSale.contractObject
# - server.insuranceSale.claim
```
Ở bước này, anh có thể đợi vài phút để data được sync từ MySQL source sang Kafka topics, và từ Kafka topics sang staging thông qua consumer.

---

### Bước 5: Xác minh Consumer

Kiểm tra consumer đang xử lý messages:

```bash
docker logs server_consumer --tail 50
```

**Log mong đợi:**
```
Successfully connected to Kafka. Subscribed to topics: [...]
[OK] Processed snapshot for stgContract, PK: xxx
[OK] Processed snapshot for stgContractObject, PK: xxx
[OK] Processed snapshot for stgClaim, PK: xxx
```

**Xác minh dữ liệu trong Staging:**
```sql
USE insuranceWarehouse;
SELECT COUNT(*) FROM stgContract;
SELECT COUNT(*) FROM stgContractObject;
SELECT COUNT(*) FROM stgClaim;
-- Ở đây, nếu số lượng rows ở staging giống với số lượng rows trong database nguồn insuranceSale thì consumer đã hoạt động đúng
```

---

### Bước 6: Load dữ liệu ban đầu vào Reporting
Vào database insuranceReporting và chạy stored procedure như bên dưới để load dữ liệu ban đầu, hoặc nếu data đã load vào đó rồi là do trigger đã tự động xử lý và không cần chạy lại lệnh dưới:

```sql
USE insuranceReporting;
CALL sp_build_profiling_analysis();

-- Xác minh dữ liệu đã được load
SELECT COUNT(*) FROM profiling_analysis;
-- Sẽ hiển thị số lượng records (phụ thuộc vào claims có contract hợp lệ)
```

---
