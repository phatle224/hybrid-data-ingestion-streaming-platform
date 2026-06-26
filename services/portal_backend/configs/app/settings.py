"""
Application settings module
"""
import os
from typing import List, Set


class AppSettings:
    """Application settings class"""
    
    def __init__(self):
        self.app_name = "InsuStream Portal CDC"
        self.version = "1.0.0"
        self.debug = os.getenv("DEBUG", "True") == "True"
        
        # CORS settings
        # In production, set CORS_ORIGINS env variable to restrict origins
        # e.g., CORS_ORIGINS=https://portal.insustream.vn,https://admin.insustream.vn
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
        self.staging_table = "stgInsuranceContractObjectOffline"
        
        # Business logic settings
        self.duplicate_check_keys = ["contractId", "peopleName", "majorName", "companyProviderName", "startDate", "endDate", "feeInsurance"]
        self.required_fields = ["contractId", "peopleName", "majorName", "companyProviderName"]
        
        # Valid database schema columns (from stgInsuranceContractObjectOffline table)
        # Only these columns can be inserted into database
        self.valid_db_columns: Set[str] = {
            # ── Metadata chung ──────────────────────────────────────────────
            'insuranceType', 'contractId', 'majorName', 'programName',
            'companyProviderName', 'companyProvider',
            'saleId', 'programCodeMiningChannel', 'termsFeePaymentMethod',
            'modifiedAt',

            # ── Phí bảo hiểm ────────────────────────────────────────────────
            'feeInsurance', 'feeMainBenefit', 'feeSideBenefit',
            'feeAdjustment', 'amountPay', 'payment_date',

            # ── Thông tin hợp đồng chung ────────────────────────────────────
            'contractObjectStartDate', 'contractObjectEndDate',
            'contractStartDate', 'contractEndDate',
            'contractPeriodValue', 'certificateNumberProvider', 'contractStatus',

            # ── Người được bảo hiểm (people*) ───────────────────────────────
            'peopleName', 'peopleDob', 'peopleGender',
            'peopleLicense', 'passport',
            'peoplePhone', 'peopleEmail', 'peopleAddress', 'peopleRelationship',

            # ── Người mua bảo hiểm (payer*) ─────────────────────────────────
            'payerName', 'payerDob', 'payerGender',
            'payerLicense', 'payerPhone', 'payerEmail', 'payerAddress',

            # ── HEALTH — quyền lợi & liên hệ ────────────────────────────────
            'outpatient_benefit', 'dental_benefit', 'maternity_benefit',
            'topup_benefit', 'invoiceInfo',
            'leadPhone', 'customerPhone', 'contactName',

            # ── VEHICLE — xe ô tô ────────────────────────────────────────────
            'licensePlate', 'chassisNumber', 'engineNumber',
            'vehicleType', 'brand', 'vehicleValue',
            'usagePurpose', 'manufactureYear', 'seatNumber', 'insurance_days',

            # ── MOTO — xe máy ────────────────────────────────────────────────
            'licensePlates', 'maker', 'packageName', 'issue_date',

            # ── TRAVEL — chuyến đi ───────────────────────────────────────────
            'startDateJourney', 'endDateJourney', 'journey_days',
            'destination_text', 'domesticOrInternational_text', 'upload_date',

            # ── MEDICAL_SOCIAL ───────────────────────────────────────────────
            'socialId', 'renewal',

            # ── Audit ────────────────────────────────────────────────────────
            'createdAt', 'createdBy', 'modifiedDate',
        }


# Global settings instance
app_settings = AppSettings()
