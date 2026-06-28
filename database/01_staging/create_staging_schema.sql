-- ============================================================================
-- FILE: 01_create_staging_schema.sql
-- PURPOSE: Tạo các bảng staging (Staging Database) trên PostgreSQL
-- DESCRIPTION:
--   Chuyển đổi cú pháp MySQL sang chuẩn PostgreSQL cho database Staging.
--   - Thêm tiền tố stgInsurance vào tên các bảng để đồng bộ với Source.
--   - Loại bỏ các cú pháp độc quyền của MySQL (backticks, ENGINE, COLLATE, v.v.).
-- USAGE: psql -h <host> -U <user> -d <database_name> -f 01_create_staging_schema.sql
-- ============================================================================

-- Khởi tạo schema nếu chưa tồn tại
CREATE SCHEMA IF NOT EXISTS "staging";

-- Thiết lập search_path về schema staging
SET search_path TO "staging", public;

-- ============================================================================
-- Table: stgInsuranceContract
-- Origin: stgContract
-- ============================================================================
CREATE TABLE IF NOT EXISTS "stgInsuranceContract" (
  "contractId" VARCHAR(255) NOT NULL,
  "contractIdDisplay" VARCHAR(256) DEFAULT NULL,
  "thirdPartyRequestId" VARCHAR(256) DEFAULT NULL,
  "reqCode" VARCHAR(256) DEFAULT NULL,
  "contractIdProvider" VARCHAR(256) DEFAULT NULL,
  "contractUrl" VARCHAR(256) DEFAULT NULL,
  "contractStatus" INTEGER DEFAULT NULL,
  "customerType" INTEGER NOT NULL,
  "upload" VARCHAR(256) DEFAULT NULL,
  "note" VARCHAR(256) DEFAULT NULL,
  "buyHelp" INTEGER DEFAULT NULL,
  "partnerStatus" INTEGER DEFAULT NULL,
  "integrationPartnerStatus" INTEGER DEFAULT NULL,
  "userId" VARCHAR(256) DEFAULT NULL, 
  "buyerId" VARCHAR(50) DEFAULT NULL,
  "name" VARCHAR(256) NOT NULL,
  "dob" DATE DEFAULT NULL,
  "gender" INTEGER DEFAULT NULL,
  "license" VARCHAR(20) DEFAULT NULL,
  "licenseFront" VARCHAR(256) DEFAULT NULL,
  "document" TEXT DEFAULT NULL,
  "licenseBack" VARCHAR(256) DEFAULT NULL,
  "licenseQr" VARCHAR(256) DEFAULT NULL,
  "licenseType" INTEGER DEFAULT NULL,
  "phone" VARCHAR(15) DEFAULT NULL,
  "email" VARCHAR(256) DEFAULT NULL,
  "address" VARCHAR(256) DEFAULT NULL,
  "cityCode" INTEGER DEFAULT NULL,
  "districtsCode" INTEGER DEFAULT NULL,
  "wardsCode" INTEGER DEFAULT NULL,
  "street" VARCHAR(256) DEFAULT NULL,
  "houseNumber" VARCHAR(256) DEFAULT NULL,
  "contractType" INTEGER NOT NULL,
  "contractIdRoot" VARCHAR(256) DEFAULT NULL,
  "companySale" VARCHAR(256) NOT NULL,
  "branchSale" VARCHAR(20) DEFAULT NULL,
  "branchSaleName" VARCHAR(256) DEFAULT NULL,
  "companySaleName" VARCHAR(256) NOT NULL,
  "contractPeriod" INTEGER DEFAULT NULL,
  "contractPeriodValue" INTEGER DEFAULT NULL,
  "contractStartDate" TIMESTAMP DEFAULT NULL,
  "contractEndDate" TIMESTAMP DEFAULT NULL,
  "contractObjectType" INTEGER NOT NULL,
  "voucherId" VARCHAR(256) DEFAULT NULL,
  "voucherCode" VARCHAR(256) DEFAULT NULL,
  "amountDiscount" NUMERIC(20,2) DEFAULT NULL,
  "amount" NUMERIC(20,2) DEFAULT NULL,
  "commission" NUMERIC(20,2) DEFAULT 0,
  "amountPay" NUMERIC(20,2) DEFAULT NULL,
  "redBill" INTEGER DEFAULT 0,
  "redBillCompanyName" VARCHAR(256) DEFAULT NULL,
  "redBillCompanyAddress" VARCHAR(256) DEFAULT NULL,
  "redBillCompanyTaxNumber" VARCHAR(256) DEFAULT NULL,
  "paymentMethod" INTEGER DEFAULT NULL,
  "paymentPeriod" VARCHAR(256) DEFAULT NULL,
  "orderNumber" VARCHAR(256) DEFAULT NULL,
  "providerOrderNumber" VARCHAR(255) DEFAULT NULL,
  "authorizationLetter" VARCHAR(256) DEFAULT NULL,
  "kinds" VARCHAR(256) DEFAULT NULL,
  "reasonCancel" TEXT DEFAULT NULL,
  "codeErrorCancel" VARCHAR(256) DEFAULT NULL,
  "messageError" VARCHAR(256) DEFAULT NULL,
  "referralCode" VARCHAR(256) DEFAULT NULL,
  "saleId" VARCHAR(256) DEFAULT NULL,
  "bonusAmount" NUMERIC(20,2) DEFAULT NULL,
  "bonusPercent" INTEGER DEFAULT NULL,
  "bonus" NUMERIC(20,2) DEFAULT NULL,
  "fromLead" VARCHAR(255) DEFAULT NULL,
  "source" INTEGER NOT NULL,
  "pushKey" VARCHAR(256) DEFAULT NULL,
  "outsideCreatedAt" TIMESTAMP DEFAULT NULL,
  "outsidePaymentAt" TIMESTAMP DEFAULT NULL,
  "outsidePaymentId" VARCHAR(256) DEFAULT NULL,
  "createdAt" TIMESTAMP DEFAULT NULL,
  "createdBy" VARCHAR(255) DEFAULT NULL,
  "modifiedAt" TIMESTAMP DEFAULT NULL,
  "modifiedBy" VARCHAR(255) DEFAULT NULL,
  "contractIdProviderReferal" VARCHAR(255) DEFAULT NULL,
  "topupRegisterDate" TIMESTAMP DEFAULT NULL,
  "relateRegisterDate" TIMESTAMP DEFAULT NULL,
  "employeeRegisterDate" TIMESTAMP DEFAULT NULL,
  "products" TEXT DEFAULT NULL,
  "levels" TEXT DEFAULT NULL,
  "isRefundCondition" INTEGER DEFAULT NULL,
  "hardCopy" INTEGER DEFAULT NULL,
  "hardCopyName" VARCHAR(256) DEFAULT NULL,
  "hardCopyPhone" VARCHAR(256) DEFAULT NULL,
  "hardCopyAddress" VARCHAR(256) DEFAULT NULL,
  "channelId" VARCHAR(255) DEFAULT NULL,
  "levelId" VARCHAR(255) DEFAULT NULL,
  "nationality" VARCHAR(256) DEFAULT NULL,
  "nationalityId" VARCHAR(256) DEFAULT NULL,
  "periodTypeFromProvider" INTEGER DEFAULT NULL,
  "insurerUrl" VARCHAR(256) DEFAULT NULL,
  "certFile" VARCHAR(256) DEFAULT NULL,
  "refundAmount" NUMERIC(20,2) DEFAULT NULL,
  "modifiedDate" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("contractId")
);


