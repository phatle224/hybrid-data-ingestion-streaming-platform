# HEALTH Insurance — Excel Field Mapping

> Loại bảo hiểm: **Sức khỏe (HEALTH)**  
> File Excel mẫu: `Health.xlsx`  
> Source of truth: `backend/configs/mappings/health_mapping.py`

---

## Ghi chú chung

- **4 Business Keys** (NOT NULL bắt buộc): `contractId`, `peopleName`, `majorName`, `companyProviderName`
- Tất cả các field khác: **optional** — có thể NULL, chưa được validate chất lượng dữ liệu
- **Buyer-as-beneficiary rule**: Nếu cột NĐBH (người được BH) trống → tự động copy từ cột BMBH (người mua) trong `post_process()`

---

## 1. Nhóm: Người được bảo hiểm (NĐBH)

| Cột Excel (file upload) | Header hiển thị | DB field | Bắt buộc | Rule / Ghi chú |
|---|---|---|:---:|---|
| `Thông tin Người được bảo hiểm` | Họ tên người được thụ hưởng BH | `peopleName` | ✅ NOT NULL | Trim + chuẩn hóa Title Case tiếng Việt (VD: `Trịnh Bảo Ngọc`), giữ dấu + khoảng trắng. **Business key #2** |
| `Ngày tháng năm sinh` | Ngày sinh NĐBH | `peopleDob` | ❌ | DD/MM/YYYY → lưu YYYY-MM-DD. Nếu trống + có `payerDob` → auto-fill |
| `Giới tính` | Giới tính NĐBH | `peopleGender` | ❌ | Dropdown: `Nam` → `1`, `Nữ` → `0`. Convert sang integer trong `post_process()` |
| `Email` | Email NĐBH | `peopleEmail` | ❌ | Định dạng email. Nếu trống + có `payerEmail` → auto-fill |
| `CCCD` | CCCD NĐBH | `peopleLicense` | ❌ | 9–12 ký số hoặc Passport. Nếu trống + có `payerLicense` → auto-fill |
| `Passport` | Passport NĐBH | `passport` | ❌ | Dùng khi không có CCCD |
| `Địa chỉ liên hệ` | Địa chỉ NĐBH | `peopleAddress` | ❌ | Trim. Nếu trống + có `payerAddress` → auto-fill |

---

## 2. Nhóm: Người mua bảo hiểm / Bên mua BH (BMBH)

| Cột Excel (file upload) | Header hiển thị | DB field | Bắt buộc | Rule / Ghi chú |
|---|---|---|:---:|---|
| `Thông tin Bên mua bảo hiểm` | Họ tên người mua BH / Người YC BH | `payerName` | ❌ | Trim + chuẩn hóa Title Case tiếng Việt (VD: `Trịnh Bảo Ngọc`), giữ dấu. Nếu `peopleName` trống → được copy lên làm `peopleName` |
| `Mối quan hệ đối với NĐBH` | Mối quan hệ với NĐBH | `peopleRelationship` | ❌ | Dropdown text → integer: `Bản thân`→`0`, `Bố/Mẹ`→`1`, `Vợ/Chồng`→`2`, `Anh/Chị/Em`→`3`, `Con`→`4`, `Khác`→`5`. Nếu buyer-as-beneficiary → auto set `0` |
| `Ngày tháng năm sinh.1` | Ngày sinh người mua BH | `payerDob` | ❌ | DD/MM/YYYY → YYYY-MM-DD |
| `CCCD/Passport` | CCCD hoặc Passport người mua | `payerLicense` | ❌ | 9–12 ký số hoặc Passport |
| `Số điện thoại` | SDT người mua BH | `payerPhone` | ❌ | 10 số, bắt đầu bằng 0. Nếu `peoplePhone` trống → auto-fill |
| `Địa chỉ liên hệ.1` | Địa chỉ người mua BH | `payerAddress` | ❌ | Trim |
| `Email.1` | Email người mua BH | `payerEmail` | ❌ | Định dạng email |

> **Tên cột `.1`** (ví dụ `Ngày tháng năm sinh.1`): Pandas tự thêm suffix khi có 2 cột cùng tên trong cùng file Excel.

---

## 3. Nhóm: Thông tin hợp đồng

