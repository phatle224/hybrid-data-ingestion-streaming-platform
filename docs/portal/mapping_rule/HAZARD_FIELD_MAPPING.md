# 📋 Hazard Insurance (BHRR / BH Tài Sản) — Field Mapping & Validation Rules

> File này mô tả mapping giữa **cột Excel upload** ↔ **field chuẩn giao nhận** ↔ **DB field**,
> kèm validation rules cho từng field dựa trên file chuẩn giao nhận BH Rủi ro / BH Tài sản.

---

## 🔑 Business Keys (4 fields KHÔNG được NULL)

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Nullable |
|---|---------------------|----------------------|----------|----------|
| 1 | `Mã hợp đồng` | Số hợp đồng | `contractId` | ❌ NOT NULL |
| 2 | `Tên khách hàng` | Tên Người được BH | `payerName` → `peopleName` | ❌ NOT NULL |
| 3 | `Sản phẩm` | Tên sản phẩm | `majorName` | ❌ NOT NULL |
| 4 | `Đối tác nhà bảo hiểm` | Nhà Bảo Hiểm | `companyProviderName` | ❌ NOT NULL |

---

## 👤 Nhóm 1: Thông tin Khách hàng

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 1 | `Tên khách hàng` | Tên Người được BH | `payerName` | string | **TRIM, UPPER, có dấu, giữ khoảng trắng giữa**. VD: `CÔNG TY A`, `NGUYỄN VĂN A` | ❌ | ⚠️ Chưa UPPER |

---

## 📄 Nhóm 2: Thông tin Hợp Đồng

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 2 | `Mã hợp đồng` | Số hợp đồng | `contractId` | string | **TRIM**. Không được trống. | ❌ | ✅ Đã map |
| 3 | `Sản phẩm` | Tên sản phẩm | `majorName` | string | **TRIM**. Chọn theo bảng set up dựa theo nhà BH. Rule: Check tên sản phẩm dựa theo nhà bảo hiểm. | ❌ | ✅ Đã map |
| 4 | `Đối tác nhà bảo hiểm` | Nhà Bảo Hiểm | `companyProviderName` | string | **TRIM**. Giá trị chuẩn. | ❌ | ✅ Đã map |

---

## 💰 Nhóm 3: Thông tin Tài chính

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 5 | `Số tiền thanh toán` | Số tiền thanh toán / Phí Bảo hiểm | `amountPay` | float | **Xóa dấu chấm ngàn** (VN format: `2.980.800` → `2980800`). Phải >= 1,000. | ❌ NOT NULL | ✅ Đã validate |

---

## 📅 Nhóm 4: Ngày tháng

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 6 | `Ngày bắt đầu` | Ngày hiệu lực/ bắt đầu | `contractObjectStartDate` | date | Input **DD/MM/YYYY** (hệ thống parse nội bộ). | ❌ NOT NULL | ✅ Đã validate |
| 7 | `Ngày kết thúc` | Ngày kết thúc | `contractObjectEndDate` | date | Input **DD/MM/YYYY** (hệ thống parse nội bộ). Phải > `contractObjectStartDate`. | ❌ NOT NULL | ✅ Đã validate |
| 8 | `Ngày thanh toán` | Ngày Thanh Toán | `payment_date` | date | Input **DD/MM/YYYY** (hệ thống parse nội bộ). Không được lớn hơn ngày hiện tại. | ❌ NOT NULL | ✅ Đã validate |
| 9 | `Ngày cập nhật` | Ngày cập nhật | `modifiedAt` | date | **DD/MM/YYYY** → `YYYY-MM-DD`. | ✅ | ✅ Đã parse |

---

## 📋 Nhóm 5: Thông tin Chung & Metadata

| # | Excel Upload Column | Field Chuẩn Giao Nhận | DB Field | Data Type | Validation Rules | Nullable | Status |
|---|---------------------|----------------------|----------|-----------|-----------------|----------|--------|
| 10 | `Trạng thái` | Hình thức thanh toán | `termsFeePaymentMethod` | string | **TRIM**. Có thể để trống (nullable). Không check enum. | ✅ Nullable (Có thể null) | ✅ Đã map |
| 11 | `Code sale` | Code sale | `saleId` | string | **TRIM**. Số điện thoại của sale. Rule: Số điện thoại gồm 10 kí tự bao gồm số 0 ở đầu (bắt buộc). | ❌ NOT NULL | ✅ Đã map |
| 12 | `Channel` | Channel | `programCodeMiningChannel` | string | **TRIM**. **BẮT BUỘC** thuộc: `DSA`, `DSA/Renew`, `DSA_NEO`, `TSA`, `Renew`, `CTV_TSA (TSA 2)`, `CTV_TSA (TSA 2)/Renew`, `HO`, `Digital`, `Referral`. **Sai chính tả/định dạng sẽ bị từ chối.** | ❌ NOT NULL | ✅ Đã validate |
| 13 | `NOTE` | Ghi chú | `note` | string | **TRIM**. | ✅ | ✅ Đã map |

