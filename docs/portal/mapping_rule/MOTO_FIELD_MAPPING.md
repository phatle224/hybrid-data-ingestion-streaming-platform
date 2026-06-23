# 📋 Moto Insurance (Xe máy) — Field Mapping & Validation Rules

> File này mô tả mapping giữa **cột Excel upload** ↔ **field chuẩn giao nhận** ↔ **DB field**,
> kèm validation rules cho từng field dựa trên file chuẩn giao nhận BH xe máy.

---

## 🔑 Business Keys (4 fields KHÔNG được NULL)

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Nullable |
|---|---------------------|----------------------|----------|----------|
| 1 | `Số hợp đồng` | Số hợp đồng | `contractId` | ❌ NOT NULL |
| 2 | `TÊN KHÁCH HÀNG` | Tên Người được BH / Tên khách hàng | `payerName` → `peopleName` | ❌ NOT NULL |
| 3 | `Sản phẩm` | Loại bảo hiểm / Sản phẩm | `majorName` | ❌ NOT NULL |
| 4 | `Đối tác nhà bảo hiểm` | Nhà Bảo Hiểm | `companyProviderName` | ❌ NOT NULL |

---

## 🏍️ Nhóm 1: Thông tin Xe — Header màu VÀNG

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 1 | `BIỂN SỐ XE` | Biển số xe | `licensePlates` | string | **TRIM, UPPER**. Loại bỏ ký tự đặc biệt, giữ chữ/số và dấu `-`. | ⚠️ 2/3 opt | ✅ Đã clean |
| 2 | `SỐ KHUNG` | Số khung | `chassisNumber` | string | **TRIM, UPPER**. Loại bỏ ký tự đặc biệt, chỉ giữ chữ/số. | ⚠️ 2/3 opt | ✅ Đã clean |
| 3 | `SỐ MÁY` | Số máy | `engineNumber` | string | **TRIM, UPPER**. Loại bỏ ký tự đặc biệt, chỉ giữ chữ/số. | ⚠️ 2/3 opt | ✅ Đã clean |
| 4 | `NHÃN HIỆU XE` | Nhãn hiệu xe | `maker` | string | **TRIM, UPPER**. VD: `HONDA`, `YAMAHA`. | ✅ | ✅ Đã map |
| 5 | `LOẠI XE` | Loại xe | `packageName` | string | Mapped để lưu thông tin loại xe. Không bắt buộc, không validate riêng. | ✅ Nullable (Có thể null) | ✅ Đã map |

---

## 👤 Nhóm 2: Thông tin Khách hàng — Header màu VÀNG

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 5 | `TÊN KHÁCH HÀNG` | Tên Người được BH / Người sở hữu | `payerName` | string | **TRIM, giữ kiểu viết bình thường**. VD: `Nguyễn Văn A` | ❌ | ✅ Đã normalize |
| 6 | `SỐ ĐIẸN THOẠI` | SĐT | `payerPhone` | string | **TRIM, loại bỏ ký tự thừa**. Format: bắt đầu 0, 10-11 chữ số (0+9-10 chữ số). | ❌ NOT NULL | ✅ Đã validate |
| 7 | `Email` | Email | `payerEmail` | string | **TRIM, LOWER**. Validate format tối thiểu phải chứa `@`. | ❌ NOT NULL | ✅ Đã validate |

---

## 💰 Nhóm 3: Thông tin Phí & Hợp đồng — Header màu XANH LÁ

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 8 | `Số hợp đồng` | Số hợp đồng | `contractId` | string | **TRIM**. Không được trống. | ❌ | ✅ Đã map |
| 9 | `PHÍ BẢO HIỂM TNDS BẮT BUỘC` | Phí bảo hiểm TNDS bắt buộc | `feeMainBenefit` | float | **Xóa dấu chấm ngàn**. Nếu có dữ liệu thì phải >= 1,000. | ✅ Nullable (Có thể null) | ✅ Đã validate |
| 10 | `PHÍ BẢO HIỂM TAI NẠN NNTX` | Phí BH tai nạn người ngồi trên xe | `feeSideBenefit` | float | **Xóa dấu chấm ngàn**. Nếu có dữ liệu thì phải >= 1,000. | ✅ Nullable (Có thể null) | ✅ Đã validate |
| 11 | `TỔNG PHÍ BẢO HIỂM` | Phí Bảo Hiểm (tổng) | `feeInsurance` | float | **Xóa dấu chấm ngàn**. Phải >= 1,000. Không bắt buộc bằng tổng 2 phí thành phần. | ❌ NOT NULL | ✅ Đã validate |
| 12 | `SỐ NĂM` | Số năm BH | `contractPeriodValue` | int | Phải > 0. Thường = 1, 2, 3. Nếu trong file NULL thì tự tính, lấy ngày kết thúc - ngày bắt đầu rồi mới tính tới trường hợp NULL | ✅ | ✅ Đã map |