| Cột Excel (file upload) | Header hiển thị | DB field | Bắt buộc | Rule / Ghi chú |
|---|---|---|:---:|---|
| `Số hợp đồng` | Số hợp đồng | `contractId` | ✅ NOT NULL | **Business key #1**. Trim |
| `Sản phẩm` | Sản phẩm (loại BH) | `majorName` | ✅ NOT NULL | **Business key #3**. Dropdown, Trim, Upper |
| `Nhà bảo hiểm` | Nhà bảo hiểm | `companyProviderName` | ✅ NOT NULL | **Business key #4**. Dropdown, Trim |
| `Chương trình bảo hiểm` | Chương trình | `programName` | ❌ | Trim |
| `Code sale` | Code sale / Tên sale | `saleId` | ❌ | Trim |
| `Channel` | Channel | `programCodeMiningChannel` | ❌ | Trim. **BẮT BUỘC** thuộc: DSA, DSA/Renew, DSA_NEO, TSA, Renew, CTV_TSA (TSA 2), CTV_TSA (TSA 2)/Renew, HO, Digital, Referral. **Sai chính tả/định dạng sẽ bị từ chối.** |
| `Hình thức thanh toán` | Hình thức TT | `termsFeePaymentMethod` | ❌ | Dropdown text, lưu as-is |
| `Số GCNBH` | Số GCNBH | `certificateNumberProvider` | ❌ | Trim |
| `Ngày hiệu lực` | Ngày hiệu lực HĐ | `contractStartDate` | ❌ | DD/MM/YYYY → YYYY-MM-DD |
| `Ngày kết thúc` | Ngày kết thúc HĐ | `contractEndDate` | ❌ | DD/MM/YYYY → YYYY-MM-DD |
| `Ngày cập nhật` | Ngày update | `modifiedAt` | ❌ | DD/MM/YYYY → YYYY-MM-DD |

---

## 4. Nhóm: Phí & Quyền lợi

| Cột Excel (file upload) | Header hiển thị | DB field | Bắt buộc | Rule / Ghi chú |
|---|---|---|:---:|---|
| `Phí bảo hiểm` | Phí bảo hiểm chính | `feeMainBenefit` | ❌ | Số thực. Có thể có dấu chấm ngàn VN (`2.980.800` → parse → `2980800.0`) |
| `Phí điều chỉnh` | Phí điều chỉnh | `feeAdjustment` | ❌ | Số thực, có thể âm |
| `Số tiền thanh toán` | Số tiền thanh toán | `amountPay` | ❌ | Số thực |
| `Ngoại trú` | Quyền lợi Ngoại trú | `outpatient_benefit` | ❌ | Số thực hoặc text mô tả gói |
| `Nha khoa` | Quyền lợi Nha khoa | `dental_benefit` | ❌ | Số thực hoặc text |
| `Thai sản` | Quyền lợi Thai sản | `maternity_benefit` | ❌ | Số thực hoặc text |
| `Top-up` | Quyền lợi Top-up | `topup_benefit` | ❌ | Số thực hoặc text |

---

## 5. Nhóm: Thông tin bổ sung

| Cột Excel (file upload) | Header hiển thị | DB field | Bắt buộc | Rule / Ghi chú |
|---|---|---|:---:|---|
| `Ngày thanh toán` | Ngày thanh toán | `payment_date` | ❌ | DD/MM/YYYY → YYYY-MM-DD |
| `Thông tin xuất hóa đơn` | Thông tin xuất HĐ | `invoiceInfo` | ❌ | Text tự do |
| `Phone trên lead` | Phone trên lead | `leadPhone` | ❌ | 10 số |
| `Phone Khách hàng` | Phone khách hàng | `customerPhone` | ❌ | 10 số |
| `Tên liên hệ` | Tên liên hệ | `contactName` | ❌ | Trim |
| `NOTE` | Ghi chú | `note` | ❌ | Text tự do |

---

## 6. Buyer-as-Beneficiary Rule (auto-fill trong `post_process()`)

Khi người mua **mua BH cho bản thân**, cột NĐBH để trống. Hệ thống tự fill:

| Nếu trường này trống... | Thì copy từ... | Rule thêm |
|---|---|---|
| `peopleName` | `payerName` | + set `peopleRelationship = 0` (Bản thân) |
| `peopleDob` | `payerDob` | |
| `peopleLicense` | `payerLicense` | |
| `peopleAddress` | `payerAddress` | |
| `peopleEmail` | `payerEmail` | |
| `peoplePhone` *(nếu có)* | `payerPhone` | |

> **Điều kiện**: chỉ apply khi field NĐBH là `None` hoặc empty string. Không ghi đè nếu đã có giá trị.

---

## 7. Xử lý đặc biệt trong code

| Vấn đề | Xử lý |
|---|---|
| Header multiline (2 dòng trong Excel) | Pandas đọc thành `"Thông tin \nNgười được bảo hiểm"` — mapping giữ nguyên ký tự `\n` |
| 2 cột cùng tên (vd: 2 cột "Ngày tháng năm sinh") | Pandas tự thêm `.1`, `.2`... — mapping dùng tên đã có suffix |
| Số có dấu chấm ngàn (`2.980.800`) | `_parse_numeric_string()` trong `base_processor.py` xử lý trước khi lưu |
| Date `DD/MM/YYYY` | `_parse_date_string()` convert → `YYYY-MM-DD` cho MySQL |
| Gender text | `post_process()` convert: `Nam`→`1`, `Nữ`→`0` |
| Relationship text | `post_process()` convert theo bảng mapping 7 giá trị (0–6) |