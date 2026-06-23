# Hướng Dẫn Chi Tiết Dữ Liệu Các Database Sandbox

Tài liệu này giải thích bằng văn bản về mục đích của từng database và chức năng lưu trữ của từng bảng (table) bên trong hệ thống sandbox (localhost), giúp người đọc dễ dàng hình dung cấu trúc dữ liệu tổng thể.

## 🗄️ Database: `affina_authentication`
**Mục đích:** Quản lý xác thực, phân quyền người dùng (cả người dùng cuối và admin), lưu trữ token và cấu hình đăng nhập SSO (Google, Facebook, Apple).

**Giải thích các bảng (Tables) trong Database:**

- **`admin`**: Lưu trữ dữ liệu chi tiết của đối tượng `admin`.
- **`app`**: Lưu trữ dữ liệu chi tiết của đối tượng `app`.
- **`authorization`**: Lưu trữ dữ liệu chi tiết của đối tượng `authorization`.
- **`otpCode`**: Lưu trữ dữ liệu chi tiết của đối tượng `otpCode`.
- **`otpConfig`**: Lưu trữ các cài đặt, cấu hình của hệ thống cho otpConfig.
- **`otpHistory`**: Thông tin lịch sử mã otp
- **`otpLynkId`**: Lưu trữ dữ liệu chi tiết của đối tượng `otpLynkId`.

---

## 🗄️ Database: `affina_normalize`
**Mục đích:** Lưu trữ dữ liệu đã được chuẩn hóa (normalize) từ các hệ thống hoặc định dạng khác nhau về chuẩn chung của hệ thống Affina, hỗ trợ quá trình ETL và đồng bộ.

**Giải thích các bảng (Tables) trong Database:**

- **`etl_watermark`**: Lưu trữ dữ liệu chi tiết của đối tượng `etl_watermark`.
- **`norClaim`**: Lưu trữ dữ liệu Claim đã được chuẩn hóa (normalize) từ các nguồn khác.
- **`norContract`**: Lưu trữ dữ liệu Contract đã được chuẩn hóa (normalize) từ các nguồn khác.
- **`norContractObject`**: Lưu trữ dữ liệu ContractObject đã được chuẩn hóa (normalize) từ các nguồn khác.

---

## 🗄️ Database: `affina_notification`
**Mục đích:** Quản lý toàn bộ hệ thống thông báo đa kênh, bao gồm template tin nhắn, cấu hình gửi và lịch sử gửi qua Email, SMS, Push Notification.

**Giải thích các bảng (Tables) trong Database:**

- **`config`**: Lưu trữ các cài đặt, cấu hình của hệ thống cho config.
- **`logs`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến logs.
- **`template`**: Lưu trữ dữ liệu chi tiết của đối tượng `template`.

---

## 🗄️ Database: `affina_other`
**Mục đích:** Lưu trữ các dữ liệu phụ trợ, nội dung hiển thị (banner, video, event), thông tin ngân hàng, và các cấu hình động không thuộc các luồng nghiệp vụ chính.

**Giải thích các bảng (Tables) trong Database:**

