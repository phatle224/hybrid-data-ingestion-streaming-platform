# Hướng Dẫn Triển Khai Hệ Thống (Deployment Guide)

Tài liệu này hướng dẫn từng bước khởi chạy toàn bộ hạ tầng dự án **Hybrid Data Ingestion & Streaming ETL Platform** cục bộ thông qua Docker Compose.

---

## 🛠️ 1. Chuẩn Bị Môi Trường
1. Sao chép cấu hình môi trường từ file mẫu:
   ```powershell
   cp .env.example .env
   ```
2. Khởi tạo mạng Docker dùng chung cho toàn bộ dự án:
   ```powershell
   docker network create cdc-network
   ```

---

## 🚀 2. Khởi Chạy Hạ Tầng (Infrastructure)

Hãy khởi chạy các thành phần hạ tầng theo thứ tự sau để đảm bảo kết nối hoạt động trơn tru:

### Bước 2.1: Chạy Hệ Cơ Sở Dữ Liệu (PostgreSQL)
Chạy cả Cơ sở dữ liệu nguồn (Production DB) và cơ sở dữ liệu đích (Staging/Reporting DB):
```powershell
docker-compose -f docker-compose.db.yml up -d
```
*   **Production DB** chạy cổng: `5432`
*   **Staging/Warehouse DB** chạy cổng: `5433`

### Bước 2.2: Chạy Redis (Chống Trùng Lặp)
```powershell
docker-compose -f docker-compose.redis.yml up -d
```

### Bước 2.3: Chạy Kafka (Hệ Thống Message Queue)
```powershell
docker-compose -f docker-compose.kafka.yml up -d
```
*Đợi khoảng 10-15 giây để Kafka Broker khởi động hoàn tất.*

### Bước 2.4: Chạy Debezium Connect (Giám Sát CDC)
```powershell
docker-compose -f docker-compose.debezium.yml up -d
```
*Đợi khoảng 20-30 giây để Debezium Connect REST API sẵn sàng.*

---

## ⚙️ 3. Đăng Ký Debezium Connector

Đăng ký connector để bắt đầu thu thập dữ liệu (CDC) từ Production DB truyền vào Kafka:

```powershell
# Sử dụng PowerShell
Invoke-RestMethod -Uri "http://localhost:8083/connectors" `
  -Method Post `
  -ContentType "application/json" `
  -Body (Get-Content configs\register-source-connector.json -Raw)
```

**Kiểm tra trạng thái hoạt động (Phải trả về trạng thái `RUNNING`):**
```powershell
Invoke-RestMethod -Uri "http://localhost:8083/connectors/postgresql-source-connector/status"
```

---

## 🐍 4. Khởi Chạy Streaming Consumer & Scheduler

### Bước 4.1: Chạy CDC Consumer
Đồng bộ các sự kiện thay đổi dữ liệu từ Kafka vào Staging Database:
```powershell
docker-compose -f docker-compose.consumer.yml up -d --build
```

### Bước 4.2: Chạy dbt Transformation Scheduler
Dịch vụ lập lịch chạy ngầm thực thi các mô hình dbt biến đổi dữ liệu sang Star Schema:
```powershell
docker-compose -f docker-compose.scheduler.yml up -d --build
```

### Bước 4.3: Chạy Mock Data Generator
Tự động chèn và giả lập tương tác trên cơ sở dữ liệu nguồn (phục vụ mục đích demo):
```powershell
docker-compose -f docker-compose.generator.yml up -d --build
```

---

## 🌐 5. Khởi Chạy Offline Ingestion Portal (Giao Diện)

Khởi động giao diện quản lý và cổng tải lên file Excel:
```powershell
docker-compose -f docker-compose.portal.yml up -d --build
```

*   **Portal Frontend**: Truy cập tại địa chỉ [http://localhost:3000](http://localhost:3000)
*   **Portal Backend API**: Truy cập tại địa chỉ [http://localhost:8000](http://localhost:8000)
*   **Kafka UI**: Truy cập tại địa chỉ [http://localhost:9999](http://localhost:9999) (giám sát các Kafka Topic)

---

## 🔍 6. Xác Minh & Kiểm Tra Dữ Liệu
Bạn có thể kết nối vào PostgreSQL Staging/Warehouse ở cổng `5433` (User: `postgres`, Password: `password`) để kiểm tra các bảng báo cáo:
- Kiểm tra các bảng Dimension: `select count(*) from warehouse.dim_customer;`
- Kiểm tra bảng Fact: `select count(*) from warehouse.fct_contracts;`
- Kiểm tra Data Mart: `select count(*) from mart.dm_profiling_analysis;`
