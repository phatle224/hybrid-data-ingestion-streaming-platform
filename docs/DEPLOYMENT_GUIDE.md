# CDC Production Deployment - Streaming ETL Architecture

## Bước 1: Cấu hình

```powershell
# Tạo .env từ template
cp .env.example .env
# Edit: MYSQL_HOST=localhost, MYSQL_USER=synthetic_db_user, MYSQL_PASSWORD=REDACTED_PASSWORD
```

---

## Bước 2: Tạo Database

```powershell
# Windows PowerShell
# 1. Create staging online and offline schema
database\01_staging\01_create_staging_schema.sql
database\01_staging\02_create_staging_offline_contract.sql

# 2. Create reporting tables
database\02_reporting\02_create_contract_wide_table.sql
database\02_reporting\01_create_profiling_analysis.sql
```

---

## Bước 3: Khởi động Docker Infrastructure

```powershell
# Tạo network
docker network create cdc-network

# 1. Start Redis (for deduplication cache)
docker-compose -f docker-compose.redis.yml up -d

# 2. Start Kafka + Zookeeper
docker-compose -f docker-compose.kafka.yml up -d

# 3. Start Debezium Connect + UI
docker-compose -f docker-compose.debezium.yml up -d

```

---

## Bước 4: Đăng ký Debezium Connectors

### 4.1. Source → Staging Connector (source prefix)

```powershell
# Đăng ký connector cho production database
Invoke-RestMethod -Uri "http://localhost:8083/connectors" `
  -Method Post `
  -ContentType "application/json" `
  -Body (Get-Content configs\register-source-connector.json -Raw)

# Kiểm tra status (phải RUNNING)
Invoke-RestMethod -Uri "http://localhost:8083/connectors/mysql-source-connector/status"
```

### 4.2. Staging → Reporting Connector (staging prefix)

```powershell
# Đăng ký connector cho staging database
Invoke-RestMethod -Uri "http://localhost:8083/connectors" `
  -Method Post `
  -ContentType "application/json" `
  -Body (Get-Content configs\register-staging-connector.json -Raw)

# Kiểm tra status (phải RUNNING)
Invoke-RestMethod -Uri "http://localhost:8083/connectors/mysql-staging-connector/status"
```

---

## Bước 5: Start Streaming Consumers

### 5.1. CDC Consumer (Source → Staging)

```powershell
# Start CDC consumer (source-consumer-v1)
docker-compose -f docker-compose.consumer.yml up -d --build

# Kiểm tra logs
docker logs cdc_consumer --tail 50 -f
```

### 5.2. Streaming ETL Consumer (Staging → Reporting)

```powershell
# Start streaming ETL consumer (staging-consumer-v1)
docker-compose -f docker-compose.streaming-etl.yml up -d --build

# Kiểm tra logs
docker logs cdc_streaming_etl --tail 50 -f
```

### 5.3. Profiling Consumer (Real-time Profiling Analysis)

```powershell
# Start profiling consumer (profiling-consumer-v1)
docker-compose -f docker-compose.profiling.yml up -d --build

# Kiểm tra logs
docker logs cdc_profiling --tail 50 -f
```


