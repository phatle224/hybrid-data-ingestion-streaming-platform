# 📋 Travel Insurance (Du lịch) — Field Mapping & Validation Rules

> File này mô tả mapping giữa **cột Excel upload** ↔ **field chuẩn giao nhận** ↔ **DB field**,
> kèm validation rules cho từng field dựa trên file chuẩn giao nhận BH du lịch.

---

## 🔑 Business Keys (4 fields KHÔNG được NULL)

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Nullable |
|---|---------------------|----------------------|----------|----------|
| 1 | `Số hợp đồng` | Số hợp đồng / Số GCNBH | `contractId` | ❌ NOT NULL |
| 2 | `Họ Và Tên` | Tên Người được BH | `peopleName` | ❌ NOT NULL |
| 3 | `Sản phẩm` | Loại bảo hiểm / Sản phẩm | `majorName` | ❌ NOT NULL |
| 4 | `Đối tác nhà BH` | Nhà Bảo Hiểm | `companyProviderName` | ❌ NOT NULL |

---

## 👤 Nhóm 1: Thông tin Người Được Bảo Hiểm (NĐBH)

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 1 | `Họ Và Tên` | Tên Người được BH | `peopleName` | string | **TRIM, UPPER, có dấu, giữ khoảng trắng giữa**. VD: `NGUYỄN VĂN A` | ❌ NOT NULL | ⚠️ Chưa UPPER |
| 2 | `Ngày sinh` | Ngày sinh NĐBH | `peopleDob` | date | **DD/MM/YYYY** → `YYYY-MM-DD`. VD: `01/01/1990` → `1990-01-01` | ❌ NOT NULL | ✅ Đã parse |
| 3 | `CCCD/CMND/Pasport ID` | Số CMTND/CCCD/Hộ chiếu NĐBH | `peopleLicense` | string | **Loại bỏ dấu " " (space), "." (dot), "-" (dash) và các ký tự đặc biệt**. Chỉ giữ số và chữ. | ❌ NOT NULL | ⚠️ Chưa clean |

> **Lưu ý:** Cột `CCCD/CMND/Pasport ID` có thể có typo `Paspost ID` (thiếu chữ r) trong một số file Excel. Mapping đã handle cả 2 trường hợp.

---

## 👨‍👩‍👧 Nhóm 2: Thông tin Người Mua BH (NMBH)

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 4 | `Họ tên người mua` | Tên người mua BH | `payerName` | string | **TRIM, UPPER, có dấu, giữ khoảng trắng giữa**. | ❌ NOT NULL | ⚠️ Chưa UPPER |
| 5 | `Ngày sinh.1` | Ngày sinh NMBH | `payerDob` | date | **DD/MM/YYYY** → `YYYY-MM-DD` | ✅ | ✅ Đã parse |
| 6 | `CCCD/CMND/Pasport ID người mua` | Số CCCD/Hộ chiếu NMBH | `payerLicense` | string | **Loại bỏ dấu " ", ".", "-" và ký tự đặc biệt**. | ❌ NOT NULL | ⚠️ Chưa clean |
| 7 | `Số Điện thoại NMBH` | SĐT NMBH | `payerPhone` | string | **TRIM, loại bỏ space/dash**. Format: bắt đầu 0, 10-11 chữ số (0+9-10 chữ số). | ✅ | ✅ Đã validate |

---

