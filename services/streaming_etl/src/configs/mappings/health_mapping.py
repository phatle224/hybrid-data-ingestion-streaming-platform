"""
Health insurance mapping configuration.
Mirrors backend configs/mappings/health_mapping.py
"""
from typing import Dict, List
from configs.mappings.base_mapping import BaseInsuranceMapping


class HealthMapping(BaseInsuranceMapping):
    """
    Health Insurance (Sức khỏe) - Health.xlsx

    Specific characteristics:
    - Has detailed benefit info (outpatient, dental, maternity, topup)
    - Has certificate number (Số GCNBH)
    - Has invoice info
    - Uses multiline Vietnamese headers
    """

    def get_insurance_type(self) -> str:
        return "HEALTH"

    def get_common_column_mapping(self) -> Dict[str, str]:
        return {
            'Ngày cập nhật': 'modifiedAt',
            'Sản phẩm': 'majorName',
            'Số hợp đồng': 'contractId',
            'Nhà bảo hiểm': 'companyProviderName',
            'Code sale': 'saleId',
            'Chương trình\nbảo hiểm': 'programName',
            'Channel': 'channelId',
            'Hình thức thanh toán': 'termsFeePaymentMethod',
            'Phí bảo hiểm': 'feeInsurance',
        }

    def get_specific_column_mapping(self) -> Dict[str, str]:
        return {
            # Insured Person Info (with multiline headers)
            'Thông tin \nNgười được bảo hiểm': 'peopleName',
            'Ngày tháng\nnăm sinh': 'peopleDob',
            'Giới tính': 'peopleGender',
            'Email': 'peopleEmail',
            'Passport': 'passport',
            'CCCD': 'peopleLicense',
            'Địa chỉ liên hệ': 'peopleAddress',

            # Payer Info
            'Thông tin \nBên mua bảo hiểm': 'payerName',
            'Mối quan hệ\nđối với NĐBH': 'peopleRelationship',
            'Ngày tháng\nnăm sinh.1': 'payerDob',
            'CCCD/Passport': 'payerLicense',
            'Số điện thoại': 'payerPhone',
            'Địa chỉ liên hệ.1': 'payerAddress',
            'Email.1': 'payerEmail',

            # Benefits Info
            'Ngoại trú': 'outpatient_benefit',
            'Nha khoa': 'dental_benefit',
            'Thai sản': 'maternity_benefit',
            'Top-up': 'topup_benefit',
            'Phí điều chỉnh': 'feeAdjustment',
            'Số tiền\nthanh toán': 'amountPay',

            # Contract Info
            'Ngày thanh toán': 'payment_date',
            'Ngày hiệu lực': 'contractObjectStartDate',
            'Ngày kết thúc': 'contractObjectEndDate',
            'Số GCNBH': 'certificateNumberProvider',

            # Other Info
            'Thông tin xuất hóa đơn': 'invoiceInfo',
            'Phone trên lead': 'leadPhone',
            'Phone\nKhách hàng': 'customerPhone',
            'Tên liên hệ': 'contactName',
            'NOTE': 'note',
        }

    def get_specific_fields(self) -> List[str]:
        return [
            'peopleName', 'peopleDob', 'peopleGender', 'peopleEmail',
            'passport', 'peopleLicense', 'peopleAddress',
            'payerName', 'payerDob', 'payerLicense', 'payerPhone',
            'payerAddress', 'payerEmail', 'peopleRelationship',
            'outpatient_benefit', 'dental_benefit', 'maternity_benefit',
            'topup_benefit', 'feeInsurance', 'feeAdjustment', 'amountPay',
            'contractObjectStartDate', 'contractObjectEndDate',
            'payment_date', 'certificateNumberProvider',
            'invoiceInfo', 'leadPhone', 'customerPhone', 'contactName', 'note',
        ]

    def get_required_fields(self) -> List[str]:
        return []  # All required validation via business keys

    def get_name_field(self) -> str:
        return 'peopleName'

    @classmethod
    def get_file_keywords(cls) -> List[str]:
        return ["health", "suc khoe", "suckhoe", "suc_khoe"]
