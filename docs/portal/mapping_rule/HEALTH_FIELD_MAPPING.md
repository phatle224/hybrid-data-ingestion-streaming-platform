# 📋 Health Insurance (Sức khỏe) — Field Mapping & Validation Rules

> File này mô tả mapping giữa **cột Excel upload** ↔ **field chuẩn giao nhận** ↔ **DB field**, 
> kèm validation rules cho từng field dựa trên file chuẩn giao nhận BH sức khỏe.

> Rule upload hiện tại: **chỉ import khi toàn bộ file hợp lệ**. Nếu còn 1 dòng lỗi thì toàn bộ file sẽ bị chặn và không import một phần.

---

## 🔑 Business Keys (6 fields KHÔNG được NULL)

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Nullable |
|---|---------------------|----------------------|----------|----------|
| 1 | `Số hợp đồng` | Số đơn bảo hiểm / Số GCNBH | `contractId` | ❌ NOT NULL |
| 2 | `Thông tin Người được bảo hiểm` | Tên người được bảo hiểm (NĐBH) | `peopleName` → `name` | ❌ NOT NULL |
| 3 | `Sản phẩm` | Sản phẩm bảo hiểm | `majorName` | ❌ NOT NULL |
| 4 | `Nhà bảo hiểm` | Tên công ty bảo hiểm | `companyProviderName` | ❌ NOT NULL |
| 5 | `Ngày bắt đầu` | Ngày bắt đầu hiệu lực | `contractStartDate` | ❌ NOT NULL |
| 6 | `Ngày kết thúc` | Ngày kết thúc hiệu lực | `contractEndDate` | ❌ NOT NULL |

---

## 👤 Nhóm 1: Thông tin Người Được Bảo Hiểm (NĐBH) — Header màu VÀNG

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 1 | `Thông tin Người được bảo hiểm` | Tên người được bảo hiểm | `peopleName` | string | **TRIM, Viết hoa chữ cái đầu, có dấu, giữ khoảng trắng giữa**. VD: `Trịnh Bảo Ngọc` | ❌ NOT NULL | ✅ Đã map |
| 2 | `CCCD` | Số CMTND/Thẻ CCCD/Hộ chiếu NĐBH | `peopleLicense` | string | **Loại bỏ dấu " " (space), "." (dot), "-" (dash) và các ký tự đặc biệt và phải có số 0 ở đầu**. Chỉ giữ số và chữ. VD: `001234567890` | ✅ | ⚠️ Chưa clean |
| 3 | `Passport` | Hộ chiếu NĐBH | `passport` | string | **Loại bỏ ký tự đặc biệt**, giữ chữ + số. VD: `B1234567` | ✅ | ⚠️ Chưa clean |
| 4 | `Ngày tháng năm sinh` | Ngày sinh NĐBH | `peopleDob` | date | **DD/MM/YYYY** → chuyển sang `DD/MM/YYYY` mới đúng. VD: `01/01/1990` → `01/01/1990` | ❌ NOT NULL | ✅ Đã parse |
| 5 | `Giới tính` | Giới tính NĐBH | `peopleGender` | string | **Enum bắt buộc:** chỉ chấp nhận `Nam`, `Nữ`. Nếu sai giá trị thì báo lỗi khi validate file. Sau khi pass validation, hệ thống mới convert nội bộ để phù hợp kiểu dữ liệu DB. | ❌ NOT NULL | ✅ Đã validate |
| 6 | `Email` | Email NĐBH | `peopleEmail` | string | **TRIM, LOWER**. Validate format email (có @ là được). | ✅ | ⚠️ Chưa validate format |
| 7 | `Địa chỉ liên hệ` | Địa chỉ NĐBH | `peopleAddress` | string | **TRIM**. Giữ nguyên dấu tiếng Việt. | ✅ | ✅ Đã trim |

---