---

## 📅 Nhóm 4: Ngày tháng — Header màu XANH LÁ

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 13 | `NGÀY CẤP ĐƠN` | Ngày cấp đơn | `issue_date` | date | **DD/MM/YYYY** → `YYYY-MM-DD` | ✅ | ✅ Đã parse |
| 14 | `NGÀY BẮT ĐẦU` | Ngày hiệu lực bắt đầu | `contractObjectStartDate` | date | Input **DD/MM/YYYY** (hệ thống parse nội bộ). | ❌ NOT NULL | ✅ Đã validate |
| 15 | `NGÀY KẾT THÚC` | Ngày kết thúc | `contractObjectEndDate` | date | Input **DD/MM/YYYY** (hệ thống parse nội bộ). Phải >= `contractObjectStartDate`. | ❌ NOT NULL | ✅ Đã validate |

---

## 📋 Nhóm 5: Thông tin Chung & Metadata

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 16 | `Sản phẩm` | Loại bảo hiểm / Sản phẩm | `majorName` | string | **TRIM**. Giá trị chuẩn. | ❌ | ✅ Đã map |
| 17 | `Đối tác nhà bảo hiểm` | Nhà Bảo Hiểm | `companyProviderName` | string | **TRIM**. Giá trị chuẩn. | ❌ | ✅ Đã map |
| 18 | `Chương trình` | Tên chương trình | `programName` | string | **TRIM**. | ✅ | ✅ Đã map |
| 19 | `Ngày update` | Ngày cập nhật | `modifiedAt` | date | **DD/MM/YYYY** → `YYYY-MM-DD`. | ✅ | ✅ Đã parse |
| 20 | `Code sale` | Code sale | `saleId` | string | **TRIM**. | ✅ | ✅ Đã map |
| 21 | `Channel` | Channel | `programCodeMiningChannel` | string | **TRIM**. **BẮT BUỘC** thuộc danh sách: `DSA`, `DSA/Renew`, `DSA_NEO`, `TSA`, `Renew`, `CTV_TSA (TSA 2)`, `CTV_TSA (TSA 2)/Renew`, `HO`, `Digital`, `Referral`. **Sai chính tả/định dạng sẽ bị từ chối.** | ❌ NOT NULL | ✅ Đã validate |
| 22 | `Hình thức thanh toán` | Hình thức thanh toán | `termsFeePaymentMethod` | string | **TRIM**. Có thể để trống (nullable). Không check enum. | ✅ Nullable (Có thể null) | ✅ Đã map |

---


---


---


---

## 🔍 Bảng Cập Nhật Kiểm Tra Null Nhanh (Quick Null Check)
> Bảng này tổng hợp nhanh các trường bắt buộc và tùy chọn để dễ hình dung tổng thể.

