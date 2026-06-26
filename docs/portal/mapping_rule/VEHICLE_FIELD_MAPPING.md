# 📋 Vehicle Insurance (Ô tô) — Field Mapping & Validation Rules

> File này mô tả mapping giữa **cột Excel upload** ↔ **field chuẩn giao nhận** ↔ **DB field**,
> kèm validation rules cho từng field dựa trên file chuẩn giao nhận BH ô tô.

---

## 🔑 Business Keys (4 fields KHÔNG được NULL)

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Nullable |
|---|---------------------|----------------------|----------|----------|
| 1 | `Số GCN` | Số GCN (Giấy chứng nhận BH) | `contractId` | ❌ NOT NULL |
| 2 | `Tên khách hàng` | Tên Người được BH | `payerName` → `peopleName` | ❌ NOT NULL |
| 3 | `Sản phẩm` | Loại bảo hiểm / Sản phẩm | `majorName` | ❌ NOT NULL |
| 4 | `Đối tác nhà bảo hiểm` | Nhà Bảo Hiểm | `companyProviderName` | ❌ NOT NULL |

---

## 🚗 Nhóm 1: Thông tin Xe — Header màu VÀNG

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 1 | `Biển số` | Biển số | `licensePlate` | string | **TRIM, UPPER**. Loại bỏ ký tự đặc biệt, giữ chữ/số và dấu `-` | ⚠️ 2/3 opt | ⚠️ Chưa clean |
| 2 | `Số Khung` | Số khung | `chassisNumber` | string | **TRIM, UPPER**. Loại bỏ ký tự đặc biệt, chỉ giữ chữ/số.| ⚠️ 2/3 opt | ⚠️ Chưa clean |
| 3 | `Số Máy` | Số máy | `engineNumber` | string | **TRIM, UPPER**. Loại bỏ ký tự đặc biệt, chỉ giữ chữ/số. | ⚠️ 2/3 opt | ⚠️ Chưa clean |
| 4 | `Loại xe` | Loại xe | `packageName` | string | **TRIM**. Không cần enum | ❌ NOT NULL | ✅ Đã map |
| 5 | `Hiệu xe` | Hiệu xe / Nhãn hiệu | `maker` | string | **TRIM, UPPER**. VD: `TOYOTA`, `KIA`. | ❌ NOT NULL | ⚠️ Chưa UPPER |
| 6 | `Trọng tải đối với xe tải` | Trọng tải (tấn) | `weight` | float | Phải ≥ 0. Chỉ áp dụng cho xe tải. | ✅ | ✅ Đã map |
| 7 | `Số chỗ ngồi` | Số chỗ ngồi | `seatNumber` | int | Phải > 0. VD: 4, 5, 7, 9, 16, 45. | ❌ NOT NULL | ✅ Đã map |
| 8 | `Giá trị xe` | Giá trị xe | `vehicleValue` | float | **Xóa dấu chấm ngàn**. Phải ≥ 1,000. loại bỏ ký tự đặc biệt như đ,.. | ✅ | ⚠️ Chưa validate |
| 9 | `Mục đích sử dụng` | Mục đích sử dụng | `usagePurpose` | string | **TRIM**. Enum: Cá nhân, Kinh doanh, etc. | ❌ NOT NULL | ✅ Đã map |
| 10 | `Năm SX` | Năm sản xuất | `manufactureYear` | int | Phải trong range hợp lý (1990 - năm hiện tại). | ✅ | ⚠️ Chưa validate |

---

## 👤 Nhóm 2: Thông tin Khách hàng — Header màu VÀNG

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 11 | `Tên khách hàng` | Tên Người được BH | `payerName` | string | **TRIM, có dấu, giữ khoảng trắng giữa**. VD: `NGUYỄN VĂN A` | ❌ | ⚠️ Chưa UPPER |
| 12 | `Số điện thoại` | SĐT | `payerPhone` | string | **TRIM, loại bỏ space/dash**. Format: **0 + 9-10 chữ số**. Regex: `^0\d{9,10}$` | ❌ NOT NULL | ✅ Đã validate |
| 13 | `email` | Email | `payerEmail` | string | **TRIM, LOWER**. Format: phải chứa ký tự `@`. | ❌ NOT NULL | ✅ Đã validate |
| 14 | `địa chỉ` | Địa chỉ | `payerAddress` | string | **TRIM**. Giữ dấu tiếng Việt. | ✅ | ✅ Đã trim |

---