---


---


---


---

## 🔍 Bảng Cập Nhật Kiểm Tra Null Nhanh (Quick Null Check)
> Bảng này tổng hợp nhanh các trường bắt buộc và tùy chọn để dễ hình dung tổng thể.

| STT | Cột Excel (Upload) | DB Field | Trạng thái Nullable |
|---|---|---|---|
| 1 | `Mã hợp đồng` | `contractId` | ❌ NOT NULL |
| 2 | `Tên khách hàng` | `payerName → peopleName` | ❌ NOT NULL |
| 3 | `Sản phẩm` | `majorName` | ❌ NOT NULL |
| 4 | `Đối tác nhà bảo hiểm` | `companyProviderName` | ❌ NOT NULL |
| 5 | `Tên khách hàng` | `payerName` | ❌ NOT NULL |
| 6 | `Số tiền thanh toán` | `amountPay` | ❌ NOT NULL |
| 7 | `Ngày bắt đầu` | `contractObjectStartDate` | ❌ NOT NULL |
| 8 | `Ngày kết thúc` | `contractObjectEndDate` | ❌ NOT NULL |
| 9 | `Ngày thanh toán` | `payment_date` | ❌ NOT NULL |
| 10 | `Ngày cập nhật` | `modifiedAt` | ✅ Nullable (Có thể null) |
| 11 | `Trạng thái` | `termsFeePaymentMethod` | ✅ Nullable (Có thể null) |
| 12 | `Code sale` | `saleId` | ❌ NOT NULL |
| 13 | `Channel` | `programCodeMiningChannel` | ❌ NOT NULL |
| 14 | `NOTE` | `note` | ✅ Nullable (Có thể null) |

## ✅ Rules Đã Implement

| Rule | Field | Trạng thái |
|------|-------|------------|
| Mirror buyer → insured | `payerName` → `peopleName` | ✅ Đã implement |
| Amount >= 1,000 + parse định dạng VN | `amountPay` | ✅ Đã implement |
| Date order | `contractObjectStartDate`, `contractObjectEndDate` | ✅ Đã implement |
| Payment date <= today | `payment_date` | ✅ Đã implement |

---

## 🧩 Color Coding từ File Chuẩn

| Màu | Ý nghĩa | Fields |
|-----|---------|--------|
| 🟠 **Cam nhạt** | Headers chung — thông tin hợp đồng | Tất cả fields |
| 🟡 **Vàng** | Sản phẩm — cần validate theo nhà BH | majorName |
| 🟡 **Vàng đậm** | Code sale, Channel, Hình thức thanh toán | saleId, programCodeMiningChannel, termsFeePaymentMethod |

---

## 📊 Ví Dụ Dữ Liệu Mẫu

```
payerName (→peopleName): "CÔNG TY A"            (UPPER, có dấu, trim)
contractId:               "7123123"              (trim)
majorName:                "Bảo hiểm mọi rủi ro" (trim)
companyProviderName:      "Bảo Minh"             (trim)
amountPay:                1061199.0              (converted)
contractObjectStartDate:  "2025-11-26"           (converted from 26/11/2025)
contractObjectEndDate:    "2026-11-25"           (converted)
payment_date:             "2025-11-20"           (parsed from input 20/11/2025)
saleId:                   "0968772892"           (10 số, bắt đầu 0)
channelId:                "DSA"
```

---

## 📌 Đặc biểm Hazard / BHRR / BH Tài Sản

- Hazard là loại BH **đơn giản nhất** — ít field nhất (chỉ ~13 fields)
- Buyer = Insured → `payerName` mirror sang `peopleName`
- Cột `Trạng thái` map sang `termsFeePaymentMethod` (design đặc biệt)
- Không có thông tin NĐBH/NMBH riêng biệt
- Loại BH này chủ yếu cho **doanh nghiệp** (Công ty), không phải cá nhân
- File chuẩn có label là **"BHRR/ BH TÀI SẢN"**

---

> **Ghi chú:** Hazard là loại BH offline-only, đơn giản nhất trong 6 loại. `payerName` được
> mirror sang `peopleName` trong `post_process()`. `Trạng thái` map sang `termsFeePaymentMethod`
> là thiết kế đặc biệt cần lưu ý.
