# Affina Portal CDC - Production Deployment

## Tech Stack
FastAPI (Backend) | React + TypeScript (Frontend) | Oracle/MySQL Database | Docker

**Hệ thống upload và xử lý file Excel hợp đồng bảo hiểm:** Sức khỏe, Xe cơ giới, Du lịch, Tai nạn, Y tế Xã hội, Xe máy.

---

## Bước 1: Chuẩn Bị Package

```powershell
# 1. Tạo .dockerignore
@"
.venv
venv
node_modules
__pycache__
*.pyc
.git
.vscode
uploads/*
!uploads/.gitkeep
"@ | Out-File -FilePath .dockerignore -Encoding UTF8

# 2. Cấu hình database connection
# Edit: backend/configs/database/db_config.py
```

---

## Bước 2: Deploy Trên Server

```powershell
# 1. Di chuyển vào thư mục dự án
cd hybrid-data-ingestion-platform

# 2. Kiểm tra config database
notepad services\portal_backend\configs\database\db_config.py

# 3. Tạo Docker network nếu chưa tạo
docker network create cdc-network

# 4. Build và start services
docker compose -f docker-compose.portal.yml up -d --build

# 5. Kiểm tra logs
docker compose -f docker-compose.portal.yml logs -f
```

---

## Bước 3: Xác Nhận Deploy Thành Công

```powershell
# Kiểm tra status containers
docker compose -f docker-compose.portal.yml ps
```

**URLs:**
- Frontend: http://localhost:3010
- Backend API: http://localhost:3011
---

## Notes

- Database nên dùng managed service hoặc dedicated server cho production
- Backup database định kỳ
- Không commit credentials vào Git
- Sử dụng environment variables cho sensitive data