-- ============================================================================
-- Table: stgInsuranceContractObject
-- Origin: stgContractObject
-- ============================================================================
CREATE TABLE IF NOT EXISTS "stgInsuranceContractObject" (
  "contractObjectId" VARCHAR(256) NOT NULL,
  "contractObjectIdDisplay" VARCHAR(256) DEFAULT NULL,
  "cardNumber" VARCHAR(256) DEFAULT NULL,
  "certificateNumberProvider" VARCHAR(50) DEFAULT NULL,
  "accountTPA" VARCHAR(256) DEFAULT NULL,
  "userId" VARCHAR(256) DEFAULT NULL,
  "contractObjectSmeStatus" INTEGER DEFAULT NULL,
  "contractIndividualStatus" INTEGER DEFAULT NULL,
  "contractObjectStartDate" TIMESTAMP DEFAULT NULL,
  "contractObjectEndDate" TIMESTAMP DEFAULT NULL,
  "contractObjectIdProvider" VARCHAR(256) DEFAULT NULL,
  "contractObjectUrl" VARCHAR(256) DEFAULT NULL,
  "contractId" VARCHAR(256) NOT NULL,
  "programTypeName" VARCHAR(256) NOT NULL,
  "programTypeId" VARCHAR(256) NOT NULL,
  "programId" VARCHAR(256) NOT NULL,
  "programName" VARCHAR(256) NOT NULL,
  "packageId" VARCHAR(256) NOT NULL,
  "packageName" VARCHAR(256) NOT NULL,
  "packageCodeFromProvider" VARCHAR(256) DEFAULT NULL,
  "fromAge" INTEGER NOT NULL,
  "toAge" INTEGER NOT NULL,
  "feeMainBenefit" NUMERIC(20,2) NOT NULL,
  "termsId" VARCHAR(256) NOT NULL,
  "termsHighlight" TEXT DEFAULT NULL,
  "termsBenefit" TEXT DEFAULT NULL,
  "termsApplicableObject" TEXT DEFAULT NULL,
  "termsFeePaymentMethod" TEXT DEFAULT NULL,
  "termsHospital" VARCHAR(256) DEFAULT NULL,
  "majorName" VARCHAR(256) NOT NULL,
  "majorId" VARCHAR(256) NOT NULL,
  "productId" VARCHAR(256) NOT NULL,
  "codeFromProvider" VARCHAR(256) NOT NULL,
  "programCodeMiningChannel" VARCHAR(256) DEFAULT NULL,
  "feeInsurance" NUMERIC(20,2) NOT NULL,
  "maximumAmount" NUMERIC(20,2) NOT NULL,
  "companyProvider" VARCHAR(256) NOT NULL,
  "companyProviderName" VARCHAR(256) NOT NULL,
  "contractObjectType" INTEGER NOT NULL,
  "peopleRelationship" INTEGER DEFAULT NULL,
  "peopleName" VARCHAR(256) DEFAULT NULL,
  "peopleDob" DATE DEFAULT NULL,
  "peopleGender" INTEGER DEFAULT NULL,
  "peopleLicense" VARCHAR(256) DEFAULT NULL,
  "peopleLicenseType" INTEGER NOT NULL,
  "peoplePhone" VARCHAR(15) DEFAULT NULL,
  "peopleEmail" VARCHAR(256) DEFAULT NULL,
  "peopleAddress" VARCHAR(256) DEFAULT NULL,
  "peopleDistrictsCode" INTEGER DEFAULT NULL,
  "peopleWardsCode" INTEGER DEFAULT NULL,
  "peopleStreet" VARCHAR(256) DEFAULT NULL,
  "peopleHouseNumber" VARCHAR(256) DEFAULT NULL,
  "peopleCityCode" INTEGER DEFAULT NULL,
  "peopleNote" VARCHAR(512) DEFAULT NULL,
  "peopleUpload" VARCHAR(2048) DEFAULT NULL,
  "peopleLicenseFront" VARCHAR(256) DEFAULT NULL,
  "peopleLicenseBack" VARCHAR(256) DEFAULT NULL,
  "peopleLicenseQr" VARCHAR(256) DEFAULT NULL,
  "customerType" INTEGER DEFAULT NULL,
  "upload" VARCHAR(256) DEFAULT NULL,
  "note" VARCHAR(256) DEFAULT NULL,
  "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "createdBy" VARCHAR(256) NOT NULL,
  "modifiedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "modifiedBy" VARCHAR(256) NOT NULL,
  "minDate" INTEGER DEFAULT NULL,
  "contractObjectIdPrev" VARCHAR(255) DEFAULT NULL,
  "memberId" VARCHAR(255) DEFAULT NULL,
  "contractObjectCardDocument" VARCHAR(255) DEFAULT NULL,
  "contractObjectCardImage" VARCHAR(255) DEFAULT NULL,
  "paymentType" INTEGER DEFAULT NULL,
  "document" TEXT DEFAULT NULL,
  "programDocument" TEXT DEFAULT NULL,
  "feeSideBenefit" NUMERIC(20,2) DEFAULT 0,
  "preVatFeeSideBenefit" NUMERIC(20,2) DEFAULT 0,
  "vatFeeSideBenefit" NUMERIC(20,2) DEFAULT 0,
  "vatFeeMainBenefit" NUMERIC(20,2) DEFAULT 0,
  "preVatFeeMainBenefit" NUMERIC(20,2) DEFAULT 0,
  "preVatFeeInsurance" NUMERIC(20,2) DEFAULT 0,
  "vatFeeInsurance" NUMERIC(20,2) DEFAULT 0,
  "contractIdDisplay" VARCHAR(50) DEFAULT NULL,
  "thirdPartyRequestId" VARCHAR(50) DEFAULT NULL,
  "reqCode" DOUBLE PRECISION DEFAULT NULL,
  "contractIdProvider" VARCHAR(50) DEFAULT NULL,
  "contractStatus" INTEGER DEFAULT NULL,
  "buyHelp" INTEGER DEFAULT NULL,
  "buyerId" VARCHAR(50) DEFAULT NULL,
  "dob" VARCHAR(50) DEFAULT NULL,
  "gender" INTEGER DEFAULT NULL,
  "license" VARCHAR(50) DEFAULT NULL,
  "licenseType" INTEGER DEFAULT NULL,
  "cityCode" INTEGER DEFAULT NULL,
  "districtsCode" INTEGER DEFAULT NULL,
  "wardsCode" INTEGER DEFAULT NULL,
  "street" VARCHAR(50) DEFAULT NULL,
  "contractType" INTEGER DEFAULT NULL,
  "contractIdRoot" VARCHAR(50) DEFAULT NULL,
  "companySale" INTEGER DEFAULT NULL,
  "branchSale" DOUBLE PRECISION DEFAULT NULL,
  "branchSaleName" VARCHAR(50) DEFAULT NULL,
  "companySaleName" VARCHAR(50) DEFAULT NULL,
  "contractPeriod" INTEGER DEFAULT NULL,
  "contractPeriodValue" INTEGER DEFAULT NULL,
  "contractStartDate" VARCHAR(50) DEFAULT NULL,
  "contractEndDate" DOUBLE PRECISION DEFAULT NULL,
  "voucherId" VARCHAR(50) DEFAULT NULL,
  "voucherCode" VARCHAR(50) DEFAULT NULL,
  "amountDiscount" VARCHAR(50) DEFAULT NULL,
  "amount" INTEGER DEFAULT NULL,
  "commission" INTEGER DEFAULT NULL,
  "amountPay" INTEGER DEFAULT NULL,
  "redBill" INTEGER DEFAULT NULL,
  "paymentMethod" INTEGER DEFAULT NULL,
  "reasonCancel" VARCHAR(50) DEFAULT NULL,
  "codeErrorCancel" VARCHAR(50) DEFAULT NULL,
  "messageError" VARCHAR(50) DEFAULT NULL,
  "referralCode" VARCHAR(50) DEFAULT NULL,
  "saleId" VARCHAR(50) DEFAULT NULL,
  "bonusAmount" VARCHAR(50) DEFAULT NULL,
  "fromLead" VARCHAR(50) DEFAULT NULL,
  "source" INTEGER DEFAULT NULL,
  "outsideCreatedAt" DOUBLE PRECISION DEFAULT NULL,
  "outsidePaymentAt" DOUBLE PRECISION DEFAULT NULL,
  "outsidePaymentId" VARCHAR(50) DEFAULT NULL,
  "channelId" VARCHAR(50) DEFAULT NULL,
  "levelId" VARCHAR(50) DEFAULT NULL,
  "certFile" VARCHAR(128) DEFAULT NULL,
  "orderNumber" VARCHAR(50) DEFAULT NULL,
  "userId_1" VARCHAR(50) DEFAULT NULL,
  "contractId_2" VARCHAR(50) DEFAULT NULL,
  "contractObjectType_3" INTEGER DEFAULT NULL,
  "customerType_4" INTEGER DEFAULT NULL,
  "upload_5" VARCHAR(256) DEFAULT NULL,
  "createdAt_7" VARCHAR(50) DEFAULT NULL,
  "modifiedAt_9" VARCHAR(50) DEFAULT NULL,
  "modifiedDate" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("contractObjectId")
);