## 💰 Nhóm 3: Thông tin Phí & Hợp đồng

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 15 | `Số GCN` | Số GCN (Số Giấy chứng nhận BH) | `contractId` | string | **TRIM**. Không được trống. | ❌ | ✅ Đã map |
| 16 | `Số tiền` | Số tiền thanh toán / Phí BH | `feeInsurance` | float | **Xóa dấu chấm ngàn**: `2.980.800` → `2980800`. Phải ≥ 1.000. Nếu < 1.000 → kiểm tra sai đơn vị (ví dụ 66 → 66.000). | ❌ NOT NULL | ✅ Đã validate |

---

## 📅 Nhóm 4: Ngày tháng

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 17 | `Ngày thanh toán` | Ngày thanh toán | `payment_date` | date | **DD/MM/YYYY** → `YYYY-MM-DD` | ❌ NOT NULL | ✅ Đã parse |
| 18 | `Giờ bắt đầu` | Giờ bắt đầu hiệu lực | `start_time` | time | **HH:MM** format. | ✅ | ✅ Đã map |
| 19 | `Ngày bắt đầu hiệu lực` + `Giờ bắt đầu` | Ngày + Giờ hiệu lực bắt đầu | `contractObjectStartDate` | datetime | **Date: DD/MM/YYYY** → `YYYY-MM-DD` **+ Time: HH:MM** từ cột `Giờ bắt đầu`. Kết hợp: `YYYY-MM-DD HH:MM`. Ngày bắt đầu. | ❌ NOT NULL | ✅ Đã parse |
| 20 | `Giờ kết thúc` | Giờ kết thúc hiệu lực | `end_time` | time | **HH:MM** format. | ✅ | ✅ Đã map |
| 21 | `Ngày kết thúc hiệu lực` + `Giờ kết thúc` | Ngày + Giờ kết thúc | `contractObjectEndDate` | datetime | **Date: DD/MM/YYYY** → `YYYY-MM-DD` **+ Time: HH:MM** từ cột `Giờ kết thúc`. Kết hợp: `YYYY-MM-DD HH:MM`. Phải > `contractObjectStartDate`. Ít nhất 1 ngày kể từ ngày bắt đầu. | ❌ NOT NULL | ✅ Đã parse |
| 22 | `Số ngày bảo hiểm` | Số ngày BH | `contractPeriodValue` | int | Phải > 0. Số nguyên dương. | ❌ NOT NULL | ✅ Đã map |

---

## 📋 Nhóm 5: Thông tin Chung & Metadata

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 23 | `Sản phẩm` | Loại bảo hiểm / Sản phẩm | `majorName` | string | **TRIM**. | ❌ | ✅ Đã map |
| 24 | `Sản Phẩm` (cột 2) | Tên sản phẩm (2) | `productName_2` | string | **TRIM**. Xử lý đồng bộ cùng 1 định dạng. | ❌ NOT NULL | ✅ Đã map |
| 25 | `Đối tác nhà bảo hiểm` | Nhà Bảo Hiểm | `companyProviderName` | string | **TRIM**. Giá trị chuẩn. | ❌ NOT NULL | ✅ Đã map |
| 26 | `Chương trình` | Tên chương trình | `programName` | string | **TRIM**. | ✅ | ✅ Đã map |
| 27 | ` ` (blank header) | Ngày cập nhật | `modifiedAt` | date | **DD/MM/YYYY** → `YYYY-MM-DD`. DD/MM/YY <= CURDATE / NOW. | ✅ | ✅ Đã parse |
| 28 | `Code sale` | Code sale | `saleId` | string | **TRIM**. Số điện thoại: 0 + 9-10 chữ số. Format: `^0\d{9,10}$` | ❌ NOT NULL | ✅ Đã map |
| 29 | `Channel` | Channel | `programCodeMiningChannel` | string | **TRIM**. **BẮT BUỘC** phải nằm trong danh sách: `DSA`, `DSA/Renew`, `DSA_NEO`, `TSA`, `Renew`, `CTV_TSA (TSA 2)`, `CTV_TSA (TSA 2)/Renew`, `HO`, `Digital`, `Referral`. **Sai chính tả hoặc định dạng sẽ bị từ chối upload.** | ❌ NOT NULL | ✅ Đã validate |
| 30 | `Hình thức thanh toán` | Hình thức thanh toán | `termsFeePaymentMethod` | string | **Enum:** Chọn từ bảng set up: Chuyển khoản nhà BH, Chuyển khoản InsuStream, Payco, OCB, POS, Renew, Payment, DSA. | ✅ | ✅ Đã map |
| 31 | `Note` | Ghi chú | `note` | string | **TRIM**. | ✅ | ✅ Đã map |