- **`affinaNews`**: Bảng chứa tin tức landing page
- **`affinaVideo`**: Lưu trữ dữ liệu chi tiết của đối tượng `affinaVideo`.
- **`agencyNews`**: Lưu trữ dữ liệu chi tiết của đối tượng `agencyNews`.
- **`agencyslider`**: Lưu trữ dữ liệu chi tiết của đối tượng `agencyslider`.
- **`agencyTopic`**: Lưu trữ dữ liệu chi tiết của đối tượng `agencyTopic`.
- **`bankFullerton`**: Lưu trữ dữ liệu chi tiết của đối tượng `bankFullerton`.
- **`bankFullerton_prod`**: Lưu trữ dữ liệu chi tiết của đối tượng `bankFullerton_prod`.
- **`bankInsmart`**: Lưu trữ dữ liệu chi tiết của đối tượng `bankInsmart`.
- **`banner`**: Lưu trữ dữ liệu chi tiết của đối tượng `banner`.
- **`card`**: Lưu trữ dữ liệu chi tiết của đối tượng `card`.
- **`cardOrder`**: Lưu trữ dữ liệu chi tiết của đối tượng `cardOrder`.
- **`cardOrderField`**: Lưu trữ dữ liệu chi tiết của đối tượng `cardOrderField`.
- **`consent`**: Lưu trữ dữ liệu chi tiết của đối tượng `consent`.
- **`country`**: Lưu trữ dữ liệu chi tiết của đối tượng `country`.
- **`coverImageProgram`**: Lưu trữ dữ liệu chi tiết của đối tượng `coverImageProgram`.
- **`Documents`**: Lưu trữ dữ liệu chi tiết của đối tượng `Documents`.
- **`encryptionFilesOfPartner`**: Lưu trữ dữ liệu chi tiết của đối tượng `encryptionFilesOfPartner`.
- **`event`**: Lưu trữ dữ liệu chi tiết của đối tượng `event`.
- **`eventConditionAge`**: Lưu trữ dữ liệu chi tiết của đối tượng `eventConditionAge`.
- **`eventConditionDistricts`**: Lưu trữ dữ liệu chi tiết của đối tượng `eventConditionDistricts`.
- **`eventHistorySent`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến eventHistorySent.
- **`eventUser`**: Lưu trữ dữ liệu chi tiết của đối tượng `eventUser`.
- **`formClaim`**: Lưu trữ dữ liệu chi tiết của đối tượng `formClaim`.
- **`groupProgram`**: Lưu trữ dữ liệu chi tiết của đối tượng `groupProgram`.
- **`health_insurance_insmart_request`**: Staging table storing claim data received from Insmart health insurance API
- **`holiday`**: Lưu trữ dữ liệu chi tiết của đối tượng `holiday`.
- **`hospitalFullerton`**: Lưu trữ dữ liệu chi tiết của đối tượng `hospitalFullerton`.
- **`hospitals`**: Lưu trữ dữ liệu chi tiết của đối tượng `hospitals`.
- **`iconBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `iconBenefit`.
- **`iconBenefitDetail`**: Lưu trữ dữ liệu chi tiết của đối tượng `iconBenefitDetail`.
- **`iconFlexi`**: Lưu trữ dữ liệu chi tiết của đối tượng `iconFlexi`.
- **`imageClaim`**: Lưu trữ dữ liệu chi tiết của đối tượng `imageClaim`.
- **`imageClaimDetail`**: Lưu trữ dữ liệu chi tiết của đối tượng `imageClaimDetail`.
- **`logo`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến logo.
- **`memberBanksFullerton`**: Lưu trữ dữ liệu chi tiết của đối tượng `memberBanksFullerton`.
- **`newProvinces`**: Data tỉnh thành mới
- **`news`**: Lưu trữ dữ liệu chi tiết của đối tượng `news`.
- **`newsComment`**: Lưu trữ dữ liệu chi tiết của đối tượng `newsComment`.
- **`newsLike`**: Lưu trữ dữ liệu chi tiết của đối tượng `newsLike`.
- **`notification`**: Lưu trữ dữ liệu chi tiết của đối tượng `notification`.
- **`notificationConditionAge`**: Lưu trữ dữ liệu chi tiết của đối tượng `notificationConditionAge`.
- **`notificationConditionDistricts`**: Lưu trữ dữ liệu chi tiết của đối tượng `notificationConditionDistricts`.
- **`notificationHistorySent`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến notificationHistorySent.
- **`notificationTopic`**: Lưu trữ dữ liệu chi tiết của đối tượng `notificationTopic`.
- **`notificationUser`**: Lưu trữ dữ liệu chi tiết của đối tượng `notificationUser`.
- **`ocrCarPart`**: Thông tin đọc được hình ảnh xe
- **`ocrCarSide`**: Thông tin đọc được hình ảnh hướng xe
- **`ocrMotoRegistrationBack`**: Thông tin đọc được mặt sau giấy đăng ký xe máy
- **`ocrMotoRegistrationFront`**: Thông tin đọc được mặt trước giấy đăng ký xe máy
- **`ocrVehicleRegistrationBack`**: Thông tin đọc được mặt sau giấy đăng ký xe
- **`ocrVehicleRegistrationFront`**: Thông tin đọc được mặt trước giấy đăng ký xe
- **`ocrVehicleRegistrationInspection`**: Thông tin đọc được giấy kiểm định xe
- **`old_district_mapping_copy`**: Lưu trữ dữ liệu chi tiết của đối tượng `old_district_mapping_copy`.
- **`old_province_mapping_copy`**: Lưu trữ dữ liệu chi tiết của đối tượng `old_province_mapping_copy`.
- **`old_ward_mapping_copy`**: Lưu trữ dữ liệu chi tiết của đối tượng `old_ward_mapping_copy`.
- **`partnerRelationship`**: Lưu trữ dữ liệu chi tiết của đối tượng `partnerRelationship`.
- **`provinces`**: provinces
- **`provincesLatLonIncluded`**: provinces
- **`provincesOutdated`**: Lưu trữ dữ liệu chi tiết của đối tượng `provincesOutdated`.
- **`provinces_1`**: Lưu trữ dữ liệu chi tiết của đối tượng `provinces_1`.
- **`relationship`**: Lưu trữ dữ liệu chi tiết của đối tượng `relationship`.
- **`SaleUpdateStatusNotification`**: Lưu trữ dữ liệu chi tiết của đối tượng `SaleUpdateStatusNotification`.
- **`schedule`**: Lưu trữ dữ liệu chi tiết của đối tượng `schedule`.
- **`topic`**: Lưu trữ dữ liệu chi tiết của đối tượng `topic`.
- **`vcard`**: Lưu trữ dữ liệu chi tiết của đối tượng `vcard`.

---

## 🗄️ Database: `affina_partner`
**Mục đích:** Quản lý thông tin đối tác phân phối, thông tin API tích hợp, đại lý, và các giao dịch, chiến dịch liên quan tới đối tác B2B.

**Giải thích các bảng (Tables) trong Database:**

- **`affina_claim_code`**: Lưu trữ dữ liệu chi tiết của đối tượng `affina_claim_code`.
- **`bao_minh_claim_history`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến bao_minh_claim_history.
- **`bao_minh_hospital`**: Lưu trữ dữ liệu chi tiết của đối tượng `bao_minh_hospital`.
- **`bao_minh_membership`**: Lưu trữ dữ liệu chi tiết của đối tượng `bao_minh_membership`.
- **`client`**: Lưu trữ dữ liệu chi tiết của đối tượng `client`.
- **`health_insurance_fullerton_request`**: Lưu trữ dữ liệu chi tiết của đối tượng `health_insurance_fullerton_request`.
- **`health_insurance_insmart_request`**: Staging table storing claim data received from Insmart health insurance API
- **`health_insurance_request`**: Lưu trữ dữ liệu chi tiết của đối tượng `health_insurance_request`.
- **`partner`**: Lưu trữ dữ liệu chi tiết của đối tượng `partner`.

---

## 🗄️ Database: `insuranceReporting`
**Mục đích:** Chứa các bảng dữ liệu tổng hợp (Data Mart/Data Warehouse thu nhỏ) phục vụ riêng cho việc xuất báo cáo, thống kê, và xây dựng biểu đồ BI.

**Giải thích các bảng (Tables) trong Database:**

- **`contract`**: ODS Wide table - merge online (CDC) + offline (Excel) data - 8 insurance types
- **`profiling_analysis`**: Lưu trữ dữ liệu chi tiết của đối tượng `profiling_analysis`.

---

## 🗄️ Database: `insuranceSale`
**Mục đích:** Quản lý luồng kinh doanh (Sale), chứa thông tin cốt lõi về hợp đồng, chứng nhận bảo hiểm, giao dịch thanh toán, hóa đơn và tiến trình bán hàng.

**Giải thích các bảng (Tables) trong Database:**

- **`addonProduct`**: Lưu trữ dữ liệu chi tiết của đối tượng `addonProduct`.
- **`answer`**: Thông tin câu trả lời
- **`benefitConfig`**: Lưu trữ các cài đặt, cấu hình của hệ thống cho benefitConfig.
- **`benefitHistory`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến benefitHistory.
- **`benefitUserList`**: Lưu trữ dữ liệu chi tiết của đối tượng `benefitUserList`.
- **`billExclusionTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `billExclusionTerms`.
- **`billFeeAndMaximumAmountOrRatioSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `billFeeAndMaximumAmountOrRatioSideBenefit`.
- **`billFeeOrMaximumAmountInsurance`**: Lưu trữ dữ liệu chi tiết của đối tượng `billFeeOrMaximumAmountInsurance`.
- **`billMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `billMainBenefit`.
- **`billMaximumAmountOrRatioMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `billMaximumAmountOrRatioMainBenefit`.
- **`billMaximumAmountOrRatioSubMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `billMaximumAmountOrRatioSubMainBenefit`.
- **`billMaximumAmountOrRatioSubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `billMaximumAmountOrRatioSubSideBenefit`.
- **`billPackage`**: Lưu trữ dữ liệu chi tiết của đối tượng `billPackage`.
- **`billParticipationTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `billParticipationTerms`.
- **`billProduct`**: Lưu trữ dữ liệu chi tiết của đối tượng `billProduct`.
- **`billProgram`**: Lưu trữ dữ liệu chi tiết của đối tượng `billProgram`.
- **`billRightToSell`**: Lưu trữ dữ liệu chi tiết của đối tượng `billRightToSell`.
- **`billSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `billSideBenefit`.
- **`billSubMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `billSubMainBenefit`.
- **`billSubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `billSubSideBenefit`.
- **`billTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `billTerms`.
- **`bonus`**: Lưu trữ dữ liệu chi tiết của đối tượng `bonus`.
- **`bonusConfig`**: Lưu trữ các cài đặt, cấu hình của hệ thống cho bonusConfig.
- **`budgetAff`**: Lưu trữ dữ liệu chi tiết của đối tượng `budgetAff`.
- **`budgetAffHistory`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến budgetAffHistory.
- **`budgetHistory`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến budgetHistory.
- **`budgetSme`**: Lưu trữ dữ liệu chi tiết của đối tượng `budgetSme`.
- **`budgetSmeHistory`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến budgetSmeHistory.
- **`budgetType`**: Lưu trữ dữ liệu chi tiết của đối tượng `budgetType`.
- **`budgetVoucher`**: Lưu trữ dữ liệu chi tiết của đối tượng `budgetVoucher`.
- **`budgetVoucherHistory`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến budgetVoucherHistory.
- **`campaignAff`**: Lưu trữ dữ liệu chi tiết của đối tượng `campaignAff`.
- **`campaignAffContent`**: Lưu trữ dữ liệu chi tiết của đối tượng `campaignAffContent`.
- **`campaignAffinaHistory`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến campaignAffinaHistory.
- **`campaignAffNotification`**: Lưu trữ dữ liệu chi tiết của đối tượng `campaignAffNotification`.
- **`campaignBannerPopup`**: Lưu trữ dữ liệu chi tiết của đối tượng `campaignBannerPopup`.
- **`campaignBannerPopupSchedule`**: Lưu trữ dữ liệu chi tiết của đối tượng `campaignBannerPopupSchedule`.
- **`campaignBudgetAff`**: Lưu trữ dữ liệu chi tiết của đối tượng `campaignBudgetAff`.
- **`campaignBudgetVoucher`**: Lưu trữ dữ liệu chi tiết của đối tượng `campaignBudgetVoucher`.
- **`campaignListVoucher`**: Lưu trữ dữ liệu chi tiết của đối tượng `campaignListVoucher`.
- **`campaignPackageAff`**: Lưu trữ dữ liệu chi tiết của đối tượng `campaignPackageAff`.
- **`campaignVoucher`**: Lưu trữ dữ liệu chi tiết của đối tượng `campaignVoucher`.
- **`campaignVoucherCondition`**: Lưu trữ dữ liệu chi tiết của đối tượng `campaignVoucherCondition`.
- **`campaignVoucherConditionAge`**: Lưu trữ dữ liệu chi tiết của đối tượng `campaignVoucherConditionAge`.
- **`campaignVoucherConditionRegion`**: Lưu trữ dữ liệu chi tiết của đối tượng `campaignVoucherConditionRegion`.
- **`campaignVoucherContent`**: Lưu trữ dữ liệu chi tiết của đối tượng `campaignVoucherContent`.
- **`campaignVoucherNotification`**: Lưu trữ dữ liệu chi tiết của đối tượng `campaignVoucherNotification`.
- **`campaignVoucherUser`**: Lưu trữ dữ liệu chi tiết của đối tượng `campaignVoucherUser`.
- **`childSubMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `childSubMainBenefit`.
- **`childSubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `childSubSideBenefit`.
- **`claim`**: Lưu trữ dữ liệu chi tiết của đối tượng `claim`.
- **`claim1`**: Lưu trữ dữ liệu chi tiết của đối tượng `claim1`.
- **`claimClone`**: Lưu trữ dữ liệu chi tiết của đối tượng `claimClone`.
- **`claimClone2`**: Lưu trữ dữ liệu chi tiết của đối tượng `claimClone2`.
- **`claimSme`**: Lưu trữ dữ liệu chi tiết của đối tượng `claimSme`.
- **`comboProduct`**: Lưu trữ dữ liệu chi tiết của đối tượng `comboProduct`.
- **`commissionApprovalHistory`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến commissionApprovalHistory.
- **`commissionWithdrawConfig`**: Bảng lưu cấu hình rút tiền hoa hồng cho từng công ty (sale)
- **`contract`**: Lưu trữ dữ liệu chi tiết của đối tượng `contract`.
- **`contractAdditionalInfo`**: Bảng lưu các thông tin thêm của hợp đồng
- **`contractAddonProduct`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractAddonProduct`.
- **`contractAddonProductBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractAddonProductBenefit`.
- **`contractCancellation`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractCancellation`.
- **`contractDropdownSelections`**: Lưu lựa chọn của khách hàng từ dropdown
- **`contractObject`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObject`.
- **`contractObjectBill`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectBill`.
- **`contractObjectBillExclusionTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectBillExclusionTerms`.
- **`contractObjectBillMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectBillMainBenefit`.
- **`contractObjectBillParticipationTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectBillParticipationTerms`.
- **`contractObjectBillSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectBillSideBenefit`.
- **`contractObjectBillSubMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectBillSubMainBenefit`.
- **`contractObjectBillSubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectBillSubSideBenefit`.
- **`contractObjectExclusionTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectExclusionTerms`.
- **`contractObjectHealthCheck`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectHealthCheck`.
- **`contractObjectHealthCheckMain`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectHealthCheckMain`.
- **`contractObjectHealthCheckMainChild`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectHealthCheckMainChild`.
- **`contractObjectHealthCheckMainGroup`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectHealthCheckMainGroup`.
- **`contractObjectHealthCheckSide`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectHealthCheckSide`.
- **`contractObjectHealthCheckSideChild`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectHealthCheckSideChild`.
- **`contractObjectHealthCheckSideGroup`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectHealthCheckSideGroup`.
- **`contractObjectHouse`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectHouse`.
- **`contractObjectHouseDetail`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectHouseDetail`.
- **`contractObjectHouseExclusionTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectHouseExclusionTerms`.
- **`contractObjectHouseMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectHouseMainBenefit`.
- **`contractObjectHouseParticipationTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectHouseParticipationTerms`.
- **`contractObjectHouseSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectHouseSideBenefit`.
- **`contractObjectHouseSubMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectHouseSubMainBenefit`.
- **`contractObjectHouseSubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectHouseSubSideBenefit`.
- **`contractObjectmedicalInsurance`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectmedicalInsurance`.
- **`contractObjectmedicalInsuranceExclusionTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectmedicalInsuranceExclusionTerms`.
- **`contractObjectmedicalInsuranceMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectmedicalInsuranceMainBenefit`.
- **`contractObjectmedicalInsuranceParticipationTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectmedicalInsuranceParticipationTerms`.
- **`contractObjectmedicalInsuranceSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectmedicalInsuranceSideBenefit`.
- **`contractObjectmedicalInsuranceSubMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectmedicalInsuranceSubMainBenefit`.
- **`contractObjectmedicalInsuranceSubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectmedicalInsuranceSubSideBenefit`.
- **`contractObjectMoto`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectMoto`.
- **`contractObjectMotoExclusionTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectMotoExclusionTerms`.
- **`contractObjectMotoMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectMotoMainBenefit`.
- **`contractObjectMotoParticipationTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectMotoParticipationTerms`.
- **`contractObjectMotoSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectMotoSideBenefit`.
- **`contractObjectMotoSubMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectMotoSubMainBenefit`.
- **`contractObjectMotoSubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectMotoSubSideBenefit`.
- **`contractObjectOffline`**: Thông tin đối tượng được bảo hiểm của loại bảo hiểm sức khỏe
- **`contractObjectParticipationTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectParticipationTerms`.
- **`contractObjectProductChildSubMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectProductChildSubMainBenefit`.
- **`contractObjectProductChildSubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectProductChildSubSideBenefit`.
- **`contractObjectProductLiability`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectProductLiability`.
- **`contractObjectProductLiabilityExclusionTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectProductLiabilityExclusionTerms`.
- **`contractObjectProductLiabilityMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectProductLiabilityMainBenefit`.
- **`contractObjectProductLiabilityParticipationTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectProductLiabilityParticipationTerms`.
- **`contractObjectProductLiabilitySideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectProductLiabilitySideBenefit`.
- **`contractObjectProductLiabilitySubMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectProductLiabilitySubMainBenefit`.
- **`contractObjectProductLiabilitySubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectProductLiabilitySubSideBenefit`.
- **`contractObjectProductMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectProductMainBenefit`.
- **`contractObjectProductSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectProductSideBenefit`.
- **`contractObjectProductSubMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectProductSubMainBenefit`.
- **`contractObjectProductSubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectProductSubSideBenefit`.
- **`contractObjectSocialInsurance`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectSocialInsurance`.
- **`contractObjectSocialInsuranceExclusionTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectSocialInsuranceExclusionTerms`.
- **`contractObjectSocialInsuranceMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectSocialInsuranceMainBenefit`.
- **`contractObjectSocialInsuranceParticipationTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectSocialInsuranceParticipationTerms`.
- **`contractObjectSocialInsuranceSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectSocialInsuranceSideBenefit`.
- **`contractObjectSocialInsuranceSubMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectSocialInsuranceSubMainBenefit`.
- **`contractObjectSocialInsuranceSubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectSocialInsuranceSubSideBenefit`.
- **`contractObjectTmp`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectTmp`.
- **`contractObjectTravel`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectTravel`.
- **`contractObjectTravelDetail`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectTravelDetail`.
- **`contractObjectTravelExclusionTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectTravelExclusionTerms`.
- **`contractObjectTravelParticipationTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectTravelParticipationTerms`.
- **`contractObjectTravelProgramBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectTravelProgramBenefit`.
- **`contractObjectTravelProgramBenefitBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectTravelProgramBenefitBenefit`.
- **`contractObjectTravelProgramBenefitBenefitGroup`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectTravelProgramBenefitBenefitGroup`.
- **`contractObjectTravelProgramBenefitSubBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectTravelProgramBenefitSubBenefit`.
- **`contractObjectVehicle`**: Thông tin đối tượng được bảo hiểm của loại bảo hiểm sức khỏe
- **`contractObjectVehicleBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObjectVehicleBenefit`.
- **`contractObject_old`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObject_old`.
- **`contractOffline`**: Thông tin các hợp đồng bảo hiểm Offline
- **`contractPermission`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractPermission`.
- **`contractQuestion`**: Đáp án khách hàng
- **`contractQuestionAdditionalInformationDetail`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractQuestionAdditionalInformationDetail`.
- **`contractRefund`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractRefund`.
- **`contractRequest`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractRequest`.
- **`contractUrlDownload`**: Bảng lưu các đường dẫn hợp đồng chưa hoàn thành
- **`customerDropdownOptions`**: Danh sách giá trị dropdown để khách hàng chọn
- **`deeplink`**: Lưu trữ dữ liệu chi tiết của đối tượng `deeplink`.
- **`deeplinkProduct`**: Lưu trữ dữ liệu chi tiết của đối tượng `deeplinkProduct`.
- **`department`**: Lưu trữ dữ liệu chi tiết của đối tượng `department`.
- **`doctors`**: Lưu trữ dữ liệu chi tiết của đối tượng `doctors`.
- **`doctor_specialty`**: Lưu trữ dữ liệu chi tiết của đối tượng `doctor_specialty`.
- **`exchangeInvite`**: Lưu trữ dữ liệu chi tiết của đối tượng `exchangeInvite`.
- **`exchangeProgram`**: Lưu trữ dữ liệu chi tiết của đối tượng `exchangeProgram`.
- **`exchangeVoucher`**: Lưu trữ dữ liệu chi tiết của đối tượng `exchangeVoucher`.
- **`exclusionTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `exclusionTerms`.
- **`favoriteHospital`**: Lưu trữ dữ liệu chi tiết của đối tượng `favoriteHospital`.
- **`feeAndMaximumAmountSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `feeAndMaximumAmountSideBenefit`.
- **`feeInsurance`**: Lưu trữ dữ liệu chi tiết của đối tượng `feeInsurance`.
- **`flexBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `flexBenefit`.
- **`frequentlyAskedQuestion`**: Lưu trữ dữ liệu chi tiết của đối tượng `frequentlyAskedQuestion`.
- **`healthCheck`**: Danh mục khám sức khỏe
- **`healthCheckChild`**: Lưu trữ dữ liệu chi tiết của đối tượng `healthCheckChild`.
- **`healthCheckGroup`**: Nhóm danh mục gói khám sức khỏe
- **`healthCheckProduct`**: Sản phẩm gói khám sức khỏe
- **`healthCheckProductMain`**: Các danh mục khám chính trong các nhóm danh mục khám chính
- **`healthCheckProductMainChild`**: Các danh mục khám con trong các danh mục khám chính
- **`healthCheckProductMainGroup`**: Các nhóm danh mục khám chính trong gói khám sức khỏe
- **`healthCheckProductSide`**: Các danh mục khám bổ sung trong các nhóm danh mục khám bổ sung
- **`healthCheckProductSideChild`**: Các danh mục khám con trong các danh mục khám bổ sung
- **`healthCheckProductSideGroup`**: Các danh mục khám bổ sung trong các nhóm danh mục khám bổ sung
- **`healthRecords`**: Lưu trữ dữ liệu chi tiết của đối tượng `healthRecords`.
- **`hierarchy`**: Lưu trữ dữ liệu chi tiết của đối tượng `hierarchy`.
- **`hospital`**: Lưu trữ dữ liệu chi tiết của đối tượng `hospital`.
- **`hospitalProvider`**: Lưu trữ dữ liệu chi tiết của đối tượng `hospitalProvider`.
- **`hospitalProviderProgram`**: Lưu trữ dữ liệu chi tiết của đối tượng `hospitalProviderProgram`.
- **`houseAmountMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `houseAmountMainBenefit`.
- **`houseAmountSubMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `houseAmountSubMainBenefit`.
- **`houseAmountSubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `houseAmountSubSideBenefit`.
- **`houseBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `houseBenefit`.
- **`houseExclusionTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `houseExclusionTerms`.
- **`houseFeeAndAmountSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `houseFeeAndAmountSideBenefit`.
- **`houseFeeInsurance`**: Lưu trữ dữ liệu chi tiết của đối tượng `houseFeeInsurance`.
- **`housePackage`**: Lưu trữ dữ liệu chi tiết của đối tượng `housePackage`.
- **`houseParticipationTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `houseParticipationTerms`.
- **`houseProduct`**: Lưu trữ dữ liệu chi tiết của đối tượng `houseProduct`.
- **`houseProductMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `houseProductMainBenefit`.
- **`houseProductSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `houseProductSideBenefit`.
- **`houseProductSubMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `houseProductSubMainBenefit`.
- **`houseProductSubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `houseProductSubSideBenefit`.
- **`houseProgram`**: Lưu trữ dữ liệu chi tiết của đối tượng `houseProgram`.
- **`houseRightToSell`**: Lưu trữ dữ liệu chi tiết của đối tượng `houseRightToSell`.
- **`houseSubBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `houseSubBenefit`.
- **`houseTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `houseTerms`.
- **`iconAnswer`**: Từng icon sẽ có một template icon
- **`iconAnswerGroup`**: Mẫu của từng nhóm icon
- **`insuranceProgramGroupIcon`**: Lưu trữ dữ liệu chi tiết của đối tượng `insuranceProgramGroupIcon`.
- **`insuranceProgramGroupSale`**: Lưu trữ dữ liệu chi tiết của đối tượng `insuranceProgramGroupSale`.
- **`insuranceProgramSale`**: Lưu trữ dữ liệu chi tiết của đối tượng `insuranceProgramSale`.
- **`ipn`**: Lưu trữ dữ liệu chi tiết của đối tượng `ipn`.
- **`ipnAppota`**: Lưu trữ dữ liệu chi tiết của đối tượng `ipnAppota`.
- **`ipnBaoKim`**: Lưu trữ dữ liệu chi tiết của đối tượng `ipnBaoKim`.
- **`ipnOCB`**: Thông tin log trả về kết quả thanh toán từ OCB
- **`ipnPVI`**: Thông tin log callback từ PVI
- **`ipnRefund`**: Lưu trữ dữ liệu chi tiết của đối tượng `ipnRefund`.
- **`ipnSmartPay`**: Lưu trữ dữ liệu chi tiết của đối tượng `ipnSmartPay`.
- **`kpi`**: Lưu trữ dữ liệu chi tiết của đối tượng `kpi`.
- **`kpiSchedule`**: Lưu trữ dữ liệu chi tiết của đối tượng `kpiSchedule`.
- **`loss_analysis`**: VIEW
- **`mainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `mainBenefit`.
- **`major`**: Lưu trữ dữ liệu chi tiết của đối tượng `major`.
- **`maximumAmountChildSubMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `maximumAmountChildSubMainBenefit`.
- **`maximumAmountChildSubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `maximumAmountChildSubSideBenefit`.
- **`maximumAmountMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `maximumAmountMainBenefit`.
- **`maximumAmountSubMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `maximumAmountSubMainBenefit`.
- **`maximumAmountSubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `maximumAmountSubSideBenefit`.
- **`medicalInsuranceExclusionTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `medicalInsuranceExclusionTerms`.
- **`medicalInsuranceFeeAndMaximumAmountSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `medicalInsuranceFeeAndMaximumAmountSideBenefit`.
- **`medicalInsuranceFeeInsurance`**: Lưu trữ dữ liệu chi tiết của đối tượng `medicalInsuranceFeeInsurance`.
- **`medicalInsuranceMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `medicalInsuranceMainBenefit`.
- **`medicalInsuranceMaximumAmountMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `medicalInsuranceMaximumAmountMainBenefit`.
- **`medicalInsuranceMaximumAmountSubMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `medicalInsuranceMaximumAmountSubMainBenefit`.
- **`medicalInsuranceMaximumAmountSubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `medicalInsuranceMaximumAmountSubSideBenefit`.
- **`medicalInsurancePackage`**: Thông tin gói bảo hiểm xã hội
- **`medicalInsuranceParticipationTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `medicalInsuranceParticipationTerms`.
- **`medicalInsuranceProduct`**: Thông tin sản phẩm sức khỏe
- **`medicalInsuranceProductMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `medicalInsuranceProductMainBenefit`.
- **`medicalInsuranceProductSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `medicalInsuranceProductSideBenefit`.
- **`medicalInsuranceProductSubMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `medicalInsuranceProductSubMainBenefit`.
- **`medicalInsuranceProductSubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `medicalInsuranceProductSubSideBenefit`.
- **`medicalInsuranceProgram`**: Thông tin chương trình bảo hiểm y tế
- **`medicalInsuranceRightToSell`**: Lưu trữ dữ liệu chi tiết của đối tượng `medicalInsuranceRightToSell`.
- **`medicalInsuranceSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `medicalInsuranceSideBenefit`.
- **`medicalInsuranceSubMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `medicalInsuranceSubMainBenefit`.
- **`medicalInsuranceSubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `medicalInsuranceSubSideBenefit`.
- **`medicalInsuranceTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `medicalInsuranceTerms`.
- **`motoExclusionTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `motoExclusionTerms`.
- **`motoFeeAndAmountSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `motoFeeAndAmountSideBenefit`.
- **`motoFeeAndAmountSubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `motoFeeAndAmountSubSideBenefit`.
- **`motoFeeInsurance`**: Lưu trữ dữ liệu chi tiết của đối tượng `motoFeeInsurance`.
- **`motoPackage`**: Lưu trữ dữ liệu chi tiết của đối tượng `motoPackage`.
- **`motoParticipationTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `motoParticipationTerms`.
- **`motoProduct`**: Lưu trữ dữ liệu chi tiết của đối tượng `motoProduct`.
- **`motoProductMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `motoProductMainBenefit`.
- **`motoProductSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `motoProductSideBenefit`.
- **`motoProductSubMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `motoProductSubMainBenefit`.
- **`motoProductSubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `motoProductSubSideBenefit`.
- **`motoProgram`**: Lưu trữ dữ liệu chi tiết của đối tượng `motoProgram`.
- **`motoRightToSell`**: Lưu trữ dữ liệu chi tiết của đối tượng `motoRightToSell`.
- **`motoTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `motoTerms`.
- **`package`**: Lưu trữ dữ liệu chi tiết của đối tượng `package`.
- **`participationTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `participationTerms`.
- **`patient`**: Lưu trữ dữ liệu chi tiết của đối tượng `patient`.
- **`pregnancy_view`**: VIEW
- **`product`**: Lưu trữ dữ liệu chi tiết của đối tượng `product`.
- **`productChildSubMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `productChildSubMainBenefit`.
- **`productChildSubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `productChildSubSideBenefit`.
- **`productConstraintApplicableRelationship`**: Lưu trữ dữ liệu chi tiết của đối tượng `productConstraintApplicableRelationship`.
- **`productLiabilityAmountMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `productLiabilityAmountMainBenefit`.
- **`productLiabilityAmountSubMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `productLiabilityAmountSubMainBenefit`.
- **`productLiabilityAmountSubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `productLiabilityAmountSubSideBenefit`.
- **`productLiabilityBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `productLiabilityBenefit`.
- **`productLiabilityCareerField`**: Lưu trữ dữ liệu chi tiết của đối tượng `productLiabilityCareerField`.
- **`productLiabilityExclusionTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `productLiabilityExclusionTerms`.
- **`productLiabilityFeeAndAmountSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `productLiabilityFeeAndAmountSideBenefit`.
- **`productLiabilityFeeInsurance`**: Lưu trữ dữ liệu chi tiết của đối tượng `productLiabilityFeeInsurance`.
- **`productLiabilityPackage`**: Lưu trữ dữ liệu chi tiết của đối tượng `productLiabilityPackage`.
- **`productLiabilityParticipationTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `productLiabilityParticipationTerms`.
- **`productLiabilityProduct`**: Lưu trữ dữ liệu chi tiết của đối tượng `productLiabilityProduct`.
- **`productLiabilityProductMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `productLiabilityProductMainBenefit`.
- **`productLiabilityProductSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `productLiabilityProductSideBenefit`.
- **`productLiabilityProductSubMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `productLiabilityProductSubMainBenefit`.
- **`productLiabilityProductSubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `productLiabilityProductSubSideBenefit`.
- **`productLiabilityProgram`**: Lưu trữ dữ liệu chi tiết của đối tượng `productLiabilityProgram`.
- **`productLiabilityRightToSell`**: Lưu trữ dữ liệu chi tiết của đối tượng `productLiabilityRightToSell`.
- **`productLiabilitySubBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `productLiabilitySubBenefit`.
- **`productLiabilityTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `productLiabilityTerms`.
- **`productLink`**: Lưu trữ dữ liệu chi tiết của đối tượng `productLink`.
- **`productMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `productMainBenefit`.
- **`productOutStanding`**: Lưu trữ dữ liệu chi tiết của đối tượng `productOutStanding`.
- **`productOutStandingConditionAge`**: Lưu trữ dữ liệu chi tiết của đối tượng `productOutStandingConditionAge`.
- **`productOutStandingConditionDistricts`**: Lưu trữ dữ liệu chi tiết của đối tượng `productOutStandingConditionDistricts`.
- **`productRule`**: Lưu trữ dữ liệu chi tiết của đối tượng `productRule`.
- **`productSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `productSideBenefit`.
- **`productSubMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `productSubMainBenefit`.
- **`productSubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `productSubSideBenefit`.
- **`profiling_analysis`**: VIEW
- **`program`**: Lưu trữ dữ liệu chi tiết của đối tượng `program`.
- **`programApplicableRelationship`**: Lưu trữ dữ liệu chi tiết của đối tượng `programApplicableRelationship`.
- **`programCommission`**: Lưu trữ dữ liệu chi tiết của đối tượng `programCommission`.
- **`programDropdownOptions`**: Danh sách giá trị dropdown clone riêng cho chương trình bảo hiểm
- **`programGroupDiscount`**: Lưu trữ dữ liệu chi tiết của đối tượng `programGroupDiscount`.
- **`programInstructionDetail`**: Lưu trữ dữ liệu chi tiết của đối tượng `programInstructionDetail`.
- **`programInstructionOverview`**: Lưu trữ dữ liệu chi tiết của đối tượng `programInstructionOverview`.
- **`programQuestion`**: Thông tin câu hỏi và chương trình
- **`programQuestionAdditionalInformation`**: Lưu trữ dữ liệu chi tiết của đối tượng `programQuestionAdditionalInformation`.
- **`programQuestionAnswer`**: Lưu trữ dữ liệu chi tiết của đối tượng `programQuestionAnswer`.
- **`programType`**: Lưu trữ dữ liệu chi tiết của đối tượng `programType`.
- **`programTypeTypeDetail`**: Lưu trữ dữ liệu chi tiết của đối tượng `programTypeTypeDetail`.
- **`programTypeTypeOverview`**: Lưu trữ dữ liệu chi tiết của đối tượng `programTypeTypeOverview`.
- **`question`**: Thông tin câu hỏi
- **`questionAdditionalInformation`**: Thông tin thêm của câu trả lời
- **`region`**: Lưu trữ dữ liệu chi tiết của đối tượng `region`.
- **`rejectReason`**: Lưu trữ dữ liệu chi tiết của đối tượng `rejectReason`.
- **`revenue`**: Lưu trữ dữ liệu chi tiết của đối tượng `revenue`.
- **`revenueTmp1`**: Lưu trữ dữ liệu chi tiết của đối tượng `revenueTmp1`.
- **`revenueTmp2`**: Lưu trữ dữ liệu chi tiết của đối tượng `revenueTmp2`.
- **`revenue_1`**: Lưu trữ dữ liệu chi tiết của đối tượng `revenue_1`.
- **`reward`**: Lưu trữ dữ liệu chi tiết của đối tượng `reward`.
- **`rewardObject`**: Lưu trữ dữ liệu chi tiết của đối tượng `rewardObject`.
- **`rightToSellHealthCheckProduct`**: Lưu trữ dữ liệu chi tiết của đối tượng `rightToSellHealthCheckProduct`.
- **`rightToSellProduct`**: Lưu trữ dữ liệu chi tiết của đối tượng `rightToSellProduct`.
- **`rightToSellProductDetail`**: Lưu trữ dữ liệu chi tiết của đối tượng `rightToSellProductDetail`.
- **`saleKpi`**: Lưu trữ dữ liệu chi tiết của đối tượng `saleKpi`.
- **`scheduleClaim`**: Schedule claim
- **`sideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `sideBenefit`.
- **`smeFlexiTransactionHistory`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến smeFlexiTransactionHistory.
- **`smeProduct`**: Lưu trữ dữ liệu chi tiết của đối tượng `smeProduct`.
- **`socialInsuranceExclusionTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `socialInsuranceExclusionTerms`.
- **`socialInsuranceFeeAndMaximumAmountSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `socialInsuranceFeeAndMaximumAmountSideBenefit`.
- **`socialInsuranceFeeInsurance`**: Lưu trữ dữ liệu chi tiết của đối tượng `socialInsuranceFeeInsurance`.
- **`socialInsuranceMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `socialInsuranceMainBenefit`.
- **`socialInsuranceMaximumAmountMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `socialInsuranceMaximumAmountMainBenefit`.
- **`socialInsuranceMaximumAmountSubMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `socialInsuranceMaximumAmountSubMainBenefit`.
- **`socialInsuranceMaximumAmountSubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `socialInsuranceMaximumAmountSubSideBenefit`.
- **`socialInsurancePackage`**: Thông tin gói bảo hiểm xã hội
- **`socialInsuranceParticipationTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `socialInsuranceParticipationTerms`.
- **`socialInsuranceProduct`**: Thông tin sản phẩm sức khỏe
- **`socialInsuranceProductMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `socialInsuranceProductMainBenefit`.
- **`socialInsuranceProductSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `socialInsuranceProductSideBenefit`.
- **`socialInsuranceProductSubMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `socialInsuranceProductSubMainBenefit`.
- **`socialInsuranceProductSubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `socialInsuranceProductSubSideBenefit`.
- **`socialInsuranceProgram`**: Thông tin chương trình bảo hiểm xã hội
- **`socialInsuranceRightToSell`**: Lưu trữ dữ liệu chi tiết của đối tượng `socialInsuranceRightToSell`.
- **`socialInsuranceSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `socialInsuranceSideBenefit`.
- **`socialInsuranceSubMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `socialInsuranceSubMainBenefit`.
- **`socialInsuranceSubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `socialInsuranceSubSideBenefit`.
- **`socialInsuranceTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `socialInsuranceTerms`.
- **`specialties`**: Lưu trữ dữ liệu chi tiết của đối tượng `specialties`.
- **`subMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `subMainBenefit`.
- **`subSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `subSideBenefit`.
- **`surveyQuestion`**: Câu hỏi mẫu khảo sát
- **`surveyQuestionAnswer`**: Đáp án câu hỏi mẫu khảo sát
- **`surveyResult`**: luu Đáp án cua tung câu hỏi mẫu khảo sát
- **`surveyTemplate`**: Mẫu khảo sát
- **`symptoms`**: Lưu trữ dữ liệu chi tiết của đối tượng `symptoms`.
- **`telehealthAppointment`**: Lưu trữ dữ liệu chi tiết của đối tượng `telehealthAppointment`.
- **`telehealthProduct`**: Lưu trữ dữ liệu chi tiết của đối tượng `telehealthProduct`.
- **`telehealthProductBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `telehealthProductBenefit`.
- **`telehealthProductFee`**: Lưu trữ dữ liệu chi tiết của đối tượng `telehealthProductFee`.
- **`telehealthSubscription`**: Lưu trữ dữ liệu chi tiết của đối tượng `telehealthSubscription`.
- **`terms`**: Lưu trữ dữ liệu chi tiết của đối tượng `terms`.
- **`test_view`**: VIEW
- **`tmpClaim`**: Thông tin các hồ sơ yêu cầu bồi thường (temp)
- **`tokenClaim`**: Lưu trữ dữ liệu chi tiết của đối tượng `tokenClaim`.
- **`tpa`**: Lưu trữ dữ liệu chi tiết của đối tượng `tpa`.
- **`tpaProgram`**: Lưu trữ dữ liệu chi tiết của đối tượng `tpaProgram`.
- **`transaction`**: Lưu trữ dữ liệu chi tiết của đối tượng `transaction`.
- **`transaction_fee_sme`**: Lưu trữ dữ liệu chi tiết của đối tượng `transaction_fee_sme`.
- **`travelBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `travelBenefit`.
- **`travelExclusionTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `travelExclusionTerms`.
- **`travelFeeInsurance`**: Lưu trữ dữ liệu chi tiết của đối tượng `travelFeeInsurance`.
- **`travelPackage`**: Lưu trữ dữ liệu chi tiết của đối tượng `travelPackage`.
- **`travelParticipationTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `travelParticipationTerms`.
- **`travelProduct`**: Lưu trữ dữ liệu chi tiết của đối tượng `travelProduct`.
- **`travelProgram`**: Lưu trữ dữ liệu chi tiết của đối tượng `travelProgram`.
- **`travelProgramBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `travelProgramBenefit`.
- **`travelProgramBenefitBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `travelProgramBenefitBenefit`.
- **`travelProgramBenefitBenefitGroup`**: Lưu trữ dữ liệu chi tiết của đối tượng `travelProgramBenefitBenefitGroup`.
- **`travelProgramBenefitSubBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `travelProgramBenefitSubBenefit`.
- **`travelProgramExcluded`**: Lưu trữ dữ liệu chi tiết của đối tượng `travelProgramExcluded`.
- **`travelQuantityDiscount`**: Lưu trữ dữ liệu chi tiết của đối tượng `travelQuantityDiscount`.
- **`travelRightToSell`**: Lưu trữ dữ liệu chi tiết của đối tượng `travelRightToSell`.
- **`travelSubBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `travelSubBenefit`.
- **`travelTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `travelTerms`.
- **`travelTotalFeeDiscount`**: Lưu trữ dữ liệu chi tiết của đối tượng `travelTotalFeeDiscount`.
- **`usingVoucher`**: Lưu trữ dữ liệu chi tiết của đối tượng `usingVoucher`.
- **`vehicle`**: Lưu trữ dữ liệu chi tiết của đối tượng `vehicle`.
- **`vehicleRightToSell`**: Lưu trữ dữ liệu chi tiết của đối tượng `vehicleRightToSell`.
- **`voucherAff`**: Lưu trữ dữ liệu chi tiết của đối tượng `voucherAff`.
- **`voucherAffContent`**: Lưu trữ dữ liệu chi tiết của đối tượng `voucherAffContent`.
- **`voucherAffNotification`**: Lưu trữ dữ liệu chi tiết của đối tượng `voucherAffNotification`.
- **`voucherAffProduct`**: Lưu trữ dữ liệu chi tiết của đối tượng `voucherAffProduct`.
- **`voucherCategory`**: Lưu trữ dữ liệu chi tiết của đối tượng `voucherCategory`.
- **`voucherCategoryProvider`**: Lưu trữ dữ liệu chi tiết của đối tượng `voucherCategoryProvider`.
- **`voucherRating`**: Lưu trữ dữ liệu chi tiết của đối tượng `voucherRating`.
- **`voucherRatingDetail`**: Lưu trữ dữ liệu chi tiết của đối tượng `voucherRatingDetail`.
- **`voucherTransaction`**: Lưu trữ dữ liệu chi tiết của đối tượng `voucherTransaction`.
- **`voucherWarehouseProviderAff`**: Lưu trữ dữ liệu chi tiết của đối tượng `voucherWarehouseProviderAff`.
- **`voucherWarehouseProviderSme`**: Lưu trữ dữ liệu chi tiết của đối tượng `voucherWarehouseProviderSme`.
- **`voucherWarehouseSme`**: Lưu trữ dữ liệu chi tiết của đối tượng `voucherWarehouseSme`.
- **`webhookSmartTPAReturnResult`**: Lưu trữ dữ liệu chi tiết của đối tượng `webhookSmartTPAReturnResult`.
- **`webhookTpaLeakstackReturn`**: Lưu trữ dữ liệu chi tiết của đối tượng `webhookTpaLeakstackReturn`.

---

## 🗄️ Database: `insuranceWarehouse`
**Mục đích:** Vùng dữ liệu đệm (Staging Area), lưu trữ dữ liệu thô (raw) tạm thời được CDC hoặc ETL đẩy vào trước khi xử lý, làm sạch và chuyển vào Data Warehouse.

**Giải thích các bảng (Tables) trong Database:**

- **`stgClaim`**: Staging table cho claim từ insuranceSale.claim
- **`stgContract`**: Staging table cho contract từ insuranceSale.contract
- **`stgContractObject`**: Staging table cho contractObject từ insuranceSale.contractObject
- **`stgContractObjectHouse`**: Staging table cho House Insurance - dữ liệu CDC từ insuranceSale.contractObjectHouse
- **`stgContractObjectMedicalInsurance`**: Staging table cho contractObjectMedicalInsurance từ insuranceSale.contractObjectMedicalInsurance
- **`stgContractObjectMoto`**: Staging table cho contractObjectMoto từ insuranceSale.contractObjectMoto
- **`stgContractObjectOffline`**: Wide table tổng hợp tất cả loại bảo hiểm offline contract
- **`stgContractObjectSocialInsurance`**: Staging table cho contractObjectSocialInsurance từ insuranceSale.contractObjectSocialInsurance
- **`stgContractObjectTravel`**: Lưu trữ dữ liệu chi tiết của đối tượng `stgContractObjectTravel`.
- **`stgContractObjectVehicle`**: Staging table cho contractObjectVehicle từ insuranceSale.contractObjectVehicle

---

## 🗄️ Database: `affina_user`
**Mục đích:** Quản lý hồ sơ người dùng cuối (End-User), thông tin cá nhân, định danh, địa chỉ, lịch sử hành động và các cấu hình ưu tiên của người dùng.

**Giải thích các bảng (Tables) trong Database:**

- **`accountAgency`**: Lưu trữ dữ liệu chi tiết của đối tượng `accountAgency`.
- **`accountBackoffice`**: Lưu trữ dữ liệu chi tiết của đối tượng `accountBackoffice`.
- **`accountDeletions`**: Lưu trữ dữ liệu chi tiết của đối tượng `accountDeletions`.
- **`accountPartner`**: Thông tin các tài khoản Partner
- **`accountSale`**: Lưu trữ dữ liệu chi tiết của đối tượng `accountSale`.
- **`accountSme`**: Lưu trữ dữ liệu chi tiết của đối tượng `accountSme`.
- **`accountStatusChange`**: Lưu trữ dữ liệu chi tiết của đối tượng `accountStatusChange`.
- **`accountUser`**: Lưu trữ dữ liệu chi tiết của đối tượng `accountUser`.
- **`accountUser1`**: Lưu trữ dữ liệu chi tiết của đối tượng `accountUser1`.
- **`accountUserClone1`**: Lưu trữ dữ liệu chi tiết của đối tượng `accountUserClone1`.
- **`accountUserCloneTemp`**: Lưu trữ dữ liệu chi tiết của đối tượng `accountUserCloneTemp`.
- **`agencyLevel`**: Lưu trữ dữ liệu chi tiết của đối tượng `agencyLevel`.
- **`backofficeDecentralization`**: Lưu trữ dữ liệu chi tiết của đối tượng `backofficeDecentralization`.
- **`bankCode`**: Lưu trữ dữ liệu chi tiết của đối tượng `bankCode`.
- **`branch`**: Lưu trữ dữ liệu chi tiết của đối tượng `branch`.
- **`collaboratorContract`**: Lưu trữ dữ liệu chi tiết của đối tượng `collaboratorContract`.
- **`collaboratorRequest`**: Lưu trữ dữ liệu chi tiết của đối tượng `collaboratorRequest`.
- **`company`**: Lưu trữ dữ liệu chi tiết của đối tượng `company`.
- **`companyChannel`**: Bảng thể hiện kênh của công ty
- **`companyChannelLevel`**: Bảng thể hiện cấp bậc trong kênh của công ty level nào, tên level nào, có đang enable hay không
- **`companyChannelLevelCommission`**: Bảng lưu trữ thông tin hoa hồng cho từng cấp bậc trong kênh của công ty Uu tiên lấy cấu hình hoa hồng theo productId, nếu không có thì lấy theo programId, nếu không có thì lấy theo programTypeId, nếu không có thì lấy theo channelId
- **`companyChannelLevelCommissionAwaiting`**: Bảng lưu trữ cấu hình hoa hồng của công ty trong tương lai
- **`companyChannelStaffManager`**: Bảng thể hiện Kênh của công ty được những ai quản lý
- **`companyDecentralization`**: Lưu trữ dữ liệu chi tiết của đối tượng `companyDecentralization`.
- **`companyLevel`**: Bảng thể hiện cấp bậc của công ty
- **`companyStaffChannelAssignment`**: Bảng thể hiện người dùng thuộc kênh nào, cấp bậc nào, người quản lý là ai
- **`companyStaffChannelAssignmentAwait`**: Bảng thể hiện người dùng thuộc kênh nào, cấp bậc nào, người quản lý là ai và chờ tham gia kênh trong tương lai.
- **`config`**: Lưu trữ các cài đặt, cấu hình của hệ thống cho config.
- **`decentralization`**: Lưu trữ dữ liệu chi tiết của đối tượng `decentralization`.
- **`eContract`**: Lưu hợp đồng điện tử với bên cung cấp dịch vụ eSign
- **`eContractPartner`**: Lưu trữ dữ liệu chi tiết của đối tượng `eContractPartner`.
- **`eContractSetup`**: Lưu danh sách các hợp đồng mẫu được setup cho từng cấp bậc trong kênh
- **`eContractTemplate`**: Lưu trữ dữ liệu chi tiết của đối tượng `eContractTemplate`.
- **`employeeSme`**: Lưu trữ dữ liệu chi tiết của đối tượng `employeeSme`.
- **`employeeSme2`**: Lưu trữ dữ liệu chi tiết của đối tượng `employeeSme2`.
- **`employeeSmeClone`**: Lưu trữ dữ liệu chi tiết của đối tượng `employeeSmeClone`.
- **`employeeSmeTest`**: Lưu trữ dữ liệu chi tiết của đối tượng `employeeSmeTest`.
- **`employeeUpload`**: Lưu trữ dữ liệu chi tiết của đối tượng `employeeUpload`.
- **`employee_log`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến employee_log.
- **`feature`**: Lưu trữ dữ liệu chi tiết của đối tượng `feature`.
- **`featureGroup`**: Lưu trữ dữ liệu chi tiết của đối tượng `featureGroup`.
- **`historyAgency`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến historyAgency.
- **`historyBackoffice`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến historyBackoffice.
- **`historySale`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến historySale.
- **`historySme`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến historySme.
- **`historyUser`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến historyUser.
- **`informationRelatives`**: Lưu trữ dữ liệu chi tiết của đối tượng `informationRelatives`.
- **`lead`**: Lưu trữ dữ liệu chi tiết của đối tượng `lead`.
- **`leadAction`**: Đây là bảng dùng để lưu hành động của trạng thái lead
- **`leadHistory`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến leadHistory.
- **`leadIntroduceLinkSetUp`**: Lưu trữ dữ liệu chi tiết của đối tượng `leadIntroduceLinkSetUp`.
- **`leadStatus`**: Đây là bảng dùng để lưu trạng thái của lead
- **`otpHistory`**: Thông tin lịch sử mã otp
- **`paymentMethod`**: Lưu trữ dữ liệu chi tiết của đối tượng `paymentMethod`.
- **`paymentMethodDetail`**: Lưu trữ dữ liệu chi tiết của đối tượng `paymentMethodDetail`.
- **`paymentPlatform`**: Lưu trữ dữ liệu chi tiết của đối tượng `paymentPlatform`.
- **`privilege`**: Lưu trữ dữ liệu chi tiết của đối tượng `privilege`.
- **`productCode`**: Lưu code sản phẩm của Nhà bảo hiểm cấp cho Sale
- **`profileRequestUpdate`**: Lưu trữ dữ liệu chi tiết của đối tượng `profileRequestUpdate`.
- **`programTypeSetUp`**: Bảng setup loại hình phục vụ cho tạo mới Lead
- **`programTypeSetUpPrinciple`**: tbl thiết lập các chính sách cho 1 loại hình. Trong đó id prefix: - mtn_ = mô tả ngắn - ttc_ = thông tin chung
- **`requestUpdateInfoSme`**: Lưu trữ dữ liệu chi tiết của đối tượng `requestUpdateInfoSme`.
- **`role`**: Lưu trữ dữ liệu chi tiết của đối tượng `role`.
- **`salePosition`**: Lưu trữ dữ liệu chi tiết của đối tượng `salePosition`.
- **`sourceLead`**: Lưu trữ dữ liệu chi tiết của đối tượng `sourceLead`.
- **`taxRequest`**: Lưu trữ dữ liệu chi tiết của đối tượng `taxRequest`.
- **`templateEContract`**: Lưu trữ dữ liệu chi tiết của đối tượng `templateEContract`.
- **`tokenForgotPassword`**: Lưu trữ dữ liệu chi tiết của đối tượng `tokenForgotPassword`.
- **`tokenRegister`**: Lưu trữ dữ liệu chi tiết của đối tượng `tokenRegister`.
- **`updateSaleHistory`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến updateSaleHistory.
- **`userDecentralization`**: Lưu trữ dữ liệu chi tiết của đối tượng `userDecentralization`.

---

## 🗄️ Database: `affina_zalo_context`
**Mục đích:** Quản lý trạng thái, ngữ cảnh (context), webhook, và các cấu hình liên quan đến việc tích hợp sâu với nền tảng Zalo (Zalo Mini App, ZOA).

**Giải thích các bảng (Tables) trong Database:**

- **`zalo_messages`**: Zalo messages with AI responses

---

## 🗄️ Database: `core_auth`
**Mục đích:** Dịch vụ Core lõi về quản lý thông tin xác thực, phân quyền cấp thấp, token bảo mật, và phiên đăng nhập của toàn hệ thống.

**Giải thích các bảng (Tables) trong Database:**

- **`auth_event`**: Lưu trữ dữ liệu chi tiết của đối tượng `auth_event`.
- **`DATABASECHANGELOG`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến DATABASECHANGELOG.
- **`DATABASECHANGELOGLOCK`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến DATABASECHANGELOGLOCK.
- **`feature`**: Lưu trữ dữ liệu chi tiết của đối tượng `feature`.
- **`feature_group`**: Lưu trữ dữ liệu chi tiết của đối tượng `feature_group`.
- **`permission`**: Lưu trữ dữ liệu chi tiết của đối tượng `permission`.
- **`privilege`**: Lưu trữ dữ liệu chi tiết của đối tượng `privilege`.
- **`role`**: Lưu trữ dữ liệu chi tiết của đối tượng `role`.
- **`role_privilege`**: Lưu trữ dữ liệu chi tiết của đối tượng `role_privilege`.
- **`user`**: Lưu trữ dữ liệu chi tiết của đối tượng `user`.
- **`user_privilege`**: Lưu trữ dữ liệu chi tiết của đối tượng `user_privilege`.
- **`user_role`**: Lưu trữ dữ liệu chi tiết của đối tượng `user_role`.

---

## 🗄️ Database: `core_claim`
**Mục đích:** Dịch vụ Core lõi quản lý quy trình giải quyết quyền lợi bảo hiểm (bồi thường/claim), hồ sơ bệnh án, trạng thái chi trả và lịch sử bồi thường.

**Giải thích các bảng (Tables) trong Database:**

- **`DATABASECHANGELOG`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến DATABASECHANGELOG.
- **`DATABASECHANGELOGLOCK`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến DATABASECHANGELOGLOCK.

---

## 🗄️ Database: `core_loyalty`
**Mục đích:** Dịch vụ Core lõi quản lý chương trình khách hàng thân thiết, điểm thưởng (point), hạng thành viên, mã giảm giá (voucher) và quà tặng.

**Giải thích các bảng (Tables) trong Database:**

- **`DATABASECHANGELOG`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến DATABASECHANGELOG.
- **`DATABASECHANGELOGLOCK`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến DATABASECHANGELOGLOCK.

---

## 🗄️ Database: `core_meta`
**Mục đích:** Dịch vụ Core lõi lưu trữ siêu dữ liệu (metadata), danh mục hệ thống (Master Data) như tỉnh/thành phố, nghề nghiệp, trạng thái động.

**Giải thích các bảng (Tables) trong Database:**

- **`app_field`**: Lưu trữ dữ liệu chi tiết của đối tượng `app_field`.
- **`app_field_car`**: Lưu trữ dữ liệu chi tiết của đối tượng `app_field_car`.
- **`app_field_interface`**: Đây là bảng để lưu các trường thông tin để validate sản phẩm
- **`banner`**: Lưu trữ dữ liệu chi tiết của đối tượng `banner`.
- **`canonical_model`**: Lưu trữ dữ liệu chi tiết của đối tượng `canonical_model`.
- **`canonical_vehicle_model_alias`**: Lưu trữ dữ liệu chi tiết của đối tượng `canonical_vehicle_model_alias`.
- **`career`**: Lưu trữ dữ liệu chi tiết của đối tượng `career`.
- **`claim_form`**: Lưu trữ dữ liệu chi tiết của đối tượng `claim_form`.
- **`claim_image`**: Lưu trữ dữ liệu chi tiết của đối tượng `claim_image`.
- **`corporation_view`**: VIEW
- **`DATABASECHANGELOG`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến DATABASECHANGELOG.
- **`DATABASECHANGELOGLOCK`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến DATABASECHANGELOGLOCK.
- **`disease`**: Lưu trữ dữ liệu chi tiết của đối tượng `disease`.
- **`district`**: Lưu trữ dữ liệu chi tiết của đối tượng `district`.
- **`insurance_program_group`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurance_program_group`.
- **`insurance_type_view`**: VIEW
- **`insurer_district`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurer_district`.
- **`insurer_province`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurer_province`.
- **`insurer_vehicle_brand`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurer_vehicle_brand`.
- **`insurer_vehicle_model`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurer_vehicle_model`.
- **`insurer_vehicle_purpose`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurer_vehicle_purpose`.
- **`insurer_vehicle_type`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurer_vehicle_type`.
- **`insurer_vehicle_version`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurer_vehicle_version`.
- **`logo`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến logo.
- **`metadata_variable`**: Lưu trữ dữ liệu chi tiết của đối tượng `metadata_variable`.
- **`province`**: Lưu trữ dữ liệu chi tiết của đối tượng `province`.
- **`vehicle_brand`**: Lưu trữ dữ liệu chi tiết của đối tượng `vehicle_brand`.
- **`vehicle_model`**: Lưu trữ dữ liệu chi tiết của đối tượng `vehicle_model`.
- **`vehicle_model_alias`**: Lưu trữ dữ liệu chi tiết của đối tượng `vehicle_model_alias`.
- **`vehicle_purpose`**: Lưu trữ dữ liệu chi tiết của đối tượng `vehicle_purpose`.
- **`vehicle_type`**: Lưu trữ dữ liệu chi tiết của đối tượng `vehicle_type`.
- **`vehicle_version`**: Lưu trữ dữ liệu chi tiết của đối tượng `vehicle_version`.
- **`ward`**: Lưu trữ dữ liệu chi tiết của đối tượng `ward`.

---

## 🗄️ Database: `core_policy`
**Mục đích:** Dịch vụ Core lõi quản lý các quy tắc nghiệp vụ bảo hiểm, chính sách điều khoản, và logic tính phí bảo hiểm.

**Giải thích các bảng (Tables) trong Database:**

- **`agency_app_payment_setting`**: Lưu trữ các cài đặt, cấu hình của hệ thống cho agency_app_payment_setting.
- **`appraisal_image`**: Lưu trữ dữ liệu chi tiết của đối tượng `appraisal_image`.
- **`appraisal_image_policy`**: Lưu trữ dữ liệu chi tiết của đối tượng `appraisal_image_policy`.
- **`assets`**: Lưu trữ dữ liệu chi tiết của đối tượng `assets`.
- **`bank_view`**: VIEW
- **`beneficiary`**: Lưu trữ dữ liệu chi tiết của đối tượng `beneficiary`.
- **`benefit_detail_copy`**: Lưu trữ dữ liệu chi tiết của đối tượng `benefit_detail_copy`.
- **`benefit_detail_copy_view`**: VIEW
- **`claim`**: Lưu trữ dữ liệu chi tiết của đối tượng `claim`.
- **`commission_modify_history`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến commission_modify_history.
- **`contact`**: Lưu trữ dữ liệu chi tiết của đối tượng `contact`.
- **`corporate_customer_copy`**: Lưu trữ dữ liệu chi tiết của đối tượng `corporate_customer_copy`.
- **`corporate_customer_copy_view`**: VIEW
- **`corporate_policy`**: Lưu trữ dữ liệu chi tiết của đối tượng `corporate_policy`.
- **`corporation_copy`**: Lưu trữ dữ liệu chi tiết của đối tượng `corporation_copy`.
- **`corporation_view`**: VIEW
- **`DATABASECHANGELOG`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến DATABASECHANGELOG.
- **`DATABASECHANGELOGLOCK`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến DATABASECHANGELOGLOCK.
- **`district`**: Lưu trữ dữ liệu chi tiết của đối tượng `district`.
- **`district_view`**: VIEW
- **`formula_apply_history`**: Lịch sử thao tác áp dụng hoặc xóa công thức phí hỗ trợ
- **`formula_modify_history`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến formula_modify_history.
- **`homes_copy`**: Lưu trữ dữ liệu chi tiết của đối tượng `homes_copy`.
- **`insurance_card_view`**: VIEW
- **`insurance_package_copy`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurance_package_copy`.
- **`insurance_package_copy_view`**: VIEW
- **`insurance_program_copy`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurance_program_copy`.
- **`insurance_program_copy_view`**: VIEW
- **`insurance_program_sale_view`**: VIEW
- **`insured_business_copy`**: Lưu trữ dữ liệu chi tiết của đối tượng `insured_business_copy`.
- **`insured_person`**: Lưu trữ dữ liệu chi tiết của đối tượng `insured_person`.
- **`insured_vehicle`**: Lưu trữ dữ liệu chi tiết của đối tượng `insured_vehicle`.
- **`insurer_district_view`**: VIEW
- **`insurer_province_view`**: VIEW
- **`insurer_vehicle_brand_view`**: VIEW
- **`insurer_vehicle_model_view`**: VIEW
- **`insurer_vehicle_purpose_view`**: VIEW
- **`insurer_vehicle_type_view`**: VIEW
- **`payment_setting_agency_app`**: Lưu trữ các cài đặt, cấu hình của hệ thống cho payment_setting_agency_app.
- **`payment_setting_user_app`**: Lưu trữ các cài đặt, cấu hình của hệ thống cho payment_setting_user_app.
- **`personal_customer_copy`**: Lưu trữ dữ liệu chi tiết của đối tượng `personal_customer_copy`.
- **`personal_customer_copy_view`**: VIEW
- **`policy`**: Lưu trữ dữ liệu chi tiết của đối tượng `policy`.
- **`policy_card_detail`**: Lưu trữ dữ liệu chi tiết của đối tượng `policy_card_detail`.
- **`province`**: Lưu trữ dữ liệu chi tiết của đối tượng `province`.
- **`province_view`**: VIEW
- **`quotation`**: Lưu trữ dữ liệu chi tiết của đối tượng `quotation`.
- **`quotation_detail`**: Lưu trữ dữ liệu chi tiết của đối tượng `quotation_detail`.
- **`support_fee_configuration`**: Lưu trữ các cài đặt, cấu hình của hệ thống cho support_fee_configuration.
- **`support_fee_global_config`**: Lưu trữ các cài đặt, cấu hình của hệ thống cho support_fee_global_config.
- **`support_fee_payout`**: Lưu trữ dữ liệu chi tiết của đối tượng `support_fee_payout`.
- **`support_fee_setup`**: Lưu trữ dữ liệu chi tiết của đối tượng `support_fee_setup`.
- **`temp_withdraw_transaction`**: Lưu trữ dữ liệu chi tiết của đối tượng `temp_withdraw_transaction`.
- **`transaction`**: Lưu trữ dữ liệu chi tiết của đối tượng `transaction`.
- **`user_app_payment_setting`**: Lưu trữ các cài đặt, cấu hình của hệ thống cho user_app_payment_setting.
- **`vehicle_copy`**: Lưu trữ dữ liệu chi tiết của đối tượng `vehicle_copy`.
- **`vehicle_copy_view`**: VIEW
- **`vehicle_model_view`**: VIEW
- **`vehicle_purpose_view`**: VIEW
- **`ward`**: Lưu trữ dữ liệu chi tiết của đối tượng `ward`.
- **`ward_view`**: VIEW
- **`withdraw_transaction`**: Lưu trữ dữ liệu chi tiết của đối tượng `withdraw_transaction`.
- **`withdraw_transaction_policy`**: Lưu trữ dữ liệu chi tiết của đối tượng `withdraw_transaction_policy`.

---

## 🗄️ Database: `core_post`
**Mục đích:** Dịch vụ Core lõi quản lý nội dung dạng bài viết (CMS), tin tức, bài blog, câu hỏi thường gặp (FAQ) được hiển thị trên hệ thống.

**Giải thích các bảng (Tables) trong Database:**

- **`agency_category`**: Lưu trữ dữ liệu chi tiết của đối tượng `agency_category`.
- **`category`**: Lưu trữ dữ liệu chi tiết của đối tượng `category`.
- **`comment`**: Lưu trữ dữ liệu chi tiết của đối tượng `comment`.
- **`DATABASECHANGELOG`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến DATABASECHANGELOG.
- **`DATABASECHANGELOGLOCK`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến DATABASECHANGELOGLOCK.
- **`post`**: Lưu trữ dữ liệu chi tiết của đối tượng `post`.
- **`reaction`**: Lưu trữ dữ liệu chi tiết của đối tượng `reaction`.
- **`user_view`**: VIEW

---

## 🗄️ Database: `core_product`
**Mục đích:** Dịch vụ Core lõi quản lý danh mục sản phẩm bảo hiểm, cấu trúc gói bảo hiểm, quyền lợi chi tiết và nhà cung cấp.

**Giải thích các bảng (Tables) trong Database:**

- **`answer`**: Lưu trữ dữ liệu chi tiết của đối tượng `answer`.
- **`answer_additional_information`**: Lưu trữ dữ liệu chi tiết của đối tượng `answer_additional_information`.
- **`benefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `benefit`.
- **`benefit_detail`**: Lưu trữ dữ liệu chi tiết của đối tượng `benefit_detail`.
- **`benefit_detail_history`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến benefit_detail_history.
- **`benefit_detail_temp`**: Lưu trữ dữ liệu chi tiết của đối tượng `benefit_detail_temp`.
- **`benefit_history`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến benefit_history.
- **`benefit_icon`**: Lưu trữ dữ liệu chi tiết của đối tượng `benefit_icon`.
- **`corporate_insurance_package`**: Lưu trữ dữ liệu chi tiết của đối tượng `corporate_insurance_package`.
- **`corporation_view`**: VIEW
- **`DATABASECHANGELOG`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến DATABASECHANGELOG.
- **`DATABASECHANGELOGLOCK`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến DATABASECHANGELOGLOCK.
- **`disease_detail`**: Lưu trữ dữ liệu chi tiết của đối tượng `disease_detail`.
- **`disease_detail_temp`**: Lưu trữ dữ liệu chi tiết của đối tượng `disease_detail_temp`.
- **`disease_view`**: VIEW
- **`district`**: Lưu trữ dữ liệu chi tiết của đối tượng `district`.
- **`featured_product`**: Lưu trữ dữ liệu chi tiết của đối tượng `featured_product`.
- **`hospital`**: Lưu trữ dữ liệu chi tiết của đối tượng `hospital`.
- **`hospital_accepted_insurance_program`**: Lưu trữ dữ liệu chi tiết của đối tượng `hospital_accepted_insurance_program`.
- **`hospital_blacklisted_insurer`**: Lưu trữ dữ liệu chi tiết của đối tượng `hospital_blacklisted_insurer`.
- **`insurance_card`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurance_card`.
- **`insurance_card_detail`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurance_card_detail`.
- **`insurance_category`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurance_category`.
- **`insurance_package`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurance_package`.
- **`insurance_package_fee_temp`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurance_package_fee_temp`.
- **`insurance_package_history`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến insurance_package_history.
- **`insurance_package_sale`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurance_package_sale`.
- **`insurance_package_temp`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurance_package_temp`.
- **`insurance_program`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurance_program`.
- **`insurance_program_group_icon`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurance_program_group_icon`.
- **`insurance_program_group_sale`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurance_program_group_sale`.
- **`insurance_program_group_sale_tab`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurance_program_group_sale_tab`.
- **`insurance_program_group_tab`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurance_program_group_tab`.
- **`insurance_program_group_view`**: VIEW
- **`insurance_program_history`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến insurance_program_history.
- **`insurance_program_question`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurance_program_question`.
- **`insurance_program_sale`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurance_program_sale`.
- **`insurance_program_sale_attach`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurance_program_sale_attach`.
- **`insurance_program_sale_benefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurance_program_sale_benefit`.
- **`insurance_program_sale_program`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurance_program_sale_program`.
- **`insurance_type`**: Lưu trữ dữ liệu chi tiết của đối tượng `insurance_type`.
- **`insurer_vehicle_brand_view`**: VIEW
- **`insurer_vehicle_model_view`**: VIEW
- **`insurer_vehicle_type_view`**: VIEW
- **`province`**: Lưu trữ dữ liệu chi tiết của đối tượng `province`.
- **`province_view`**: VIEW
- **`question`**: Lưu trữ dữ liệu chi tiết của đối tượng `question`.
- **`rule_template`**: Lưu trữ dữ liệu chi tiết của đối tượng `rule_template`.
- **`rule_variable`**: Lưu trữ dữ liệu chi tiết của đối tượng `rule_variable`.
- **`user_default_insurance_card`**: Lưu trữ dữ liệu chi tiết của đối tượng `user_default_insurance_card`.
- **`vehicle_purpose_view`**: VIEW
- **`vehicle_type_view`**: VIEW
- **`ward`**: Lưu trữ dữ liệu chi tiết của đối tượng `ward`.
- **`ward_view`**: VIEW

