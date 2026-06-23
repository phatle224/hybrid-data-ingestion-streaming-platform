"""
Hazard insurance mapping configuration.
Mirrors backend configs/mappings/hazard_mapping.py
"""
from typing import Dict, List
from configs.mappings.base_mapping import BaseInsuranceMapping


class HazardMapping(BaseInsuranceMapping):
    """
    Hazard Insurance (Bảo hiểm rủi ro) - Hazard.xlsx

    Specific characteristics:
    - Offline-only insurance type
    - Uses 'peopleName' for customer name
    - Field 'Trạng thái' maps to termsFeePaymentMethod
    """

    def get_insurance_type(self) -> str:
        return "HAZARD"

    def get_common_column_mapping(self) -> Dict[str, str]:
        return {
            'Ngày cập nhật': 'modifiedAt',
            'Mã hợp đồng': 'contractId',
            'Sản phẩm': 'majorName',
            'Đối tác nhà bảo hiểm': 'companyProviderName',
            'Code sale': 'saleId',
            'Channel': 'channelId',
            'Trạng thái': 'termsFeePaymentMethod',
        }

    def get_specific_column_mapping(self) -> Dict[str, str]:
        return {
            # Customer Info
            'Tên khách hàng': 'peopleName',

            # Financial Info
            'Số tiền thanh toán': 'feeInsurance',

            # Contract Dates
            'Ngày bắt đầu': 'contractObjectStartDate',
            'Ngày kết thúc': 'contractObjectEndDate',

            # Payment Info
            'Ngày thanh toán': 'outsidePaymentAt',

            # Note
            'NOTE': 'note',
        }

    def get_specific_fields(self) -> List[str]:
        return [
            'peopleName',
            'feeInsurance',
            'contractObjectStartDate', 'contractObjectEndDate',
            'outsidePaymentAt',
            'termsFeePaymentMethod',
            'note',
        ]

    def get_required_fields(self) -> List[str]:
        return []  # All required validation via business keys

    def get_name_field(self) -> str:
        return 'peopleName'

    @classmethod
    def get_file_keywords(cls) -> List[str]:
        return ["hazard", "rui ro", "ruiro", "rủi ro", "bao hiem rui ro"]
