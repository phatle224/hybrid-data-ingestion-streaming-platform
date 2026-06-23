# 📋 Medical & Social Insurance (BHYT & BHXH) — Field Mapping & Validation Rules

> File này mô tả mapping giữa **cột Excel upload** ↔ **field chuẩn giao nhận** ↔ **DB field**,
> kèm validation rules cho từng field dựa trên file chuẩn giao nhận BH Y tế & Xã hội.

---

## 🔑 Business Keys (4 fields KHÔNG được NULL)

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Nullable |
|---|---------------------|----------------------|----------|----------|
| 1 | `Mã tờ khai` | Mã tờ khai / Số hợp đồng | `contractId` | ❌ NOT NULL |
| 2 | `Họ tên NĐBH` | Tên Người được BH | `peopleName` | ❌ NOT NULL |
| 3 | `Sản phẩm` | Sản phẩm (BHYT/BHXH) | `majorName` | ❌ NOT NULL |
| 4 | `Đối tác NBH` | Nhà Bảo Hiểm | `companyProviderName` | ❌ NOT NULL |

---

## 👤 Nhóm 1: Thông tin Người Được Bảo Hiểm (NĐBH)

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 1 | `Họ tên NĐBH` | Tên Người được BH | `peopleName` | string | **TRIM, có dấu, giữ khoảng trắng giữa**. Hiện chưa có rule UPPER tự động. | ❌ NOT NULL | ✅ Đã trim |
| 2 | `Ngày sinh` | Ngày sinh NĐBH | `peopleDob` | date | **DD/MM/YYYY** → `YYYY-MM-DD` | ❌ NOT NULL | ✅ Đã parse |
| 3 | `Giới tính` | Giới tính NĐBH | `peopleGender` | string | **Enum bắt buộc:** chỉ chấp nhận `Nam`, `Nữ`. Nếu sai giá trị thì báo lỗi khi validate file. Sau khi pass validation, hệ thống mới convert nội bộ để phù hợp kiểu dữ liệu DB | ❌ NOT NULL | ✅ Đã convert |
| 4 | `CCCD` | Số CMTND/CCCD/Hộ chiếu NĐBH | `peopleLicense` | string | **Loại bỏ dấu " " (space), "." (dot), "-" (dash) và các ký tự đặc biệt và phải có số 0 ở đầu**. Chỉ giữ số và chữ. VD: `001234567890` | ❌ NOT NULL | ⚠️ Chưa clean |
| 5 | `Địa chỉ` | Địa chỉ NĐBH | `peopleAddress` | string | **TRIM**. Giữ dấu tiếng Việt. | ❌ NOT NULL | ✅ Đã trim |
| 6 | `SĐT` | SĐT NĐBH | `peoplePhone` | string |  **Chuẩn hóa số điện thoại**: bỏ khoảng trắng/ký tự thừa, khôi phục `0` đầu nếu Excel làm rơi, validate bắt đầu 0, 10-11 chữ số (0+9-10 chữ số).| ✅ | ⚠️ Chưa validate |
| 7 | `Email` | Email NĐBH | `peopleEmail` | string | **TRIM, LOWER**. Validate format email (có @domain). | ✅ | ⚠️ Chưa validate |

---

## 👨‍👩‍👧 Nhóm 2: Thông tin Bên Mua BH (BMBH)

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 8 | `Họ tên BMBH` | Tên người mua BH | `payerName` | string | **TRIM, có dấu, giữ khoảng trắng giữa**. Hiện chưa có rule UPPER tự động. | ✅ Nullable (Có thể null) | ✅ Đã trim |
| 9 | `Ngày sinh.1` | Ngày sinh BMBH | `payerDob` | date | **DD/MM/YYYY** → `YYYY-MM-DD` | ✅ Nullable (Có thể null) | ✅ Đã parse |
| 10 | `CCCD.1` | CCCD/Passport BMBH | `payerLicense` | string | **Loại bỏ dấu " ", ".", "-" và ký tự đặc biệt và phải có số 0 ở đầu**. Chỉ giữ số và chữ. VD: `001234567890` | ✅ Nullable (Có thể null) | ⚠️ Chưa clean |
| 11 | `Mối quan hệ với NĐBH` | Mối quan hệ | `peopleRelationship` | string | **Enum bắt buộc:** Bản thân, Bố/Mẹ, Vợ/Chồng, Anh/Chị/Em, Con, Khác, Bố/Mẹ vợ/chồng. Nếu sai giá trị thì báo lỗi khi validate file. Sau khi pass validation, hệ thống mới convert nội bộ để phù hợp kiểu dữ liệu DB | ❌ NOT NULL | ✅ Đã convert |
| 12 | `Địa chỉ.1` | Địa chỉ BMBH | `payerAddress` | string | **TRIM**. | ✅ | ✅ Đã trim |
| 13 | `SĐT ` (có space cuối) | SĐT BMBH | `payerPhone` | string |  **Chuẩn hóa số điện thoại**: bỏ khoảng trắng/ký tự thừa, khôi phục `0` đầu nếu Excel làm rơi, validate bắt đầu 0, 10-11 chữ số (0+9-10 chữ số). | ✅ | ⚠️ Chưa validate |
| 14 | `Email.1` | Email BMBH | `payerEmail` | string | **TRIM, LOWER**. Validate format email. | ✅ | ⚠️ Chưa validate |