-- ============================================================================
-- Table: stgInsuranceClaim
-- Origin: stgClaim
-- ============================================================================
CREATE TABLE IF NOT EXISTS "stgInsuranceClaim" (
  "id" VARCHAR(256) NOT NULL,
  "contractId" VARCHAR(256) NOT NULL,
  "contractObjectId" VARCHAR(256) NOT NULL,
  "amountClaim" NUMERIC(20,2) DEFAULT NULL,
  "compensationAmount" NUMERIC(20,2) DEFAULT NULL,
  "note" TEXT DEFAULT NULL,
  "bankId" VARCHAR(10) DEFAULT NULL,
  "bankCode" VARCHAR(45) DEFAULT NULL,
  "bankName" VARCHAR(256) DEFAULT NULL,
  "bankBranch" VARCHAR(256) DEFAULT NULL,
  "accountNumberBank" VARCHAR(50) DEFAULT NULL,
  "accountName" VARCHAR(256) DEFAULT NULL,
  "relationship" INTEGER DEFAULT NULL,
  "claimType" INTEGER NOT NULL,
  "hospitalizedDate" DATE DEFAULT NULL,
  "hospitalDischargeDate" DATE DEFAULT NULL,
  "placeOfTreatment" VARCHAR(256) DEFAULT NULL,
  "diagnostic" TEXT DEFAULT NULL,
  "upload" TEXT DEFAULT NULL,
  "name" VARCHAR(256) DEFAULT NULL,
  "phone" VARCHAR(256) DEFAULT NULL,
  "email" VARCHAR(256) DEFAULT NULL,
  "status" INTEGER NOT NULL,
  "additionalDocument" TEXT DEFAULT NULL,
  "benefitCost" TEXT DEFAULT NULL,
  "groupCost" TEXT DEFAULT NULL,
  "tpaId" VARCHAR(256) DEFAULT NULL,
  "claimIdTpa" VARCHAR(256) DEFAULT NULL,
  "requireUpdateStatus" INTEGER DEFAULT NULL,
  "paperDocument" TEXT DEFAULT NULL,
  "createdAt" TIMESTAMP NOT NULL,
  "createdBy" VARCHAR(256) NOT NULL,
  "modifiedAt" TIMESTAMP NOT NULL,
  "modifiedBy" VARCHAR(256) NOT NULL,
  "connectType" VARCHAR(255) DEFAULT NULL,
  "source" VARCHAR(255) DEFAULT NULL,
  "parentId" VARCHAR(255) DEFAULT NULL,
  "admissionDate" TIMESTAMP DEFAULT NULL,
  "treatmentType" VARCHAR(255) DEFAULT NULL,
  "handlerFullname" VARCHAR(255) DEFAULT NULL,
  "handlerEmail" VARCHAR(255) DEFAULT NULL,
  "beneficiaryFullname" VARCHAR(255) DEFAULT NULL,
  "beneficiaryReceptionMethod" VARCHAR(255) DEFAULT NULL,
  "cause" VARCHAR(255) DEFAULT NULL,
  "causeDate" TIMESTAMP DEFAULT NULL,
  "placeOfTreatmentId" VARCHAR(255) DEFAULT NULL,
  "compensationDetail" TEXT DEFAULT NULL,
  "modifiedDate" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("id")
);


-- ============================================================================
-- Table: stgInsuranceContractObjectVehicle
-- Origin: stgContractObjectVehicle
-- ============================================================================
CREATE TABLE IF NOT EXISTS "stgInsuranceContractObjectVehicle" (
  "contractObjectId" VARCHAR(256) NOT NULL,
  "contractObjectIdDisplay" VARCHAR(256) DEFAULT NULL,
  "cardNumber" VARCHAR(256) DEFAULT NULL,
  "certificateNumberProvider" VARCHAR(50) DEFAULT NULL,
  "accountTPA" VARCHAR(256) DEFAULT NULL,
  "userId" VARCHAR(256) DEFAULT NULL,
  "contractObjectSmeStatus" INTEGER DEFAULT NULL,
  "contractObjectStartDate" TIMESTAMP DEFAULT NULL,
  "contractObjectEndDate" TIMESTAMP DEFAULT NULL,
  "contractObjectIdProvider" VARCHAR(256) DEFAULT NULL,
  "contractObjectUrl" VARCHAR(256) DEFAULT NULL,
  "contractId" VARCHAR(256) DEFAULT NULL,
  "programTypeName" VARCHAR(256) DEFAULT NULL,
  "programTypeId" VARCHAR(256) DEFAULT NULL,
  "programId" VARCHAR(256) DEFAULT NULL,
  "programName" VARCHAR(256) DEFAULT NULL,
  "packageId" VARCHAR(256) DEFAULT NULL,
  "packageName" VARCHAR(256) DEFAULT NULL,
  "packageCodeFromProvider" VARCHAR(256) DEFAULT NULL,
  "vehicleId" VARCHAR(256) DEFAULT NULL,
  "feeMainBenefit" NUMERIC(20,2) DEFAULT NULL,
  "termsId" VARCHAR(256) DEFAULT NULL,
  "termsHighlight" TEXT DEFAULT NULL,
  "termsBenefit" TEXT DEFAULT NULL,
  "termsApplicableObject" TEXT DEFAULT NULL,
  "termsFeePaymentMethod" TEXT DEFAULT NULL,
  "termsHospital" VARCHAR(256) DEFAULT NULL,
  "majorName" VARCHAR(256) DEFAULT NULL,
  "majorId" VARCHAR(256) DEFAULT NULL,
  "productId" VARCHAR(256) DEFAULT NULL,
  "codeFromProvider" VARCHAR(256) DEFAULT NULL,
  "programCodeMiningChannel" VARCHAR(256) DEFAULT NULL,
  "feeInsurance" NUMERIC(20,2) DEFAULT NULL,
  "maximumAmount" NUMERIC(20,2) DEFAULT NULL,
  "companyProvider" VARCHAR(256) DEFAULT NULL,
  "companyProviderName" VARCHAR(256) DEFAULT NULL,
  "contractObjectType" INTEGER DEFAULT NULL,
  "peopleRelationship" INTEGER DEFAULT NULL,
  "peopleName" VARCHAR(256) DEFAULT NULL,
  "peopleDob" DATE DEFAULT NULL,
  "peopleGender" INTEGER DEFAULT NULL,
  "peopleLicense" VARCHAR(256) DEFAULT NULL,
  "peopleLicenseType" INTEGER DEFAULT NULL,
  "peoplePhone" VARCHAR(15) DEFAULT NULL,
  "peopleEmail" VARCHAR(256) DEFAULT NULL,
  "peopleAddress" VARCHAR(256) DEFAULT NULL,
  "peopleDistrictsCode" INTEGER DEFAULT NULL,
  "peopleWardsCode" INTEGER DEFAULT NULL,
  "peopleStreet" VARCHAR(256) DEFAULT NULL,
  "peopleHouseNumber" VARCHAR(256) DEFAULT NULL,
  "peopleCityCode" INTEGER DEFAULT NULL,
  "peopleNote" VARCHAR(512) DEFAULT NULL,
  "peopleUpload" VARCHAR(2048) DEFAULT NULL,
  "peopleLicenseFront" VARCHAR(256) DEFAULT NULL,
  "peopleLicenseBack" VARCHAR(256) DEFAULT NULL,
  "customerType" INTEGER DEFAULT NULL,
  "upload" VARCHAR(256) DEFAULT NULL,
  "note" VARCHAR(256) DEFAULT NULL,
  "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "createdBy" VARCHAR(256) DEFAULT NULL,
  "modifiedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "modifiedBy" VARCHAR(256) DEFAULT NULL,
  "minDate" INTEGER DEFAULT NULL,
  "contractObjectIdPrev" VARCHAR(255) DEFAULT NULL,
  "memberId" VARCHAR(255) DEFAULT NULL,
  "contractObjectCardImage" TEXT DEFAULT NULL,
  "contractObjectCardDocument" TEXT DEFAULT NULL,
  "paymentType" INTEGER DEFAULT NULL,
  "programDocument" TEXT DEFAULT NULL,
  "modifiedDate" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("contractObjectId")
);

CREATE INDEX IF NOT EXISTS "idx_stgInsuranceContractObjectVehicle_contractId" ON "stgInsuranceContractObjectVehicle"("contractId");
CREATE INDEX IF NOT EXISTS "idx_stgInsuranceContractObjectVehicle_userId" ON "stgInsuranceContractObjectVehicle"("userId");
CREATE INDEX IF NOT EXISTS "idx_stgInsuranceContractObjectVehicle_modifiedDate" ON "stgInsuranceContractObjectVehicle"("modifiedDate");


