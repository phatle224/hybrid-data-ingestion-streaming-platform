# 🔄 Portal → CDC Reporting — Sync Changelog

> Tài liệu này mô tả các thay đổi đã thực hiện trên **Portal (`affina_portal_cdc`)** và những cập nhật tương ứng cần thực hiện trên **CDC Reporting (`cdc_reporting`)** để hai hệ thống đồng bộ.

---

## 📌 Tổng quan

Portal đã có 2 nhóm thay đổi rõ rệt:
1. **Thay đổi cấu trúc chung (Áp dụng cho TOÀN BỘ lỗi bảo hiểm)**: Cập nhật Business Keys check duplicate (từ 4 → 7 fields) và đổi tên mapping field thanh toán chung.
2. **Thay đổi riêng cho loại bảo hiểm HEALTH (Sức khỏe)**: Thêm validation rules chi tiết, chuẩn hoá dữ liệu và chỉnh sửa mapping bị sai.

---

## 🌍 BẢN CHUNG: ÁP DỤNG CHO TOÀN BỘ 7 LOẠI BẢO HIỂM

### 1. Đồng bộ Field `termsFeePaymentMethod` (Áp dụng: Toàn bộ)
Trong **Portal**, field `'Hình thức thanh toán'` đã được đổi mapping từ `paymentMethod` thành `termsFeePaymentMethod` để khớp với DB Schema. 
- **Bên CDC Reporting ([excel_mapping_config.py](file:///D:/affina/phase_cdc/cdc_reporting/services/streaming_etl/src/excel_mapping_config.py))**: Hiện tại TẤT CẢ các loại bảo hiểm đang map là `'paymentMethod'`.
  👉 **Hành động**: Cần thay đổi chữ `'paymentMethod'` thành `'termsFeePaymentMethod'` ở toàn bộ cấu hình: `TRAVEL_MAPPING`, `VEHICLE_MAPPING`, `MOTO_MAPPING`, `MEDICAL_SOCIAL_MAPPING` v.v trong CDC Reporting.

### 2. Cập nhật 7 Business Keys Deduplication (Áp dụng: Toàn bộ)
Portal hiện tại đã nâng cấp rule chống trùng lặp từ **4 keys** lên **7 Business Keys** cho DỮ LIỆU CỦA TẤT CẢ LOẠI BẢO HIỂM. Các field bao gồm: `contractId`, `peopleName/name`, `majorName`, `companyProviderName`, `contractStartDate/startDate`, `contractEndDate/endDate`, `feeInsurance`.

👉 **Các mục cần đổi bên CDC Reporting**:
- [streaming_etl_consumer.py](file:///D:/affina/phase_cdc/cdc_reporting/services/streaming_etl/src/streaming_etl_consumer.py): Các module [_has_online_duplicate()](file:///D:/affina/phase_cdc/cdc_reporting/services/streaming_etl/src/streaming_etl_consumer.py#264-302) và [_remove_conflicting_offline()](file:///D:/affina/phase_cdc/cdc_reporting/services/streaming_etl/src/streaming_etl_consumer.py#539-575) cần được cập nhật SQL check bằng 7 fields để tương thích. 
- [redis_cache_builder.py](file:///D:/affina/phase_cdc/cdc_reporting/services/streaming_etl/src/redis_cache_builder.py): Khóa Redis hiện chỉ cache 4 keys `contractId + name + majorName + companyProviderName`. Phải SỬA ĐỔI để thu thập và cache bổ sung 3 field: `startDate`, `endDate`, và `feeInsurance`. *(Lưu ý Date phải parse về chuẩn `YYYY-MM-DD` và feeInsurance phải xoá trailing zeros để compare an toàn)*.

---

## 🏥 BẢN RIÊNG: ÁP DỤNG CHO BẢO HIỂM HEALTH (SỨC KHOẺ)

### 1. Field Mapping — [health_mapping.py](file:///d:/affina/phase_cdc/affina_portal_cdc/backend/configs/mappings/health_mapping.py)
| Thông tin | Cột Excel | Portal Map | CDC Map Cũ | Cần Phải Đổi Thành |
|---|---|---|---|---|
| Chỉnh sửa Phí | `Phí bảo hiểm` | `feeInsurance` | `feeMainBenefit` | `feeInsurance` |

> [!WARNING]
> Các bảo hiểm khác (MOTO, VEHICLE, MEDICAL, TRAVEL) trong hệ thống CDC hiện **ĐÃ MAP ĐÚNG** `feeInsurance`. Riêng HEALTH ngày xưa map nhầm sang `feeMainBenefit`. Vì Portal ghi vào `feeInsurance`, nếu CDC quét file mà vẫn dùng `feeMainBenefit` sẽ gây MẤT DATA phí bảo hiểm do 2 tên field lệch nhau.

### 2. Danh sách Mở rộng NOT NULL (Portal [health_mapping.py](file:///d:/affina/phase_cdc/affina_portal_cdc/backend/configs/mappings/health_mapping.py))
| | Nội dung kiểm tra | Chi tiết quy tắc đã đưa vào Cổng Portal |
|---|---|---|
| **OR logic** | Quản lý CCCD / Passport | 1 trong 2 bắt buộc phải có thông tin (Không kiểm tra riêng từng cái).
| **Danh sách field** | Bắt buộc 17+ fields | Đảm bảo nhập tối đa dữ liệu thông tin (SDT, Email, DOB NĐBH...).

### 3. Tăng cường Validation & Normalize — [health_processor.py](file:///d:/affina/phase_cdc/affina_portal_cdc/backend/services/processors/health_processor.py)
Nếu CDC muốn implement cùng rule để giữ tính nhất quán, hãy chỉnh sửa [processors/health_processor.py](file:///d:/affina/phase_cdc/affina_portal_cdc/backend/services/processors/health_processor.py):
- **Title Case**: Viết hoa chữ cái đầu cho `peopleName`, `payerName` (vd: `Trịnh Bảo Ngọc`).
- **Phone format**: Normalize regex `^0\d{9,10}$`, tự động thêm prepent `0` vào đầu để khôi phục sdt bị Excel nuốt.
- **Buyer-as-beneficiary fallback**: Nếu `peopleName` trống → copy từ `payerName`; set `peopleRelationship = 'Bản thân'`. *(Chưa có trong source CDC cũ).*
- **Phân tách Validation Phase**: Gender và Relationship trong Portal được kiểm tra Enum trước (Pass/Fail) -> Rồi Convert sau. Trong CDC cũ chỉ đơn giản get và Convert, Fail thì Remove.

---

## 📋 Checklist Công Việc CDC Reporting Cần Làm Ngay

| # | File CDC Reporting | Thay đổi | Mức độ | Status |
|---|-------------------|----------|--------|--------|
| 1 | [excel_mapping_config.py](file:///D:/affina/phase_cdc/cdc_reporting/services/streaming_etl/src/excel_mapping_config.py) | Rename **tất cả** `paymentMethod` → `termsFeePaymentMethod` cho Toàn Bộ Bảo Hiểm. Đổi `feeMainBenefit`→`feeInsurance` **riêng** cho HEALTH_MAPPING. | 🔴 Quan trọng | ✅ Đã xong |
| 2 | `configs/mappings/*_mapping.py` | Rename field đồng loạt giống mục (1), cập nhật List return fields của từng loại. | 🔴 Quan trọng | ✅ Đã xong |
| 3 | [streaming_etl_consumer.py](file:///D:/affina/phase_cdc/cdc_reporting/services/streaming_etl/src/streaming_etl_consumer.py) | **Update deduplication logic** ([_has_online_duplicate](file:///D:/affina/phase_cdc/cdc_reporting/services/streaming_etl/src/streaming_etl_consumer.py#264-302), [_remove_conflicting_offline](file:///D:/affina/phase_cdc/cdc_reporting/services/streaming_etl/src/streaming_etl_consumer.py#539-575)) và Redis bk keys dùng 7 Business Keys | 🔴 Quan trọng | ✅ Đã xong |
| 4 | [redis_cache_builder.py](file:///D:/affina/phase_cdc/cdc_reporting/services/streaming_etl/src/redis_cache_builder.py) | **Cập nhật Build Redis cache** check 7 Business Keys thay vì 4. Bổ sung normalization Date & Fee. | 🔴 Quan trọng | ✅ Đã xong |
| 5 | Các `*_processor.py` | Xây dựng logic normalize dữ liệu chung (TitleCase, Format Date & Phone) và Fallback mua hộ giống của Cổng Portal. | 🟡 Nên làm | ✅ Đã xong (HEALTH) |
| 6 | [merge_etl.py](file:///D:/affina/phase_cdc/cdc_reporting/services/streaming_etl/src/merge_etl.py) | **KHÔNG CẦN** thay đổi (đọc từ dữ liệu hệ staging CDC online schema, keys khác) | ✅ Không cần | ✅ OK |

---
> **Ghi chú**: Đội ngũ CDC lưu ý xử lý toàn diện các update Cấu hình General (Mục 1) và Cấu hình Redis/ETL (Mục 2) đầu tiên trước khi scale sâu vào Rule Validate của riêng Health.