---

## 🏥 Nhóm 3: Thông tin BH Đặc thù (BHXH/BHYT)

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 15 | `Mã BHXH` | Mã bảo hiểm xã hội | `socialId` | string | **TRIM**.Loại bỏ dấu " ", ".", "-" và ký tự đặc biệt. | ❌ NOT NULL | ⚠️ Chưa validate |
| 16 | `Phương án KH` | Tên phương án/gói tham gia | `renewal` | string | **TRIM**. Enum: Tái tục --> 0, Mua mới --> 1 | ❌ NOT NULL | ✅ Đã map |

---

## 📄 Nhóm 4: Thông tin Hợp Đồng & Thanh Toán

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 18 | `Mã tờ khai` | Mã tờ khai = Mã hợp đồng | `contractId` | string | **TRIM**. Không được trống. | ❌ NOT NULL | ✅ Đã map |
| 19 | `Phí Bảo hiểm` | Phí Bảo hiểm | `feeInsurance` | float | **Xóa dấu chấm ngàn**. Đồng bộ rule các loại BH: ưu tiên kiểm tra **>= 1.000** và cảnh báo sai đơn vị khi quá nhỏ. | ❌ NOT NULL | ⚠️ Chưa validate |
| 20 | `Ngày thanh toán` | Ngày thanh toán | `payment_date` | date | **DD/MM/YYYY** → `YYYY-MM-DD` | ❌ NOT NULL | ✅ Đã parse |
| 21 | `Ngày bắt đầu` | Ngày bắt đầu hiệu lực | `contractObjectStartDate` | date | **DD/MM/YYYY** → `YYYY-MM-DD` | ❌ NOT NULL | ✅ Đã parse |
| 22 | `Ngày kết thúc` | Ngày kết thúc hiệu lực | `contractObjectEndDate` | date | **DD/MM/YYYY** → `YYYY-MM-DD`. Phải > `contractObjectStartDate`. | ❌ NOT NULL | ✅ Đã parse |
| 23 | `Trạng thái` | Trạng thái hợp đồng | `contractStatus` | string/int | **TRIM**. Giá trị theo enum trạng thái hợp đồng. | ✅ Nullable (Có thể null) | ✅ Đã map |
| 24 | `Hình thức thanh toán` | Hình thức thanh toán | `termsFeePaymentMethod` | string | **TRIM**. Có thể để trống (nullable). Không check enum.| ✅ | ✅ Đã map |

---

## 📋 Nhóm 5: Thông tin Chung & Metadata

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 25 | `Sản phẩm` | Sản phẩm (BHYT/BHXH) | `majorName` | string | **TRIM**. Giá trị chuẩn. Dùng để resolve MEDICAL vs SOCIAL. | ❌ NOT NULL | ✅ Đã map |
| 26 | `Đối tác NBH` | Nhà Bảo Hiểm | `companyProviderName` | string | **TRIM**. Giá trị chuẩn. | ❌ NOT NULL | ✅ Đã map |
| 27 | `Ngày update` | Ngày cập nhật | `modifiedAt` | date | **DD/MM/YYYY** → `YYYY-MM-DD`. | ✅ | ✅ Đã parse |
| 28 | `Code sales` | Code sale | `saleId` | string | **TRIM**. | ❌ NOT NULL | ✅ Đã map |
| 29 | `Channel` | Channel | `programCodeMiningChannel` | string | **TRIM**. **BẮT BUỘC** thuộc: `DSA`, `DSA/Renew`, `DSA_NEO`, `TSA`, `Renew`, `CTV_TSA (TSA 2)`, `CTV_TSA (TSA 2)/Renew`, `HO`, `Digital`, `Referral`. **Sai chính tả/định dạng sẽ bị từ chối.** | ❌ NOT NULL | ✅ Đã validate |

---


---


---


---

## 🔍 Bảng Cập Nhật Kiểm Tra Null Nhanh (Quick Null Check)
> Bảng này tổng hợp nhanh các trường bắt buộc và tùy chọn để dễ hình dung tổng thể.