-- ============================================================================
-- Table: stgInsuranceContractObjectTravel
-- Origin: stgContractObjectTravel
-- ============================================================================
CREATE TABLE IF NOT EXISTS "stgInsuranceContractObjectTravel" (
  "id" VARCHAR(256) NOT NULL,
  "idDisplay" VARCHAR(256) DEFAULT NULL,
  "cardNumber" VARCHAR(256) DEFAULT NULL,
  "certificateNumberProvider" VARCHAR(50) DEFAULT NULL,
  "accountTPA" VARCHAR(256) DEFAULT NULL,
  "userId" VARCHAR(256) NOT NULL,
  "startDate" TIMESTAMP DEFAULT NULL,
  "endDate" TIMESTAMP DEFAULT NULL,
  "idProvider" VARCHAR(256) DEFAULT NULL,
  "url" VARCHAR(256) DEFAULT NULL,
  "contractId" VARCHAR(256) NOT NULL,
  "programTypeName" VARCHAR(256) NOT NULL,
  "programTypeId" VARCHAR(256) NOT NULL,
  "programId" VARCHAR(256) NOT NULL,
  "programName" VARCHAR(256) NOT NULL,
  "packageId" VARCHAR(256) NOT NULL,
  "packageName" VARCHAR(256) NOT NULL,
  "feeMainBenefit" NUMERIC(20,2) NOT NULL,
  "termsId" VARCHAR(256) NOT NULL,
  "termsHighlight" TEXT DEFAULT NULL,
  "termsBenefit" TEXT DEFAULT NULL,
  "termsApplicableObject" TEXT DEFAULT NULL,
  "majorName" VARCHAR(256) NOT NULL,
  "majorId" VARCHAR(256) NOT NULL,
  "productId" VARCHAR(256) NOT NULL,
  "codeFromProvider" VARCHAR(256) DEFAULT NULL,
  "programCodeMiningChannel" VARCHAR(256) DEFAULT NULL,
  "programObject" INTEGER NOT NULL,
  "feeInsurance" NUMERIC(20,2) NOT NULL,
  "companyProvider" VARCHAR(256) NOT NULL,
  "companyProviderName" VARCHAR(256) NOT NULL,
  "name" VARCHAR(256) DEFAULT NULL,
  "dob" DATE DEFAULT NULL,
  "gender" INTEGER DEFAULT NULL,
  "license" VARCHAR(256) DEFAULT NULL,
  "licenseType" INTEGER NOT NULL,
  "licenseFront" VARCHAR(256) DEFAULT NULL,
  "licenseBack" VARCHAR(256) DEFAULT NULL,
  "phone" VARCHAR(15) DEFAULT NULL,
  "email" VARCHAR(256) DEFAULT NULL,
  "address" VARCHAR(256) DEFAULT NULL,
  "districtsCode" INTEGER DEFAULT NULL,
  "wardsCode" INTEGER DEFAULT NULL,
  "street" VARCHAR(256) DEFAULT NULL,
  "houseNumber" VARCHAR(256) DEFAULT NULL,
  "cityCode" INTEGER DEFAULT NULL,
  "note" VARCHAR(512) DEFAULT NULL,
  "upload" VARCHAR(2048) DEFAULT NULL,
  "customerType" INTEGER DEFAULT NULL,
  "nationality" VARCHAR(256) DEFAULT NULL,
  "domesticOrInternational" INTEGER NOT NULL,
  "departure" VARCHAR(256) NOT NULL,
  "destination" INTEGER DEFAULT NULL,
  "destinationDomestic" VARCHAR(256) DEFAULT NULL,
  "journey" VARCHAR(256) DEFAULT NULL,
  "startDateJourney" DATE DEFAULT NULL,
  "endDateJourney" DATE DEFAULT NULL,
  "payerUserId" VARCHAR(256) DEFAULT NULL,
  "payerName" VARCHAR(256) DEFAULT NULL,
  "payerDob" DATE DEFAULT NULL,
  "payerGender" INTEGER DEFAULT NULL,
  "payerLicense" VARCHAR(256) DEFAULT NULL,
  "payerLicenseType" INTEGER NOT NULL,
  "payerLicenseFront" VARCHAR(256) DEFAULT NULL,
  "payerLicenseBack" VARCHAR(256) DEFAULT NULL,
  "payerPhone" VARCHAR(15) DEFAULT NULL,
  "payerEmail" VARCHAR(256) DEFAULT NULL,
  "payerAddress" VARCHAR(256) DEFAULT NULL,
  "payerDistrictsCode" INTEGER DEFAULT NULL,
  "payerWardsCode" INTEGER DEFAULT NULL,
  "payerStreet" VARCHAR(256) DEFAULT NULL,
  "payerHouseNumber" VARCHAR(256) DEFAULT NULL,
  "payerCityCode" INTEGER DEFAULT NULL,
  "payerNote" VARCHAR(512) DEFAULT NULL,
  "payerUpload" VARCHAR(2048) DEFAULT NULL,
  "payerCustomerType" INTEGER DEFAULT NULL,
  "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "createdBy" VARCHAR(256) NOT NULL,
  "modifiedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "modifiedBy" VARCHAR(256) NOT NULL,
  "nationalityId" VARCHAR(256) DEFAULT NULL,
  "programObjectFromProvider" VARCHAR(256) DEFAULT NULL,
  "destinationFromProvider" VARCHAR(256) DEFAULT NULL,
  "codePackageFromProvider" VARCHAR(256) DEFAULT NULL,
  "adults" INTEGER DEFAULT NULL,
  "children" INTEGER DEFAULT NULL,
  "programDocument" TEXT DEFAULT NULL,
  "modifiedDate" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("id")
);


-- ============================================================================
-- Table: stgInsuranceContractObjectMoto
-- Origin: stgContractObjectMoto
-- ============================================================================
CREATE TABLE IF NOT EXISTS "stgInsuranceContractObjectMoto" (
  "id" VARCHAR(256) NOT NULL,
  "idDisplay" VARCHAR(256) DEFAULT NULL,
  "cardNumber" VARCHAR(256) DEFAULT NULL,
  "certificateNumberProvider" VARCHAR(50) DEFAULT NULL,
  "accountTPA" VARCHAR(256) DEFAULT NULL,
  "userId" VARCHAR(256) NOT NULL,
  "startDate" TIMESTAMP DEFAULT NULL,
  "endDate" TIMESTAMP DEFAULT NULL,
  "idProvider" VARCHAR(256) DEFAULT NULL,
  "url" VARCHAR(256) DEFAULT NULL,
  "contractId" VARCHAR(256) NOT NULL,
  "programTypeName" VARCHAR(256) NOT NULL,
  "programTypeId" VARCHAR(256) NOT NULL,
  "programId" VARCHAR(256) NOT NULL,
  "programName" VARCHAR(256) NOT NULL,
  "packageId" VARCHAR(256) NOT NULL,
  "packageName" VARCHAR(256) NOT NULL,
  "feeMainBenefit" NUMERIC(20,2) NOT NULL,
  "termsId" VARCHAR(256) NOT NULL,
  "termsHighlight" TEXT DEFAULT NULL,
  "termsBenefit" TEXT DEFAULT NULL,
  "termsApplicableObject" TEXT DEFAULT NULL,
  "majorName" VARCHAR(256) NOT NULL,
  "majorId" VARCHAR(256) NOT NULL,
  "productId" VARCHAR(256) NOT NULL,
  "codeFromProvider" VARCHAR(256) DEFAULT NULL,
  "programCodeMiningChannel" VARCHAR(256) DEFAULT NULL,
  "feeInsurance" NUMERIC(20,2) NOT NULL,
  "maximumAmount" NUMERIC(20,2) NOT NULL,
  "companyProvider" VARCHAR(256) NOT NULL,
  "companyProviderName" VARCHAR(256) NOT NULL,
  "name" VARCHAR(256) DEFAULT NULL,
  "dob" DATE DEFAULT NULL,
  "gender" INTEGER DEFAULT NULL,
  "license" VARCHAR(256) DEFAULT NULL,
  "licenseType" INTEGER DEFAULT NULL,
  "licenseFront" VARCHAR(256) DEFAULT NULL,
  "licenseBack" VARCHAR(256) DEFAULT NULL,
  "phone" VARCHAR(15) DEFAULT NULL,
  "email" VARCHAR(256) DEFAULT NULL,
  "address" VARCHAR(256) DEFAULT NULL,
  "districtsCode" INTEGER DEFAULT NULL,
  "wardsCode" INTEGER DEFAULT NULL,
  "street" VARCHAR(256) DEFAULT NULL,
  "houseNumber" VARCHAR(256) DEFAULT NULL,
  "cityCode" INTEGER DEFAULT NULL,
  "note" VARCHAR(512) DEFAULT NULL,
  "upload" VARCHAR(2048) DEFAULT NULL,
  "customerType" INTEGER DEFAULT NULL,
  "licensePlates" VARCHAR(256) DEFAULT NULL,
  "chassisNumber" VARCHAR(256) DEFAULT NULL,
  "engineNumber" VARCHAR(256) DEFAULT NULL,
  "maker" VARCHAR(256) DEFAULT NULL,
  "type" INTEGER NOT NULL,
  "line" VARCHAR(256) DEFAULT NULL,
  "seatNumber" INTEGER DEFAULT NULL,
  "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "createdBy" VARCHAR(256) NOT NULL,
  "modifiedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "modifiedBy" VARCHAR(256) NOT NULL,
  "programDocument" TEXT DEFAULT NULL,
  "feeSideBenefit" NUMERIC(20,2) DEFAULT 0,
  "preVatFeeSideBenefit" NUMERIC(20,2) DEFAULT 0,
  "vatFeeSideBenefit" NUMERIC(20,2) DEFAULT 0,
  "vatFeeMainBenefit" NUMERIC(20,2) DEFAULT 0,
  "preVatFeeMainBenefit" NUMERIC(20,2) DEFAULT 0,
  "preVatFeeInsurance" NUMERIC(20,2) DEFAULT 0,
  "vatFeeInsurance" NUMERIC(20,2) DEFAULT 0,
  "modifiedDate" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("id")
);

