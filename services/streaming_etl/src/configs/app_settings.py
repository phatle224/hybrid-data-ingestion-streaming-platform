"""
Application settings for ETL consumer.
Mirrors backend configs/app/settings.py pattern.
"""
from typing import Set


class AppSettings:
    """ETL application settings - mirrors backend AppSettings pattern."""

    def __init__(self):
        self.app_name = "Affina CDC ETL Consumer"
        self.version = "1.0.0"

        # Database table names
        self.staging_table = "stgContractObjectOffline"

        # Business logic settings
        self.duplicate_check_keys = ["contractId", "name", "majorName", "companyProviderName"]
        self.required_fields = ["contractId", "name", "majorName", "companyProviderName"]

        # Insurance types
        self.insurance_types = [
            'TRAVEL', 'VEHICLE', 'MOTO', 'SOCIAL', 'MEDICAL',
            'HEALTH', 'HAZARD', 'HOUSE',
        ]

        # Table routing (insurance type → staging table)
        self.staging_table_mapping = {
            'TRAVEL': 'stgContractObjectOffline',
            'VEHICLE': 'stgContractObjectOffline',
            'MOTO': 'stgContractObjectOffline',
            'SOCIAL': 'stgContractObjectOffline',
            'MEDICAL': 'stgContractObjectOffline',
            'HEALTH': 'stgContractObjectOffline',
            'HAZARD': 'stgContractObjectOffline',
            'HOUSE': 'stgContractObjectHouse',
        }

        # Valid database schema columns (from stgContractObjectOffline table)
        # Only these columns can be inserted into database
        # Matches backend AppSettings.valid_db_columns exactly
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


# Global settings instance (singleton pattern, matches backend)
app_settings = AppSettings()
