# Issue: Thiếu thông tin người thụ hưởng khi người mua mua BH cho bản thân

---

## 1. Mô tả vấn đề

Hiện tại file Excel offline upload có 2 kiểu dữ liệu:

| Kiểu | Người mua (`payer`) | Người thụ hưởng (`insured`) |
|------|--------------------|-----------------------------|
| **Mua cho người khác** | Khác với người thụ hưởng | Có đầy đủ thông tin riêng |
| **Mua cho bản thân** | Chính là người thụ hưởng | Cột người thụ hưởng **để trống** |

Khi cột người thụ hưởng trống, hệ thống hiện tại không fill gì cả → database lưu `NULL` cho các trường `peopleName`, `peopleDob`, `peopleGender`, ... → dữ liệu reporting bị thiếu.

---

## 2. Mapping field theo loại BH

| Loại BH | Field người thụ hưởng | Field người mua |
|---------|----------------------|-----------------|
| HEALTH  | `peopleName`, `peopleDob`, `peopleGender`, `peopleLicense` | `stgContract.name`, `stgContract.dob` |
| VEHICLE | `peopleName`, `peopleDob`, `peopleGender`, `peopleLicense` | `stgContract.name`, `stgContract.dob` |
| SOCIAL  | `peopleName`, `peopleDob`, `peopleGender`, `peopleLicense` | `stgContract.name`, `stgContract.dob` |
| MEDICAL | `peopleName`, `peopleDob`, `peopleGender`, `peopleLicense` | `stgContract.name`, `stgContract.dob` |
| TRAVEL  | `name`, `dob`, `gender`, `license` | `payerName`, `payerDob` |
| MOTO    | `name`, `dob`, `gender`, `license` | *(không có cột riêng — cùng người)* |

---

## 3. Giải pháp

**Logic:** *Nếu thông tin người thụ hưởng bị trống → lấy từ thông tin người mua.*

Implement trong `post_process()` của từng processor, sau khi đã transform xong record từ Excel.

### 3.1 HEALTH / VEHICLE / SOCIAL / MEDICAL

File: `services/processors/health_processor.py`, `vehicle_processor.py`, `medical_social_processor.py`

Bổ sung vào method `post_process()`, sau các logic hiện có:

```python
for record in records:
    raw = record._raw_data

    # Nếu không có thông tin người thụ hưởng → người mua là người thụ hưởng
    # Lấy từ stgContract (contractId tương ứng) hoặc từ cột buyer trong Excel
    # Excel thường map: 'Họ tên' → 'name', 'Ngày sinh' → 'dob' (buyer info)
    if not raw.get('peopleName'):
        raw['peopleName'] = raw.get('name') or raw.get('buyerName')
        # Đồng thời set relationship = 0 (SELF/Bản thân)
        if raw.get('peopleName') and not raw.get('peopleRelationship'):
            raw['peopleRelationship'] = 0

    if not raw.get('peopleDob'):
        raw['peopleDob'] = raw.get('dob') or raw.get('buyerDob')

    if raw.get('peopleGender') is None:
        buyer_gender = raw.get('gender') or raw.get('buyerGender')
        if buyer_gender is not None:
            raw['peopleGender'] = buyer_gender

    if not raw.get('peopleLicense'):
        raw['peopleLicense'] = raw.get('license') or raw.get('buyerLicense')
```

> **Lưu ý:** Tên field buyer trong Excel có thể khác nhau tùy mapping. Cần kiểm tra `configs/mappings/health_mapping.py`, `vehicle_mapping.py`, `medical_social_mapping.py` để xác định đúng tên field sau khi đã rename.

### 3.2 TRAVEL

File: `services/processors/travel_processor.py`

Bổ sung vào `post_process()`:

```python
for record in records:
    raw = record._raw_data

    # Nếu không có thông tin người thụ hưởng → người mua là người thụ hưởng
    if not raw.get('name'):
        raw['name'] = raw.get('payerName')
        record.name = raw['name']

    if not raw.get('dob'):
        raw['dob'] = raw.get('payerDob')

    if raw.get('gender') is None:
        raw['gender'] = raw.get('payerGender')

    if not raw.get('license'):
        raw['license'] = raw.get('payerLicense')
```

### 3.3 MOTO

File: `services/processors/moto_processor.py`

MOTO không có cột payer riêng biệt (người mua = người thụ hưởng trong tất cả trường hợp). Không cần thay đổi logic — chỉ cần đảm bảo các trường `name`, `dob`, `gender`, `license` không bị drop khi NULL.

---

## 4. Điều kiện áp dụng

Logic chỉ fill khi **cả hai điều kiện** đều đúng:
1. Field người thụ hưởng bị `None` hoặc chuỗi rỗng sau khi đọc Excel
2. Field người mua tương ứng có giá trị

Không ghi đè nếu người thụ hưởng đã có thông tin riêng.

---
## 6. Lý do implement ở portal, không phải CDC pipeline

- Logic fill phải xảy ra **tại bước đọc Excel**, trước khi lưu vào `staging schema (insuranceWarehouse)`
- Nếu fix ở tầng CDC reporting (merge_etl), staging vẫn lưu NULL → data không đúng source of truth
- Portal là điểm entry của offline data → đây là nơi duy nhất có thể can thiệp trước khi data lan ra toàn pipeline
