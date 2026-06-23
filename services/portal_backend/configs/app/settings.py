"""
Application settings module
"""
import os
from typing import List, Set


class AppSettings:
    """Application settings class"""
    
    def __init__(self):
        self.app_name = "Affina Portal CDC"
        self.version = "1.0.0"
        self.debug = os.getenv("DEBUG", "True") == "True"
        
        # CORS settings
        # In production, set CORS_ORIGINS env variable to restrict origins
        # e.g., CORS_ORIGINS=https://portal.affina.vn,https://admin.affina.vn
        cors_env = os.getenv("CORS_ORIGINS", "")
        if cors_env:
            self.cors_origins: List[str] = [o.strip() for o in cors_env.split(",") if o.strip()]
        else:
            # Development defaults
            self.cors_origins: List[str] = [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:3001",
                "http://127.0.0.1:3001",
                "http://localhost:3010",
                "http://127.0.0.1:3010",
                "*",  # WARNING: Remove in production by setting CORS_ORIGINS env var
            ]
        
        # Upload settings
        self.upload_folder = "uploads"
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_extensions = [".xlsx", ".xls"]
        
        # Database table names
        self.staging_table = "stgContractObjectOffline"
        
        # Business logic settings
        self.duplicate_check_keys = ["contractId", "peopleName", "majorName", "companyProviderName", "startDate", "endDate", "feeInsurance"]
        self.required_fields = ["contractId", "peopleName", "majorName", "companyProviderName"]
        
        # Valid database schema columns (from stgContractObjectOffline table)
        # Only these columns can be inserted into database
        self.valid_db_columns: Set[str] = {
            'contractObjectId', 'contractObjectIdDisplay', 'insuranceType', 'cardNumber',
            'certificateNumberProvider', 'accountTPA', 'userId', 'contractId', 'contractIdDisplay',
            'contractObjectSmeStatus', 'contractIndividualStatus', 'contractObjectStartDate',
            'contractObjectEndDate', 'contractObjectIdProvider', 'contractObjectUrl',
            'programTypeName', 'programTypeId', 'programId', 'programName', 'packageId',
            'packageName', 'packageCodeFromProvider', 'programCodeMiningChannel', 'programDocument',
            'fromAge', 'toAge', 'feeMainBenefit', 'feeSideBenefit', 'feeInsurance', 'maximumAmount',
            'preVatFeeMainBenefit', 'vatFeeMainBenefit', 'preVatFeeSideBenefit', 'vatFeeSideBenefit',
            'preVatFeeInsurance', 'vatFeeInsurance', 'termsId', 'termsHighlight', 'termsBenefit',
            'termsApplicableObject', 'termsFeePaymentMethod', 'termsHospital', 'majorName', 'majorId',
            'productId', 'codeFromProvider', 'companyProvider', 'companyProviderName',
            'contractObjectType', 'peopleRelationship', 'peopleName', 'peopleDob', 'peopleGender',
            'peopleLicense', 'peopleLicenseType', 'peoplePhone', 'peopleEmail', 'peopleAddress',
            'peopleDistrictsCode', 'peopleWardsCode', 'peopleStreet', 'peopleHouseNumber',
            'peopleCityCode', 'peopleNote', 'peopleUpload', 'peopleLicenseFront', 'peopleLicenseBack',
            'peopleLicenseQr', 'name', 'dob', 'gender', 'license', 'licenseType', 'licenseFront',
            'licenseBack', 'phone', 'email', 'address', 'districtsCode', 'wardsCode', 'street',
            'houseNumber', 'cityCode', 'customerType', 'upload', 'note', 'createdAt', 'createdBy',
            'modifiedAt', 'modifiedBy', 'modifiedDate', 'minDate', 'contractObjectIdPrev',
            'memberId', 'contractObjectCardDocument', 'contractObjectCardImage', 'paymentType',
            'document', 'vehicleId', 'licensePlates', 'chassisNumber', 'engineNumber', 'maker',
            'type', 'line', 'seatNumber', 'programObject', 'nationality', 'nationalityId',
            'domesticOrInternational', 'departure', 'destination', 'destinationDomestic', 'journey',
            'startDateJourney', 'endDateJourney', 'programObjectFromProvider', 'destinationFromProvider',
            'codePackageFromProvider', 'adults', 'children', 'payerUserId', 'payerName', 'payerDob',
            'payerGender', 'payerLicense', 'payerLicenseType', 'payerLicenseFront', 'payerLicenseBack',
            'payerPhone', 'payerEmail', 'payerAddress', 'payerDistrictsCode', 'payerWardsCode',
            'payerStreet', 'payerHouseNumber', 'payerCityCode', 'payerNote', 'payerUpload',
            'payerCustomerType', 'declarationType', 'remunerationType', 'oldCardStartDate',
            'oldCardEndDate', 'renewal', 'socialFamilyId', 'socialId', 'monthlyIncome', 'paymentPeriod',
            'supportBudget', 'oldBhxhCodeUnit', 'oldRegisterDate', 'percent', 'discountAmount',
            'fiveYearDate', 'medicalId', 'hospitalCode', 'hospitalName', 'hospitalCityRegisteredCode',
            'hospitalCityRegisteredName', 'nation', 'ethnicity', 'thirdPartyRequestId', 'reqCode',
            'contractIdProvider', 'contractStatus', 'buyHelp', 'buyerId', 'contractType',
            'contractIdRoot', 'companySale', 'branchSale', 'branchSaleName', 'companySaleName',
            'contractPeriod', 'contractPeriodValue', 'contractStartDate', 'contractEndDate',
            'voucherId', 'voucherCode', 'amountDiscount', 'amount', 'commission', 'amountPay',
            'redBill', 'paymentMethod', 'reasonCancel', 'codeErrorCancel', 'messageError',
            'referralCode', 'saleId', 'bonusAmount', 'fromLead', 'source', 'outsideCreatedAt',
            'outsidePaymentAt', 'outsidePaymentId', 'channelId', 'levelId', 'certFile', 'orderNumber',
        }


# Global settings instance
app_settings = AppSettings()
