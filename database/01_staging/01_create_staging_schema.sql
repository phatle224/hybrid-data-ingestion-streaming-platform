-- ============================================================================
-- FILE: create_staging_schema.sql
-- PURPOSE: Tạo database insuranceWarehouse và 3 tables: stgContract, stgContractObject, stgClaim
-- USAGE: mysql -h <host> -u <user> -p < create_staging_schema.sql
-- ============================================================================

-- Tạo database insuranceWarehouse
CREATE DATABASE IF NOT EXISTS `insuranceWarehouse` 
    DEFAULT CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE `insuranceWarehouse`;

-- ============================================================================
-- Table: stgContract
-- Source: insuranceSale.contract
-- Purpose: Staging table chứa dữ liệu hợp đồng từ CDC
-- ============================================================================
CREATE TABLE IF NOT EXISTS `stgContract` (
  `contractId` varchar(255) NOT NULL,
  `contractIdDisplay` varchar(256) DEFAULT '`contractId`',
  `thirdPartyRequestId` varchar(256) DEFAULT NULL,
  `reqCode` varchar(256) DEFAULT NULL,
  `contractIdProvider` varchar(256) DEFAULT NULL,
  `contractUrl` varchar(256) DEFAULT NULL,
  `contractStatus` int(11) DEFAULT NULL,
  `customerType` int(2) NOT NULL COMMENT 'Map with enum StaticEnum.CustomerType',
  `upload` varchar(256) DEFAULT NULL,
  `note` varchar(256) DEFAULT NULL,
  `buyHelp` int(11) DEFAULT NULL COMMENT 'Map with enum StaticEnum.BuyHelpEnum',
  `partnerStatus` int(11) DEFAULT NULL COMMENT 'Map with enum StaticEnum.PartnerDeclarationStatus',
  `integrationPartnerStatus` int(11) DEFAULT NULL,
  `userId` varchar(256) DEFAULT NULL COMMENT 'Không dùng đến nữa từ bảng tách field người tạo contract với người mua trong hợp đồng', 
  `buyerId` varchar(50) DEFAULT NULL COMMENT 'Mã định danh người/công ty sme mua bảo hiểm trong hệ thống affina',
  `name` varchar(256) NOT NULL,
  `dob` date DEFAULT NULL,
  `gender` int(11) DEFAULT NULL,
  `license` varchar(20) DEFAULT NULL,
  `licenseFront` varchar(256) DEFAULT NULL,
  `document` longtext DEFAULT '\'[]\'',
  `licenseBack` varchar(256) DEFAULT NULL,
  `licenseQr` varchar(256) DEFAULT NULL,
  `licenseType` int(11) DEFAULT NULL COMMENT 'Map with enum StaticEnum.LicenseType',
  `phone` varchar(15) DEFAULT NULL,
  `email` varchar(256) DEFAULT NULL,
  `address` varchar(256) DEFAULT NULL,
  `cityCode` int(11) DEFAULT NULL,
  `districtsCode` int(11) DEFAULT NULL,
  `wardsCode` int(11) DEFAULT NULL,
  `street` varchar(256) DEFAULT NULL,
  `houseNumber` varchar(256) DEFAULT NULL,
  `contractType` int(11) NOT NULL COMMENT 'Map with enum StaticEnum.ContractType',
  `contractIdRoot` varchar(256) DEFAULT NULL COMMENT 'Mã hợp đồng gốc',
  `companySale` varchar(256) NOT NULL COMMENT 'Công ty sale',
  `branchSale` varchar(20) DEFAULT NULL,
  `branchSaleName` varchar(256) DEFAULT NULL,
  `companySaleName` varchar(256) NOT NULL,
  `contractPeriod` int(11) DEFAULT NULL COMMENT 'Thời hạn bảo hiểm map with enum StaticEnum.ContractPeriod',
  `contractPeriodValue` int(11) DEFAULT NULL COMMENT 'Số năm/tháng/ngày',
  `contractStartDate` datetime DEFAULT NULL COMMENT 'Thời gian bắt đầu',
  `contractEndDate` datetime DEFAULT NULL COMMENT 'Thời gian kết thúc',
  `contractObjectType` int(11) NOT NULL COMMENT 'Đối tượng được bảo hiểm map with enum StaticEnum.contractObjectType',
  `voucherId` varchar(256) DEFAULT NULL COMMENT 'Chương trình giảm phí 2, mã giảm, chỉ có khi KH dùng app',
  `voucherCode` varchar(256) DEFAULT NULL,
  `amountDiscount` decimal(20,0) DEFAULT NULL,
  `amount` decimal(20,0) DEFAULT NULL,
  `commission` decimal(20,0) DEFAULT 0 COMMENT 'Tiền hoa hồng',
  `amountPay` decimal(20,0) DEFAULT NULL COMMENT 'Số tiên cần phải thanh toán',
  `redBill` int(11) DEFAULT 0 COMMENT 'Map with enum StaticEnum.RedBillEnum',
  `redBillCompanyName` varchar(256) DEFAULT NULL,
  `redBillCompanyAddress` varchar(256) DEFAULT NULL,
  `redBillCompanyTaxNumber` varchar(256) DEFAULT NULL,
  `paymentMethod` int(11) DEFAULT NULL COMMENT 'Map with enum StaticEnum.paymentMethod',
  `paymentPeriod` varchar(256) DEFAULT NULL,
  `orderNumber` varchar(256) DEFAULT NULL COMMENT 'Mã hóa đơn từ PVI',
  `providerOrderNumber` varchar(255) DEFAULT NULL,
  `authorizationLetter` varchar(256) DEFAULT NULL,
  `kinds` varchar(256) DEFAULT NULL,
  `reasonCancel` text DEFAULT NULL,
  `codeErrorCancel` varchar(256) DEFAULT NULL,
  `messageError` varchar(256) DEFAULT NULL,
  `referralCode` varchar(256) DEFAULT NULL,
  `saleId` varchar(256) DEFAULT NULL,
  `bonusAmount` decimal(20,0) DEFAULT NULL,
  `bonusPercent` int(11) DEFAULT NULL,
  `bonus` decimal(20,0) DEFAULT NULL,
  `fromLead` varchar(255) DEFAULT NULL,
  `source` int(11) NOT NULL COMMENT 'Hợp đồng được tạo từ đâu. Map với enum StaticEnum.SourceContractEnum',
  `pushKey` varchar(256) DEFAULT NULL COMMENT 'Khóa của firebase dùng để gửi thông báo về điện thoại',
  `outsideCreatedAt` datetime DEFAULT NULL COMMENT 'Thời gian tạo hợp đồng thực tế bên ngoài',
  `outsidePaymentAt` datetime DEFAULT NULL COMMENT 'Thời gian thanh toán hợp đồng thực tế bên ngoài',
  `outsidePaymentId` varchar(256) DEFAULT NULL COMMENT 'Mã thanh toán hợp đồng thực tế bên ngoài',
  `createdAt` datetime DEFAULT NULL,
  `createdBy` varchar(255) DEFAULT NULL,
  `modifiedAt` datetime DEFAULT NULL,
  `modifiedBy` varchar(255) DEFAULT NULL,
  `contractIdProviderReferal` varchar(255) DEFAULT NULL,
  `topupRegisterDate` datetime DEFAULT NULL,
  `relateRegisterDate` datetime DEFAULT NULL,
  `employeeRegisterDate` datetime DEFAULT NULL,
  `products` longtext DEFAULT NULL,
  `levels` text DEFAULT NULL,
  `isRefundCondition` int(11) DEFAULT NULL,
  `hardCopy` int(11) DEFAULT NULL,
  `hardCopyName` varchar(256) DEFAULT NULL,
  `hardCopyPhone` varchar(256) DEFAULT NULL,
  `hardCopyAddress` varchar(256) DEFAULT NULL,
  `channelId` varchar(255) DEFAULT NULL,
  `levelId` varchar(255) DEFAULT NULL,
  `nationality` varchar(256) DEFAULT NULL,
  `nationalityId` varchar(256) DEFAULT NULL,
  `periodTypeFromProvider` int(11) DEFAULT NULL,
  `insurerUrl` varchar(256) DEFAULT NULL COMMENT 'Link giấu chứng nhận của nhà bảo hiểm',
  `certFile` varchar(256) DEFAULT NULL COMMENT 'File giấy chứng nhận đã mã hoá',
  `refundAmount` decimal(20,0) DEFAULT NULL,
  `modifiedDate` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT 'Thời điểm CDC cập nhật record',
  PRIMARY KEY (`contractId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Staging table cho contract từ insuranceSale.contract';


-- ============================================================================
-- Table: stgContractObject
-- Source: insuranceSale.contractObject
-- Purpose: Staging table chứa dữ liệu đối tượng hợp đồng từ CDC
-- ============================================================================
CREATE TABLE IF NOT EXISTS `stgContractObject` (
  `contractObjectId` varchar(256) NOT NULL,
  `contractObjectIdDisplay` varchar(256) DEFAULT '`contractObjectId`',
  `cardNumber` varchar(256) DEFAULT NULL,
  `certificateNumberProvider` varchar(50) DEFAULT NULL COMMENT 'Số giấy chứng nhận của nhà cung cấp',
  `accountTPA` varchar(256) DEFAULT NULL COMMENT 'Tài khoản TPA',
  `userId` varchar(256) DEFAULT NULL,
  `contractObjectSmeStatus` int(11) DEFAULT NULL COMMENT 'Map with enum StaticEnum.ContractObjectSmeStatus',
  `contractIndividualStatus` int(11) DEFAULT NULL COMMENT '1: hop dong ca nhan hieu luc, 0: hop dong ca nhan het han',
  `contractObjectStartDate` datetime DEFAULT NULL COMMENT 'Thời gian bắt đầu',
  `contractObjectEndDate` datetime DEFAULT NULL COMMENT 'Thời gian kết thúc',
  `contractObjectIdProvider` varchar(256) DEFAULT NULL COMMENT 'Mã chứng nhận nhà bảo hiểm',
  `contractObjectUrl` varchar(256) DEFAULT NULL,
  `contractId` varchar(256) NOT NULL,
  `programTypeName` varchar(256) NOT NULL,
  `programTypeId` varchar(256) NOT NULL,
  `programId` varchar(256) NOT NULL,
  `programName` varchar(256) NOT NULL,
  `packageId` varchar(256) NOT NULL,
  `packageName` varchar(256) NOT NULL,
  `packageCodeFromProvider` varchar(256) DEFAULT NULL,
  `fromAge` int(11) NOT NULL,
  `toAge` int(11) NOT NULL,
  `feeMainBenefit` decimal(20,0) NOT NULL,
  `termsId` varchar(256) NOT NULL,
  `termsHighlight` text DEFAULT NULL,
  `termsBenefit` text DEFAULT NULL,
  `termsApplicableObject` text DEFAULT NULL,
  `termsFeePaymentMethod` text DEFAULT NULL,
  `termsHospital` varchar(256) DEFAULT NULL,
  `majorName` varchar(256) NOT NULL,
  `majorId` varchar(256) NOT NULL,
  `productId` varchar(256) NOT NULL,
  `codeFromProvider` varchar(256) NOT NULL,
  `programCodeMiningChannel` varchar(256) DEFAULT NULL,
  `feeInsurance` decimal(20,0) NOT NULL COMMENT 'Phí bảo hiểm',
  `maximumAmount` decimal(20,0) NOT NULL COMMENT 'Số tiền tối đa có thể nhận',
  `companyProvider` varchar(256) NOT NULL,
  `companyProviderName` varchar(256) NOT NULL,
  `contractObjectType` int(11) NOT NULL COMMENT 'Đối tượng được bảo hiểm map with enum StaticEnum.ContractObjectType',
  `peopleRelationship` int(11) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0, Mối quan hệ map with enum StaticEnum.ContractObjectPeopleRelationshipEnum',
  `peopleName` varchar(256) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleDob` date DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleGender` int(11) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleLicense` varchar(256) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleLicenseType` int(11) NOT NULL COMMENT 'Map with enum StaticEnum.LicenseType',
  `peoplePhone` varchar(15) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleEmail` varchar(256) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleAddress` varchar(256) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleDistrictsCode` int(11) DEFAULT NULL,
  `peopleWardsCode` int(11) DEFAULT NULL,
  `peopleStreet` varchar(256) DEFAULT NULL,
  `peopleHouseNumber` varchar(256) DEFAULT NULL,
  `peopleCityCode` int(11) DEFAULT NULL,
  `peopleNote` varchar(512) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleUpload` varchar(2048) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleLicenseFront` varchar(256) DEFAULT NULL,
  `peopleLicenseBack` varchar(256) DEFAULT NULL,
  `peopleLicenseQr` varchar(256) DEFAULT NULL,
  `customerType` int(11) DEFAULT NULL COMMENT 'Map with enum StaticEnum.CustomerType',
  `upload` varchar(256) DEFAULT NULL,
  `note` varchar(256) DEFAULT NULL,
  `createdAt` datetime NOT NULL DEFAULT curtime(),
  `createdBy` varchar(256) NOT NULL,
  `modifiedAt` datetime NOT NULL DEFAULT curtime(),
  `modifiedBy` varchar(256) NOT NULL,
  `minDate` int(11) DEFAULT NULL,
  `contractObjectIdPrev` varchar(255) DEFAULT NULL,
  `memberId` varchar(255) DEFAULT NULL,
  `contractObjectCardDocument` varchar(255) DEFAULT NULL,
  `contractObjectCardImage` varchar(255) DEFAULT NULL,
  `paymentType` int(11) DEFAULT NULL,
  `document` text DEFAULT NULL,
  `programDocument` longtext DEFAULT '\'[]\'',
  `feeSideBenefit` decimal(20,0) DEFAULT 0,
  `preVatFeeSideBenefit` decimal(20,0) DEFAULT 0,
  `vatFeeSideBenefit` decimal(20,0) DEFAULT 0,
  `vatFeeMainBenefit` decimal(20,0) DEFAULT 0,
  `preVatFeeMainBenefit` decimal(20,0) DEFAULT 0,
  `preVatFeeInsurance` decimal(20,0) DEFAULT 0,
  `vatFeeInsurance` decimal(20,0) DEFAULT 0,
  `contractIdDisplay` varchar(50) DEFAULT NULL,
  `thirdPartyRequestId` varchar(50) DEFAULT NULL,
  `reqCode` double DEFAULT NULL,
  `contractIdProvider` varchar(50) DEFAULT NULL,
  `contractStatus` int(11) DEFAULT NULL,
  `buyHelp` int(11) DEFAULT NULL,
  `buyerId` varchar(50) DEFAULT NULL,
  `dob` varchar(50) DEFAULT NULL,
  `gender` int(11) DEFAULT NULL,
  `license` varchar(50) DEFAULT NULL,
  `licenseType` int(11) DEFAULT NULL,
  `cityCode` int(11) DEFAULT NULL,
  `districtsCode` int(11) DEFAULT NULL,
  `wardsCode` int(11) DEFAULT NULL,
  `street` varchar(50) DEFAULT NULL,
  `contractType` int(11) DEFAULT NULL,
  `contractIdRoot` varchar(50) DEFAULT NULL,
  `companySale` int(11) DEFAULT NULL,
  `branchSale` double DEFAULT NULL,
  `branchSaleName` varchar(50) DEFAULT NULL,
  `companySaleName` varchar(50) DEFAULT NULL,
  `contractPeriod` int(11) DEFAULT NULL,
  `contractPeriodValue` int(11) DEFAULT NULL,
  `contractStartDate` varchar(50) DEFAULT NULL,
  `contractEndDate` double DEFAULT NULL,
  `voucherId` varchar(50) DEFAULT NULL,
  `voucherCode` varchar(50) DEFAULT NULL,
  `amountDiscount` varchar(50) DEFAULT NULL,
  `amount` int(11) DEFAULT NULL,
  `commission` int(11) DEFAULT NULL,
  `amountPay` int(11) DEFAULT NULL,
  `redBill` int(11) DEFAULT NULL,
  `paymentMethod` int(11) DEFAULT NULL,
  `reasonCancel` varchar(50) DEFAULT NULL,
  `codeErrorCancel` varchar(50) DEFAULT NULL,
  `messageError` varchar(50) DEFAULT NULL,
  `referralCode` varchar(50) DEFAULT NULL,
  `saleId` varchar(50) DEFAULT NULL,
  `bonusAmount` varchar(50) DEFAULT NULL,
  `fromLead` varchar(50) DEFAULT NULL,
  `source` int(11) DEFAULT NULL,
  `outsideCreatedAt` double DEFAULT NULL,
  `outsidePaymentAt` double DEFAULT NULL,
  `outsidePaymentId` varchar(50) DEFAULT NULL,
  `channelId` varchar(50) DEFAULT NULL,
  `levelId` varchar(50) DEFAULT NULL,
  `certFile` varchar(128) DEFAULT NULL,
  `orderNumber` varchar(50) DEFAULT NULL,
  `userId_1` varchar(50) DEFAULT NULL,
  `contractId_2` varchar(50) DEFAULT NULL,
  `contractObjectType_3` int(11) DEFAULT NULL,
  `customerType_4` int(11) DEFAULT NULL,
  `upload_5` varchar(256) DEFAULT NULL,
  `createdAt_7` varchar(50) DEFAULT NULL,
  `modifiedAt_9` varchar(50) DEFAULT NULL,
  `modifiedDate` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT 'Thời điểm CDC cập nhật record',
  PRIMARY KEY (`contractObjectId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Staging table cho contractObject từ insuranceSale.contractObject';


-- ============================================================================
-- Table: stgClaim
-- Source: insuranceSale.claim
-- Purpose: Staging table chứa dữ liệu yêu cầu bồi thường từ CDC
-- ============================================================================
CREATE TABLE IF NOT EXISTS `stgClaim` (
  `id` varchar(256) NOT NULL,
  `contractId` varchar(256) NOT NULL,
  `contractObjectId` varchar(256) NOT NULL,
  `amountClaim` decimal(20,0) DEFAULT NULL COMMENT 'Số tiền yêu cầu bồi thường',
  `compensationAmount` decimal(20,0) DEFAULT NULL COMMENT 'Số tiền được bồi thường',
  `note` longtext DEFAULT NULL COMMENT 'Chú thích lý do không chi trả...',
  `bankId` varchar(10) DEFAULT NULL,
  `bankCode` varchar(45) DEFAULT NULL COMMENT 'Map with TPA, not map table bankCode',
  `bankName` varchar(256) DEFAULT NULL,
  `bankBranch` varchar(256) DEFAULT NULL,
  `accountNumberBank` varchar(50) DEFAULT NULL,
  `accountName` varchar(256) DEFAULT NULL,
  `relationship` int(11) DEFAULT NULL COMMENT 'Mối quan hệ với người được bảo hiểm',
  `claimType` int(11) NOT NULL COMMENT 'Map with enum StaticEnum.ClaimType',
  `hospitalizedDate` date DEFAULT NULL COMMENT 'Ngày khám bệnh hoặc ngày nhập viện',
  `hospitalDischargeDate` date DEFAULT NULL COMMENT 'Ngày ra viện',
  `placeOfTreatment` varchar(256) DEFAULT NULL COMMENT 'Nơi điều trị',
  `diagnostic` longtext DEFAULT NULL COMMENT 'Chuẩn đoán',
  `upload` longtext DEFAULT NULL COMMENT 'Chứng từ đính kèm',
  `name` varchar(256) DEFAULT NULL COMMENT 'Tên người liên hệ',
  `phone` varchar(256) DEFAULT NULL COMMENT 'Số điện thoại người liên hệ',
  `email` varchar(256) DEFAULT NULL COMMENT 'Email người liên hệ',
  `status` int(11) NOT NULL COMMENT 'Map with enum StaticEnum.ClaimStatus',
  `additionalDocument` text DEFAULT NULL,
  `benefitCost` text DEFAULT NULL,
  `groupCost` text DEFAULT NULL,
  `tpaId` varchar(256) DEFAULT NULL,
  `claimIdTpa` varchar(256) DEFAULT NULL,
  `requireUpdateStatus` int(11) DEFAULT NULL COMMENT 'Map with enum StaticEnum.RequireUpdateStatus',
  `paperDocument` text DEFAULT NULL,
  `createdAt` datetime NOT NULL,
  `createdBy` varchar(256) NOT NULL,
  `modifiedAt` datetime NOT NULL,
  `modifiedBy` varchar(256) NOT NULL,
  `connectType` varchar(255) DEFAULT NULL,
  `source` varchar(255) DEFAULT NULL,
  `parentId` varchar(255) DEFAULT NULL,
  `admissionDate` datetime DEFAULT NULL,
  `treatmentType` varchar(255) DEFAULT NULL,
  `handlerFullname` varchar(255) DEFAULT NULL,
  `handlerEmail` varchar(255) DEFAULT NULL,
  `beneficiaryFullname` varchar(255) DEFAULT NULL,
  `beneficiaryReceptionMethod` varchar(255) DEFAULT NULL,
  `cause` varchar(255) DEFAULT NULL,
  `causeDate` datetime DEFAULT NULL,
  `placeOfTreatmentId` varchar(255) DEFAULT NULL,
  `compensationDetail` longtext DEFAULT NULL,
  `modifiedDate` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT 'Thời điểm CDC cập nhật record',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Staging table cho claim từ insuranceSale.claim';

-- ============================================================================
-- Table: stgContractObjectVehicle
-- Source: insuranceSale.contractObjectVehicle
-- Purpose: Staging table chứa dữ liệu bảo hiểm ô tô từ CDC
-- ============================================================================
CREATE TABLE IF NOT EXISTS `stgContractObjectVehicle` (
  `contractObjectId` varchar(256) NOT NULL,
  `contractObjectIdDisplay` varchar(256) DEFAULT NULL,
  `cardNumber` varchar(256) DEFAULT NULL,
  `certificateNumberProvider` varchar(50) DEFAULT NULL COMMENT 'Số giấy chứng nhận của nhà cung cấp',
  `accountTPA` varchar(256) DEFAULT NULL COMMENT 'Tài khoản TPA',
  `userId` varchar(256) DEFAULT NULL,
  `contractObjectSmeStatus` int(11) DEFAULT NULL COMMENT 'Map with enum StaticEnum.ContractObjectSmeStatus',
  `contractObjectStartDate` datetime DEFAULT NULL COMMENT 'Thời gian bắt đầu',
  `contractObjectEndDate` datetime DEFAULT NULL COMMENT 'Thời gian kết thúc',
  `contractObjectIdProvider` varchar(256) DEFAULT NULL COMMENT 'Mã chứng nhận nhà bảo hiểm',
  `contractObjectUrl` varchar(256) DEFAULT NULL,
  `contractId` varchar(256) DEFAULT NULL,
  `programTypeName` varchar(256) DEFAULT NULL,
  `programTypeId` varchar(256) DEFAULT NULL,
  `programId` varchar(256) DEFAULT NULL,
  `programName` varchar(256) DEFAULT NULL,
  `packageId` varchar(256) DEFAULT NULL,
  `packageName` varchar(256) DEFAULT NULL,
  `packageCodeFromProvider` varchar(256) DEFAULT NULL,
  `vehicleId` varchar(256) DEFAULT NULL,
  `feeMainBenefit` decimal(20,0) DEFAULT NULL,
  `termsId` varchar(256) DEFAULT NULL,
  `termsHighlight` text DEFAULT NULL,
  `termsBenefit` text DEFAULT NULL,
  `termsApplicableObject` text DEFAULT NULL,
  `termsFeePaymentMethod` text DEFAULT NULL,
  `termsHospital` varchar(256) DEFAULT NULL,
  `majorName` varchar(256) DEFAULT NULL,
  `majorId` varchar(256) DEFAULT NULL,
  `productId` varchar(256) DEFAULT NULL,
  `codeFromProvider` varchar(256) DEFAULT NULL,
  `programCodeMiningChannel` varchar(256) DEFAULT NULL,
  `feeInsurance` decimal(20,0) DEFAULT NULL COMMENT 'Phí bảo hiểm',
  `maximumAmount` decimal(20,0) DEFAULT NULL COMMENT 'Số tiền tối đa có thể nhận',
  `companyProvider` varchar(256) DEFAULT NULL,
  `companyProviderName` varchar(256) DEFAULT NULL,
  `contractObjectType` int(11) DEFAULT NULL COMMENT 'Đối tượng được bảo hiểm map with enum StaticEnum.ContractObjectType',
  `peopleRelationship` int(11) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0, Mối quan hệ map with enum StaticEnum.ContractObjectPeopleRelationshipEnum',
  `peopleName` varchar(256) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleDob` date DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleGender` int(11) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleLicense` varchar(256) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleLicenseType` int(11) DEFAULT NULL COMMENT 'Map with enum StaticEnum.LicenseType',
  `peoplePhone` varchar(15) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleEmail` varchar(256) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleAddress` varchar(256) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleDistrictsCode` int(11) DEFAULT NULL,
  `peopleWardsCode` int(11) DEFAULT NULL,
  `peopleStreet` varchar(256) DEFAULT NULL,
  `peopleHouseNumber` varchar(256) DEFAULT NULL,
  `peopleCityCode` int(11) DEFAULT NULL,
  `peopleNote` varchar(512) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleUpload` varchar(2048) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleLicenseFront` varchar(256) DEFAULT NULL,
  `peopleLicenseBack` varchar(256) DEFAULT NULL,
  `customerType` int(11) DEFAULT NULL COMMENT 'Map with enum StaticEnum.CustomerType',
  `upload` varchar(256) DEFAULT NULL,
  `note` varchar(256) DEFAULT NULL,
  `createdAt` datetime NOT NULL DEFAULT current_timestamp(),
  `createdBy` varchar(256) DEFAULT NULL,
  `modifiedAt` datetime NOT NULL DEFAULT current_timestamp(),
  `modifiedBy` varchar(256) DEFAULT NULL,
  `minDate` int(11) DEFAULT NULL,
  `contractObjectIdPrev` varchar(255) DEFAULT NULL,
  `memberId` varchar(255) DEFAULT NULL,
  `contractObjectCardImage` longtext DEFAULT NULL,
  `contractObjectCardDocument` longtext DEFAULT NULL,
  `paymentType` int(11) DEFAULT NULL,
  `programDocument` longtext DEFAULT '[]',
  `modifiedDate` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT 'Thời điểm CDC cập nhật record',
  PRIMARY KEY (`contractObjectId`),
  INDEX idx_contractId (`contractId`),
  INDEX idx_userId (`userId`),
  INDEX idx_modifiedDate (`modifiedDate`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Staging table cho contractObjectVehicle từ insuranceSale.contractObjectVehicle';


-- ============================================================================
-- Table: stgContractObjectTravel
-- Source: insuranceSale.contractObjectTravel
-- Purpose: Staging table chứa dữ liệu bảo hiểm du lịch từ CDC
-- ============================================================================
CREATE TABLE `stgContractObjectTravel` (
  `id` varchar(256) NOT NULL,
  `idDisplay` varchar(256) DEFAULT `id`,
  `cardNumber` varchar(256) DEFAULT NULL,
  `certificateNumberProvider` varchar(50) DEFAULT NULL COMMENT 'Số giấy chứng nhận của nhà cung cấp',
  `accountTPA` varchar(256) DEFAULT NULL COMMENT 'Tài khoản TPA',
  `userId` varchar(256) NOT NULL,
  `startDate` datetime DEFAULT NULL COMMENT 'Thời gian bắt đầu',
  `endDate` datetime DEFAULT NULL COMMENT 'Thời gian kết thúc',
  `idProvider` varchar(256) DEFAULT NULL COMMENT 'Mã chứng nhận nhà bảo hiểm',
  `url` varchar(256) DEFAULT NULL,
  `contractId` varchar(256) NOT NULL,
  `programTypeName` varchar(256) NOT NULL,
  `programTypeId` varchar(256) NOT NULL,
  `programId` varchar(256) NOT NULL,
  `programName` varchar(256) NOT NULL,
  `packageId` varchar(256) NOT NULL,
  `packageName` varchar(256) NOT NULL,
  `feeMainBenefit` decimal(20,0) NOT NULL,
  `termsId` varchar(256) NOT NULL,
  `termsHighlight` text DEFAULT NULL,
  `termsBenefit` text DEFAULT NULL,
  `termsApplicableObject` text DEFAULT NULL,
  `majorName` varchar(256) NOT NULL,
  `majorId` varchar(256) NOT NULL,
  `productId` varchar(256) NOT NULL,
  `codeFromProvider` varchar(256) DEFAULT NULL,
  `programCodeMiningChannel` varchar(256) DEFAULT NULL,
  `programObject` int(11) NOT NULL COMMENT 'Map with enum StaticEnum.TravelProgramObject',
  `feeInsurance` decimal(20,0) NOT NULL COMMENT 'Phí bảo hiểm',
  `companyProvider` varchar(256) NOT NULL,
  `companyProviderName` varchar(256) NOT NULL,
  `name` varchar(256) DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `gender` int(11) DEFAULT NULL,
  `license` varchar(256) DEFAULT NULL,
  `licenseType` int(11) NOT NULL COMMENT 'Map with enum StaticEnum.LicenseType',
  `licenseFront` varchar(256) DEFAULT NULL,
  `licenseBack` varchar(256) DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `email` varchar(256) DEFAULT NULL,
  `address` varchar(256) DEFAULT NULL,
  `districtsCode` int(11) DEFAULT NULL,
  `wardsCode` int(11) DEFAULT NULL,
  `street` varchar(256) DEFAULT NULL,
  `houseNumber` varchar(256) DEFAULT NULL,
  `cityCode` int(11) DEFAULT NULL,
  `note` varchar(512) DEFAULT NULL,
  `upload` varchar(2048) DEFAULT NULL,
  `customerType` int(11) DEFAULT NULL COMMENT 'Map with enum StaticEnum.CustomerType',
  `nationality` varchar(256) DEFAULT NULL,
  `domesticOrInternational` int(11) NOT NULL COMMENT 'Trong nước hay quốc tế. Map with enum StaticEnum.DomesticOrInternationalEnum',
  `departure` varchar(256) NOT NULL COMMENT 'Nơi bắt đầu',
  `destination` int(11) DEFAULT NULL COMMENT 'Nơi đến quốc tế. Map with enum StaticEnum.TravelProductDestination',
  `destinationDomestic` varchar(256) DEFAULT NULL COMMENT 'Nơi đến trong nước',
  `journey` varchar(256) DEFAULT NULL COMMENT 'hành trình',
  `startDateJourney` date DEFAULT NULL,
  `endDateJourney` date DEFAULT NULL,
  `payerUserId` varchar(256) DEFAULT NULL,
  `payerName` varchar(256) DEFAULT NULL,
  `payerDob` date DEFAULT NULL,
  `payerGender` int(11) DEFAULT NULL,
  `payerLicense` varchar(256) DEFAULT NULL,
  `payerLicenseType` int(11) NOT NULL COMMENT 'Map with enum StaticEnum.LicenseType',
  `payerLicenseFront` varchar(256) DEFAULT NULL,
  `payerLicenseBack` varchar(256) DEFAULT NULL,
  `payerPhone` varchar(15) DEFAULT NULL,
  `payerEmail` varchar(256) DEFAULT NULL,
  `payerAddress` varchar(256) DEFAULT NULL,
  `payerDistrictsCode` int(11) DEFAULT NULL,
  `payerWardsCode` int(11) DEFAULT NULL,
  `payerStreet` varchar(256) DEFAULT NULL,
  `payerHouseNumber` varchar(256) DEFAULT NULL,
  `payerCityCode` int(11) DEFAULT NULL,
  `payerNote` varchar(512) DEFAULT NULL,
  `payerUpload` varchar(2048) DEFAULT NULL,
  `payerCustomerType` int(11) DEFAULT NULL COMMENT 'Map with enum StaticEnum.CustomerType',
  `createdAt` datetime NOT NULL DEFAULT curtime(),
  `createdBy` varchar(256) NOT NULL,
  `modifiedAt` datetime NOT NULL DEFAULT curtime(),
  `modifiedBy` varchar(256) NOT NULL,
  `nationalityId` varchar(256) DEFAULT NULL,
  `programObjectFromProvider` varchar(256) DEFAULT NULL,
  `destinationFromProvider` varchar(256) DEFAULT NULL,
  `codePackageFromProvider` varchar(256) DEFAULT NULL,
  `adults` int(11) DEFAULT NULL,
  `children` int(11) DEFAULT NULL,
  `programDocument` longtext DEFAULT '[]',
  `modifiedDate` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT 'Thời điểm CDC cập nhật record',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;


-- ============================================================================
-- Table: stgContractObjectMoto
-- Source: insuranceSale.contractObjectMoto
-- Purpose: Staging table chứa dữ liệu bảo hiểm xe máy từ CDC
-- ============================================================================
CREATE TABLE IF NOT EXISTS `stgContractObjectMoto` (
  `id` varchar(256) NOT NULL,
  `idDisplay` varchar(256) DEFAULT NULL,
  `cardNumber` varchar(256) DEFAULT NULL,
  `certificateNumberProvider` varchar(50) DEFAULT NULL COMMENT 'Số giấy chứng nhận của nhà cung cấp',
  `accountTPA` varchar(256) DEFAULT NULL COMMENT 'Tài khoản TPA',
  `userId` varchar(256) NOT NULL,
  `startDate` datetime DEFAULT NULL COMMENT 'Thời gian bắt đầu',
  `endDate` datetime DEFAULT NULL COMMENT 'Thời gian kết thúc',
  `idProvider` varchar(256) DEFAULT NULL COMMENT 'Mã chứng nhận nhà bảo hiểm',
  `url` varchar(256) DEFAULT NULL,
  `contractId` varchar(256) NOT NULL,
  `programTypeName` varchar(256) NOT NULL,
  `programTypeId` varchar(256) NOT NULL,
  `programId` varchar(256) NOT NULL,
  `programName` varchar(256) NOT NULL,
  `packageId` varchar(256) NOT NULL,
  `packageName` varchar(256) NOT NULL,
  `feeMainBenefit` decimal(20,0) NOT NULL,
  `termsId` varchar(256) NOT NULL,
  `termsHighlight` text DEFAULT NULL,
  `termsBenefit` text DEFAULT NULL,
  `termsApplicableObject` text DEFAULT NULL,
  `majorName` varchar(256) NOT NULL,
  `majorId` varchar(256) NOT NULL,
  `productId` varchar(256) NOT NULL,
  `codeFromProvider` varchar(256) DEFAULT NULL,
  `programCodeMiningChannel` varchar(256) DEFAULT NULL,
  `feeInsurance` decimal(20,0) NOT NULL COMMENT 'Phí bảo hiểm',
  `maximumAmount` decimal(20,0) NOT NULL COMMENT 'Số tiền tối đa có thể nhận',
  `companyProvider` varchar(256) NOT NULL,
  `companyProviderName` varchar(256) NOT NULL,
  `name` varchar(256) DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `gender` int(11) DEFAULT NULL,
  `license` varchar(256) DEFAULT NULL,
  `licenseType` int(11) DEFAULT NULL,
  `licenseFront` varchar(256) DEFAULT NULL,
  `licenseBack` varchar(256) DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `email` varchar(256) DEFAULT NULL,
  `address` varchar(256) DEFAULT NULL,
  `districtsCode` int(11) DEFAULT NULL,
  `wardsCode` int(11) DEFAULT NULL,
  `street` varchar(256) DEFAULT NULL,
  `houseNumber` varchar(256) DEFAULT NULL,
  `cityCode` int(11) DEFAULT NULL,
  `note` varchar(512) DEFAULT NULL,
  `upload` varchar(2048) DEFAULT NULL,
  `customerType` int(11) DEFAULT NULL COMMENT 'Map with enum StaticEnum.CustomerType',
  `licensePlates` varchar(256) DEFAULT NULL COMMENT 'Biển số',
  `chassisNumber` varchar(256) DEFAULT NULL COMMENT 'Số khung',
  `engineNumber` varchar(256) DEFAULT NULL COMMENT 'Số máy',
  `maker` varchar(256) DEFAULT NULL COMMENT 'Hãng xe',
  `type` int(11) NOT NULL COMMENT 'Map with enum StaticEnum.MotoType',
  `line` varchar(256) DEFAULT NULL COMMENT 'Dòng xe',
  `seatNumber` int(11) DEFAULT NULL,
  `createdAt` datetime NOT NULL DEFAULT current_timestamp(),
  `createdBy` varchar(256) NOT NULL,
  `modifiedAt` datetime NOT NULL DEFAULT current_timestamp(),
  `modifiedBy` varchar(256) NOT NULL,
  `programDocument` longtext DEFAULT '[]',
  `feeSideBenefit` decimal(20,0) DEFAULT 0,
  `preVatFeeSideBenefit` decimal(20,0) DEFAULT 0,
  `vatFeeSideBenefit` decimal(20,0) DEFAULT 0,
  `vatFeeMainBenefit` decimal(20,0) DEFAULT 0,
  `preVatFeeMainBenefit` decimal(20,0) DEFAULT 0,
  `preVatFeeInsurance` decimal(20,0) DEFAULT 0,
  `VatFeeInsurance` decimal(20,0) DEFAULT 0,
  `modifiedDate` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT 'Thời điểm CDC cập nhật record',
  PRIMARY KEY (`id`),
  INDEX idx_contractId (`contractId`),
  INDEX idx_userId (`userId`),
  INDEX idx_modifiedDate (`modifiedDate`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Staging table cho contractObjectMoto từ insuranceSale.contractObjectMoto';


-- ============================================================================
-- Table: stgContractObjectSocialInsurance
-- Source: insuranceSale.contractObjectSocialInsurance
-- Purpose: Staging table chứa dữ liệu bảo hiểm xã hội từ CDC
-- ============================================================================
CREATE TABLE IF NOT EXISTS `stgContractObjectSocialInsurance` (
  `contractObjectId` varchar(256) NOT NULL,
  `contractObjectIdDisplay` varchar(256) DEFAULT NULL,
  `cardNumber` varchar(256) DEFAULT NULL,
  `certificateNumberProvider` varchar(50) DEFAULT NULL COMMENT 'Số giấy chứng nhận của nhà cung cấp',
  `accountTPA` varchar(256) DEFAULT NULL COMMENT 'Tài khoản TPA',
  `userId` varchar(256) DEFAULT NULL,
  `contractObjectSmeStatus` int(11) DEFAULT NULL COMMENT 'Map with enum StaticEnum.ContractObjectSmeStatus',
  `contractIndividualStatus` int(11) DEFAULT NULL COMMENT '1: hop dong ca nhan hieu luc, 0: hop dong ca nhan het han',
  `contractObjectStartDate` datetime DEFAULT NULL COMMENT 'Thời gian bắt đầu',
  `contractObjectEndDate` datetime DEFAULT NULL COMMENT 'Thời gian kết thúc',
  `contractObjectIdProvider` varchar(256) DEFAULT NULL COMMENT 'Mã chứng nhận nhà bảo hiểm',
  `contractObjectUrl` varchar(256) DEFAULT NULL,
  `contractId` varchar(256) NOT NULL,
  `programTypeName` varchar(256) NOT NULL,
  `programTypeId` varchar(256) NOT NULL,
  `programId` varchar(256) NOT NULL,
  `programName` varchar(256) NOT NULL,
  `declarationType` int(11) NOT NULL DEFAULT 0,
  `remunerationType` int(11) NOT NULL DEFAULT 0 COMMENT 'Loại thù lao',
  `packageId` varchar(256) NOT NULL,
  `packageName` varchar(256) NOT NULL,
  `packageCodeFromProvider` varchar(256) DEFAULT NULL,
  `fromAge` int(11) NOT NULL,
  `toAge` int(11) NOT NULL,
  `feeMainBenefit` decimal(20,0) NOT NULL,
  `termsId` varchar(256) DEFAULT NULL,
  `termsHighlight` text DEFAULT NULL,
  `termsBenefit` text DEFAULT NULL,
  `termsApplicableObject` text DEFAULT NULL,
  `termsFeePaymentMethod` text DEFAULT NULL,
  `termsHospital` varchar(256) DEFAULT NULL,
  `majorName` varchar(256) NOT NULL,
  `majorId` varchar(256) NOT NULL,
  `productId` varchar(256) NOT NULL,
  `codeFromProvider` varchar(256) DEFAULT NULL,
  `programCodeMiningChannel` varchar(256) DEFAULT NULL,
  `feeInsurance` decimal(20,0) NOT NULL COMMENT 'Phí bảo hiểm',
  `maximumAmount` decimal(20,0) NOT NULL COMMENT 'Số tiền tối đa có thể nhận',
  `companyProvider` varchar(256) NOT NULL,
  `companyProviderName` varchar(256) NOT NULL,
  `contractObjectType` int(11) NOT NULL COMMENT 'Đối tượng được bảo hiểm map with enum StaticEnum.ContractObjectType',
  `peopleRelationship` int(11) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0, Mối quan hệ map with enum StaticEnum.ContractObjectPeopleRelationshipEnum',
  `peopleName` varchar(256) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleDob` date DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleGender` int(11) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleLicense` varchar(256) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleLicenseType` int(11) NOT NULL COMMENT 'Map with enum StaticEnum.LicenseType',
  `peoplePhone` varchar(15) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleEmail` varchar(256) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleAddress` varchar(256) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleDistrictsCode` int(11) DEFAULT NULL,
  `peopleWardsCode` int(11) DEFAULT NULL,
  `peopleStreet` varchar(256) DEFAULT NULL,
  `peopleHouseNumber` varchar(256) DEFAULT NULL,
  `peopleCityCode` int(11) DEFAULT NULL,
  `peopleNote` varchar(512) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleUpload` varchar(2048) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleLicenseFront` varchar(256) DEFAULT NULL,
  `peopleLicenseBack` varchar(256) DEFAULT NULL,
  `peopleLicenseQr` varchar(256) DEFAULT NULL,
  `customerType` int(11) DEFAULT NULL COMMENT 'Map with enum StaticEnum.CustomerType',
  `upload` varchar(256) DEFAULT NULL,
  `note` varchar(256) DEFAULT NULL,
  `createdAt` datetime NOT NULL DEFAULT current_timestamp(),
  `createdBy` varchar(256) NOT NULL,
  `modifiedAt` datetime NOT NULL DEFAULT current_timestamp(),
  `modifiedBy` varchar(256) NOT NULL,
  `oldCardStartDate` date DEFAULT NULL COMMENT 'Ngày đầu thẻ cũ',
  `oldCardEndDate` date DEFAULT NULL COMMENT 'Ngày cuối thẻ cũ',
  `socialId` varchar(256) DEFAULT NULL COMMENT 'Số BHXH (10 số cuối) của người được BH',
  `monthlyIncome` decimal(20,0) DEFAULT 0 COMMENT 'Số tiền thu nhập hàng tháng của người được BH',
  `paymentPeriod` int(11) DEFAULT NULL COMMENT 'Kỳ hạn đóng BH',
  `supportBudget` decimal(20,0) DEFAULT 0 COMMENT 'Mức hỗ trợ của nhà nước Theo quy định của Luật BHXH x số tháng đóng BH',
  `renewal` int(11) DEFAULT NULL COMMENT 'Đóng nối tiếp -> (true, 1), đóng mới -> (false, 0)',
  `socialFamilyId` varchar(256) DEFAULT NULL COMMENT 'Mã hộ gia đình',
  `oldBhxhCodeUnit` varchar(256) DEFAULT NULL COMMENT 'Mã đơn vị cấp BHXH kỳ trước lấy maDmBhxh từ Tra cứu thông tin BHXH',
  `oldRegisterDate` varchar(256) DEFAULT NULL COMMENT 'Ngày đăng ký đóng kỳ trước lấy ngayDk từ Tra cứu thông tin BHXH',
  `percent` double DEFAULT NULL,
  `minDate` int(11) DEFAULT NULL,
  `contractObjectIdPrev` varchar(255) DEFAULT NULL,
  `memberId` varchar(255) DEFAULT NULL,
  `contractObjectCardDocument` varchar(255) DEFAULT NULL,
  `contractObjectCardImage` varchar(255) DEFAULT NULL,
  `paymentType` int(11) DEFAULT NULL,
  `document` text DEFAULT NULL,
  `programDocument` longtext DEFAULT '[]',
  `feeSideBenefit` decimal(20,0) DEFAULT NULL,
  `preVatFeeSideBenefit` decimal(20,0) DEFAULT 0,
  `vatFeeSideBenefit` decimal(20,0) DEFAULT 0,
  `vatFeeMainBenefit` decimal(20,0) DEFAULT 0,
  `preVatFeeMainBenefit` decimal(20,0) DEFAULT 0,
  `preVatFeeInsurance` decimal(20,0) DEFAULT 0,
  `vatFeeInsurance` decimal(20,0) DEFAULT 0,
  `discountAmount` decimal(10,0) DEFAULT NULL,
  `modifiedDate` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT 'Thời điểm CDC cập nhật record',
  PRIMARY KEY (`contractObjectId`),
  INDEX idx_contractId (`contractId`),
  INDEX idx_userId (`userId`),
  INDEX idx_modifiedDate (`modifiedDate`),
  INDEX idx_packageName (`packageName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Staging table cho contractObjectSocialInsurance từ insuranceSale.contractObjectSocialInsurance';


-- ============================================================================
-- Table: stgContractObjectMedicalInsurance
-- Source: insuranceSale.contractObjectMedicalInsurance
-- Purpose: Staging table chứa dữ liệu bảo hiểm y tế từ CDC
-- ============================================================================
CREATE TABLE IF NOT EXISTS `stgContractObjectMedicalInsurance` (
  `contractObjectId` varchar(256) NOT NULL,
  `contractObjectIdDisplay` varchar(256) DEFAULT NULL,
  `cardNumber` varchar(256) DEFAULT NULL,
  `certificateNumberProvider` varchar(50) DEFAULT NULL COMMENT 'Số giấy chứng nhận của nhà cung cấp',
  `accountTPA` varchar(256) DEFAULT NULL COMMENT 'Tài khoản TPA',
  `userId` varchar(256) DEFAULT NULL,
  `contractObjectSmeStatus` int(11) DEFAULT NULL COMMENT 'Map with enum StaticEnum.ContractObjectSmeStatus',
  `contractIndividualStatus` int(11) DEFAULT NULL COMMENT '1: hop dong ca nhan hieu luc, 0: hop dong ca nhan het han',
  `contractObjectStartDate` datetime DEFAULT NULL COMMENT 'Thời gian bắt đầu',
  `contractObjectEndDate` datetime DEFAULT NULL COMMENT 'Thời gian kết thúc',
  `contractObjectIdProvider` varchar(256) DEFAULT NULL COMMENT 'Mã chứng nhận nhà bảo hiểm',
  `contractObjectUrl` varchar(256) DEFAULT NULL,
  `contractId` varchar(256) NOT NULL,
  `programTypeName` varchar(256) NOT NULL,
  `programTypeId` varchar(256) NOT NULL,
  `programId` varchar(256) NOT NULL,
  `programName` varchar(256) NOT NULL,
  `packageId` varchar(256) NOT NULL,
  `declarationType` int(11) NOT NULL DEFAULT 0,
  `remunerationType` int(11) NOT NULL DEFAULT 0 COMMENT 'Loại thù lao',
  `packageName` varchar(256) NOT NULL,
  `packageCodeFromProvider` varchar(256) DEFAULT NULL,
  `fromAge` int(11) DEFAULT NULL,
  `toAge` int(11) DEFAULT NULL,
  `feeMainBenefit` decimal(20,0) NOT NULL,
  `termsId` varchar(256) DEFAULT NULL,
  `termsHighlight` text DEFAULT NULL,
  `termsBenefit` text DEFAULT NULL,
  `termsApplicableObject` text DEFAULT NULL,
  `termsFeePaymentMethod` text DEFAULT NULL,
  `termsHospital` varchar(256) DEFAULT NULL,
  `majorName` varchar(256) NOT NULL,
  `majorId` varchar(256) NOT NULL,
  `productId` varchar(256) NOT NULL,
  `codeFromProvider` varchar(256) DEFAULT NULL,
  `programCodeMiningChannel` varchar(256) DEFAULT NULL,
  `feeInsurance` decimal(20,0) NOT NULL COMMENT 'Phí bảo hiểm',
  `maximumAmount` decimal(20,0) NOT NULL COMMENT 'Số tiền tối đa có thể nhận',
  `companyProvider` varchar(256) NOT NULL,
  `companyProviderName` varchar(256) NOT NULL,
  `contractObjectType` int(11) NOT NULL COMMENT 'Đối tượng được bảo hiểm map with enum StaticEnum.ContractObjectType',
  `peopleRelationship` int(11) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0, Mối quan hệ map with enum StaticEnum.ContractObjectPeopleRelationshipEnum',
  `peopleName` varchar(256) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleDob` date DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleGender` int(11) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleLicense` varchar(256) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleLicenseType` int(11) NOT NULL COMMENT 'Map with enum StaticEnum.LicenseType',
  `peoplePhone` varchar(15) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleEmail` varchar(256) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleAddress` varchar(256) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleDistrictsCode` int(11) DEFAULT NULL,
  `peopleWardsCode` int(11) DEFAULT NULL,
  `peopleStreet` varchar(256) DEFAULT NULL,
  `peopleHouseNumber` varchar(256) DEFAULT NULL,
  `peopleCityCode` int(11) DEFAULT NULL,
  `peopleNote` varchar(512) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleUpload` varchar(2048) DEFAULT NULL COMMENT 'Chỉ có giá trị khi contractObjectType là 0',
  `peopleLicenseFront` varchar(256) DEFAULT NULL,
  `peopleLicenseBack` varchar(256) DEFAULT NULL,
  `peopleLicenseQr` varchar(256) DEFAULT NULL,
  `customerType` int(11) DEFAULT NULL COMMENT 'Map with enum StaticEnum.CustomerType',
  `upload` varchar(256) DEFAULT NULL,
  `note` varchar(256) DEFAULT NULL,
  `createdAt` datetime NOT NULL DEFAULT current_timestamp(),
  `createdBy` varchar(256) NOT NULL,
  `modifiedAt` datetime NOT NULL DEFAULT current_timestamp(),
  `modifiedBy` varchar(256) NOT NULL,
  `oldCardStartDate` date DEFAULT NULL COMMENT 'Ngày đầu thẻ cũ, lấy từ tra cứu',
  `oldCardEndDate` date DEFAULT NULL COMMENT 'Ngày cuối thẻ cũ, lấy từ tra cứu',
  `renewal` int(11) DEFAULT NULL COMMENT 'Đóng nối tiếp -> (true, 1), đóng mới -> (false, 0)',
  `fiveYearDate` varchar(255) DEFAULT NULL COMMENT 'Đủ điều kiện 5 năm liên tục lấy "ngay5Nam " từ Tra cứu thông tin BHXH',
  `medicalId` varchar(255) DEFAULT NULL COMMENT 'Mã thẻ bảo hiểm y tế (10 số cuối)',
  `socialFamilyId` varchar(255) DEFAULT NULL COMMENT 'Mã hộ gia đình lấy ho_gia_dinh từ Tra cứu thông tin BHXH',
  `minDate` int(11) DEFAULT NULL,
  `contractObjectIdPrev` varchar(255) DEFAULT NULL,
  `memberId` varchar(255) DEFAULT NULL,
  `contractObjectCardDocument` varchar(255) DEFAULT NULL,
  `contractObjectCardImage` varchar(255) DEFAULT NULL,
  `paymentType` int(11) DEFAULT NULL,
  `document` text DEFAULT NULL,
  `programDocument` longtext DEFAULT '[]',
  `feeSideBenefit` decimal(20,0) DEFAULT 0,
  `preVatFeeSideBenefit` decimal(20,0) DEFAULT 0,
  `vatFeeSideBenefit` decimal(20,0) DEFAULT 0,
  `vatFeeMainBenefit` decimal(20,0) DEFAULT 0,
  `preVatFeeMainBenefit` decimal(20,0) DEFAULT 0,
  `preVatFeeInsurance` decimal(20,0) DEFAULT 0,
  `vatFeeInsurance` decimal(20,0) DEFAULT 0,
  `hospitalCode` varchar(256) DEFAULT NULL COMMENT 'Mã bệnh viện khám',
  `hospitalName` varchar(256) DEFAULT NULL COMMENT 'Tên bệnh viện khám',
  `hospitalCityRegisteredCode` int(11) DEFAULT NULL COMMENT 'Mã tỉnh bệnh viện',
  `hospitalCityRegisteredName` varchar(256) DEFAULT NULL COMMENT 'Tỉnh bệnh viện',
  `nation` varchar(100) DEFAULT NULL COMMENT 'Tỉnh bệnh viện',
  `ethnicity` varchar(100) DEFAULT NULL,
  `socialId` varchar(64) DEFAULT NULL,
  `modifiedDate` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT 'Thời điểm CDC cập nhật record',
  PRIMARY KEY (`contractObjectId`),
  INDEX idx_contractId (`contractId`),
  INDEX idx_userId (`userId`),
  INDEX idx_modifiedDate (`modifiedDate`),
  INDEX idx_packageName (`packageName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Staging table cho contractObjectMedicalInsurance từ insuranceSale.contractObjectMedicalInsurance';

-- ============================================================================
-- Table: stgContractObjectHouse
-- Source: insuranceSale.contractObjectHouse (CDC - Online data)
-- Purpose: Staging table cho Bảo hiểm nhà ở - dữ liệu CDC từ database
-- ============================================================================
CREATE TABLE IF NOT EXISTS `stgContractObjectHouse` (
  `id` varchar(256) NOT NULL COMMENT 'Mã hợp đồng cá nhân affina sản phẩm nhà - PRIMARY KEY',
  `idDisplay` varchar(256) DEFAULT NULL COMMENT 'Mã hợp đồng cá nhân affina dùng để hiển thị',
  `cardNumber` varchar(256) DEFAULT NULL COMMENT 'Số thẻ hợp đồng cá nhân',
  `certificateNumberProvider` varchar(256) DEFAULT NULL COMMENT 'Số giấy chứng nhận của nhà cung cấp',
  `accountTPA` varchar(256) DEFAULT NULL COMMENT 'Tài khoản TPA',
  `userId` varchar(256) DEFAULT NULL COMMENT 'Mã của người mua bảo hiểm',
  `contractId` varchar(256) DEFAULT NULL COMMENT 'Mã hợp đồng nhóm của affina',
  `idProvider` varchar(256) DEFAULT NULL COMMENT 'Mã chứng nhận nhà bảo hiểm',
  `url` varchar(256) DEFAULT NULL COMMENT 'Đường dẫn tệp hợp đồng',
  `contractObjectStartDate` datetime DEFAULT NULL COMMENT 'Thời gian bắt đầu (source: startDate)',
  `contractObjectEndDate` datetime DEFAULT NULL COMMENT 'Thời gian kết thúc (source: endDate)',
  `programTypeName` varchar(256) DEFAULT NULL COMMENT 'Tên loại hình',
  `programTypeId` varchar(256) DEFAULT NULL COMMENT 'Mã loại hình',
  `programId` varchar(256) DEFAULT NULL COMMENT 'Mã chương trình',
  `programName` varchar(256) DEFAULT NULL COMMENT 'Tên chương trình',
  `packageId` varchar(256) DEFAULT NULL COMMENT 'Mã gói',
  `packageName` varchar(256) DEFAULT NULL COMMENT 'Tên gói',
  `majorName` varchar(256) DEFAULT NULL COMMENT 'Tên nghiệp vụ',
  `majorId` varchar(256) DEFAULT NULL COMMENT 'Mã nghiệp vụ',
  `productId` varchar(256) DEFAULT NULL COMMENT 'Mã sản phẩm',
  `codeFromProvider` varchar(256) DEFAULT NULL COMMENT 'Mã từ nhà cung cấp',
  `programCodeMiningChannel` varchar(256) DEFAULT NULL COMMENT 'Mã kênh khai thác từ nhà cung cấp',
  `feeMainBenefit` decimal(20,0) DEFAULT NULL COMMENT 'Phí của các quyền lợi chính',
  `feeInsurance` decimal(20,0) DEFAULT NULL COMMENT 'Phí bảo hiểm',
  `maximumAmount` decimal(20,0) DEFAULT NULL COMMENT 'Số tiền tối đa có thể nhận',
  `termsId` varchar(256) DEFAULT NULL COMMENT 'Mã điều khoản điều kiện',
  `termsHighlight` text DEFAULT NULL COMMENT 'Điều khoản nổi bật',
  `termsBenefit` text DEFAULT NULL COMMENT 'Quyền lợi trong điều kiện điều khoản',
  `termsApplicableObject` text DEFAULT NULL COMMENT 'Đối tượng áp dụng trong điều kiện điều khoản',
  `companyProvider` varchar(256) DEFAULT NULL COMMENT 'Mã công ty nhà cung cấp',
  `companyProviderName` varchar(256) DEFAULT NULL COMMENT 'Tên công ty nhà cung cấp',
  `name` varchar(256) DEFAULT NULL COMMENT 'Tên người chủ tài sản',
  `dob` date DEFAULT NULL COMMENT 'Ngày sinh người chủ tài sản',
  `gender` int(11) DEFAULT NULL COMMENT 'Giới tính người chủ tài sản',
  `license` varchar(256) DEFAULT NULL COMMENT 'Số giấy tờ người chủ tài sản',
  `licenseType` int(11) DEFAULT NULL COMMENT 'Loại giấy tờ người chủ tài sản',
  `licenseFront` varchar(256) DEFAULT NULL COMMENT 'Đường dẫn hình mặt trước giấy tờ',
  `licenseBack` varchar(256) DEFAULT NULL COMMENT 'Đường dẫn hình mặt sau giấy tờ',
  `phone` varchar(256) DEFAULT NULL COMMENT 'Số điện thoại người chủ tài sản',
  `email` varchar(256) DEFAULT NULL COMMENT 'Email người chủ tài sản',
  `address` text DEFAULT NULL COMMENT 'Địa chỉ người chủ tài sản',
  `districtsCode` int(11) DEFAULT NULL COMMENT 'Mã quận huyện thị xã người chủ tài sản',
  `wardsCode` int(11) DEFAULT NULL COMMENT 'Mã phường xã thị trấn người chủ tài sản',
  `street` varchar(256) DEFAULT NULL COMMENT 'Tên đường người chủ tài sản',
  `houseNumber` varchar(1024) DEFAULT NULL COMMENT 'Số nhà người chủ tài sản',
  `cityCode` int(11) DEFAULT NULL COMMENT 'Mã thành phố tỉnh người chủ tài sản',
  `note` text DEFAULT NULL COMMENT 'Ghi chú của người chủ tài sản',
  `upload` text DEFAULT NULL COMMENT 'Đính kèm của người chủ tài sản',
  `customerType` int(11) DEFAULT NULL COMMENT 'Loại khách hàng',
  `ownership` text DEFAULT NULL COMMENT 'Hình thức sở hữu tài sản',
  `levelId` varchar(256) DEFAULT NULL COMMENT 'Cấp nhà ID',
  `programObject` int(11) DEFAULT NULL COMMENT 'Đối tượng ngôi nhà',
  `houseName` varchar(256) DEFAULT NULL COMMENT 'Tên chung cư, khu dân cư',
  `numberFloors` int(11) DEFAULT NULL COMMENT 'Số tầng',
  `houseAddress` text DEFAULT NULL COMMENT 'Địa chỉ căn nhà hoặc căn hộ',
  `houseDistrictsCode` int(11) DEFAULT NULL COMMENT 'Mã quận huyện thị xã căn nhà',
  `houseWardsCode` int(11) DEFAULT NULL COMMENT 'Mã phường xã thị trấn căn nhà',
  `houseStreet` varchar(256) DEFAULT NULL COMMENT 'Tên đường căn nhà',
  `houseHouseNumber` varchar(256) DEFAULT NULL COMMENT 'Số nhà căn nhà',
  `houseCityCode` int(11) DEFAULT NULL COMMENT 'Mã thành phố tỉnh căn nhà',
  `latitude` varchar(256) DEFAULT NULL COMMENT 'Vĩ độ căn nhà',
  `longitude` varchar(256) DEFAULT NULL COMMENT 'Kinh độ căn nhà',
  `acreage` double DEFAULT NULL COMMENT 'Diện tích căn nhà, đơn vị tính m2',
  `completionYear` int(11) DEFAULT NULL COMMENT 'Năm hoàn thiện xây dựng và đưa vào sử dụng',
  `houseValue` decimal(20,0) DEFAULT NULL COMMENT 'Giá trị thực tế của ngôi nhà',
  `houseValueInsured` decimal(20,0) DEFAULT NULL COMMENT 'Giá trị tham gia bảo hiểm của ngôi nhà',
  `propertyValue` decimal(20,0) DEFAULT NULL COMMENT 'Giá trị tài sản thực tế',
  `propertyValueInsured` decimal(20,0) DEFAULT NULL COMMENT 'Giá trị tài sản tham gia bảo hiểm',
  `uses` int(11) DEFAULT NULL COMMENT 'Mục đích sử dụng',
  `business` text DEFAULT NULL COMMENT 'Ngành kinh doanh',
  `companyType` text DEFAULT NULL COMMENT 'Loại công ty',
  `foundingYear` int(11) DEFAULT NULL COMMENT 'Năm thành lập công ty',
  `isStone` int(11) DEFAULT NULL COMMENT 'Ngôi nhà có được xây dựng bằng gạch đá không',
  `widthAlley` double DEFAULT NULL COMMENT 'Chiều rộng ngõ vào nhà',
  `insuranceDeductible` decimal(20,0) DEFAULT NULL COMMENT 'Số tiền miễn thường bảo hiểm ngôi nhà',
  `certificateNumber` varchar(256) DEFAULT NULL COMMENT 'Số giấy chứng nhận quyền sử dụng đất',
  `numberInApartment` varchar(256) DEFAULT NULL COMMENT 'Số căn hộ trong chung cư',
  `apartmentNameOrNumber` varchar(256) DEFAULT NULL COMMENT 'Tên hoặc số căn hộ',
  `numberUseHouse` double DEFAULT NULL COMMENT 'Số người sử dụng nhà',
  `rentAmount` decimal(20,0) DEFAULT NULL COMMENT 'Số tiền thuê nhà/tháng',
  `paymentPeriod` int(11) DEFAULT NULL COMMENT 'Tần suất thanh toán',
  `paymentPeriodValue` int(11) DEFAULT NULL COMMENT 'Khoảng cách thanh toán',
  `paymentNumber` int(11) DEFAULT NULL COMMENT 'Số kỳ thanh toán',
  `paymentRatio` double DEFAULT NULL COMMENT 'Tỉ lệ % thanh toán',
  `paymentType` int(11) DEFAULT NULL COMMENT 'Loại thanh toán',
  `bankName` varchar(256) DEFAULT NULL COMMENT 'Tên ngân hàng vay thế chấp',
  `bankAddress` text DEFAULT NULL COMMENT 'Địa chỉ ngân hàng vay thế chấp',
  `bankEmail` varchar(256) DEFAULT NULL COMMENT 'Email ngân hàng vay thế chấp',
  `bankCode` varchar(256) DEFAULT NULL COMMENT 'Mã ngân hàng',
  `scope` text DEFAULT NULL COMMENT 'Phạm vi địa lý',
  `classificationCode` text DEFAULT NULL COMMENT 'Mã phân loại ngôi nhà',
  `partnerHouseId` varchar(256) DEFAULT NULL COMMENT 'Mã nhà từ đối tác',
  `partnerAccountId` varchar(256) DEFAULT NULL COMMENT 'Mã tài khoản phía đối tác',
  `contractIndividualStatus` int(11) DEFAULT NULL COMMENT '1: hợp đồng cá nhân hiệu lực, 0: hợp đồng cá nhân hết hạn',
  `programDocument` text DEFAULT NULL COMMENT 'Tài liệu chương trình',
  `createdAt` datetime DEFAULT NULL COMMENT 'Ngày tạo từ source',
  `createdBy` varchar(256) DEFAULT NULL COMMENT 'Người tạo từ source',
  `modifiedAt` datetime DEFAULT NULL COMMENT 'Ngày cập nhật từ source',
  `modifiedBy` varchar(256) DEFAULT NULL COMMENT 'Người cập nhật từ source',
  `modifiedDate` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Thời điểm cập nhật record trong staging (CDC tracking)',
  PRIMARY KEY (`id`),
  INDEX `idx_contractId` (`contractId`),
  INDEX `idx_userId` (`userId`),
  INDEX `idx_modifiedDate` (`modifiedDate`),
  INDEX `idx_companyProvider` (`companyProvider`),
  INDEX `idx_majorId` (`majorId`),
  INDEX `idx_programId` (`programId`),
  INDEX `idx_contractIndividualStatus` (`contractIndividualStatus`),
  INDEX `idx_houseCityCode` (`houseCityCode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Staging table cho House Insurance - dữ liệu CDC từ insuranceSale.contractObjectHouse';


-- ============================================================================
-- FILE: create_wide_table_offline_contract.sql
-- PURPOSE: Tạo Wide Table tổng hợp cho 7 loại bảo hiểm offline contract
-- USAGE: mysql -h <host> -u <user> -p < create_wide_table_offline_contract.sql
-- DESCRIPTION:
--   Bảng này kết hợp tất cả các field từ 7 loại contractObject:
--   1. ContractObject (BH Sức khỏe)
--   2. ContractObjectVehicle (BH Ô tô)
--   3. ContractObjectTravel (BH Du lịch)
--   4. ContractObjectMoto (BH Xe máy)
--   5. ContractObjectSocialInsurance (BH Xã hội)
--   6. ContractObjectMedicalInsurance (BH Y tế)
--   7. ContractObjectHazard (BH Rủi ro - Offline only)
-- ============================================================================

USE `insuranceWarehouse`;

-- ============================================================================
-- Table: stgContractObjectOffline
-- Purpose: Wide table chứa dữ liệu tổng hợp của tất cả loại bảo hiểm offline
-- ============================================================================
CREATE TABLE IF NOT EXISTS `stgContractObjectOffline` (
  `offline_id` BIGINT AUTO_INCREMENT COMMENT 'ID tự tăng cho mỗi bản ghi',
  -- =========================================================================
  -- PRIMARY KEY & COMMON IDENTIFIERS
  -- Dùng cho: ALL (Tất cả 6 loại BH)
  -- =========================================================================
  `contractObjectId` TEXT DEFAULT NULL COMMENT 'ID đối tượng hợp đồng',
  `contractObjectIdDisplay` TEXT DEFAULT NULL COMMENT 'ID hiển thị - ALL',
  `insuranceType` VARCHAR(50) NOT NULL COMMENT 'Loại BH: HEALTH, VEHICLE, TRAVEL, MOTO, SOCIAL, MEDICAL, HAZARD',
  
  -- =========================================================================
  -- CARD & CERTIFICATE INFORMATION
  -- Dùng cho: ALL
  -- =========================================================================
  `cardNumber` TEXT DEFAULT NULL COMMENT 'Số thẻ - ALL',
  `certificateNumberProvider` TEXT DEFAULT NULL COMMENT 'Số giấy chứng nhận của nhà cung cấp - ALL',
  `accountTPA` TEXT DEFAULT NULL COMMENT 'Tài khoản TPA - ALL',
  
  -- =========================================================================
  -- USER & CONTRACT RELATIONSHIP
  -- Dùng cho: ALL
  -- =========================================================================
  `userId` TEXT DEFAULT NULL COMMENT 'User ID - ALL',
  `contractId` TEXT DEFAULT NULL COMMENT 'Contract ID - ALL',
  `contractIdDisplay` TEXT DEFAULT NULL COMMENT 'Contract ID hiển thị - HEALTH',
  
  -- =========================================================================
  -- STATUS & DATES
  -- Dùng cho: ALL (với tên field khác nhau)
  -- =========================================================================
  `contractObjectSmeStatus` INT(11) DEFAULT NULL COMMENT 'Trạng thái SME - HEALTH, VEHICLE, SOCIAL, MEDICAL',
  `contractIndividualStatus` INT(11) DEFAULT NULL COMMENT 'Trạng thái hợp đồng cá nhân - HEALTH, SOCIAL, MEDICAL',
  `contractObjectStartDate` DATETIME DEFAULT NULL COMMENT 'Ngày bắt đầu - ALL (startDate cho TRAVEL/MOTO)',
  `contractObjectEndDate` DATETIME DEFAULT NULL COMMENT 'Ngày kết thúc - ALL (endDate cho TRAVEL/MOTO)',
  `contractObjectIdProvider` TEXT DEFAULT NULL COMMENT 'Mã chứng nhận nhà BH - ALL (idProvider cho TRAVEL/MOTO)',
  `contractObjectUrl` TEXT DEFAULT NULL COMMENT 'URL đối tượng - ALL (url cho TRAVEL/MOTO)',
  
  -- =========================================================================
  -- PROGRAM & PACKAGE INFORMATION
  -- Dùng cho: ALL
  -- =========================================================================
  `programTypeName` TEXT DEFAULT NULL COMMENT 'Tên loại chương trình - ALL',
  `programTypeId` TEXT DEFAULT NULL COMMENT 'ID loại chương trình - ALL',
  `programId` TEXT DEFAULT NULL COMMENT 'ID chương trình - ALL',
  `programName` TEXT DEFAULT NULL COMMENT 'Tên chương trình - ALL',
  `packageId` TEXT DEFAULT NULL COMMENT 'ID gói - ALL',
  `packageName` TEXT DEFAULT NULL COMMENT 'Tên gói - ALL',
  `packageCodeFromProvider` TEXT DEFAULT NULL COMMENT 'Mã gói từ nhà cung cấp - ALL',
  `programCodeMiningChannel` TEXT DEFAULT NULL COMMENT 'Mã khai thác kênh - ALL',
  `programDocument` LONGTEXT DEFAULT '[]' COMMENT 'Tài liệu chương trình - ALL',
  
  -- =========================================================================
  -- AGE RANGE
  -- Dùng cho: HEALTH, SOCIAL, MEDICAL
  -- =========================================================================
  `fromAge` INT(11) DEFAULT NULL COMMENT 'Tuổi từ - HEALTH, SOCIAL, MEDICAL',
  `toAge` INT(11) DEFAULT NULL COMMENT 'Tuổi đến - HEALTH, SOCIAL, MEDICAL',
  
  -- =========================================================================
  -- FEE & AMOUNT INFORMATION
  -- Dùng cho: ALL
  -- =========================================================================
  `feeMainBenefit` DECIMAL(20,0) DEFAULT NULL COMMENT 'Phí quyền lợi chính - ALL',
  `feeSideBenefit` DECIMAL(20,0) DEFAULT 0 COMMENT 'Phí quyền lợi phụ - HEALTH, MOTO, SOCIAL, MEDICAL',
  `feeInsurance` DECIMAL(20,0) DEFAULT NULL COMMENT 'Phí bảo hiểm - ALL',
  `maximumAmount` DECIMAL(20,0) DEFAULT NULL COMMENT 'Số tiền tối đa - ALL',
  
  -- VAT & Pre-VAT Fee breakdown
  `preVatFeeMainBenefit` DECIMAL(20,0) DEFAULT 0 COMMENT 'Phí chính trước VAT - HEALTH, MOTO, SOCIAL, MEDICAL',
  `vatFeeMainBenefit` DECIMAL(20,0) DEFAULT 0 COMMENT 'VAT phí chính - HEALTH, MOTO, SOCIAL, MEDICAL',
  `preVatFeeSideBenefit` DECIMAL(20,0) DEFAULT 0 COMMENT 'Phí phụ trước VAT - HEALTH, MOTO, SOCIAL, MEDICAL',
  `vatFeeSideBenefit` DECIMAL(20,0) DEFAULT 0 COMMENT 'VAT phí phụ - HEALTH, MOTO, SOCIAL, MEDICAL',
  `preVatFeeInsurance` DECIMAL(20,0) DEFAULT 0 COMMENT 'Phí BH trước VAT - HEALTH, MOTO, SOCIAL, MEDICAL',
  `vatFeeInsurance` DECIMAL(20,0) DEFAULT 0 COMMENT 'VAT phí BH - HEALTH, MOTO, SOCIAL, MEDICAL',
  
  -- =========================================================================
  -- TERMS & CONDITIONS
  -- Dùng cho: ALL
  -- =========================================================================
  `termsId` TEXT DEFAULT NULL COMMENT 'ID điều khoản - ALL',
  `termsHighlight` TEXT DEFAULT NULL COMMENT 'Điểm nổi bật - ALL',
  `termsBenefit` TEXT DEFAULT NULL COMMENT 'Quyền lợi - ALL',
  `termsApplicableObject` TEXT DEFAULT NULL COMMENT 'Đối tượng áp dụng - ALL',
  `termsFeePaymentMethod` TEXT DEFAULT NULL COMMENT 'Phương thức thanh toán - HEALTH, SOCIAL, MEDICAL',
  `termsHospital` TEXT DEFAULT NULL COMMENT 'Bệnh viện - HEALTH, SOCIAL, MEDICAL',
  
  -- =========================================================================
  -- PRODUCT CLASSIFICATION
  -- Dùng cho: ALL
  -- =========================================================================
  `majorName` TEXT DEFAULT NULL COMMENT 'Tên ngành - ALL',
  `majorId` TEXT DEFAULT NULL COMMENT 'ID ngành - ALL',
  `productId` TEXT DEFAULT NULL COMMENT 'ID sản phẩm - ALL',
  `codeFromProvider` TEXT DEFAULT NULL COMMENT 'Mã từ nhà cung cấp - ALL',
  
  -- =========================================================================
  -- PROVIDER INFORMATION
  -- Dùng cho: ALL
  -- =========================================================================
  `companyProvider` TEXT DEFAULT NULL COMMENT 'Mã công ty cung cấp - ALL',
  `companyProviderName` TEXT DEFAULT NULL COMMENT 'Tên công ty cung cấp - ALL',
  
  -- =========================================================================
  -- CONTRACT OBJECT TYPE & PEOPLE INFORMATION
  -- Dùng cho: HEALTH, SOCIAL, MEDICAL (contractObjectType)
  -- Note: TRAVEL có các field riêng (name, dob, gender, etc.)
  -- =========================================================================
  `contractObjectType` INT(11) DEFAULT NULL COMMENT 'Loại đối tượng BH - HEALTH, VEHICLE, SOCIAL, MEDICAL',
  `peopleRelationship` INT(11) DEFAULT NULL COMMENT 'Mối quan hệ - HEALTH, SOCIAL, MEDICAL',
  `peopleName` TEXT DEFAULT NULL COMMENT 'Tên người được BH - HEALTH, SOCIAL, MEDICAL',
  `peopleDob` DATE DEFAULT NULL COMMENT 'Ngày sinh người được BH - HEALTH, SOCIAL, MEDICAL',
  `peopleGender` INT(11) DEFAULT NULL COMMENT 'Giới tính - HEALTH, SOCIAL, MEDICAL',
  `peopleLicense` TEXT DEFAULT NULL COMMENT 'CMND/CCCD - HEALTH, SOCIAL, MEDICAL',
  `peopleLicenseType` INT(11) DEFAULT NULL COMMENT 'Loại giấy tờ - HEALTH, SOCIAL, MEDICAL',
  `peoplePhone` VARCHAR(15) DEFAULT NULL COMMENT 'SĐT - HEALTH, SOCIAL, MEDICAL',
  `peopleEmail` TEXT DEFAULT NULL COMMENT 'Email - HEALTH, SOCIAL, MEDICAL',
  `peopleAddress` TEXT DEFAULT NULL COMMENT 'Địa chỉ - HEALTH, SOCIAL, MEDICAL',
  `peopleDistrictsCode` INT(11) DEFAULT NULL COMMENT 'Mã quận - HEALTH, VEHICLE, SOCIAL, MEDICAL',
  `peopleWardsCode` INT(11) DEFAULT NULL COMMENT 'Mã phường - HEALTH, VEHICLE, SOCIAL, MEDICAL',
  `peopleStreet` TEXT DEFAULT NULL COMMENT 'Đường - HEALTH, VEHICLE, SOCIAL, MEDICAL',
  `peopleHouseNumber` TEXT DEFAULT NULL COMMENT 'Số nhà - HEALTH, VEHICLE, SOCIAL, MEDICAL',
  `peopleCityCode` INT(11) DEFAULT NULL COMMENT 'Mã tỉnh - HEALTH, VEHICLE, SOCIAL, MEDICAL',
  `peopleNote` TEXT DEFAULT NULL COMMENT 'Ghi chú - HEALTH, VEHICLE, SOCIAL, MEDICAL',
  `peopleUpload` MEDIUMTEXT DEFAULT NULL COMMENT 'File upload - HEALTH, VEHICLE, SOCIAL, MEDICAL',
  `peopleLicenseFront` TEXT DEFAULT NULL COMMENT 'Ảnh CMND mặt trước - HEALTH, VEHICLE, SOCIAL, MEDICAL',
  `peopleLicenseBack` TEXT DEFAULT NULL COMMENT 'Ảnh CMND mặt sau - HEALTH, VEHICLE, SOCIAL, MEDICAL',
  `peopleLicenseQr` TEXT DEFAULT NULL COMMENT 'QR CMND - HEALTH, SOCIAL, MEDICAL',
  
  -- =========================================================================
  -- TRAVEL - INSURED PERSON INFORMATION
  -- Dùng cho: TRAVEL, MOTO (người được bảo hiểm)
  -- =========================================================================
  `name` TEXT DEFAULT NULL COMMENT 'Tên người được BH - TRAVEL, MOTO',
  `dob` TEXT DEFAULT NULL COMMENT 'Ngày sinh - TRAVEL, MOTO, HEALTH (contract info)',
  `gender` INT(11) DEFAULT NULL COMMENT 'Giới tính - TRAVEL, MOTO, HEALTH (contract info)',
  `license` TEXT DEFAULT NULL COMMENT 'CMND/CCCD - TRAVEL, MOTO, HEALTH (contract info)',
  `licenseType` INT(11) DEFAULT NULL COMMENT 'Loại giấy tờ - TRAVEL, MOTO, HEALTH (contract info)',
  `licenseFront` TEXT DEFAULT NULL COMMENT 'Ảnh giấy tờ mặt trước - TRAVEL, MOTO',
  `licenseBack` TEXT DEFAULT NULL COMMENT 'Ảnh giấy tờ mặt sau - TRAVEL, MOTO',
  `phone` VARCHAR(15) DEFAULT NULL COMMENT 'SĐT - TRAVEL, MOTO',
  `email` TEXT DEFAULT NULL COMMENT 'Email - TRAVEL, MOTO',
  `address` TEXT DEFAULT NULL COMMENT 'Địa chỉ - TRAVEL, MOTO',
  `districtsCode` INT(11) DEFAULT NULL COMMENT 'Mã quận - TRAVEL, MOTO, HEALTH (contract info)',
  `wardsCode` INT(11) DEFAULT NULL COMMENT 'Mã phường - TRAVEL, MOTO, HEALTH (contract info)',
  `street` TEXT DEFAULT NULL COMMENT 'Đường - TRAVEL, MOTO, HEALTH (contract info)',
  `houseNumber` TEXT DEFAULT NULL COMMENT 'Số nhà - TRAVEL, MOTO',
  `cityCode` INT(11) DEFAULT NULL COMMENT 'Mã tỉnh - TRAVEL, MOTO, HEALTH (contract info)',
  
  -- =========================================================================
  -- CUSTOMER TYPE & GENERAL INFO
  -- Dùng cho: ALL
  -- =========================================================================
  `customerType` INT(11) DEFAULT NULL COMMENT 'Loại khách hàng - ALL',
  `upload` TEXT DEFAULT NULL COMMENT 'File upload - ALL',
  `note` TEXT DEFAULT NULL COMMENT 'Ghi chú - ALL',
  
  -- =========================================================================
  -- AUDIT FIELDS
  -- Dùng cho: ALL
  -- =========================================================================
  `createdAt` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Ngày tạo - ALL',
  `createdBy` TEXT DEFAULT NULL COMMENT 'Người tạo - ALL',
  `modifiedAt` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Ngày cập nhật - ALL',
  `modifiedBy` TEXT DEFAULT NULL COMMENT 'Người cập nhật - ALL',
  `modifiedDate` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Ngày CDC cập nhật - ALL',
  
  -- =========================================================================
  -- MEMBERSHIP & DOCUMENTS
  -- Dùng cho: HEALTH, VEHICLE, SOCIAL, MEDICAL
  -- =========================================================================
  `minDate` INT(11) DEFAULT NULL COMMENT 'Ngày tối thiểu - HEALTH, VEHICLE, SOCIAL, MEDICAL',
  `contractObjectIdPrev` TEXT DEFAULT NULL COMMENT 'ID đối tượng trước - HEALTH, VEHICLE, SOCIAL, MEDICAL',
  `memberId` TEXT DEFAULT NULL COMMENT 'Mã thành viên - HEALTH, VEHICLE, SOCIAL, MEDICAL',
  `contractObjectCardDocument` LONGTEXT COMMENT 'Tài liệu thẻ - HEALTH, VEHICLE, SOCIAL, MEDICAL',
  `contractObjectCardImage` LONGTEXT COMMENT 'Ảnh thẻ - HEALTH, VEHICLE, SOCIAL, MEDICAL',
  `paymentType` INT(11) DEFAULT NULL COMMENT 'Loại thanh toán - HEALTH, VEHICLE, SOCIAL, MEDICAL',
  `document` TEXT DEFAULT NULL COMMENT 'Tài liệu - HEALTH, SOCIAL, MEDICAL',
  
  -- =========================================================================
  -- VEHICLE SPECIFIC FIELDS
  -- Dùng cho: VEHICLE only
  -- =========================================================================
  `vehicleId` TEXT DEFAULT NULL COMMENT 'ID phương tiện - VEHICLE',
  
  -- =========================================================================
  -- MOTO SPECIFIC FIELDS
  -- Dùng cho: MOTO only
  -- =========================================================================
  `licensePlates` TEXT DEFAULT NULL COMMENT 'Biển số xe - MOTO',
  `chassisNumber` TEXT DEFAULT NULL COMMENT 'Số khung - MOTO',
  `engineNumber` TEXT DEFAULT NULL COMMENT 'Số máy - MOTO',
  `maker` TEXT DEFAULT NULL COMMENT 'Hãng xe - MOTO',
  `type` INT(11) DEFAULT NULL COMMENT 'Loại xe - MOTO',
  `line` TEXT DEFAULT NULL COMMENT 'Dòng xe - MOTO',
  `seatNumber` INT(11) DEFAULT NULL COMMENT 'Số chỗ ngồi - MOTO',
  
  -- =========================================================================
  -- TRAVEL SPECIFIC FIELDS
  -- Dùng cho: TRAVEL only
  -- =========================================================================
  `programObject` INT(11) DEFAULT NULL COMMENT 'Đối tượng chương trình - TRAVEL',
  `nationality` TEXT DEFAULT NULL COMMENT 'Quốc tịch - TRAVEL',
  `nationalityId` TEXT DEFAULT NULL COMMENT 'ID quốc tịch - TRAVEL',
  `domesticOrInternational` INT(11) DEFAULT NULL COMMENT 'Trong nước/Quốc tế - TRAVEL',
  `departure` TEXT DEFAULT NULL COMMENT 'Điểm khởi hành - TRAVEL',
  `destination` INT(11) DEFAULT NULL COMMENT 'Điểm đến quốc tế - TRAVEL',
  `destinationDomestic` TEXT DEFAULT NULL COMMENT 'Điểm đến trong nước - TRAVEL',
  `journey` TEXT DEFAULT NULL COMMENT 'Hành trình - TRAVEL',
  `startDateJourney` DATE DEFAULT NULL COMMENT 'Ngày bắt đầu hành trình - TRAVEL',
  `endDateJourney` DATE DEFAULT NULL COMMENT 'Ngày kết thúc hành trình - TRAVEL',
  `programObjectFromProvider` TEXT DEFAULT NULL COMMENT 'Đối tượng từ nhà cung cấp - TRAVEL',
  `destinationFromProvider` TEXT DEFAULT NULL COMMENT 'Điểm đến từ nhà cung cấp - TRAVEL',
  `codePackageFromProvider` TEXT DEFAULT NULL COMMENT 'Mã gói từ nhà cung cấp - TRAVEL',
  `adults` INT(11) DEFAULT NULL COMMENT 'Số người lớn - TRAVEL',
  `children` INT(11) DEFAULT NULL COMMENT 'Số trẻ em - TRAVEL',
  
  -- =========================================================================
  -- TRAVEL - PAYER INFORMATION
  -- Dùng cho: TRAVEL only
  -- =========================================================================
  `payerUserId` TEXT DEFAULT NULL COMMENT 'User ID người trả - TRAVEL',
  `payerName` TEXT DEFAULT NULL COMMENT 'Tên người trả - TRAVEL',
  `payerDob` DATE DEFAULT NULL COMMENT 'Ngày sinh người trả - TRAVEL',
  `payerGender` INT(11) DEFAULT NULL COMMENT 'Giới tính người trả - TRAVEL',
  `payerLicense` TEXT DEFAULT NULL COMMENT 'CMND người trả - TRAVEL',
  `payerLicenseType` INT(11) DEFAULT NULL COMMENT 'Loại giấy tờ người trả - TRAVEL',
  `payerLicenseFront` TEXT DEFAULT NULL COMMENT 'Ảnh CMND mặt trước người trả - TRAVEL',
  `payerLicenseBack` TEXT DEFAULT NULL COMMENT 'Ảnh CMND mặt sau người trả - TRAVEL',
  `payerPhone` VARCHAR(15) DEFAULT NULL COMMENT 'SĐT người trả - TRAVEL',
  `payerEmail` TEXT DEFAULT NULL COMMENT 'Email người trả - TRAVEL',
  `payerAddress` TEXT DEFAULT NULL COMMENT 'Địa chỉ người trả - TRAVEL',
  `payerDistrictsCode` INT(11) DEFAULT NULL COMMENT 'Mã quận người trả - TRAVEL',
  `payerWardsCode` INT(11) DEFAULT NULL COMMENT 'Mã phường người trả - TRAVEL',
  `payerStreet` TEXT DEFAULT NULL COMMENT 'Đường người trả - TRAVEL',
  `payerHouseNumber` TEXT DEFAULT NULL COMMENT 'Số nhà người trả - TRAVEL',
  `payerCityCode` INT(11) DEFAULT NULL COMMENT 'Mã tỉnh người trả - TRAVEL',
  `payerNote` TEXT DEFAULT NULL COMMENT 'Ghi chú người trả - TRAVEL',
  `payerUpload` MEDIUMTEXT DEFAULT NULL COMMENT 'File upload người trả - TRAVEL',
  `payerCustomerType` INT(11) DEFAULT NULL COMMENT 'Loại khách hàng người trả - TRAVEL',
  
  -- =========================================================================
  -- SOCIAL & MEDICAL INSURANCE SPECIFIC FIELDS
  -- Dùng cho: SOCIAL, MEDICAL
  -- =========================================================================
  `declarationType` INT(11) DEFAULT NULL COMMENT 'Loại khai báo - SOCIAL, MEDICAL',
  `remunerationType` INT(11) DEFAULT NULL COMMENT 'Loại thù lao - SOCIAL, MEDICAL',
  `oldCardStartDate` DATE DEFAULT NULL COMMENT 'Ngày bắt đầu thẻ cũ - SOCIAL, MEDICAL',
  `oldCardEndDate` DATE DEFAULT NULL COMMENT 'Ngày kết thúc thẻ cũ - SOCIAL, MEDICAL',
  `renewal` INT(11) DEFAULT NULL COMMENT 'Đóng nối tiếp (1) / Đóng mới (0) - SOCIAL, MEDICAL',
  `socialFamilyId` TEXT DEFAULT NULL COMMENT 'Mã hộ gia đình - SOCIAL, MEDICAL',
  
  -- =========================================================================
  -- SOCIAL INSURANCE SPECIFIC FIELDS
  -- Dùng cho: SOCIAL only
  -- =========================================================================
  `socialId` TEXT DEFAULT NULL COMMENT 'Số BHXH - SOCIAL, MEDICAL',
  `monthlyIncome` DECIMAL(20,0) DEFAULT 0 COMMENT 'Thu nhập hàng tháng - SOCIAL',
  `paymentPeriod` INT(11) DEFAULT NULL COMMENT 'Kỳ hạn đóng BH - SOCIAL',
  `supportBudget` DECIMAL(20,0) DEFAULT 0 COMMENT 'Mức hỗ trợ nhà nước - SOCIAL',
  `oldBhxhCodeUnit` TEXT DEFAULT NULL COMMENT 'Mã đơn vị cấp BHXH kỳ trước - SOCIAL',
  `oldRegisterDate` TEXT DEFAULT NULL COMMENT 'Ngày đăng ký đóng kỳ trước - SOCIAL',
  `percent` DOUBLE DEFAULT NULL COMMENT 'Phần trăm - SOCIAL',
  `discountAmount` DECIMAL(10,0) DEFAULT NULL COMMENT 'Số tiền giảm giá - SOCIAL',
  
  -- =========================================================================
  -- MEDICAL INSURANCE SPECIFIC FIELDS
  -- Dùng cho: MEDICAL only
  -- =========================================================================
  `fiveYearDate` TEXT DEFAULT NULL COMMENT 'Ngày đủ 5 năm liên tục - MEDICAL',
  `medicalId` TEXT DEFAULT NULL COMMENT 'Mã thẻ BHYT (10 số cuối) - MEDICAL',
  `hospitalCode` TEXT DEFAULT NULL COMMENT 'Mã bệnh viện khám - MEDICAL',
  `hospitalName` TEXT DEFAULT NULL COMMENT 'Tên bệnh viện khám - MEDICAL',
  `hospitalCityRegisteredCode` INT(11) DEFAULT NULL COMMENT 'Mã tỉnh bệnh viện - MEDICAL',
  `hospitalCityRegisteredName` TEXT DEFAULT NULL COMMENT 'Tỉnh bệnh viện - MEDICAL',
  `nation` TEXT DEFAULT NULL COMMENT 'Dân tộc - MEDICAL',
  `ethnicity` TEXT DEFAULT NULL COMMENT 'Sắc tộc - MEDICAL',
  
  -- =========================================================================
  -- HAZARD INSURANCE SPECIFIC FIELDS
  -- Dùng cho: HAZARD only
  -- =========================================================================
  `paymentDueDate` DATE DEFAULT NULL COMMENT 'Ngày đến hạn thanh toán - HAZARD',
  `paymentDate` DATE DEFAULT NULL COMMENT 'Ngày thanh toán thực tế - HAZARD',
  `uploadedAt` DATETIME DEFAULT NULL COMMENT 'Thời điểm upload file Excel - HAZARD',
  
  -- =========================================================================
  -- HEALTH (CONTRACT) SPECIFIC FIELDS
  -- Dùng cho: HEALTH only - các field từ contract
  -- =========================================================================
  `thirdPartyRequestId` TEXT DEFAULT NULL COMMENT 'Request ID bên thứ 3 - HEALTH',
  `reqCode` DOUBLE DEFAULT NULL COMMENT 'Mã yêu cầu - HEALTH',
  `contractIdProvider` TEXT DEFAULT NULL COMMENT 'Mã hợp đồng từ nhà cung cấp - HEALTH',
  `contractStatus` INT(11) DEFAULT NULL COMMENT 'Trạng thái hợp đồng - HEALTH',
  `buyHelp` INT(11) DEFAULT NULL COMMENT 'Mua hộ - HEALTH',
  `buyerId` TEXT DEFAULT NULL COMMENT 'ID người mua - HEALTH',
  `contractType` INT(11) DEFAULT NULL COMMENT 'Loại hợp đồng - HEALTH',
  `contractIdRoot` TEXT DEFAULT NULL COMMENT 'ID hợp đồng gốc - HEALTH',
  `companySale` INT(11) DEFAULT NULL COMMENT 'Công ty bán - HEALTH',
  `branchSale` DOUBLE DEFAULT NULL COMMENT 'Chi nhánh bán - HEALTH',
  `branchSaleName` TEXT DEFAULT NULL COMMENT 'Tên chi nhánh bán - HEALTH',
  `companySaleName` TEXT DEFAULT NULL COMMENT 'Tên công ty bán - HEALTH',
  `contractPeriod` INT(11) DEFAULT NULL COMMENT 'Kỳ hạn hợp đồng - HEALTH',
  `contractPeriodValue` INT(11) DEFAULT NULL COMMENT 'Giá trị kỳ hạn - HEALTH',
  `contractStartDate` DATE DEFAULT NULL COMMENT 'Ngày bắt đầu hợp đồng - HEALTH',
  `contractEndDate` DATE DEFAULT NULL COMMENT 'Ngày kết thúc hợp đồng - HEALTH',
  `voucherId` TEXT DEFAULT NULL COMMENT 'ID voucher - HEALTH',
  `voucherCode` TEXT DEFAULT NULL COMMENT 'Mã voucher - HEALTH',
  `amountDiscount` TEXT DEFAULT NULL COMMENT 'Số tiền giảm giá - HEALTH',
  `amount` INT(11) DEFAULT NULL COMMENT 'Số tiền - HEALTH',
  `commission` INT(11) DEFAULT NULL COMMENT 'Hoa hồng - HEALTH',
  `amountPay` INT(11) DEFAULT NULL COMMENT 'Số tiền thanh toán - HEALTH',
  `redBill` INT(11) DEFAULT NULL COMMENT 'Hóa đơn đỏ - HEALTH',
  `paymentMethod` INT(11) DEFAULT NULL COMMENT 'Phương thức thanh toán - HEALTH',
  `reasonCancel` TEXT DEFAULT NULL COMMENT 'Lý do hủy - HEALTH',
  `codeErrorCancel` TEXT DEFAULT NULL COMMENT 'Mã lỗi hủy - HEALTH',
  `messageError` TEXT DEFAULT NULL COMMENT 'Thông báo lỗi - HEALTH',
  `referralCode` TEXT DEFAULT NULL COMMENT 'Mã giới thiệu - HEALTH',
  `saleId` TEXT DEFAULT NULL COMMENT 'ID sale - HEALTH',
  `bonusAmount` TEXT DEFAULT NULL COMMENT 'Số tiền thưởng - HEALTH',
  `fromLead` TEXT DEFAULT NULL COMMENT 'Từ lead - HEALTH',
  `source` INT(11) DEFAULT NULL COMMENT 'Nguồn - HEALTH',
  `outsideCreatedAt` DATETIME DEFAULT NULL COMMENT 'Ngày tạo bên ngoài - HEALTH',
  `outsidePaymentAt` DATETIME DEFAULT NULL COMMENT 'Ngày thanh toán bên ngoài - HEALTH',
  `outsidePaymentId` TEXT DEFAULT NULL COMMENT 'ID thanh toán bên ngoài - HEALTH',
  `channelId` TEXT DEFAULT NULL COMMENT 'ID kênh - HEALTH',
  `levelId` TEXT DEFAULT NULL COMMENT 'ID cấp độ - HEALTH',
  `certFile` TEXT DEFAULT NULL COMMENT 'File chứng chỉ - HEALTH',
  `orderNumber` TEXT DEFAULT NULL COMMENT 'Số đơn hàng - HEALTH',
  
  -- Duplicate fields from stgContractObject (có vẻ là lỗi trong schema gốc)
  `userId_1` TEXT DEFAULT NULL COMMENT 'userId duplicate - HEALTH',
  `contractId_2` TEXT DEFAULT NULL COMMENT 'contractId duplicate - HEALTH',
  `contractObjectType_3` INT(11) DEFAULT NULL COMMENT 'contractObjectType duplicate - HEALTH',
  `customerType_4` INT(11) DEFAULT NULL COMMENT 'customerType duplicate - HEALTH',
  `upload_5` TEXT DEFAULT NULL COMMENT 'upload duplicate - HEALTH',
  `createdAt_7` TEXT DEFAULT NULL COMMENT 'createdAt duplicate - HEALTH',
  `modifiedAt_9` TEXT DEFAULT NULL COMMENT 'modifiedAt duplicate - HEALTH',
  
  -- =========================================================================
  -- INDEXES & CONSTRAINTS
  -- =========================================================================
  PRIMARY KEY (`offline_id`),
  INDEX `idx_insuranceType` (`insuranceType`),
  INDEX `idx_contractId` (`contractId`(50)),
  INDEX `idx_userId` (`userId`(50)),
  INDEX `idx_modifiedDate` (`modifiedDate`),
  INDEX `idx_packageName` (`packageName`(100)),
  INDEX `idx_contractStatus` (`contractStatus`),
  INDEX `idx_createdAt` (`createdAt`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Wide table tổng hợp tất cả loại bảo hiểm offline contract';

-- ============================================================================
-- NOTES:
-- ============================================================================
-- 1. Field `insuranceType` dùng để phân biệt loại bảo hiểm:
--    - 'HEALTH': BH Sức khỏe (stgContractObject)
--    - 'VEHICLE': BH Ô tô (stgContractObjectVehicle)
--    - 'TRAVEL': BH Du lịch (stgContractObjectTravel)
--    - 'MOTO': BH Xe máy (stgContractObjectMoto)
--    - 'SOCIAL': BH Xã hội (stgContractObjectSocialInsurance)
--    - 'MEDICAL': BH Y tế (stgContractObjectMedicalInsurance)
--    - 'HAZARD': BH Rủi ro (stgContractObjectHazard) - Excel upload
--
-- 2. Các field có comment "ALL" được sử dụng bởi tất cả loại BH
--
-- 3. Các field có tên khác nhau nhưng ý nghĩa giống nhau đã được gộp:
--    - contractObjectId / id -> contractObjectId
--    - contractObjectIdDisplay / idDisplay -> contractObjectIdDisplay
--    - contractObjectStartDate / startDate -> contractObjectStartDate
--    - contractObjectEndDate / endDate -> contractObjectEndDate
--    - contractObjectIdProvider / idProvider -> contractObjectIdProvider
--    - contractObjectUrl / url -> contractObjectUrl
--
-- 4. TRAVEL và MOTO có 2 bộ field cho người được BH:
--    - Các field `people*` (dùng cho HEALTH, SOCIAL, MEDICAL, VEHICLE)
--    - Các field không prefix (name, dob, gender...) dùng cho TRAVEL, MOTO
--
-- 5. HEALTH có rất nhiều field từ contract (các field liên quan đến sale, payment, etc.)
--    mà các loại BH khác không có
--
-- 6. Một số field duplicate (_1, _2, etc.) trong stgContractObject có vẻ là lỗi schema
--    nhưng được giữ lại để đảm bảo không mất dữ liệu
--
-- 7. Khuyến nghị khi insert data:
--    - Luôn set `insuranceType` để dễ query và filter
--    - NULL các field không áp dụng cho loại BH đó
--    - Validate data trước khi insert để đảm bảo field mapping đúng
--
-- ============================================================================
-- END OF FILE
-- ============================================================================