## ✈️ Nhóm 3: Thông tin Hành trình

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 8 | `Ngày đi` | Ngày đi | `startDateJourney` | date | **DD/MM/YYYY** → `YYYY-MM-DD`. Phải là ngày hợp lệ. | ❌ NOT NULL | ✅ Đã parse |
| 9 | `Ngày về` | Ngày về | `endDateJourney` | date | **DD/MM/YYYY** → `YYYY-MM-DD`. Phải > `startDateJourney`. | ❌ NOT NULL | ✅ Đã parse |
| 10 | `Số ngày` | Số ngày | `journey_days` | int | Phải > 0. | ❌ NOT NULL | ✅ Đã map |
| 11 | `Nơi đến` | Nơi đến | `destination_text` | string | **TRIM**. VD: Đà Lạt, Bangkok, Tokyo. | ✅ | ✅ Đã map |
| 12 | `Phạm vi` | Phạm vi (Nội địa/Quốc tế) | `domesticOrInternational_text` | string | **Enum:** Nội địa (Domestic), Quốc tế (International). | ❌ NOT NULL | ✅ Đã map |

---

## 📄 Nhóm 4: Thông tin Hợp Đồng & Phí

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 13 | `Số hợp đồng` | Số hợp đồng / GCNBH | `contractId` | string | **TRIM**. Không được trống. | ❌ NOT NULL | ✅ Đã map |
| 14 | `Phí bảo hiểm` | Phí Bảo Hiểm | `feeInsurance` | float | **Xóa dấu chấm ngàn** (VN: `2.980.800` → `2980800`). Phải >= 1,000. | ❌ NOT NULL | ✅ Đã validate |
| 15 | `Ngày thanh toán` | Ngày thanh toán | `payment_date` | date | **DD/MM/YYYY** → `YYYY-MM-DD` | ❌ NOT NULL | ✅ Đã parse |
| 16 | `Gói tham gia` | Gói tham gia | `packageName` | string | **TRIM**. VD: Gói Bạc, Gói Vàng, Gói Kim Cương. | ❌ NOT NULL | ✅ Đã map |
| 17 | `Plan tham gia` | Chương trình tham gia | `programName` | string | **TRIM**. | ✅ | ✅ Đã map |

---

## 📋 Nhóm 5: Thông tin Chung & Metadata

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 18 | `Sản phẩm` | Loại bảo hiểm / Sản phẩm | `majorName` | string | **TRIM**. Giá trị chuẩn. | ❌ | ✅ Đã map |
| 19 | `Đối tác nhà BH` | Nhà Bảo Hiểm | `companyProviderName` | string | **TRIM**. Giá trị chuẩn. | ❌ | ✅ Đã map |
| 20 | `Ngày` | Ngày upload | `upload_date` | date | **DD/MM/YYYY** → `YYYY-MM-DD`. | ✅ | ✅ Đã parse |
| 21 | `Tên sale` | Tên sale | `saleId` | string | **TRIM**. | ✅ | ✅ Đã map |
| 22 | `Channel` | Channel | `programCodeMiningChannel` | string | **TRIM**. **BẮT BUỘC** thuộc danh sách: `DSA`, `DSA/Renew`, `DSA_NEO`, `TSA`, `Renew`, `CTV_TSA (TSA 2)`, `CTV_TSA (TSA 2)/Renew`, `HO`, `Digital`, `Referral`. **Sai chính tả/định dạng sẽ bị từ chối.** | ❌ NOT NULL | ✅ Đã validate |
| 23 | `Hình thức thanh toán` | Hình thức thanh toán | `termsFeePaymentMethod` | string | **TRIM**. Có thể để trống (nullable). Không check enum. | ✅ Nullable (Có thể null) | ✅ Đã map |

---


---


---


---

## 🔍 Bảng Cập Nhật Kiểm Tra Null Nhanh (Quick Null Check)
> Bảng này tổng hợp nhanh các trường bắt buộc và tùy chọn để dễ hình dung tổng thể.