CREATE INDEX IF NOT EXISTS "idx_stgInsuranceContractObjectMoto_contractId" ON "stgInsuranceContractObjectMoto"("contractId");
CREATE INDEX IF NOT EXISTS "idx_stgInsuranceContractObjectMoto_userId" ON "stgInsuranceContractObjectMoto"("userId");
CREATE INDEX IF NOT EXISTS "idx_stgInsuranceContractObjectMoto_modifiedDate" ON "stgInsuranceContractObjectMoto"("modifiedDate");


-- ============================================================================
-- Table: stgInsuranceContractObjectSocialInsurance
-- Origin: stgContractObjectSocialInsurance
-- ============================================================================
CREATE TABLE IF NOT EXISTS "stgInsuranceContractObjectSocialInsurance" (
  "contractObjectId" VARCHAR(256) NOT NULL,
  "contractObjectIdDisplay" VARCHAR(256) DEFAULT NULL,
  "cardNumber" VARCHAR(256) DEFAULT NULL,
  "certificateNumberProvider" VARCHAR(50) DEFAULT NULL,
  "accountTPA" VARCHAR(256) DEFAULT NULL,
  "userId" VARCHAR(256) DEFAULT NULL,
  "contractObjectSmeStatus" INTEGER DEFAULT NULL,
  "contractIndividualStatus" INTEGER DEFAULT NULL,
  "contractObjectStartDate" TIMESTAMP DEFAULT NULL,
  "contractObjectEndDate" TIMESTAMP DEFAULT NULL,
  "contractObjectIdProvider" VARCHAR(256) DEFAULT NULL,
  "contractObjectUrl" VARCHAR(256) DEFAULT NULL,
  "contractId" VARCHAR(256) NOT NULL,
  "programTypeName" VARCHAR(256) NOT NULL,
  "programTypeId" VARCHAR(256) NOT NULL,
  "programId" VARCHAR(256) NOT NULL,
  "programName" VARCHAR(256) NOT NULL,
  "declarationType" INTEGER NOT NULL DEFAULT 0,
  "remunerationType" INTEGER NOT NULL DEFAULT 0,
  "packageId" VARCHAR(256) NOT NULL,
  "packageName" VARCHAR(256) NOT NULL,
  "packageCodeFromProvider" VARCHAR(256) DEFAULT NULL,
  "fromAge" INTEGER NOT NULL,
  "toAge" INTEGER NOT NULL,
  "feeMainBenefit" NUMERIC(20,2) NOT NULL,
  "termsId" VARCHAR(256) DEFAULT NULL,
  "termsHighlight" TEXT DEFAULT NULL,
  "termsBenefit" TEXT DEFAULT NULL,
  "termsApplicableObject" TEXT DEFAULT NULL,
  "termsFeePaymentMethod" TEXT DEFAULT NULL,
  "termsHospital" VARCHAR(256) DEFAULT NULL,
  "majorName" VARCHAR(256) NOT NULL,
  "majorId" VARCHAR(256) NOT NULL,
  "productId" VARCHAR(256) NOT NULL,
  "codeFromProvider" VARCHAR(256) DEFAULT NULL,
  "programCodeMiningChannel" VARCHAR(256) DEFAULT NULL,
  "feeInsurance" NUMERIC(20,2) NOT NULL,
  "maximumAmount" NUMERIC(20,2) NOT NULL,
  "companyProvider" VARCHAR(256) NOT NULL,
  "companyProviderName" VARCHAR(256) NOT NULL,
  "contractObjectType" INTEGER NOT NULL,
  "peopleRelationship" INTEGER DEFAULT NULL,
  "peopleName" VARCHAR(256) DEFAULT NULL,
  "peopleDob" DATE DEFAULT NULL,
  "peopleGender" INTEGER DEFAULT NULL,
  "peopleLicense" VARCHAR(256) DEFAULT NULL,
  "peopleLicenseType" INTEGER NOT NULL,
  "peoplePhone" VARCHAR(15) DEFAULT NULL,
  "peopleEmail" VARCHAR(256) DEFAULT NULL,
  "peopleAddress" VARCHAR(256) DEFAULT NULL,
  "peopleDistrictsCode" INTEGER DEFAULT NULL,
  "peopleWardsCode" INTEGER DEFAULT NULL,
  "peopleStreet" VARCHAR(256) DEFAULT NULL,
  "peopleHouseNumber" VARCHAR(256) DEFAULT NULL,
  "peopleCityCode" INTEGER DEFAULT NULL,
  "peopleNote" VARCHAR(512) DEFAULT NULL,
  "peopleUpload" VARCHAR(2048) DEFAULT NULL,
  "peopleLicenseFront" VARCHAR(256) DEFAULT NULL,
  "peopleLicenseBack" VARCHAR(256) DEFAULT NULL,
  "peopleLicenseQr" VARCHAR(256) DEFAULT NULL,
  "customerType" INTEGER DEFAULT NULL,
  "upload" VARCHAR(256) DEFAULT NULL,
  "note" VARCHAR(256) DEFAULT NULL,
  "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "createdBy" VARCHAR(256) NOT NULL,
  "modifiedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "modifiedBy" VARCHAR(256) NOT NULL,
  "oldCardStartDate" DATE DEFAULT NULL,
  "oldCardEndDate" DATE DEFAULT NULL,
  "socialId" VARCHAR(256) DEFAULT NULL,
  "monthlyIncome" NUMERIC(20,2) DEFAULT 0,
  "paymentPeriod" INTEGER DEFAULT NULL,
  "supportBudget" NUMERIC(20,2) DEFAULT 0,
  "renewal" INTEGER DEFAULT NULL,
  "socialFamilyId" VARCHAR(256) DEFAULT NULL,
  "oldBhxhCodeUnit" VARCHAR(256) DEFAULT NULL,
  "oldRegisterDate" VARCHAR(256) DEFAULT NULL,
  "percent" DOUBLE PRECISION DEFAULT NULL,
  "minDate" INTEGER DEFAULT NULL,
  "contractObjectIdPrev" VARCHAR(255) DEFAULT NULL,
  "memberId" VARCHAR(255) DEFAULT NULL,
  "contractObjectCardDocument" VARCHAR(255) DEFAULT NULL,
  "contractObjectCardImage" VARCHAR(255) DEFAULT NULL,
  "paymentType" INTEGER DEFAULT NULL,
  "document" TEXT DEFAULT NULL,
  "programDocument" TEXT DEFAULT NULL,
  "feeSideBenefit" NUMERIC(20,2) DEFAULT NULL,
  "preVatFeeSideBenefit" NUMERIC(20,2) DEFAULT 0,
  "vatFeeSideBenefit" NUMERIC(20,2) DEFAULT 0,
  "vatFeeMainBenefit" NUMERIC(20,2) DEFAULT 0,
  "preVatFeeMainBenefit" NUMERIC(20,2) DEFAULT 0,
  "preVatFeeInsurance" NUMERIC(20,2) DEFAULT 0,
  "vatFeeInsurance" NUMERIC(20,2) DEFAULT 0,
  "discountAmount" NUMERIC(10,2) DEFAULT NULL,
  "modifiedDate" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("contractObjectId")
);

CREATE INDEX IF NOT EXISTS "idx_stgInsuranceContractObjectSocialInsurance_contractId" ON "stgInsuranceContractObjectSocialInsurance"("contractId");
CREATE INDEX IF NOT EXISTS "idx_stgInsuranceContractObjectSocialInsurance_userId" ON "stgInsuranceContractObjectSocialInsurance"("userId");
CREATE INDEX IF NOT EXISTS "idx_stgInsuranceContractObjectSocialInsurance_modifiedDate" ON "stgInsuranceContractObjectSocialInsurance"("modifiedDate");
CREATE INDEX IF NOT EXISTS "idx_stgInsuranceContractObjectSocialInsurance_packageName" ON "stgInsuranceContractObjectSocialInsurance"("packageName");


