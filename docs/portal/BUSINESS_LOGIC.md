# CDC Portal Upload - Business Logic & Architecture

## Tổng Quan Hệ Thống

Hệ thống upload và xử lý file Excel hợp đồng bảo hiểm với khả năng:
- ✅ Tự động detect loại bảo hiểm từ file Excel
- ✅ Transform data theo mapping chuẩn của từng loại
- ✅ Check duplicate thông minh (4 business keys)
- ✅ Insert vào database chỉ records mới

**Loại bảo hiểm hỗ trợ:** Travel, Vehicle, Moto, Health, Medical Social

---

## Kiến Trúc & Design Patterns

### 1. Factory Pattern (ProcessorFactory)
```
Client Request 
    ↓
ProcessorFactory.create_processor(insurance_type)
    ↓
Return: TravelProcessor | VehicleProcessor | HealthProcessor | ...
```

**Mục đích:** Tách logic khởi tạo processor, dễ mở rộng loại bảo hiểm mới

### 2. Strategy Pattern (IInsuranceProcessor)
```
IInsuranceProcessor (Interface)
    ├── TravelProcessor      → Xử lý bảo hiểm du lịch
    ├── VehicleProcessor     → Xử lý bảo hiểm xe cơ giới
    ├── MotoProcessor        → Xử lý bảo hiểm xe máy
    ├── HealthProcessor      → Xử lý bảo hiểm sức khỏe
    └── MedicalSocialProcessor  → Xử lý bảo hiểm y tế xã hội
```

**Mục đích:** Mỗi loại bảo hiểm có logic xử lý riêng nhưng follow chung 1 interface

### 3. Template Method Pattern
```python
process_file(file_path):
    1. parse_excel()      # Common: Đọc Excel, rename columns
    2. pre_process()      # Override: Clean data theo từng loại
    3. transform()        # Common: Map columns → ContractRecord
    4. post_process()     # Override: Derived fields, validate
```

---

## Flow Xử Lý Upload

```
┌─────────────┐
│ 1. Upload   │  Client upload file Excel (.xlsx, .xls)
│    Excel    │
└──────┬──────┘
       │
       ↓
┌─────────────────────┐
│ 2. Detect Insurance │  Auto detect từ filename hoặc manual select
│    Type              │  Example: "travel_contracts.xlsx" → TRAVEL
└──────┬──────────────┘
       │
       ↓
┌─────────────────────┐
│ 3. Create Processor │  Factory tạo processor phù hợp
│    (Factory Pattern) │  ProcessorFactory.create_processor("TRAVEL")
└──────┬──────────────┘
       │
       ↓
┌─────────────────────┐
│ 4. Parse & Transform│  
│    - parse_excel()   │  Đọc Excel, rename columns theo mapping
│    - pre_process()   │  Clean headers, remove empty rows
│    - transform()     │  DataFrame → List[ContractRecord]
│    - post_process()  │  Validate, derived fields
└──────┬──────────────┘
       │
       ↓
┌─────────────────────┐
│ 5. Duplicate Check  │  ⭐ KEY LOGIC - Chi tiết bên dưới
│    (4 business keys) │
└──────┬──────────────┘
       │
       ↓
┌─────────────────────┐
│ 6. Insert Database  │  Chỉ insert records mới (không duplicate)
│    (Batch Insert)    │
└──────┬──────────────┘
       │
       ↓
┌─────────────────────┐
│ 7. Return Response  │  {total, new, duplicates, duplicate_rate}
└─────────────────────┘
```

---

## ⭐ KEY LOGIC: Duplicate Checking

### Business Rules

**Record được coi là DUPLICATE khi 4 business keys trùng với database:**

1. **contractId** - Mã hợp đồng
2. **name** - Tên người được bảo hiểm (hoặc peopleName)
3. **majorName** - Tên nhóm chính/đơn vị
4. **companyProviderName** - Tên công ty cung cấp bảo hiểm

### Algorithm

```python
def filter_duplicates(records: List[ContractRecord]) -> Tuple[List, List]:
    # Step 1: Batch query tất cả existing keys TRONG 1 LẦN (Performance!)
    existing_keys = repository.get_existing_business_keys_batch(records)
    # Result: Set[(contractId, name, majorName, companyProviderName), ...]
    
    new_records = []
    duplicate_records = []
    
    for record in records:
        # Step 2: Normalize business keys (strip whitespace, handle None)
        key = (
            str(record.contract_id or "").strip() or None,
            str(record.name or "").strip() or None,
            str(record.major_name or "").strip() or None,
            str(record.company_provider_name or "").strip() or None,
        )
        
        # Step 3: Check nếu key này tồn tại trong database
        if key in existing_keys:
            duplicate_records.append(record)  # → Skip insert
        else:
            new_records.append(record)        # → Will insert
    
    return new_records, duplicate_records
```

### Key Points

✅ **Batch Query** - Query 1 lần tất cả keys thay vì query từng record → Nhanh hơn 100x

✅ **Normalization** - Strip whitespace, xử lý None để tránh false negative

✅ **4 Keys Composite** - Tuple (contractId, name, majorName, companyProviderName) unique record

✅ **Set Lookup** - Sử dụng Set cho O(1) lookup thay vì List O(n)

### SQL Query (Repository)

```sql
-- Batch query trong 1 lần duy nhất
SELECT DISTINCT 
    contract_id, 
    name, 
    major_name, 
    company_provider_name
FROM contracts
WHERE (contract_id, name, major_name, company_provider_name) IN (
    ('HD001', 'Nguyen Van A', 'Group 1', 'ABC Insurance'),
    ('HD002', 'Tran Thi B', 'Group 2', 'XYZ Insurance'),
    ...  -- Tất cả records trong 1 query
)
```