---


---


---


---

## 🔍 Bảng Cập Nhật Kiểm Tra Null Nhanh (Quick Null Check)
> Bảng này tổng hợp nhanh các trường bắt buộc và tùy chọn để dễ hình dung tổng thể.

| STT | Cột Excel (Upload) | DB Field | Trạng thái Nullable |
|---|---|---|---|
| 1 | `Số GCN` | `contractId` | ❌ NOT NULL |
| 2 | `Tên khách hàng` | `payerName → peopleName` | ❌ NOT NULL |
| 3 | `Sản phẩm` | `majorName` | ❌ NOT NULL |
| 4 | `Đối tác nhà bảo hiểm` | `companyProviderName` | ❌ NOT NULL |
| 5 | `Biển số` | `licensePlate` | ⚠️ Tùy chọn 2/3 |
| 6 | `Số Khung` | `chassisNumber` | ⚠️ Tùy chọn 2/3 |
| 7 | `Số Máy` | `engineNumber` | ⚠️ Tùy chọn 2/3 |
| 8 | `Loại xe` | `packageName` | ❌ NOT NULL |
| 9 | `Hiệu xe` | `maker` | ❌ NOT NULL | 
| 10 | `Trọng tải đối với xe tải` | `weight` | ✅ Nullable (Có thể null) | bỏ, ko map
| 11 | `Số chỗ ngồi` | `seatNumber` | ❌ NOT NULL |
| 12 | `Giá trị xe` | `vehicleValue` | ✅ Nullable (Có thể null) | bỏ, ko map
| 13 | `Mục đích sử dụng` | `usagePurpose` | ❌ NOT NULL | bỏ, ko map
| 14 | `Năm SX` | `manufactureYear` | ✅ Nullable (Có thể null) | bỏ, ko map
| 15 | `Tên khách hàng` | `payerName` | ❌ NOT NULL |
| 16 | `Số điện thoại` | `payerPhone` | ❌ NOT NULL |
| 17 | `email` | `payerEmail` | ❌ NOT NULL |
| 18 | `địa chỉ` | `payerAddress` | ✅ Nullable (Có thể null) |
| 19 | `Số tiền` | `feeInsurance` | ❌ NOT NULL |
| 20 | `Ngày thanh toán` | `payment_date` | ❌ NOT NULL |
| 21 | `Giờ bắt đầu` | `start_time` | ✅ Nullable (Có thể null) | bỏ, ko map
| 22 | `Ngày bắt đầu hiệu lực` | `contractObjectStartDate` | ❌ NOT NULL |
| 23 | `Giờ kết thúc` | `end_time` | ✅ Nullable (Có thể null) | bỏ, ko map
| 24 | `Ngày kết thúc hiệu lực` | `contractObjectEndDate` | ❌ NOT NULL |
| 25 | `Số ngày bảo hiểm` | `contractPeriodValue` | ❌ NOT NULL |
| 26 | `Sản Phẩm` (cột 2) | `productName_2` | ❌ NOT NULL | bỏ, ko map
| 27 | `Chương trình` | `programName` | ✅ Nullable (Có thể null) |
| 28 | ` ` (blank header) | `modifiedAt` | ✅ Nullable (Có thể null) |
| 29 | `Code sale` | `saleId` | ❌ NOT NULL |
| 30 | `Channel` | `programCodeMiningChannel` | ❌ NOT NULL |
| 31 | `Hình thức thanh toán` | `termsFeePaymentMethod` | ✅ Nullable (Có thể null) |
| 32 | `Note` | `note` | ✅ Nullable (Có thể null) |

## ⚠️ Các Rules Đã Implement / Đang Cập Nhật