-- ============================================================================
-- Table: stgInsuranceContractObjectMedicalInsurance
-- Origin: stgContractObjectMedicalInsurance
-- ============================================================================
CREATE TABLE IF NOT EXISTS "stgInsuranceContractObjectMedicalInsurance" (
  "contractObjectId" VARCHAR(256) NOT NULL,
  "contractObjectIdDisplay" VARCHAR(256) DEFAULT NULL,
  "cardNumber" VARCHAR(256) DEFAULT NULL,
  "certificateNumberProvider" VARCHAR(50) DEFAULT NULL,
  "accountTPA" VARCHAR(256) DEFAULT NULL,
  "userId" VARCHAR(256) DEFAULT NULL,
  "contractObjectSmeStatus" INTEGER DEFAULT NULL,
  "contractIndividualStatus" INTEGER DEFAULT NULL,
  "contractObjectStartDate" TIMESTAMP DEFAULT NULL,
  "contractObjectEndDate" TIMESTAMP DEFAULT NULL,
  "contractObjectIdProvider" VARCHAR(256) DEFAULT NULL,
  "contractObjectUrl" VARCHAR(256) DEFAULT NULL,
  "contractId" VARCHAR(256) NOT NULL,
  "programTypeName" VARCHAR(256) NOT NULL,
  "programTypeId" VARCHAR(256) NOT NULL,
  "programId" VARCHAR(256) NOT NULL,
  "programName" VARCHAR(256) NOT NULL,
  "packageId" VARCHAR(256) NOT NULL,
  "declarationType" INTEGER NOT NULL DEFAULT 0,
  "remunerationType" INTEGER NOT NULL DEFAULT 0,
  "packageName" VARCHAR(256) NOT NULL,
  "packageCodeFromProvider" VARCHAR(256) DEFAULT NULL,
  "fromAge" INTEGER DEFAULT NULL,
  "toAge" INTEGER DEFAULT NULL,
  "feeMainBenefit" NUMERIC(20,2) NOT NULL,
  "termsId" VARCHAR(256) DEFAULT NULL,
  "termsHighlight" TEXT DEFAULT NULL,
  "termsBenefit" TEXT DEFAULT NULL,
  "termsApplicableObject" TEXT DEFAULT NULL,
  "termsFeePaymentMethod" TEXT DEFAULT NULL,
  "termsHospital" VARCHAR(256) DEFAULT NULL,
  "majorName" VARCHAR(256) NOT NULL,
  "majorId" VARCHAR(256) NOT NULL,
  "productId" VARCHAR(256) NOT NULL,
  "codeFromProvider" VARCHAR(256) DEFAULT NULL,
  "programCodeMiningChannel" VARCHAR(256) DEFAULT NULL,
  "feeInsurance" NUMERIC(20,2) NOT NULL,
  "maximumAmount" NUMERIC(20,2) NOT NULL,
  "companyProvider" VARCHAR(256) NOT NULL,
  "companyProviderName" VARCHAR(256) NOT NULL,
  "contractObjectType" INTEGER NOT NULL,
  "peopleRelationship" INTEGER DEFAULT NULL,
  "peopleName" VARCHAR(256) DEFAULT NULL,
  "peopleDob" DATE DEFAULT NULL,
  "peopleGender" INTEGER DEFAULT NULL,
  "peopleLicense" VARCHAR(256) DEFAULT NULL,
  "peopleLicenseType" INTEGER NOT NULL,
  "peoplePhone" VARCHAR(15) DEFAULT NULL,
  "peopleEmail" VARCHAR(256) DEFAULT NULL,
  "peopleAddress" VARCHAR(256) DEFAULT NULL,
  "peopleDistrictsCode" INTEGER DEFAULT NULL,
  "peopleWardsCode" INTEGER DEFAULT NULL,
  "peopleStreet" VARCHAR(256) DEFAULT NULL,
  "peopleHouseNumber" VARCHAR(256) DEFAULT NULL,
  "peopleCityCode" INTEGER DEFAULT NULL,
  "peopleNote" VARCHAR(512) DEFAULT NULL,
  "peopleUpload" VARCHAR(2048) DEFAULT NULL,
  "peopleLicenseFront" VARCHAR(256) DEFAULT NULL,
  "peopleLicenseBack" VARCHAR(256) DEFAULT NULL,
  "peopleLicenseQr" VARCHAR(256) DEFAULT NULL,
  "customerType" INTEGER DEFAULT NULL,
  "upload" VARCHAR(256) DEFAULT NULL,
  "note" VARCHAR(256) DEFAULT NULL,
  "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "createdBy" VARCHAR(256) NOT NULL,
  "modifiedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "modifiedBy" VARCHAR(256) NOT NULL,
  "oldCardStartDate" DATE DEFAULT NULL,
  "oldCardEndDate" DATE DEFAULT NULL,
  "renewal" INTEGER DEFAULT NULL,
  "fiveYearDate" VARCHAR(255) DEFAULT NULL,
  "medicalId" VARCHAR(255) DEFAULT NULL,
  "socialFamilyId" VARCHAR(255) DEFAULT NULL,
  "minDate" INTEGER DEFAULT NULL,
  "contractObjectIdPrev" VARCHAR(255) DEFAULT NULL,
  "memberId" VARCHAR(255) DEFAULT NULL,
  "contractObjectCardDocument" VARCHAR(255) DEFAULT NULL,
  "contractObjectCardImage" VARCHAR(255) DEFAULT NULL,
  "paymentType" INTEGER DEFAULT NULL,
  "document" TEXT DEFAULT NULL,
  "programDocument" TEXT DEFAULT NULL,
  "feeSideBenefit" NUMERIC(20,2) DEFAULT 0,
  "preVatFeeSideBenefit" NUMERIC(20,2) DEFAULT 0,
  "vatFeeSideBenefit" NUMERIC(20,2) DEFAULT 0,
  "vatFeeMainBenefit" NUMERIC(20,2) DEFAULT 0,
  "preVatFeeMainBenefit" NUMERIC(20,2) DEFAULT 0,
  "preVatFeeInsurance" NUMERIC(20,2) DEFAULT 0,
  "vatFeeInsurance" NUMERIC(20,2) DEFAULT 0,
  "hospitalCode" VARCHAR(256) DEFAULT NULL,
  "hospitalName" VARCHAR(256) DEFAULT NULL,
  "hospitalCityRegisteredCode" INTEGER DEFAULT NULL,
  "hospitalCityRegisteredName" VARCHAR(256) DEFAULT NULL,
  "nation" VARCHAR(100) DEFAULT NULL,
  "ethnicity" VARCHAR(100) DEFAULT NULL,
  "socialId" VARCHAR(64) DEFAULT NULL,
  "modifiedDate" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("contractObjectId")
);

CREATE INDEX IF NOT EXISTS "idx_stgInsuranceContractObjectMedicalInsurance_contractId" ON "stgInsuranceContractObjectMedicalInsurance"("contractId");
CREATE INDEX IF NOT EXISTS "idx_stgInsuranceContractObjectMedicalInsurance_userId" ON "stgInsuranceContractObjectMedicalInsurance"("userId");
CREATE INDEX IF NOT EXISTS "idx_stgInsuranceContractObjectMedicalInsurance_modifiedDate" ON "stgInsuranceContractObjectMedicalInsurance"("modifiedDate");
CREATE INDEX IF NOT EXISTS "idx_stgInsuranceContractObjectMedicalInsurance_packageName" ON "stgInsuranceContractObjectMedicalInsurance"("packageName");


