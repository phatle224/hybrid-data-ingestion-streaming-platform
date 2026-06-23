"""
Moto insurance mapping configuration.
Mirrors backend configs/mappings/moto_mapping.py
"""
from typing import Dict, List
from configs.mappings.base_mapping import BaseInsuranceMapping


class MotoMapping(BaseInsuranceMapping):
    """
    Moto Insurance (Xe máy) - Moto.xlsx

    Specific characteristics:
    - Has vehicle info (license plates, chassis, engine)
    - Has main benefit + side benefit fees
    - Uses uppercase Vietnamese headers
    """

    def get_insurance_type(self) -> str:
        return "MOTO"

    def get_common_column_mapping(self) -> Dict[str, str]:
        return {
            'Ngày update': 'modifiedAt',
            'Sản phẩm': 'majorName',
            'Số hợp đồng': 'contractId',
            'Đối tác nhà bảo hiểm': 'companyProviderName',
            'Code sale': 'saleId',
            'Chương trình': 'programName',
            'Channel': 'channelId',
            'Hình thức thanh toán': 'termsFeePaymentMethod',
            'TỔNG PHÍ BẢO HIỂM': 'feeInsurance',
        }

    def get_specific_column_mapping(self) -> Dict[str, str]:
        return {
            # Vehicle Info
            'BIỂN SỐ XE': 'licensePlates',
            'SỐ KHUNG': 'chassisNumber',
            'SỐ MÁY': 'engineNumber',
            'NHÃN HIỆU XE': 'maker',

            # Owner Info
            'TÊN KHÁCH HÀNG': 'peopleName',
            'SỐ ĐIẸN THOẠI': 'peoplePhone',
            'Email': 'peopleEmail',

            # Fee Info
            'PHÍ BẢO HIỂM TNDS BẮT BUỘC': 'feeMainBenefit',
            'PHÍ BẢO HIỂM TAI NẠN NNTX': 'feeSideBenefit',
            'SỐ NĂM': 'contractPeriodValue',

            # Contract Info
            'NGÀY CẤP ĐƠN': 'issue_date',
            'NGÀY BẮT ĐẦU': 'contractObjectStartDate',
            'NGÀY KẾT THÚC': 'contractObjectEndDate',
        }

    def get_specific_fields(self) -> List[str]:
        return [
            'peopleName', 'peoplePhone', 'peopleEmail',
            'licensePlates', 'chassisNumber', 'engineNumber',
            'vehicleType', 'maker',
            'feeMainBenefit', 'feeSideBenefit', 'contractPeriodValue',
            'contractObjectStartDate', 'contractObjectEndDate',
            'issue_date',
        ]

    def get_required_fields(self) -> List[str]:
        return []  # All required validation via business keys

    def get_name_field(self) -> str:
        return 'peopleName'

    @classmethod
    def get_file_keywords(cls) -> List[str]:
        return ["moto", "xe may", "xemay", "xe_may"]
