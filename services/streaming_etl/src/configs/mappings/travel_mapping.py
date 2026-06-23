"""
Travel insurance mapping configuration.
Mirrors backend configs/mappings/travel_mapping.py
"""
from typing import Dict, List
from configs.mappings.base_mapping import BaseInsuranceMapping


class TravelMapping(BaseInsuranceMapping):
    """
    Travel Insurance (Du lịch) - Travel.xlsx

    Specific characteristics:
    Specific characteristics:
    - Has journey dates (contractObjectStartDate, contractObjectEndDate)
    - Has destination and scope (domestic/international)
    - Has payer information separate from insured person
    """

    def get_insurance_type(self) -> str:
        return "TRAVEL"

    def get_common_column_mapping(self) -> Dict[str, str]:
        return {
            'Ngày': 'upload_date',
            'Sản phẩm': 'majorName',
            'Số hợp đồng': 'contractId',
            'Đối tác nhà BH': 'companyProviderName',
            'Tên sale': 'saleId',
            'Channel': 'channelId',
            'Hình thức thanh toán': 'termsFeePaymentMethod',
            'Phí bảo hiểm': 'feeInsurance',
        }

    def get_specific_column_mapping(self) -> Dict[str, str]:
        return {
            # Insured Person Info
            'Họ Và Tên': 'peopleName',
            'Ngày sinh': 'peopleDob',
            'CCCD/CMND/Pasport ID': 'peopleLicense',
            'CCCD/CMND/Paspost ID': 'peopleLicense',  # Typo variant

            # Journey Info
            'Ngày thanh toán': 'payment_date',
            'Ngày đi': 'contractObjectStartDate',
            'Ngày về': 'contractObjectEndDate',
            'Số ngày': 'journey_days',
            'Nơi đến': 'destination_text',
            'Phạm vi': 'domesticOrInternational_text',

            # Program Info
            'Gói tham gia': 'packageName',
            'Plan tham gia': 'programName',

            # Payer Info
            'Họ tên người mua': 'payerName',
            'Ngày sinh.1': 'payerDob',
            'CCCD/CMND/Pasport ID người mua': 'payerLicense',
            'CCCD/CMND/Paspost ID người mua': 'payerLicense',  # Typo variant
            'Số Điện thoại NMBH': 'payerPhone',
        }

    def get_specific_fields(self) -> List[str]:
        return [
            'peopleName', 'peopleDob', 'peopleLicense',
            'contractObjectStartDate', 'contractObjectEndDate', 'journey_days',
            'destination_text', 'domesticOrInternational_text',
            'packageName',
            'payerName', 'payerDob', 'payerLicense', 'payerPhone',
            'payment_date', 'upload_date',
        ]

    def get_required_fields(self) -> List[str]:
        return []  # All required validation via business keys

    def get_name_field(self) -> str:
        return 'peopleName'

    @classmethod
    def get_file_keywords(cls) -> List[str]:
        return ["travel", "du lich", "dulich", "du_lich"]