| STT | Cột Excel (Upload) | DB Field | Trạng thái Nullable |
|---|---|---|---|
| 1 | `Số hợp đồng` | `contractId` | ❌ NOT NULL |
| 2 | `Họ Và Tên` | `peopleName` | ❌ NOT NULL |
| 3 | `Sản phẩm` | `majorName` | ❌ NOT NULL |
| 4 | `Đối tác nhà BH` | `companyProviderName` | ❌ NOT NULL |
| 5 | `Ngày sinh` | `peopleDob` | ❌ NOT NULL |
| 6 | `CCCD/CMND/Pasport ID` | `peopleLicense` | ❌ NOT NULL |
| 7 | `Họ tên người mua` | `payerName` | ❌ NOT NULL |
| 8 | `Ngày sinh.1` | `payerDob` | ✅ Nullable (Có thể null) |
| 9 | `CCCD/CMND/Pasport ID người mua` | `payerLicense` | ❌ NOT NULL |
| 10 | `Số Điện thoại NMBH` | `payerPhone` | ✅ Nullable (Có thể null) |
| 11 | `Ngày đi` | `startDateJourney` | ❌ NOT NULL |
| 12 | `Ngày về` | `endDateJourney` | ❌ NOT NULL |
| 13 | `Số ngày` | `journey_days` | ❌ NOT NULL |
| 14 | `Nơi đến` | `destination_text` | ✅ Nullable (Có thể null) |
| 15 | `Phạm vi` | `domesticOrInternational_text` | ✅ Nullable (Có thể null) |
| 16 | `Phí bảo hiểm` | `feeInsurance` | ❌ NOT NULL |
| 17 | `Ngày thanh toán` | `payment_date` | ❌ NOT NULL |
| 18 | `Gói tham gia` | `packageName` | ❌ NOT NULL |
| 19 | `Plan tham gia` | `programName` | ✅ Nullable (Có thể null) |
| 20 | `Ngày` | `upload_date` | ✅ Nullable (Có thể null) |
| 21 | `Tên sale` | `saleId` | ❌ NOT NULL |
| 22 | `Channel` | `programCodeMiningChannel` | ❌ NOT NULL |
| 23 | `Hình thức thanh toán` | `termsFeePaymentMethod` | ✅ Nullable (Có thể null) |

## ⚠️ Các Rules CHƯA Được Implement (cần bổ sung)

| Rule | Field | Mô tả | Ưu tiên |
|------|-------|-------|---------|
| **UPPER** tên | `peopleName`, `payerName` | Tên phải viết HOA có dấu | 🔴 Cao |
| **Clean CCCD/Passport** | `peopleLicense`, `payerLicense` | Loại bỏ space, dot, dash, ký tự đặc biệt | 🔴 Cao |
| **Clean phone** | `payerPhone` | Loại bỏ space, dash. Validate 10-11 số | 🟡 Vừa |
| **Phí ≥ 0** | `feeInsurance` | Phí không được âm | 🟡 Vừa |
| **Date range** | `startDateJourney` < `endDateJourney` | Ngày đi phải trước ngày về | 🟡 Vừa |
| **Journey days** | `journey_days` | Chỉ kiểm tra > 0 (không đối chiếu với ngày đi/ngày về) | 🟡 Vừa |

---

## 📊 Ví Dụ Dữ Liệu Mẫu

```
peopleName:               "NGUYỄN VĂN A"        (UPPER, có dấu, trim)
peopleDob:                "1990-01-01"           (converted from 01/01/1990)
peopleLicense:            "001234567890"         (đã clean)
payerName:                "TRẦN THỊ B"           (UPPER, có dấu, trim)
payerPhone:               "0901234567"           (clean, 10 số)
contractId:               "HD-2024-001234"       (trim)
feeInsurance:             350000.0               (converted)
startDateJourney:         "2024-03-15"           (converted from 15/03/2024)
endDateJourney:           "2024-03-20"           (converted)
journey_days:             6
destination_text:         "Bangkok"
domesticOrInternational_text: "Quốc tế"
```

---

> **Ghi chú:** Travel có cả `peopleName` (NĐBH) và `payerName` (NMBH). Buyer-as-beneficiary
> fallback sẽ fill `peopleName` từ `payerName` nếu NĐBH trống. Cột CCCD có typo
> `Pasport`/`Paspost` — mapping đã handle.
