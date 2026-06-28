# CDC Portal Ingestion Service

## Introduction

An insurance contract Excel file upload and processing system featuring intelligent duplicate checking.

**Features:**
- Upload Excel files (.xlsx, .xls)  
- Auto-detect insurance type from the filename
- Transform data according to standard mappings
- Perform duplicate checks using 7 business keys
- Insert only new records into the database
- Display detailed report metrics (total, new, duplicates)

---

## Tech Stack

**Backend:**
- FastAPI (Python 3.11)
- Pandas (Excel processing)
- SQLAlchemy (ORM)
- PostgreSQL Database

**Frontend:**
- React + TypeScript
- Vite (Build tool)
- Nginx (Production web server)

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
│   │   └── mappings/                    # Column mappings for each insurance type
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
│   │   ├── duplicate_service.py         # Duplicate check logic
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

### 1. Database Configuration

Edit `services/portal_backend/configs/database/db_config.py`:
```python
DB_HOST = "localhost"
DB_USER = "postgres"
DB_PASSWORD = "your_password"
DB_NAME = "insuranceWarehouse"
```

### 2. Deploy with Docker

```powershell
# Create network if not already created
docker network create cdc-network

# Build and start services
docker compose -f docker-compose.portal.yml up -d --build

# View container logs
docker compose -f docker-compose.portal.yml logs -f
```

### 3. Accessing the Application

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

## Supported Insurance Types

| Type | Key | Filename Pattern |
|------|-----|------------------|
| Travel | TRAVEL | *travel*.xlsx |
| Motor Vehicle | VEHICLE | *vehicle*.xlsx |
| Motorcycle | MOTO | *moto*.xlsx |
| Health | HEALTH | *health*.xlsx |
| Medical Social | MEDICAL_SOCIAL | *medical*.xlsx |

---

## Duplicate Check Logic

### 7 Business Keys

A record is marked as a **DUPLICATE** when these 7 business keys match an existing database record:

1. **contractId** - Contract identifier
2. **peopleName** - Insured person name
3. **majorName** - Insurance program/major name
4. **companyProviderName** - Insurance company provider
5. **startDate** - Policy start date
6. **endDate** - Policy end date
7. **feeInsurance** - Insurance fee

### Algorithm

```python
# Batch query all existing keys in a single query
existing_keys = repository.get_existing_business_keys_batch(records)

for record in records:
    key = (contractId, name, majorName, companyProviderName, startDate, endDate, feeInsurance)
    
    if key in existing_keys:
        # Skip (Duplicate)
    else:
        # Insert (New)
```

**Performance:** 1,000 records verified within 0.1 - 0.5 seconds (via batch query + set lookup).

---

## Development

### Local Development (Backend)

```powershell
# Create virtual environment
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

### Manual Testing

1. Prepare a test Excel file with the correct column format.
2. Upload via the UI: http://localhost:3010
3. Verify the response metrics (total, new, duplicates).
4. Verify database contents: `SELECT * FROM contracts;`

### Test Duplicate Logic

```sql
-- Insert test data
INSERT INTO contracts (contract_id, name, major_name, company_provider_name, start_date, end_date, fee_insurance)
VALUES ('HD001', 'Nguyen Van A', 'Group 1', 'ABC Insurance', '2026-01-01', '2026-12-31', 500000);

-- Upload an Excel file containing duplicate records -> Should detect as duplicate
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
DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "postgres"
DB_PASSWORD = "***"
DB_NAME = "insuranceWarehouse"
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
- Check database credentials in `db_config.py`.
- Verify database server is running.
- Test connection: `docker exec -it cdc_portal_backend bash`.

### No Records Inserted
- Check logs: `docker logs cdc_portal_backend`.
- Verify Excel format matches the target mapping.
- Check if all records are duplicates.

---

## Deployment Notes

### Excluded files:
- `.venv/` - Virtual environment
- `node_modules/` - Node dependencies
- `__pycache__/` - Python compilation cache

Docker will automatically install all dependencies from `requirements.txt` and `package.json`.

### Production Checklist:
- Update database credentials
- Configure firewall rules
- Enable HTTPS (reverse proxy)
- Setup backup strategy
- Configure logging/monitoring
- Set resource limits (CPU, Memory)

---

## Support

**Documentation:**
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Detailed deployment instructions
- [PROJECT_ARCHITECTURE.md](./PROJECT_ARCHITECTURE.md) - Project architecture and data flow

**Contact:**
- Email: support@insustream.com
- Team: CDC Development Team
