# [Portal → CDC] Thay đổi Business Key: `name` → `payerName`

> **Ngày:** 10/03/2026  
> **Phạm vi ảnh hưởng:** Business key dùng để check trùng (dedup), cả Portal lẫn CDC

---

## 1. Bối cảnh

Field `name` ở Portal trước đây bị dùng không nhất quán:
- Loại VEHICLE, HAZARD: `name` = tên **người được bảo hiểm** (insured)
- Loại MOTO: `name` = tên **chủ xe** (owner/buyer)
- Loại HEALTH, MEDICAL_SOCIAL, TRAVEL: `name` đôi khi là buyer, đôi khi là insured

Để phân biệt rõ ràng, Portal đã chuẩn hóa thành 2 field riêng biệt:

| Field | Ý nghĩa | Vai trò trong business key |
|---|---|---|
| `payerName` | Người **mua** bảo hiểm (bên mua BH) | ✅ **Business key mới** |
| `peopleName` | Người **được** bảo hiểm (NĐBH) | Không dùng trong business key |
| `name` | Legacy, giữ lại nhưng **không dùng** cho mapping mới | ❌ Không còn là business key |

---

## 2. Thay đổi Business Key

### Trước (cũ)
```
contractId + name + majorName + companyProviderName
```

### Sau (mới)
```
contractId + payerName + majorName + companyProviderName
```

> **Lưu ý quan trọng:** Field `name` vẫn tồn tại trong bảng `stgContractObjectOffline` nhưng Portal **không còn ghi dữ liệu vào đó** nữa. Giá trị `name` trong DB sẽ là `NULL` với tất cả record mới.

---

## 3. Mapping Excel → DB field mới theo từng loại bảo hiểm

### VEHICLE (Ô tô)
| Cột Excel | DB field cũ | DB field mới |
|---|---|---|
| Tên khách hàng | `peopleName` | `payerName` ← **đổi** |
| Số điện thoại | `peoplePhone` | `payerPhone` ← **đổi** |
| email | `peopleEmail` | `payerEmail` ← **đổi** |
| địa chỉ | `peopleAddress` | `payerAddress` ← **đổi** |

Post-process: `payerName` → mirror → `peopleName` (vì buyer = insured với xe ô tô)

### MOTO (Xe máy)
| Cột Excel | DB field cũ | DB field mới |
|---|---|---|
| TÊN KHÁCH HÀNG | `name` | `payerName` ← **đổi** |
| SỐ ĐIẸN THOẠI | `phone` | `payerPhone` ← **đổi** |
| Email | `email` | `payerEmail` ← **đổi** |

Post-process: `payerName` → mirror → `peopleName`

### HAZARD (Rủi ro)
| Cột Excel | DB field cũ | DB field mới |
|---|---|---|
| Tên khách hàng | `peopleName` | `payerName` ← **đổi** |

Post-process: `payerName` → mirror → `peopleName`

### TRAVEL (Du lịch)
| Cột Excel | DB field cũ | DB field mới |
|---|---|---|
| Họ Và Tên (insured) | `name` | `peopleName` ← **đổi** |
| Ngày sinh (insured) | `dob` | `peopleDob` ← **đổi** |
| CCCD/CMND (insured) | `license` | `peopleLicense` ← **đổi** |
| Họ tên người mua | `payerName` | `payerName` (giữ nguyên) |

Business key dùng `payerName` (người mua). Fallback: nếu `peopleName` trống → copy từ `payerName`.

### HEALTH (Sức khỏe) & MEDICAL_SOCIAL (BHYT/BHXH)
- Mapping field giữ nguyên (`payerName`, `peopleName` đã đúng từ trước)
- **Thay đổi:** `get_name_field()` trả về `'payerName'` thay vì `'peopleName'`
- Business key nay dùng `payerName` (người mua) thay vì `peopleName`

---

## 4. Cần CDC cập nhật

### 4.1 Redis duplicate check key

Nếu CDC đang dùng Redis để cache/check trùng theo pattern:
```
# Cũ
key = f"{contractId}:{name}:{majorName}:{companyProviderName}"

# Mới — phải đổi thành:
key = f"{contractId}:{payerName}:{majorName}:{companyProviderName}"
```

### 4.2 Query check trùng từ DB

Nếu CDC query trực tiếp từ `stgContractObjectOffline` để check trùng:
```sql
-- Cũ
WHERE contractId = ? AND (name = ? OR peopleName = ?) AND majorName = ? AND companyProviderName = ?

-- Mới
WHERE contractId = ? AND payerName = ? AND majorName = ? AND companyProviderName = ?
```

### 4.3 Đọc dữ liệu từ Portal

Khi CDC đọc record từ `stgContractObjectOffline`:
- Field `name` sẽ là `NULL` với tất cả record mới từ Portal
- Dùng `payerName` để lấy tên người mua
- Dùng `peopleName` để lấy tên người được bảo hiểm

---

## 5. Schema DB không thay đổi

Bảng `stgContractObjectOffline` **không cần ALTER TABLE**. Tất cả các field (`name`, `payerName`, `peopleName`, v.v.) đã tồn tại sẵn. Chỉ cần cập nhật logic đọc/ghi ở tầng application.

---

## 6. Tóm tắt nhanh cho CDC dev

```
CŨ: business key = contractId + name + majorName + companyProviderName
MỚI: business key = contractId + payerName + majorName + companyProviderName

- name       → NULL (không dùng nữa, legacy)
- payerName  → Người MUA bảo hiểm (business key)
- peopleName → Người ĐƯỢC bảo hiểm (không phải business key)
```