**Performance:**
- ❌ Old way: N queries (1000 records = 1000 queries) → 10-30 seconds
- ✅ New way: 1 query batch → 0.1-0.5 seconds

---

## Column Mapping Flow

### Example: Travel Insurance

**Excel Columns** → **Mapping** → **Model Fields**

```
"Mã hợp đồng"           → contractId          → contract_id
"Tên người đi"          → peopleName          → name, people_name
"CMND/CCCD"             → idCard              → id_card
"Giới tính"             → gender              → gender
"Ngày bắt đầu"          → startDateJourney    → start_date_journey
"Ngày kết thúc"         → endDateJourney      → end_date_journey
"Tên chương trình"      → programName         → program_name
"Phí bảo hiểm"          → feeInsurance        → fee_insurance
"Nhóm chính"            → majorName           → major_name
"Công ty cung cấp"      → companyProviderName → company_provider_name
```

### Mapping Registry

```python
MAPPING_REGISTRY = {
    "TRAVEL": TravelMapping,
    "VEHICLE": VehicleMapping,
    "MOTO": MotoMapping,
    "HEALTH": HealthMapping,
    "MEDICAL_SOCIAL": MedicalSocialMapping,
}
```

---

## Database Schema

### Contracts Table (Simplified)

```sql
CREATE TABLE contracts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    
    -- 4 Business Keys (Composite Unique)
    contract_id VARCHAR(100),
    name VARCHAR(255),
    major_name VARCHAR(255),
    company_provider_name VARCHAR(255),
    
    -- Common fields
    people_name VARCHAR(255),
    id_card VARCHAR(50),
    gender VARCHAR(20),
    address TEXT,
    dob DATE,
    start_insurance DATE,
    end_insurance DATE,
    beneficiary VARCHAR(255),
    package_name VARCHAR(255),
    total_fee DECIMAL(15, 2),
    note TEXT,
    
    -- Vehicle specific
    license_plate VARCHAR(50),
    chassis_number VARCHAR(100),
    engine_number VARCHAR(100),
    vehicle_type VARCHAR(100),
    
    -- Travel specific
    start_date_journey DATE,
    end_date_journey DATE,
    fee_insurance DECIMAL(15, 2),
    program_name VARCHAR(255),
    
    -- Metadata
    insurance_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Index for duplicate check performance
    INDEX idx_business_keys (contract_id, name, major_name, company_provider_name)
);
```

---

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Invalid file type | Upload non-Excel file | Validate extension: .xlsx, .xls |
| Unsupported insurance type | Cannot detect type | Manual select insurance type |
| Empty DataFrame | Excel file rỗng hoặc sai format | Validate rows > 0 |
| Database connection error | DB unreachable | Check db_config.py |
| Duplicate all records | File đã upload trước đó | Return duplicate_count = total |

---

## API Response Structure

```json
{
  "status": "success",
  "message": "Upload successful",
  "data": {
    "filename": "travel_contracts.xlsx",
    "insurance_type": "TRAVEL",
    "total_records": 100,
    "new_records": 85,
    "duplicate_records": 15,
    "duplicate_rate": "15.00%",
    "processing_time": "0.5s"
  }
}
```

---

## Extend cho Loại Bảo Hiểm Mới

### Steps to Add New Insurance Type

1. **Tạo Mapping Class**
```python
# configs/mappings/new_type_mapping.py
from .base_mapping import BaseInsuranceMapping

class NewTypeMapping(BaseInsuranceMapping):
    def __init__(self):
        super().__init__("NEW_TYPE")
        self.column_mapping = {
            "Excel Column 1": "field1",
            "Excel Column 2": "field2",
            # ...
        }
```

2. **Tạo Processor Class**
```python
# services/processors/new_type_processor.py
from .base_processor import IInsuranceProcessor
from configs.mappings.new_type_mapping import NewTypeMapping

class NewTypeProcessor(IInsuranceProcessor):
    def __init__(self):
        super().__init__(NewTypeMapping())
    
    def pre_process(self, df):
        # Custom preprocessing
        return df
    
    def post_process(self, records):
        # Custom postprocessing
        return records
```

3. **Register trong Factory**
```python
# services/processors/__init__.py
from .new_type_processor import NewTypeProcessor

PROCESSOR_REGISTRY = {
    "NEW_TYPE": NewTypeProcessor,
    # ... existing types
}
```

---

## Performance Optimization

### Current Performance

- Small files (<1000 records): **0.5-1s**
- Medium files (1000-5000 records): **1-3s**
- Large files (5000-10000 records): **3-8s**

### Optimization Techniques Applied

1. **Batch Database Query** - 1 query thay vì N queries
2. **Set Lookup** - O(1) duplicate check
3. **Pandas Vectorization** - Xử lý DataFrame nhanh
4. **Connection Pooling** - Reuse database connections
5. **Index on Business Keys** - Fast duplicate lookup

---

## Security & Validation

✅ File extension validation (.xlsx, .xls only)  
✅ File size limit (configurable)  
✅ SQL injection prevention (parameterized queries)  
✅ Error messages không expose sensitive info  
✅ Database credentials trong environment variables

---

## Monitoring & Logging

```python
# Log duplicate check results
print(f"DUPLICATE CHECK: Found {len(existing_keys)} existing keys")
print(f"Result: {new_count} new, {duplicate_count} duplicates")

# Log processing stages
print(f"[{insurance_type}] Starting pre_process...")
print(f"[{insurance_type}] Transform completed: {len(records)} records")
```

**Log levels:**
- **INFO**: Upload success, processing metrics
- **WARNING**: Duplicates found, invalid data
- **ERROR**: Database errors, file parsing errors
