# CDC Portal Upload - Project Overview

## Giới Thiệu

Hệ thống upload và xử lý file Excel hợp đồng bảo hiểm với tính năng duplicate checking thông minh.

**Features:**
- 📁 Upload file Excel (.xlsx, .xls)  
- 🔍 Auto-detect loại bảo hiểm từ filename
- ✨ Transform data theo mapping chuẩn
- 🎯 Check duplicate bằng 4 business keys
- 💾 Insert database chỉ records mới
- 📊 Report chi tiết (total, new, duplicates)

---

## Tech Stack

**Backend:**
- FastAPI (Python 3.11)
- Pandas (Excel processing)
- SQLAlchemy (ORM)
- MySQL/Oracle Database

**Frontend:**
- React + TypeScript
- Vite (Build tool)
- Nginx (Production server)

**Deployment:**
- Docker & Docker Compose
- Container names: `cdc_portal_upload_backend`, `cdc_portal_upload_frontend`

---

## Project Structure

```
services/
├── portal_backend/
│   ├── configs/
│   │   ├── app/settings.py              # App config
│   │   ├── database/db_config.py        # Database config
│   │   └── mappings/                    # Column mappings cho từng loại BH
│   │       ├── travel_mapping.py
│   │       ├── vehicle_mapping.py
│   │       └── ...
│   ├── models/
│   │   └── contract_model.py            # ContractRecord model
│   ├── repositories/
│   │   └── contract_repository.py       # Database access layer
│   ├── routes/
│   │   └── upload_routes.py             # API endpoints
│   ├── services/
│   │   ├── excel_service.py             # Factory Pattern
│   │   ├── duplicate_service.py         # ⭐ Duplicate check logic
│   │   └── processors/                  # Strategy Pattern
│   │       ├── base_processor.py        # Interface
│   │       ├── travel_processor.py
│   │       ├── vehicle_processor.py
│   │       └── ...
│   ├── main.py                          # FastAPI app entry
│   ├── requirements.txt
│   └── Dockerfile
│
├── portal_frontend/
│   ├── src/
│   │   ├── components/UploadForm.tsx    # Upload UI
│   │   ├── services/api.ts              # API client
│   │   └── types/index.ts               # TypeScript types
│   ├── package.json
│   ├── nginx.conf
│   └── Dockerfile
```

---

## Quick Start

### 1. Cấu hình Database

Sửa `services/portal_backend/configs/database/db_config.py`:
```python
MYSQL_HOST = "172.16.10.32"
MYSQL_USER = "aff_admin"
MYSQL_PASSWORD = "your_password"
MYSQL_DATABASE = "affina_staging"
```

### 2. Deploy với Docker

```powershell
# Tạo network nếu chưa tạo
docker network create cdc-network

# Build và start
docker compose -f docker-compose.portal.yml up -d --build

# Xem logs
docker compose -f docker-compose.portal.yml logs -f
```

### 3. Access Application

- **Frontend**: http://localhost:3010
- **Backend API**: http://localhost:3011
- **API Docs**: http://localhost:3011/docs

---

## API Endpoints

### Upload Excel

**POST** `/api/upload/excel`

**Request:**
```bash
curl -X POST http://localhost:3011/api/upload/excel \
  -F "file=@travel_contracts.xlsx" \
  -F "insurance_type=TRAVEL"
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "filename": "travel_contracts.xlsx",
    "insurance_type": "TRAVEL",
    "total_records": 100,
    "new_records": 85,
    "duplicate_records": 15,
    "duplicate_rate": "15.00%"
  }
}
```

### Health Check

**GET** `/api/health/`

---

## Loại Bảo Hiểm Hỗ Trợ

| Loại | Key | Filename Pattern |
|------|-----|------------------|
| Du lịch | TRAVEL | *travel*.xlsx |
| Xe cơ giới | VEHICLE | *vehicle*.xlsx |
| Xe máy | MOTO | *moto*.xlsx |
| Sức khỏe | HEALTH | *health*.xlsx |
| Y tế xã hội | MEDICAL_SOCIAL | *medical*.xlsx |

---

## Duplicate Check Logic (Key Feature)

### 4 Business Keys

Record được coi là **DUPLICATE** khi 4 keys này trùng với database:

1. **contractId** - Mã hợp đồng
2. **name** - Tên người được bảo hiểm
3. **majorName** - Tên nhóm chính
4. **companyProviderName** - Công ty bảo hiểm

### Algorithm

```python
# Batch query tất cả existing keys TRONG 1 LẦN
existing_keys = repository.get_existing_business_keys_batch(records)

for record in records:
    key = (contractId, name, majorName, companyProviderName)
    
    if key in existing_keys:
        → Skip (Duplicate)
    else:
        → Insert (New)
```

**Performance:** 1000 records check trong 0.1-0.5 giây (batch query + Set lookup)

---

## Development

### Local Development (Backend)

```powershell
# Tạo virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r services/portal_backend/requirements.txt

# Run dev server
cd services/portal_backend
uvicorn main:app --reload --port 3011
```

### Local Development (Frontend)

```bash
cd services/portal_frontend
npm install
npm run dev
```

---

## Testing

### Manual Test

1. Prepare test Excel file với đúng format columns
2. Upload qua UI: http://localhost:3010
3. Check response: total, new, duplicates
4. Verify database: `SELECT * FROM contracts;`

### Test Duplicate Logic

```sql
-- Insert test data
INSERT INTO contracts (contract_id, name, major_name, company_provider_name)
VALUES ('HD001', 'Nguyen Van A', 'Group 1', 'ABC Insurance');

-- Upload Excel có record trùng → Should detect as duplicate
```

---

## Configuration Files

### Backend Config

**`services/portal_backend/configs/app/settings.py`**
```python
UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = [".xlsx", ".xls"]
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
```

**`services/portal_backend/configs/database/db_config.py`**
```python
MYSQL_HOST = "172.16.10.32"
MYSQL_PORT = 3306
MYSQL_USER = "aff_admin"
MYSQL_PASSWORD = "***"
MYSQL_DATABASE = "affina_staging"
```

---

## Common Issues

### Port Already in Use
```powershell
# Check ports
netstat -ano | findstr :3010
netstat -ano | findstr :3011

# Kill process
taskkill /PID <PID> /F
```

### Database Connection Failed
- Check database credentials in `db_config.py`
- Verify database server is running
- Test connection: `docker exec -it cdc_portal_backend bash`

### No Records Inserted
- Check logs: `docker logs cdc_portal_backend`
- Verify Excel format matches mapping
- Check if all records are duplicates

---

## Deployment Notes

### Files KHÔNG đóng gói:
- ❌ `.venv/` - Virtual environment (100-500MB)
- ❌ `node_modules/` - Node dependencies (200MB-1GB)
- ❌ `__pycache__/` - Python cache

→ Docker sẽ tự động cài từ `requirements.txt` và `package.json`

### Production Checklist:
- [ ] Update database credentials
- [ ] Configure firewall rules
- [ ] Enable HTTPS (reverse proxy)
- [ ] Setup backup strategy
- [ ] Configure logging/monitoring
- [ ] Set resource limits (CPU, Memory)

---

## Support

**Documentation:**
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Hướng dẫn deploy chi tiết
- [BUSINESS_LOGIC.md](./BUSINESS_LOGIC.md) - Business logic và architecture

**Contact:**
- Email: support@affina.com.vn
- Team: CDC Development Team