## 👨‍👩‍👧 Nhóm 2: Thông tin Bên Mua Bảo Hiểm (NMBH) — Header màu VÀNG

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 8 | `Thông tin Bên mua bảo hiểm` | Tên người mua bảo hiểm | `payerName` | string | **TRIM, Viết hoa chữ cái đầu, có dấu, giữ khoảng trắng giữa**. VD: `Trịnh Bảo Ngọc` | ❌ NOT NULL | ✅ Đã format |
| 9 | `Mối quan hệ đối với NĐBH` | Mối quan hệ với NĐBH | `peopleRelationship` | string | **Enum bắt buộc:** Bản thân, Bố/Mẹ, Vợ/Chồng, Anh/Chị/Em, Con, Khác, Bố/Mẹ vợ/chồng. Nếu sai giá trị thì báo lỗi khi validate file. Sau khi pass validation, hệ thống mới convert nội bộ để phù hợp kiểu dữ liệu DB. | ❌ NOT NULL | ✅ Đã validate |
| 10 | `Ngày tháng năm sinh.1` | Ngày sinh NMBH | `payerDob` | date | **DD/MM/YYYY** → `DD/MM/YYYY` | ❌ NOT NULL | ⚠️ Chưa parse |
| 11 | `CCCD/Passport` | Số CMTND/CCCD/Hộ chiếu NMBH | `payerLicense` | string | **Loại bỏ dấu " ", ".", "-" và ký tự đặc biệt**. Chỉ giữ số và chữ. | ✅ | ⚠️ Chưa clean |
| 12 | `Số điện thoại` | Số điện thoại NMBH | `payerPhone` | string | **Chuẩn hóa số điện thoại**: bỏ khoảng trắng/ký tự thừa, khôi phục `0` đầu nếu Excel làm rơi, validate bắt đầu 0, 10-11 chữ số (0+9-10 chữ số). | ❌ NOT NULL | ✅ Đã validate |
| 13 | `Địa chỉ liên hệ.1` | Địa chỉ NMBH | `payerAddress` | string | **TRIM**. Giữ dấu tiếng Việt. | ✅ | ✅ Đã trim |
| 14 | `Email.1` | Email NMBH | `payerEmail` | string | **TRIM, LOWER**. Validate format email. | ✅ | ⚠️ Chưa validate |

---

## 📄 Nhóm 3: Thông tin Hợp Đồng / Bảo Hiểm — Header màu XANH LÁ + TÍM

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 15 | `Số hợp đồng` | Số đơn bảo hiểm | `contractId` | string | **TRIM**. Không được trống. | ❌ NOT NULL | ✅ Đã map |
| 16 | `Số GCNBH` | Số giấy chứng nhận bảo hiểm | `certificateNumberProvider` | string | **TRIM**. | ✅ | ✅ Đã map |
| 17 | `Sản phẩm` | Sản phẩm bảo hiểm | `majorName` | string | **TRIM**. Giá trị enum (tên sản phẩm chuẩn). | ❌ | ✅ Đã map |
| 18 | `Nhà bảo hiểm` | Tên công ty bảo hiểm | `companyProviderName` | string | **TRIM**. Giá trị enum (tên NHB chuẩn). | ❌ | ✅ Đã map |
| 19 | `Chương trình bảo hiểm` | Tên chương trình bảo hiểm | `programName` | string | **TRIM**. VD: `Bảo Việt Tâm An`. | ❌ NOT NULL | ✅ Đã map |
| 20 | `Ngày hiệu lực` | Ngày bắt đầu hiệu lực | `contractStartDate` | date | **DD/MM/YYYY** → `DD/MM/YYYY` DD/MM/YYYY >= Ngày thanh toán (thường thì sẽ là T + 1).                             Rule: Nếu người được BH chưa đủ 30 ngày tuổi thì ngày hiệu lực sẽ bắt đầu từ ngày người được BH đủ 30 ngày tuổi | ❌ NOT NULL | ⚠️ Chưa convert |
| 21 | `Ngày kết thúc` | Ngày kết thúc hiệu lực | `contractEndDate` | date | **DD/MM/YYYY** → `DD/MM/YYYY`,  DD/MM/YYYY > Ngày bắt đầu| ❌ NOT NULL | ⚠️ Chưa convert |

