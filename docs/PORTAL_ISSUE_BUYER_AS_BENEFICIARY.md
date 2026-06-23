# Logic Người Mua BH vs Người Được BH

Tài liệu này mô tả logic hiện tại trong backend về mối quan hệ giữa:
- Người mua bảo hiểm (`payer*`)
- Người được hưởng/được bảo hiểm (`people*`)

---

## 1. Nguyên tắc chung

1. Dữ liệu luôn ưu tiên giữ cả 2 nhóm field:
- `payer*`: thông tin bên mua
- `people*`: thông tin người được bảo hiểm

2. Business key dùng cho validate + duplicate luôn lấy theo phía `people`:
- `contractId`
- `peopleName`
- `majorName`
- `companyProviderName`

3. Nếu `peopleName` bị thiếu, hệ thống có cơ chế fallback từ `payerName` (tùy loại BH), để đảm bảo record không fail vì thiếu business key.

---

## 2. Flow xử lý chuẩn

### Bước A: Transform từ Excel -> ContractRecord

Trong `transform_records`, hệ thống đảm bảo có `peopleName`:
- Nếu `peopleName` trống
- Và mapping của loại BH trả về `name_field != peopleName`
- Thì copy `row_dict[name_field]` vào `row_dict[peopleName]`

Mục tiêu: không để thiếu `peopleName` trước khi validate business key.

### Bước B: Post-process theo từng loại

Mỗi processor sẽ áp dụng logic fallback/mirror khác nhau giữa `payer*` và `people*`.

### Bước C: Validate

- Validate required fields luôn kiểm tra `peopleName` (không kiểm tra `payerName` thay thế cho business key).
- Ngoài ra còn kiểm tra các field bắt buộc riêng theo từng loại BH.

### Bước D: Duplicate check

Duplicate dùng key 7 trường:
- `contractId`, `peopleName`, `majorName`, `companyProviderName`, `startDate`, `endDate`, `feeInsurance`

Trong đó tên luôn lấy từ `peopleName` (đã qua fallback từ các bước trên nếu cần).

---

## 3. Logic theo từng loại bảo hiểm

## 3.1. MOTO

Đặc thù: buyer gần như là insured.

- `get_name_field()` trả về `payerName`
- Post-process:
  - Nếu `peopleName` trống và có `payerName` -> `peopleName = payerName`
  - Nếu `peoplePhone` trống và có `payerPhone` -> `peoplePhone = payerPhone`
  - Nếu `peopleEmail` trống và có `payerEmail` -> `peopleEmail = payerEmail`
  - Nếu `peopleRelationship` trống -> set `0` (bản thân)

Kết luận: MOTO đang dùng mô hình buyer = beneficiary mặc định.

## 3.2. HAZARD

Đặc thù: tương tự MOTO (1 người là chính).

- `get_name_field()` trả về `payerName`
- Post-process:
  - Nếu `peopleName` trống và có `payerName` -> `peopleName = payerName`
  - Nếu `peopleRelationship` trống -> set `0`

Kết luận: HAZARD cũng theo mô hình buyer = beneficiary mặc định.

## 3.3. VEHICLE

Đặc thù: owner/insured thường trùng nhau, nhưng mapping gốc có cột insured.

- `get_name_field()` vẫn là `peopleName`
- Post-process có fallback các field contact từ `payer` sang `people`:
  - `peoplePhone <- payerPhone` nếu thiếu
  - `peopleEmail <- payerEmail` nếu thiếu
  - `peopleAddress <- payerAddress` nếu thiếu
  - `peopleName <- payerName` nếu `peopleName` trống
- Nếu `peopleRelationship` trống -> set `0`

Kết luận: ưu tiên people, nhưng tự bù từ payer khi thiếu.

## 3.4. HEALTH

Đặc thù: thường có cả người mua và người được BH tách biệt, nhưng hỗ trợ self-purchase.

- `get_name_field()` trả về `peopleName`
- Post-process:
  - Chuẩn hóa cả `payerName` và `peopleName`
  - Buyer-as-beneficiary fallback:
    - Nếu `peopleName` trống và có `payerName` -> copy sang people
    - Đồng thời fill thêm `peopleDob`, `peopleLicense`, `peopleAddress`, `peopleEmail`, `peoplePhone` từ payer nếu thiếu
    - Nếu `peopleRelationship` trống -> set về "Bản thân"

Kết luận: HEALTH hỗ trợ cả 2 mô hình (mua cho người khác hoặc tự mua cho mình).

## 3.5. MEDICAL_SOCIAL

Đặc thù: tương tự HEALTH nhưng enum/validate riêng cho BHYT/BHXH.

- `get_name_field()` trả về `payerName`
- Post-process:
  - Buyer-as-beneficiary fallback gần giống HEALTH
  - Nếu `peopleName` trống và có `payerName` -> copy sang people
  - Fill các field people từ payer nếu thiếu (`Dob`, `License`, `Address`, `Phone`, `Email`)
  - Nếu quan hệ thiếu -> set self

Kết luận: thiên về logic self-purchase fallback, vẫn giữ được cả 2 nhóm field.

## 3.6. TRAVEL

Đặc thù: hỗ trợ mạnh dữ liệu một phía (chỉ buyer hoặc chỉ insured).

- Post-process dùng two-way fallback:
  - Nếu `peopleName` trống và có `payerName` -> `peopleName = payerName`
  - Nếu `payerName` trống và có `peopleName` -> `payerName = peopleName`
  - Tương tự cho một số field khác như `Dob`, `License`, `Phone`

Kết luận: TRAVEL linh hoạt nhất, đồng bộ hai chiều giữa buyer và insured.

---

## 4. Kết luận nghiệp vụ

1. Hệ thống luôn cần `peopleName` để làm business key.
2. `payerName` là nguồn fallback quan trọng để cứu dữ liệu thiếu.
3. Với loại BH cá nhân (MOTO/HAZARD), hệ thống mặc định buyer = insured.
4. Với loại có thể mua cho người khác (HEALTH/TRAVEL/MEDICAL_SOCIAL/VEHICLE), hệ thống ưu tiên giữ tách biệt, nhưng có fallback để tránh rớt dữ liệu.

---

## 5. Gợi ý vận hành dữ liệu

1. Nếu file có đủ cả người mua và người được BH, hãy điền đầy đủ cả hai nhóm cột để tránh suy diễn fallback.
2. Nếu nghiệp vụ thực sự là tự mua cho chính mình, có thể chỉ cần nhóm buyer; hệ thống sẽ tự bù sang people theo rules của từng loại.
3. Khi debug duplicate, luôn kiểm tra `peopleName` sau post-process vì đây là field tham gia key.