---

## 🗄️ Database: `core_push`
**Mục đích:** Dịch vụ Core lõi xử lý hệ thống queue và worker để đẩy Push Notification tốc độ cao tới các thiết bị di động/web.

**Giải thích các bảng (Tables) trong Database:**

- **`DATABASECHANGELOG`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến DATABASECHANGELOG.
- **`DATABASECHANGELOGLOCK`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến DATABASECHANGELOGLOCK.
- **`notification`**: Lưu trữ dữ liệu chi tiết của đối tượng `notification`.
- **`notification_history`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến notification_history.
- **`template`**: Thông tin template cho các hành đồng gửi message
- **`topic`**: Lưu trữ dữ liệu chi tiết của đối tượng `topic`.

---

## 🗄️ Database: `core_stakeholder`
**Mục đích:** Dịch vụ Core lõi quản lý hồ sơ các bên liên quan bao gồm nhà bảo hiểm, bệnh viện/phòng khám (TPA), đối tác doanh nghiệp.

**Giải thích các bảng (Tables) trong Database:**

- **`agent`**: Lưu trữ dữ liệu chi tiết của đối tượng `agent`.
- **`backofficer`**: Lưu trữ dữ liệu chi tiết của đối tượng `backofficer`.
- **`bank`**: Lưu trữ dữ liệu chi tiết của đối tượng `bank`.
- **`branch`**: Lưu trữ dữ liệu chi tiết của đối tượng `branch`.
- **`commission_extra_mapping`**: Lưu trữ dữ liệu chi tiết của đối tượng `commission_extra_mapping`.
- **`contact_info`**: Thông tin liên hệ khách hàng báo giá
- **`corporate_customer`**: Lưu trữ dữ liệu chi tiết của đối tượng `corporate_customer`.
- **`corporate_payment_method`**: Lưu trữ dữ liệu chi tiết của đối tượng `corporate_payment_method`.
- **`corporation`**: Lưu trữ dữ liệu chi tiết của đối tượng `corporation`.
- **`corporation_channel`**: Bảng lưu thông tin các kênh phân phối/kinh doanh của công ty
- **`corporation_channel_level`**: Bảng quản lý các cấp bậc trong từng kênh của công ty, bao gồm trạng thái và vai trò tuyển dụng
- **`corporation_channel_level_commission`**: Bảng cấu hình hoa hồng áp dụng theo cấp bậc trong từng kênh công ty
- **`corporation_channel_level_commission_schedule_history`**: Bảng cấu hình hoa hồng áp dụng theo cấp bậc trong từng kênh công ty
- **`corporation_channel_staff_manager`**: Bảng lưu thông tin người quản lý của từng kênh công ty
- **`corporation_code_seq`**: Lưu trữ dữ liệu chi tiết của đối tượng `corporation_code_seq`.
- **`corporation_industry_sector`**: Lưu trữ dữ liệu chi tiết của đối tượng `corporation_industry_sector`.
- **`corporation_staff_channel_assignment`**: Bảng thể hiện người dùng được gán vào kênh cụ thể, với cấp bậc và người quản lý trực tiếp
- **`customer_selected_product`**: Thông tin sản phẩm khách hàng đã chọn báo giá.
- **`DATABASECHANGELOG`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến DATABASECHANGELOG.
- **`DATABASECHANGELOGLOCK`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến DATABASECHANGELOGLOCK.
- **`department`**: Lưu trữ dữ liệu chi tiết của đối tượng `department`.
- **`district`**: Lưu trữ dữ liệu chi tiết của đối tượng `district`.
- **`employee`**: Lưu trữ dữ liệu chi tiết của đối tượng `employee`.
- **`homes`**: Lưu trữ dữ liệu chi tiết của đối tượng `homes`.
- **`industry_sector`**: Lưu trữ dữ liệu chi tiết của đối tượng `industry_sector`.
- **`insured_business`**: Lưu trữ dữ liệu chi tiết của đối tượng `insured_business`.
- **`job_title`**: Lưu trữ dữ liệu chi tiết của đối tượng `job_title`.
- **`lead`**: Lưu trữ dữ liệu chi tiết của đối tượng `lead`.
- **`lead_source`**: Lưu trữ dữ liệu chi tiết của đối tượng `lead_source`.
- **`legal_document`**: Lưu trữ dữ liệu chi tiết của đối tượng `legal_document`.
- **`personal_customer`**: Lưu trữ dữ liệu chi tiết của đối tượng `personal_customer`.
- **`personal_customer_history`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến personal_customer_history.
- **`personal_customer_segment`**: Lưu trữ dữ liệu chi tiết của đối tượng `personal_customer_segment`.
- **`province`**: Lưu trữ dữ liệu chi tiết của đối tượng `province`.
- **`segment`**: Lưu trữ dữ liệu chi tiết của đối tượng `segment`.
- **`seller`**: Lưu trữ dữ liệu chi tiết của đối tượng `seller`.
- **`seller_level`**: Lưu trữ dữ liệu chi tiết của đối tượng `seller_level`.
- **`support_fee`**: Lưu trữ dữ liệu chi tiết của đối tượng `support_fee`.
- **`user_view`**: VIEW
- **`vehicle`**: Lưu trữ dữ liệu chi tiết của đối tượng `vehicle`.
- **`vehicle_history`**: Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến vehicle_history.
- **`ward`**: Lưu trữ dữ liệu chi tiết của đối tượng `ward`.