---

## 💰 Nhóm 4: Thông tin Tài chính — Header màu XANH LÁ

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 22 | `Phí bảo hiểm` | Phí bảo hiểm (bao gồm VAT) | `feeInsurance` | float | **Xóa dấu chấm ngàn** (VN format: `2.980.800` → `2980800`). Phải >= 1,000. | ❌ NOT NULL | ✅ Đã parse |
| 23 | `Ngoại trú` | Quyền lợi ngoại trú | `outpatient_benefit` | string | **TRIM**. | ✅ | ✅ Đã map |
| 24 | `Nha khoa` | Quyền lợi nha khoa | `dental_benefit` | string | **TRIM**. | ✅ | ✅ Đã map |
| 25 | `Thai sản` | Quyền lợi thai sản | `maternity_benefit` | string | **TRIM**. | ✅ | ✅ Đã map |
| 26 | `Top-up` | Quyền lợi top-up | `topup_benefit` | string | **TRIM**. | ✅ | ✅ Đã map |
| 27 | `Phí điều chỉnh` | Phí điều chỉnh | `feeAdjustment` | float | **Xóa dấu chấm ngàn**. Có thể âm. | ✅ | ✅ Đã map |
| 28 | `Số tiền thanh toán` | Số tiền thanh toán | `amountPay` | float | **Xóa dấu chấm ngàn**. Phải >= 1,000. 

Số tiền thanh toán <= Phí bảo hiểm (check lại)

Nếu 1 SHĐ & 1 Tên NĐBH > 1 thì Số tiền thanh toán < Phí bảo hiểm | ❌ NOT NULL | ✅ Đã parse |
| 29 | `Ngày thanh toán` | Ngày thanh toán | `payment_date` | date | **DD/MM/YYYY** → `DD/MM/YYYY` nhỏ hơn hoặc bằng ngày hiện tại| ❌ NOT NULL | ⚠️ Chưa convert |
| 30 | `Hình thức thanh toán` | Hình thức thanh toán | `termsFeePaymentMethod` | string | **TRIM**. Có thể để trống (nullable). Không check enum. | ✅ Nullable (Có thể null) | ✅ Đã map |

---

## 📞 Nhóm 5: Thông tin Liên hệ & Khác — Header màu VÀNG nhạt

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 31 | `Code sale` | Mã sale / Tên sale | `saleId` | string | **TRIM** | ✅ | ✅ Đã map |
| 32 | `Channel` | Kênh phân phối | `programCodeMiningChannel` | string | **TRIM**. **BẮT BUỘC** thuộc: `DSA`, `DSA/Renew`, `DSA_NEO`, `TSA`, `Renew`, `CTV_TSA (TSA 2)`, `CTV_TSA (TSA 2)/Renew`, `HO`, `Digital`, `Referral`. **Sai chính tả/định dạng sẽ bị từ chối.** | ❌ NOT NULL | ✅ Đã validate |
| 33 | `Ngày cập nhật` | Ngày cập nhật dữ liệu | `modifiedAt` | date | **DD/MM/YYYY** → `DD/MM/YYYY` | ✅ | ⚠️ Chưa convert |
| 34 | `Phone trên lead` | SĐT lead | `leadPhone` | string | **TRIM, loại bỏ space/dash**, có số 0 ở đầu nếu Excel làm rơi. Chỉ dùng fallback khi `Số điện thoại` trống. | ✅ | ✅ Đã normalize |
| 35 | `Phone Khách hàng` | SĐT khách hàng | `customerPhone` | string | **TRIM, loại bỏ space/dash**, có số 0 ở đầu nếu Excel làm rơi. Chỉ dùng fallback khi `Số điện thoại` trống. | ✅ | ✅ Đã normalize |
| 36 | `Tên liên hệ` | Tên liên hệ | `contactName` | string | **TRIM**. | ✅ | ✅ Đã map |
| 37 | `Thông tin xuất hóa đơn` | Thông tin xuất hóa đơn | `invoiceInfo` | string | **TRIM**. | ✅ | ✅ Đã map |
| 38 | `NOTE` | Ghi chú | `note` | string | **TRIM**. | ✅ | ✅ Đã map |