| STT | Cột Excel (Upload) | DB Field | Trạng thái Nullable |
|---|---|---|---|
| 1 | `Mã tờ khai` | `contractId` | ❌ NOT NULL |
| 2 | `Họ tên NĐBH` | `peopleName` | ❌ NOT NULL |
| 3 | `Sản phẩm` | `majorName` | ❌ NOT NULL |
| 4 | `Đối tác NBH` | `companyProviderName` | ❌ NOT NULL |
| 5 | `Ngày sinh` | `peopleDob` | ❌ NOT NULL |
| 6 | `Giới tính` | `peopleGender` | ❌ NOT NULL |
| 7 | `CCCD` | `peopleLicense` | ❌ NOT NULL |
| 8 | `Địa chỉ` | `peopleAddress` | ❌ NOT NULL |
| 9 | `SĐT` | `peoplePhone` | ✅ Nullable (Có thể null) |
| 10 | `Email` | `peopleEmail` | ✅ Nullable (Có thể null) |
| 11 | `Họ tên BMBH` | `payerName` | ✅ Nullable (Có thể null) |
| 12 | `Ngày sinh.1` | `payerDob` | ✅ Nullable (Có thể null) |
| 13 | `CCCD.1` | `payerLicense` | ✅ Nullable (Có thể null) |
| 14 | `Mối quan hệ với NĐBH` | `peopleRelationship` | ❌ NOT NULL |
| 15 | `Địa chỉ.1` | `payerAddress` | ✅ Nullable (Có thể null) |
| 16 | `SĐT ` | `payerPhone` | ✅ Nullable (Có thể null) |
| 17 | `Email.1` | `payerEmail` | ✅ Nullable (Có thể null) |
| 18 | `Mã BHXH` | `socialId` | ❌ NOT NULL | 
| 19 | `Phương án KH` | `renewal` | ❌ NOT NULL |
| 21 | `Phí Bảo hiểm` | `feeInsurance` | ❌ NOT NULL |
| 22 | `Ngày thanh toán` | `payment_date` | ❌ NOT NULL |
| 23 | `Ngày bắt đầu` | `contractObjectStartDate` | ❌ NOT NULL |
| 24 | `Ngày kết thúc` | `contractObjectEndDate` | ❌ NOT NULL |
| 25 | `Trạng thái` | `contractStatus` | ✅ Nullable (Có thể null) |
| 26 | `Hình thức thanh toán` | `termsFeePaymentMethod` | ✅ Nullable (Có thể null) |
| 27 | `Ngày update` | `modifiedAt` | ✅ Nullable (Có thể null) |
| 28 | `Code sales` | `saleId` | ❌ NOT NULL |
| 29 | `Channel` | `programCodeMiningChannel` | ❌ NOT NULL |

> Ghi chú mapping theo DB: đã bỏ khỏi tài liệu/mapping các field gây lệch như
> `approval_date`, `refund_date`, `insuranceType_text`, `contractStatus_text`.

## ⚠️ Các Rules CHƯA Được Implement (cần bổ sung)

| Rule | Field | Mô tả | Ưu tiên |
|------|-------|-------|---------|
| **UPPER** tên | `peopleName`, `payerName` | Chưa áp dụng trong code hiện tại; nếu cần sẽ bổ sung normalize riêng | 🔴 Cao |
| **Clean CCCD** | `peopleLicense`, `payerLicense` | Loại bỏ space, dot, dash, ký tự đặc biệt | 🔴 Cao |
| **Clean phone** | `peoplePhone`, `payerPhone` | Loại bỏ space, dash. Validate 10-11 số | 🟡 Vừa |
| **Email validate** | `peopleEmail`, `payerEmail` | Validate @domain. LOWER | 🟡 Vừa |
| **Mã BHXH valid** | `socialId` | Validate 10 ký tự | 🟡 Vừa |
| **Phí >= 1.000** | `feeInsurance` | Đồng bộ các loại BH: parse số và cảnh báo sai đơn vị khi giá trị quá nhỏ | 🟡 Vừa |
| **Date range** | `contractObjectStartDate` < `contractObjectEndDate` | Start phải < End | 🟡 Vừa |

---

## 🔄 Đặc biệt: Sub-type Resolution (MEDICAL vs SOCIAL)

Medical Social là loại BH đặc biệt vì 1 file Excel có thể chứa cả BHYT và BHXH.
Processor tự động resolve sub-type dựa trên `majorName`:

```python
# Keywords for resolution:
SOCIAL:  ['bhxh', 'bảo hiểm xã hội', 'xã hội']
MEDICAL: ['bhyt', 'bảo hiểm y tế', 'y tế']

# Example:
majorName = "BHYTHGD 12 THÁNG"  → MEDICAL
majorName = "BHXH TỰ NGUYỆN"    → SOCIAL
```

---

## 📊 Ví Dụ Dữ Liệu Mẫu

```
peopleName:               "Nguyễn Văn A"        (trim, có dấu, giữ định dạng nhập)
peopleDob:                "1990-01-01"           (converted from 01/01/1990)
peopleGender:             1                      (converted from "Nam")
peopleLicense:            "001234567890"         (đã clean)
payerName:                "Trần Thị B"           (trim, có dấu, giữ định dạng nhập)
peopleRelationship:       2                      (converted from "Vợ/Chồng")
socialId:                 "0123456789"           (10 ký tự)
contractId:               "MTK-2024-001234"      (trim)
feeInsurance:             1375294.0              (converted)
contractObjectStartDate:  "2024-04-01"           (converted from 01/04/2024)
insuranceType:            "MEDICAL"              (resolved from majorName)
```

---

> **Ghi chú:** Medical Social có buyer-as-beneficiary fallback tương tự Health.
> `peopleName` fill từ `payerName` nếu NĐBH trống. Gender và Relationship đã
> được convert trong `post_process()`. Đặc biệt: `SĐT ` (cột BMBH) có space
> ở cuối header — mapping đã handle.