---

## 🗄️ Database: `prod_affina_other`
**Mục đích:** Bản lưu trữ hoặc dữ liệu ánh xạ từ hệ thống Production cho module affina_other, dùng để đối soát hoặc test luồng production.

**Giải thích các bảng (Tables) trong Database:**

- **`card`**: Lưu trữ dữ liệu chi tiết của đối tượng `card`.
- **`cardOrder`**: Lưu trữ dữ liệu chi tiết của đối tượng `cardOrder`.
- **`cardOrderField`**: Lưu trữ dữ liệu chi tiết của đối tượng `cardOrderField`.
- **`provinces`**: Lưu trữ dữ liệu chi tiết của đối tượng `provinces`.

---

## 🗄️ Database: `prod_insuranceSale`
**Mục đích:** Bản lưu trữ hoặc dữ liệu ánh xạ từ hệ thống Production cho module insuranceSale, chứa dữ liệu kinh doanh thực tế.

**Giải thích các bảng (Tables) trong Database:**

- **`contract`**: Lưu trữ dữ liệu chi tiết của đối tượng `contract`.
- **`contractObject`**: Lưu trữ dữ liệu chi tiết của đối tượng `contractObject`.
- **`exclusionTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `exclusionTerms`.
- **`mainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `mainBenefit`.
- **`major`**: Lưu trữ dữ liệu chi tiết của đối tượng `major`.
- **`participationTerms`**: Lưu trữ dữ liệu chi tiết của đối tượng `participationTerms`.
- **`productMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `productMainBenefit`.
- **`productSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `productSideBenefit`.
- **`productSubMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `productSubMainBenefit`.
- **`productSubSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `productSubSideBenefit`.
- **`program`**: Lưu trữ dữ liệu chi tiết của đối tượng `program`.
- **`programType`**: Lưu trữ dữ liệu chi tiết của đối tượng `programType`.
- **`saveImageCard`**: Lưu trữ dữ liệu chi tiết của đối tượng `saveImageCard`.
- **`sideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `sideBenefit`.
- **`subMainBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `subMainBenefit`.
- **`subSideBenefit`**: Lưu trữ dữ liệu chi tiết của đối tượng `subSideBenefit`.
- **`terms`**: Lưu trữ dữ liệu chi tiết của đối tượng `terms`.

---

## 🗄️ Database: `prod_affina_user`
**Mục đích:** Bản lưu trữ hoặc dữ liệu ánh xạ từ hệ thống Production cho module affina_user, chứa dữ liệu người dùng thực tế.

**Giải thích các bảng (Tables) trong Database:**

- **`bankCode`**: Lưu trữ dữ liệu chi tiết của đối tượng `bankCode`.
- **`company`**: Lưu trữ dữ liệu chi tiết của đối tượng `company`.
- **`employeeSme`**: Lưu trữ dữ liệu chi tiết của đối tượng `employeeSme`.

---

## 🗄️ Database: `profiling_analysis`
**Mục đích:** Chứa các dữ liệu log, footprint, trackings phục vụ cho việc phân tích hành vi người dùng, đánh giá hiệu năng (profiling) và phân tích dữ liệu (Data Analysis).

**Giải thích các bảng (Tables) trong Database:**

- **`pregnancy_view`**: VIEW
- **`raw_data`**: Lưu trữ dữ liệu chi tiết của đối tượng `raw_data`.
- **`test_view`**: VIEW

---