---


---


---

## 🔍 Bảng Cập Nhật Kiểm Tra Null Nhanh (Quick Null Check)
> Bảng này tổng hợp nhanh các trường bắt buộc và tùy chọn để dễ hình dung tổng thể.

| STT | Cột Excel (Upload) | DB Field | Trạng thái Nullable |
|---|---|---|---|   
| 1 | `Số hợp đồng` | `contractId` | ❌ NOT NULL |
| 2 | `Thông tin Người được bảo hiểm` | `peopleName → name` | ❌ NOT NULL |
| 3 | `Sản phẩm` | `majorName` | ❌ NOT NULL |
| 4 | `Nhà bảo hiểm` | `companyProviderName` | ❌ NOT NULL |
| 5 | `Thông tin Người được bảo hiểm` | `peopleName` | ❌ NOT NULL |
| 6 | `CCCD` | `peopleLicense` | ❌ NOT NULL |
| 7 | `Passport` | `passport` | ❌ NOT NULL |
| 8 | `Ngày tháng năm sinh` | `peopleDob` | ❌ NOT NULL |
| 9 | `Giới tính` | `peopleGender` | ❌ NOT NULL |
| 10 | `Email` | `peopleEmail` | ✅ Nullable (Có thể null) |
| 11 | `Địa chỉ liên hệ` | `peopleAddress` | ✅ Nullable (Có thể null) |
| 12 | `Thông tin Bên mua bảo hiểm` | `payerName` | ❌ NOT NULL |
| 13 | `Mối quan hệ đối với NĐBH` | `peopleRelationship` | ❌ NOT NULL |
| 14 | `Ngày tháng năm sinh.1` | `payerDob` | ✅ Nullable (Có thể null) |
| 15 | `CCCD/Passport` | `payerLicense` | ✅ Nullable (Có thể null) |
| 16 | `Số điện thoại` | `payerPhone` | ❌ NOT NULL |
| 17 | `Địa chỉ liên hệ.1` | `payerAddress` | ✅ Nullable (Có thể null) |
| 18 | `Email.1` | `payerEmail` | ❌ NOT NULL |
| 19 | `Số GCNBH` | `certificateNumberProvider` | ✅ Nullable (Có thể null) |
| 20 | `Chương trình bảo hiểm` | `programName` | ❌ NOT NULL |
| 21 | `Ngày hiệu lực` | `contractStartDate` | ❌ NOT NULL |
| 22 | `Ngày kết thúc` | `contractEndDate` | ❌ NOT NULL |
| 23 | `Phí bảo hiểm` | `feeInsurance` | ❌ NOT NULL |
| 24 | `Ngoại trú` | `outpatient_benefit` | ✅ Nullable (Có thể null) |
| 25 | `Nha khoa` | `dental_benefit` | ✅ Nullable (Có thể null) |
| 26 | `Thai sản` | `maternity_benefit` | ✅ Nullable (Có thể null) |
| 27 | `Top-up` | `topup_benefit` | ✅ Nullable (Có thể null) |
| 28 | `Phí điều chỉnh` | `feeAdjustment` | ✅ Nullable (Có thể null) |
| 29 | `Số tiền thanh toán` | `amountPay` | ❌ NOT NULL |
| 30 | `Ngày thanh toán` | `payment_date` | ❌  NOT NULL |
| 31 | `Hình thức thanh toán` | `termsFeePaymentMethod` | ✅ Nullable (Có thể null) |
| 32 | `Code sale` | `saleId` | ❌ NOT NULL |
| 33 | `Channel` | `programCodeMiningChannel` | ❌ NOT NULL |
| 34 | `Ngày cập nhật` | `modifiedAt` | ✅ Nullable (Có thể null) |
| 35 | `Phone trên lead` | `leadPhone` | ✅ Nullable (Có thể null) |
| 36 | `Phone Khách hàng` | `customerPhone` | ✅ Nullable (Có thể null) |
| 37 | `Tên liên hệ` | `contactName` | ✅ Nullable (Có thể null) |
| 38 | `Thông tin xuất hóa đơn` | `invoiceInfo` | ✅ Nullable (Có thể null) |
| 39 | `NOTE` | `note` | ✅ Nullable (Có thể null) |