-- ============================================================================
-- Table: stgInsuranceContractObjectHouse
-- Origin: stgContractObjectHouse
-- ============================================================================
CREATE TABLE IF NOT EXISTS "stgInsuranceContractObjectHouse" (
  "id" VARCHAR(256) NOT NULL,
  "idDisplay" VARCHAR(256) DEFAULT NULL,
  "cardNumber" VARCHAR(256) DEFAULT NULL,
  "certificateNumberProvider" VARCHAR(256) DEFAULT NULL,
  "accountTPA" VARCHAR(256) DEFAULT NULL,
  "userId" VARCHAR(256) DEFAULT NULL,
  "contractId" VARCHAR(256) DEFAULT NULL,
  "idProvider" VARCHAR(256) DEFAULT NULL,
  "url" VARCHAR(256) DEFAULT NULL,
  "contractObjectStartDate" TIMESTAMP DEFAULT NULL,
  "contractObjectEndDate" TIMESTAMP DEFAULT NULL,
  "programTypeName" VARCHAR(256) DEFAULT NULL,
  "programTypeId" VARCHAR(256) DEFAULT NULL,
  "programId" VARCHAR(256) DEFAULT NULL,
  "programName" VARCHAR(256) DEFAULT NULL,
  "packageId" VARCHAR(256) DEFAULT NULL,
  "packageName" VARCHAR(256) DEFAULT NULL,
  "majorName" VARCHAR(256) DEFAULT NULL,
  "majorId" VARCHAR(256) DEFAULT NULL,
  "productId" VARCHAR(256) DEFAULT NULL,
  "codeFromProvider" VARCHAR(256) DEFAULT NULL,
  "programCodeMiningChannel" VARCHAR(256) DEFAULT NULL,
  "feeMainBenefit" NUMERIC(20,2) DEFAULT NULL,
  "feeInsurance" NUMERIC(20,2) DEFAULT NULL,
  "maximumAmount" NUMERIC(20,2) DEFAULT NULL,
  "termsId" VARCHAR(256) DEFAULT NULL,
  "termsHighlight" TEXT DEFAULT NULL,
  "termsBenefit" TEXT DEFAULT NULL,
  "termsApplicableObject" TEXT DEFAULT NULL,
  "companyProvider" VARCHAR(256) DEFAULT NULL,
  "companyProviderName" VARCHAR(256) DEFAULT NULL,
  "name" VARCHAR(256) DEFAULT NULL,
  "dob" DATE DEFAULT NULL,
  "gender" INTEGER DEFAULT NULL,
  "license" VARCHAR(256) DEFAULT NULL,
  "licenseType" INTEGER DEFAULT NULL,
  "licenseFront" VARCHAR(256) DEFAULT NULL,
  "licenseBack" VARCHAR(256) DEFAULT NULL,
  "phone" VARCHAR(256) DEFAULT NULL,
  "email" VARCHAR(256) DEFAULT NULL,
  "address" TEXT DEFAULT NULL,
  "districtsCode" INTEGER DEFAULT NULL,
  "wardsCode" INTEGER DEFAULT NULL,
  "street" VARCHAR(256) DEFAULT NULL,
  "houseNumber" VARCHAR(1024) DEFAULT NULL,
  "cityCode" INTEGER DEFAULT NULL,
  "note" TEXT DEFAULT NULL,
  "upload" TEXT DEFAULT NULL,
  "customerType" INTEGER DEFAULT NULL,
  "ownership" TEXT DEFAULT NULL,
  "levelId" VARCHAR(256) DEFAULT NULL,
  "programObject" INTEGER DEFAULT NULL,
  "houseName" VARCHAR(256) DEFAULT NULL,
  "numberFloors" INTEGER DEFAULT NULL,
  "houseAddress" TEXT DEFAULT NULL,
  "houseDistrictsCode" INTEGER DEFAULT NULL,
  "houseWardsCode" INTEGER DEFAULT NULL,
  "houseStreet" VARCHAR(256) DEFAULT NULL,
  "houseHouseNumber" VARCHAR(256) DEFAULT NULL,
  "houseCityCode" INTEGER DEFAULT NULL,
  "latitude" VARCHAR(256) DEFAULT NULL,
  "longitude" VARCHAR(256) DEFAULT NULL,
  "acreage" DOUBLE PRECISION DEFAULT NULL,
  "completionYear" INTEGER DEFAULT NULL,
  "houseValue" NUMERIC(20,2) DEFAULT NULL,
  "houseValueInsured" NUMERIC(20,2) DEFAULT NULL,
  "propertyValue" NUMERIC(20,2) DEFAULT NULL,
  "propertyValueInsured" NUMERIC(20,2) DEFAULT NULL,
  "uses" INTEGER DEFAULT NULL,
  "business" TEXT DEFAULT NULL,
  "companyType" TEXT DEFAULT NULL,
  "foundingYear" INTEGER DEFAULT NULL,
  "isStone" INTEGER DEFAULT NULL,
  "widthAlley" DOUBLE PRECISION DEFAULT NULL,
  "insuranceDeductible" NUMERIC(20,2) DEFAULT NULL,
  "certificateNumber" VARCHAR(256) DEFAULT NULL,
  "numberInApartment" VARCHAR(256) DEFAULT NULL,
  "apartmentNameOrNumber" VARCHAR(256) DEFAULT NULL,
  "numberUseHouse" DOUBLE PRECISION DEFAULT NULL,
  "rentAmount" NUMERIC(20,2) DEFAULT NULL,
  "paymentPeriod" INTEGER DEFAULT NULL,
  "paymentPeriodValue" INTEGER DEFAULT NULL,
  "paymentNumber" INTEGER DEFAULT NULL,
  "paymentRatio" DOUBLE PRECISION DEFAULT NULL,
  "paymentType" INTEGER DEFAULT NULL,
  "bankName" VARCHAR(256) DEFAULT NULL,
  "bankAddress" TEXT DEFAULT NULL,
  "bankEmail" VARCHAR(256) DEFAULT NULL,
  "bankCode" VARCHAR(256) DEFAULT NULL,
  "scope" TEXT DEFAULT NULL,
  "classificationCode" TEXT DEFAULT NULL,
  "partnerHouseId" VARCHAR(256) DEFAULT NULL,
  "partnerAccountId" VARCHAR(256) DEFAULT NULL,
  "contractIndividualStatus" INTEGER DEFAULT NULL,
  "programDocument" TEXT DEFAULT NULL,
  "createdAt" TIMESTAMP DEFAULT NULL,
  "createdBy" VARCHAR(256) DEFAULT NULL,
  "modifiedAt" TIMESTAMP DEFAULT NULL,
  "modifiedBy" VARCHAR(256) DEFAULT NULL,
  "modifiedDate" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("id")
);

CREATE INDEX IF NOT EXISTS "idx_stgInsuranceContractObjectHouse_contractId" ON "stgInsuranceContractObjectHouse"("contractId");
CREATE INDEX IF NOT EXISTS "idx_stgInsuranceContractObjectHouse_userId" ON "stgInsuranceContractObjectHouse"("userId");
CREATE INDEX IF NOT EXISTS "idx_stgInsuranceContractObjectHouse_modifiedDate" ON "stgInsuranceContractObjectHouse"("modifiedDate");
CREATE INDEX IF NOT EXISTS "idx_stgInsuranceContractObjectHouse_companyProvider" ON "stgInsuranceContractObjectHouse"("companyProvider");
CREATE INDEX IF NOT EXISTS "idx_stgInsuranceContractObjectHouse_majorId" ON "stgInsuranceContractObjectHouse"("majorId");
CREATE INDEX IF NOT EXISTS "idx_stgInsuranceContractObjectHouse_programId" ON "stgInsuranceContractObjectHouse"("programId");
CREATE INDEX IF NOT EXISTS "idx_stgInsuranceContractObjectHouse_contractIndividualStatus" ON "stgInsuranceContractObjectHouse"("contractIndividualStatus");
CREATE INDEX IF NOT EXISTS "idx_stgInsuranceContractObjectHouse_houseCityCode" ON "stgInsuranceContractObjectHouse"("houseCityCode");


