"""
Medical & Social insurance mapping configuration.
Mirrors backend configs/mappings/medical_social_mapping.py
"""
from typing import Dict, List
from configs.mappings.base_mapping import BaseInsuranceMapping


class MedicalSocialMapping(BaseInsuranceMapping):
    """
    Medical & Social Insurance (BHYT & BHXH) - Medical-Social.xlsx

    Specific characteristics:
    - Contains both BHYT (Medical) and BHXH (Social) insurance
    - Has detailed payer info (Bên mua BH)
    - Has social security ID (Mã BHXH)
    - Uses 'Mã tờ khai' as contractId
    """

    def get_insurance_type(self) -> str:
        return "MEDICAL_SOCIAL"

    def get_common_column_mapping(self) -> Dict[str, str]:
        return {
            'Ngày update': 'modifiedAt',
            'Sản phẩm': 'majorName',
            'Mã tờ khai': 'contractId',
            'Đối tác NBH': 'companyProviderName',
            'Code sales': 'saleId',
            'Channel': 'channelId',
            'Phí Bảo hiểm': 'feeInsurance',
            'Hình thức thanh toán': 'termsFeePaymentMethod',
        }

    def get_specific_column_mapping(self) -> Dict[str, str]:
        return {
            # Insured Person Info
            'Họ tên NĐBH': 'peopleName',
            'Ngày sinh': 'peopleDob',
            'Giới tính': 'peopleGender',
            'CCCD': 'peopleLicense',
            'Địa chỉ': 'peopleAddress',
            'SĐT': 'peoplePhone',
            'Email': 'peopleEmail',

            # Payer Info
            'Họ tên BMBH': 'payerName',
            'Ngày sinh.1': 'payerDob',
            'CCCD.1': 'payerLicense',
            'Mối quan hệ với NĐBH': 'peopleRelationship',
            'Địa chỉ.1': 'payerAddress',
            'SĐT ': 'payerPhone',  # Note: trailing space
            'Email.1': 'payerEmail',

            # Insurance Info
            'Mã BHXH': 'socialId',
            'Loại sản phẩm': 'insuranceType_text',
            'Phương án KH': 'packageName',

            # Contract Info
            'Ngày thanh toán': 'payment_date',
            'Ngày bắt đầu': 'contractObjectStartDate',
            'Ngày kết thúc': 'contractObjectEndDate',
            'Ngày duyệt': 'approval_date',
            'Ngày hoàn phí': 'refund_date',
            'Trạng thái': 'contractStatus_text',

            # Contact Info
            'Phone Khách hàng': 'customerPhone',
            'Tên liên hệ': 'contactName',
            'Sản phẩm (cũ_có ràng dữ liệu)': 'productName_old',
            'Phương án thù lao': 'remunerationType_text',
        }

    def get_specific_fields(self) -> List[str]:
        return [
            'peopleName', 'peopleDob', 'peopleGender', 'peopleLicense',
            'peopleAddress', 'peoplePhone', 'peopleEmail',
            'payerName', 'payerDob', 'payerLicense', 'payerAddress',
            'payerPhone', 'payerEmail', 'peopleRelationship',
            'socialId', 'insuranceType_text', 'packageName',
            'contractObjectStartDate', 'contractObjectEndDate',
            'payment_date', 'approval_date', 'refund_date',
            'contractStatus_text', 'customerPhone', 'contactName',
            'productName_old', 'remunerationType_text',
        ]

    def get_required_fields(self) -> List[str]:
        return []  # All required validation via business keys

    def get_name_field(self) -> str:
        return 'peopleName'

    @classmethod
    def get_file_keywords(cls) -> List[str]:
        return ["medical", "social", "bhyt", "bhxh", "medical-social", "medical_social"]