## ⚠️ Các Rules CHƯA Được Implement (cần bổ sung)

### 🔴 Ưu tiên cao (ảnh hưởng data quality)

| Rule | Field | Mô tả | Hiện trạng |
|------|-------|-------|------------|
| **Title Case** tên | `peopleName`, `payerName` | Tên phải viết hoa chữ cái đầu: `Trịnh Bảo Ngọc` | ✅ Đã implement |
| **Clean CCCD/Passport** | `peopleLicense`, `payerLicense`, `passport` | Loại bỏ dấu space, dot, dash, ký tự đặc biệt | ❌ Chưa implement |
| **Clean phone** | `payerPhone`, `leadPhone`, `customerPhone` | Loại bỏ space, dash. Validate 10-11 số. | ✅ Đã implement |
| **Email format** | `peopleEmail`, `payerEmail` | Validate có @domain. LOWER. | ❌ Chưa implement |

### 🟡 Ưu tiên vừa (cải thiện data consistency)

| Rule | Field | Mô tả | Hiện trạng |
|------|-------|-------|------------|
| **Enum validate** | `peopleGender`, `peopleRelationship` | `peopleGender` chỉ nhận `Nam`, `Nữ`; `peopleRelationship` chỉ nhận danh sách enum cho phép. | ✅ Đã implement |
| **Số tiền >= 0** | `feeInsurance`, `amountPay` | Phí bảo hiểm không được âm | ✅ Đã validate |
| **Date range** | `contractStartDate`, `contractEndDate` | Start phải < End | ✅ Đã validate |

---

## 🧩 Tổng hợp Color Coding từ File Chuẩn

| Màu | Ý nghĩa | Fields |
|-----|---------|--------|
| 🟡 **Vàng** | Thông tin định danh quan trọng (tên, CCCD, ngày sinh, liên hệ) | peopleName, peopleLicense, peopleDob, payerName, payerLicense, payerPhone, email |
| 🟢 **Xanh lá** | Thông tin bảo hiểm & thanh toán | Quyền lợi BH, phí, thời hạn, hình thức thanh toán |
| 🟣 **Tím** | Metadata chương trình & nhà cung cấp | programName, companyProviderName |
| 🟠 **Cam** | Mối quan hệ (cần chuyển đổi enum) | peopleRelationship |

---

## 📊 Ví Dụ Dữ Liệu Mẫu (từ file chuẩn)

```
peopleName:           "Trịnh Bảo Ngọc"        (Title Case, có dấu, trim)
peopleLicense:        "001234567890"           (chỉ số, đã clean)
peopleDob:            "01/01/1990"             (DD/MM/YYYY)
peopleGender:         "Nam"                    (string, không map ra 0,1)
payerName:            "Trịnh Bảo Ngọc"        (Title Case, có dấu, trim)
peopleRelationship:   "Vợ/Chồng"               (string, Enum dropdown)
contractId:           "HD-2024-001234"         (trim)
feeInsurance:         2980800.0                (converted from "2.980.800")
contractStartDate:    "15/01/2024"             (DD/MM/YYYY)
```

---

> **Ghi chú:** File này dựa trên file chuẩn giao nhận BH Sức khỏe (hình được cung cấp) kết hợp với
> mapping hiện tại trong `health_mapping.py`. Các field có status ⚠️ cần bổ sung validation rules
> trong `HealthProcessor.post_process()` hoặc tạo riêng một `DataCleaningService`.