| Rule | Field | Mô tả | Status | Ghi chú |
|------|-------|-------|--------|----------|
| **Phone format** | `payerPhone` | Loại bỏ space, dash. Format: `0 + 9-10 số`. Regex: `^0\d{9,10}$` | ✅ Đã validate | Sync với Moto |
| **Email format** | `payerEmail` | Phải chứa `@`. TRIM + LOWER. | ✅ Đã validate | Sync với Moto |
| **Phí ≥ 1.000** | `feeInsurance` | Xóa dấu phân cách. Phải ≥ 1.000. Sai đơn vị? Ví dụ 66 → 66.000. | ✅ Đã validate | Sync với Moto |
| **Date + Time** | `contractObjectStartDate` | Kết hợp Ngày (DD/MM/YYYY) + Giờ (HH:MM). Format: `YYYY-MM-DD HH:MM` | ✅ Đã adjust | **Mới** |
| **Date + Time** | `contractObjectEndDate` | Kết hợp Ngày (DD/MM/YYYY) + Giờ (HH:MM). Format: `YYYY-MM-DD HH:MM`. Phải > StartDate. | ✅ Đã adjust | **Mới** |
| **UPPER** tên | `payerName` → `peopleName` | Tên phải viết HOA có dấu | ⏳ Chưa | Ưu tiên cao |
| **Clean biển số** | `licensePlate` | Xóa space/dash, standardize format | ⏳ Chưa | Ưu tiên cao |
| **Clean số khung/máy** | `chassisNumber`, `engineNumber` | Xóa space, dash | ⏳ Chưa | Ưu tiên cao |
| **Năm SX valid** | `manufactureYear` | 1990 ≤ năm ≤ năm hiện tại | ⏳ Chưa | Ưu tiên vừa |
| **Channel validate** | `programCodeMiningChannel` | Phải thuộc danh sách: DSA, DSA/Renew, DSA_NEO, TSA, Renew, CTV_TSA (TSA 2), CTV_TSA (TSA 2)/Renew, HO, Digital, Referral | ✅ Đã validate | **Mới - Quan trọng** |

---

## 📊 Ví Dụ Dữ Liệu Mẫu

```
payerName (→peopleName): "CÔNG TY A"            (TRIM, có dấu)
licensePlate:             "51A12345"             (TRIM, UPPER, giữ dấu `-`)
chassisNumber:            "MRHGD81D1PP123456"    (TRIM, UPPER)
engineNumber:             "1NR1234567"           (TRIM, UPPER)
packageName:              "Xe con"               (TRIM)
maker:                    "TOYOTA"               (TRIM, UPPER)
seatNumber:               5
contractId:               "GCN-2024-001"         (TRIM)
payerPhone:               "0912345678"           (loại bỏ space/dash)
payerEmail:               "customer@example.com" (TRIM, LOWER)
feeInsurance:             1061199.0              (converted, xóa dấu phân cách)
contractObjectStartDate:  "2025-11-26 08:00"     (converted from 26/11/2025 + 08:00)
contractObjectEndDate:    "2026-11-25 18:00"     (converted from 25/11/2026 + 18:00)
```

---

## 🚫 Các Cột KHÔNG Được Mapping vào Database

> Các cột sau chỉ dùng để tham khảo trong Excel upload nhưng **KHÔNG** được xử lý/lưu vào database:

| # | Cột Excel | DB Field | Lý do | Ghi chú |
|---|-----------|----------|---------|----------|
| 1 | `Trọng tải đối với xe tải` | `weight` | Thông tin không cần lưu staging | Chỉ áp dụng xe tải |
| 2 | `Giá trị xe` | `vehicleValue` | Thông tin không cần lưu staging | Không validate |
| 3 | `Mục đích sử dụng` | `usagePurpose` | Thông tin không cần lưu staging | Enum: Cá nhân, Kinh doanh |
| 4 | `Năm SX` | `manufactureYear` | Thông tin không cần lưu staging | Range: 1990 - hiện tại |
| 5 | `Giờ bắt đầu` | `start_time` | Đã merge vào `contractObjectStartDate` | Không lưu riêng |
| 6 | `Giờ kết thúc` | `end_time` | Đã merge vào `contractObjectEndDate` | Không lưu riêng |
| 7 | `Sản Phẩm` (cột 2) | `productName_2` | Thông tin không cần lưu staging | Xử lý riêng |

---

> **Ghi chú:** 
> - Vehicle là loại BH đơn giản (buyer = insured), nên `payerName` sẽ được mirror sang `peopleName` trong `post_process()`.
> - Vehicle có nhiều field xe cần cleaning: **biển số** (TRIM, UPPER, giữ dấu `-`), **số khung/máy** (TRIM, UPPER, chỉ chữ/số).
> - **Field mới**: `packageName` thay `vehicleType`, `maker` thay `brand`.
> - **Datetime merge**: `contractObjectStartDate` và `contractObjectEndDate` được tạo từ kết hợp ngày + giờ từ 2 cột riêng biệt.
> - **7 cột không map**: Xem phần "Các Cột KHÔNG Được Mapping vào Database" ở trên.