| STT | Cột Excel (Upload) | DB Field | Trạng thái Nullable |
|---|---|---|---|
| 1 | `Số hợp đồng` | `contractId` | ❌ NOT NULL |
| 2 | `TÊN KHÁCH HÀNG` | `payerName → peopleName` | ❌ NOT NULL |
| 3 | `Sản phẩm` | `majorName` | ❌ NOT NULL |
| 4 | `Đối tác nhà bảo hiểm` | `companyProviderName` | ❌ NOT NULL |
| 5 | `BIỂN SỐ XE` | `licensePlates` | ⚠️ Tùy chọn 2/3 |
| 6 | `SỐ KHUNG` | `chassisNumber` | ⚠️ Tùy chọn 2/3 |
| 7 | `SỐ MÁY` | `engineNumber` | ⚠️ Tùy chọn 2/3 |
| 8 | `NHÃN HIỆU XE` | `maker` | ✅ Nullable (Có thể null) |
| 9 | `TÊN KHÁCH HÀNG` | `payerName` | ❌ NOT NULL |
| 10 | `SỐ ĐIẸN THOẠI` | `payerPhone` | ❌ NOT NULL |
| 11 | `Email` | `payerEmail` | ❌ NOT NULL |
| 12 | `PHÍ BẢO HIỂM TNDS BẮT BUỘC` | `feeMainBenefit` | ✅ Nullable (Có thể null) |
| 13 | `PHÍ BẢO HIỂM TAI NẠN NNTX` | `feeSideBenefit` | ✅ Nullable (Có thể null) |
| 14 | `TỔNG PHÍ BẢO HIỂM` | `feeInsurance` | ❌ NOT NULL |
| 15 | `SỐ NĂM` | `contractPeriodValue` | ✅ Nullable (Có thể null) |
| 16 | `NGÀY CẤP ĐƠN` | `issue_date` | ✅ Nullable (Có thể null) |
| 17 | `NGÀY BẮT ĐẦU` | `contractObjectStartDate` | ❌ NOT NULL |
| 18 | `NGÀY KẾT THÚC` | `contractObjectEndDate` | ❌ NOT NULL |
| 19 | `Chương trình` | `programName` | ✅ Nullable (Có thể null) |
| 20 | `Ngày update` | `modifiedAt` | ✅ Nullable (Có thể null) |
| 21 | `Code sale` | `saleId` | ❌ NOT NULL |
| 22 | `Channel` | `programCodeMiningChannel` | ❌ NOT NULL |
| 23 | `Hình thức thanh toán` | `termsFeePaymentMethod` | ✅ Nullable (Có thể null) |
| 24 | `Loại xe` | `packageName` | ✅ Nullable (Có thể null) |

## ✅ Các Rules Đã Implement

| Rule | Field | Mô tả | Ưu tiên |
|------|-------|-------|---------|
| **Trim + mirror tên** | `payerName` → `peopleName` | Buyer = insured cho Moto (không ép UPPER) | ✅ Done |
| **Clean biển số** | `licensePlates` | Xóa ký tự lạ, giữ chữ/số và dấu `-` | ✅ Done |
| **Clean số khung/máy** | `chassisNumber`, `engineNumber` | Chỉ giữ chữ/số, UPPER | ✅ Done |
| **Clean phone + validate** | `payerPhone` | Validate bắt đầu 0, 10-11 số | ✅ Done |
| **Email validate** | `payerEmail` | Validate tối thiểu phải chứa `@` | ✅ Done |
| **Phí thành phần** | `feeMainBenefit`, `feeSideBenefit` | Ít nhất 1 trong 2 field phải có dữ liệu; nếu có thì >= 1,000 | ✅ Done |
| **Tổng phí** | `feeInsurance` | Phải >= 1,000; không check bằng tổng 2 phí thành phần | ✅ Done |
| **Date range** | `contractObjectStartDate` <= `contractObjectEndDate` | End phải >= Start | ✅ Done |
| **Vehicle IDs 2/3** | `licensePlates`, `chassisNumber`, `engineNumber` | Cần tối thiểu 2/3 trường có dữ liệu | ✅ Done |

---

## 🧩 Color Coding từ File Chuẩn

| Màu | Ý nghĩa | Fields |
|-----|---------|--------|
| 🟡 **Vàng** | Thông tin xe & khách hàng (bắt buộc/quan trọng) | licensePlates, chassisNumber, engineNumber, payerName, payerPhone |
| 🟢 **Xanh lá** | Thông tin hợp đồng & thanh toán | contractId, fees, dates, paymentMethod |
| 🟣 **Tím** | (Không có ở Moto) | — |
| 🟡 **Vàng đậm** | Channel, Code sale | programCodeMiningChannel, saleId |

---

## 📊 Ví Dụ Dữ Liệu Mẫu

```
payerName (→peopleName): "Nguyễn Văn A"        (trim, giữ kiểu viết bình thường)
licensePlates:            "51F112345"            (đã clean space)
chassisNumber:            "RLHJC1106PY123456"    (UPPER, trim)
engineNumber:             "JC11E1234567"         (UPPER, trim)
contractId:               "HD-2024-001234"       (trim)
feeMainBenefit:           66000.0                (converted)
feeSideBenefit:           20000.0                (converted)
feeInsurance:             86000.0                (sum)
contractObjectStartDate:  "2024-01-15"           (converted from DD/MM/YYYY)
```

---

> **Ghi chú:** Moto là loại BH đơn giản (buyer = insured), nên `payerName` sẽ được mirror sang
> `peopleName` trong `post_process()`. Các field vehicle-specific (biển số, số khung, số máy)
> cần cleaning rules riêng (UPPER, xóa ký tự đặc biệt).