-- ============================================================================
-- Table: stgInsuranceContractObjectOffline
-- Purpose: Wide table chứa dữ liệu tổng hợp của tất cả loại bảo hiểm offline
--          Được portal_backend ghi trực tiếp sau khi upload Excel.
--
-- Các loại bảo hiểm được hỗ trợ (insuranceType):
--   VEHICLE, MOTO, HEALTH, TRAVEL, MEDICAL_SOCIAL
-- ============================================================================
CREATE TABLE IF NOT EXISTS "stgInsuranceContractObjectOffline" (
  "offline_id"                      SERIAL PRIMARY KEY,

  -- ── Metadata chung ────────────────────────────────────────────────────────
  "insuranceType"                   VARCHAR(50)   NOT NULL,          -- VEHICLE | MOTO | HEALTH | TRAVEL | MEDICAL_SOCIAL
  "contractId"                      TEXT          NOT NULL,          -- Số hợp đồng / Số GCN / Mã tờ khai
  "majorName"                       TEXT          DEFAULT NULL,      -- Loại bảo hiểm (Sản phẩm)
  "programName"                     TEXT          DEFAULT NULL,      -- Chương trình / Plan
  "companyProviderName"             TEXT          DEFAULT NULL,      -- Nhà bảo hiểm
  "companyProvider"                 TEXT          DEFAULT NULL,      -- Mã nhà bảo hiểm (nếu có)
  "saleId"                          TEXT          DEFAULT NULL,      -- Code sale / Tên sale
  "programCodeMiningChannel"        TEXT          DEFAULT NULL,      -- Channel (DSA, TSA, Renew…)
  "termsFeePaymentMethod"           TEXT          DEFAULT NULL,      -- Hình thức thanh toán
  "modifiedAt"                      TIMESTAMP     DEFAULT NULL,      -- Ngày update/cập nhật từ Excel

  -- ── Phí bảo hiểm ─────────────────────────────────────────────────────────
  "feeInsurance"                    NUMERIC(20,2) DEFAULT NULL,      -- Tổng phí BH (tất cả loại)
  "feeMainBenefit"                  NUMERIC(20,2) DEFAULT NULL,      -- Phí chính (MOTO: TNDS BẮT BUỘC)
  "feeSideBenefit"                  NUMERIC(20,2) DEFAULT NULL,      -- Phí phụ  (MOTO: TAI NẠN NNTX)
  "feeAdjustment"                   NUMERIC(20,2) DEFAULT NULL,      -- Phí điều chỉnh (HEALTH)
  "amountPay"                       NUMERIC(20,2) DEFAULT NULL,      -- Số tiền thanh toán (HEALTH)
  "payment_date"                    DATE          DEFAULT NULL,      -- Ngày thanh toán (tất cả loại)

  -- ── Thông tin hợp đồng chung ─────────────────────────────────────────────
  "contractObjectStartDate"         TIMESTAMP     DEFAULT NULL,      -- Ngày bắt đầu hiệu lực (VEHICLE, MOTO, MEDICAL_SOCIAL)
  "contractObjectEndDate"           TIMESTAMP     DEFAULT NULL,      -- Ngày kết thúc hiệu lực (VEHICLE, MOTO, MEDICAL_SOCIAL)
  "contractStartDate"               DATE          DEFAULT NULL,      -- Ngày hiệu lực (HEALTH)
  "contractEndDate"                 DATE          DEFAULT NULL,      -- Ngày kết thúc (HEALTH)
  "contractPeriodValue"             INTEGER       DEFAULT NULL,      -- Số năm / ngày BH (VEHICLE, MOTO)
  "certificateNumberProvider"       TEXT          DEFAULT NULL,      -- Số GCNBH (HEALTH)
  "contractStatus"                  INTEGER       DEFAULT NULL,      -- Trạng thái hợp đồng (MEDICAL_SOCIAL)

  -- ── Người được bảo hiểm (NĐBH / people*) ────────────────────────────────
  "peopleName"                      TEXT          DEFAULT NULL,      -- Họ tên NĐBH (business key)
  "peopleDob"                       DATE          DEFAULT NULL,      -- Ngày sinh NĐBH
  "peopleGender"                    INTEGER       DEFAULT NULL,      -- Giới tính (0=Nữ, 1=Nam)
  "peopleLicense"                   TEXT          DEFAULT NULL,      -- CCCD / CMND NĐBH
  "passport"                        TEXT          DEFAULT NULL,      -- Hộ chiếu NĐBH (HEALTH)
  "peoplePhone"                     VARCHAR(15)   DEFAULT NULL,      -- SĐT NĐBH
  "peopleEmail"                     TEXT          DEFAULT NULL,      -- Email NĐBH
  "peopleAddress"                   TEXT          DEFAULT NULL,      -- Địa chỉ NĐBH
  "peopleRelationship"              INTEGER       DEFAULT NULL,      -- Mối quan hệ (0=Bản thân, 1=Bố/Mẹ…)

  -- ── Người mua bảo hiểm (Bên mua / payer*) ───────────────────────────────
  "payerName"                       TEXT          DEFAULT NULL,      -- Họ tên người mua
  "payerDob"                        DATE          DEFAULT NULL,      -- Ngày sinh người mua
  "payerGender"                     INTEGER       DEFAULT NULL,      -- Giới tính người mua
  "payerLicense"                    TEXT          DEFAULT NULL,      -- CCCD / CMND người mua
  "payerPhone"                      VARCHAR(15)   DEFAULT NULL,      -- SĐT người mua
  "payerEmail"                      TEXT          DEFAULT NULL,      -- Email người mua
  "payerAddress"                    TEXT          DEFAULT NULL,      -- Địa chỉ người mua

  -- ── HEALTH — thông tin gói quyền lợi ─────────────────────────────────────
  "outpatient_benefit"              TEXT          DEFAULT NULL,      -- Ngoại trú
  "dental_benefit"                  TEXT          DEFAULT NULL,      -- Nha khoa
  "maternity_benefit"               TEXT          DEFAULT NULL,      -- Thai sản
  "topup_benefit"                   TEXT          DEFAULT NULL,      -- Top-up
  "invoiceInfo"                     TEXT          DEFAULT NULL,      -- Thông tin xuất hoá đơn
  "leadPhone"                       VARCHAR(15)   DEFAULT NULL,      -- Phone trên lead
  "customerPhone"                   VARCHAR(15)   DEFAULT NULL,      -- Phone khách hàng
  "contactName"                     TEXT          DEFAULT NULL,      -- Tên liên hệ

  -- ── VEHICLE — thông tin xe ô tô ──────────────────────────────────────────
  "licensePlate"                    TEXT          DEFAULT NULL,      -- Biển số xe (Vehicle)
  "chassisNumber"                   TEXT          DEFAULT NULL,      -- Số khung (Vehicle + Moto)
  "engineNumber"                    TEXT          DEFAULT NULL,      -- Số máy (Vehicle + Moto)
  "vehicleType"                     TEXT          DEFAULT NULL,      -- Loại xe (Vehicle: text từ Excel 'Loại xe')
  "brand"                           TEXT          DEFAULT NULL,      -- Hiệu xe / Nhãn hiệu (Vehicle)
  "vehicleValue"                    NUMERIC(20,2) DEFAULT NULL,      -- Giá trị xe
  "usagePurpose"                    TEXT          DEFAULT NULL,      -- Mục đích sử dụng
  "manufactureYear"                 INTEGER       DEFAULT NULL,      -- Năm sản xuất
  "seatNumber"                      INTEGER       DEFAULT NULL,      -- Số chỗ ngồi (Vehicle)
  "insurance_days"                  INTEGER       DEFAULT NULL,      -- Số ngày bảo hiểm (Vehicle)

  -- ── MOTO — thông tin xe máy ──────────────────────────────────────────────
  "licensePlates"                   TEXT          DEFAULT NULL,      -- Biển số xe (Moto)
  "maker"                           TEXT          DEFAULT NULL,      -- Nhãn hiệu xe (Moto)
  "packageName"                     TEXT          DEFAULT NULL,      -- Loại xe máy (Moto)
  "issue_date"                      DATE          DEFAULT NULL,      -- Ngày cấp đơn (Moto)

  -- ── TRAVEL — thông tin chuyến đi ─────────────────────────────────────────
  "startDateJourney"                DATE          DEFAULT NULL,      -- Ngày đi
  "endDateJourney"                  DATE          DEFAULT NULL,      -- Ngày về
  "journey_days"                    INTEGER       DEFAULT NULL,      -- Số ngày hành trình
  "destination_text"                TEXT          DEFAULT NULL,      -- Nơi đến (text từ Excel)
  "domesticOrInternational_text"    TEXT          DEFAULT NULL,      -- Phạm vi (Trong nước / Quốc tế)
  "upload_date"                     DATE          DEFAULT NULL,      -- Ngày upload (cột 'Ngày' trong Travel.xlsx)

  -- ── MEDICAL_SOCIAL — bảo hiểm y tế xã hội ───────────────────────────────
  "socialId"                        TEXT          DEFAULT NULL,      -- Mã BHXH
  "renewal"                         INTEGER       DEFAULT NULL,      -- Phương án KH (Gia hạn)

  -- ── Audit timestamps ──────────────────────────────────────────────────────
  "createdAt"                       TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "createdBy"                       TEXT          DEFAULT NULL,
  "modifiedDate"                    TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS "idx_stgOffline_insuranceType"   ON "stgInsuranceContractObjectOffline"("insuranceType");
CREATE INDEX IF NOT EXISTS "idx_stgOffline_contractId"      ON "stgInsuranceContractObjectOffline"("contractId");
CREATE INDEX IF NOT EXISTS "idx_stgOffline_peopleName"      ON "stgInsuranceContractObjectOffline"("peopleName");
CREATE INDEX IF NOT EXISTS "idx_stgOffline_majorName"       ON "stgInsuranceContractObjectOffline"("majorName");
CREATE INDEX IF NOT EXISTS "idx_stgOffline_companyProvider" ON "stgInsuranceContractObjectOffline"("companyProviderName");
CREATE INDEX IF NOT EXISTS "idx_stgOffline_payment_date"    ON "stgInsuranceContractObjectOffline"("payment_date");
CREATE INDEX IF NOT EXISTS "idx_stgOffline_createdAt"       ON "stgInsuranceContractObjectOffline"("createdAt");
CREATE INDEX IF NOT EXISTS "idx_stgOffline_saleId"          ON "stgInsuranceContractObjectOffline"("saleId");
CREATE INDEX IF NOT EXISTS "idx_stgOffline_channel"         ON "stgInsuranceContractObjectOffline"("programCodeMiningChannel");

