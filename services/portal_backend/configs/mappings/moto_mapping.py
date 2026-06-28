"""
Moto insurance mapping configuration
Inherits from BaseInsuranceMapping
"""
from typing import Dict, List, Any
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
        """Override common mapping for Moto-specific Vietnamese headers"""
        return {
            'Ngày update': 'modifiedAt',
            'Sản phẩm': 'majorName',
            'Số hợp đồng': 'contractId',
            'Đối tác nhà bảo hiểm': 'companyProviderName',
            'Code sale': 'saleId',
            'Chương trình': 'programName',
            'Channel': 'programCodeMiningChannel',
            'Hình thức thanh toán': 'termsFeePaymentMethod',
            'TỔNG PHÍ BẢO HIỂM': 'feeInsurance',
        }
    
    def get_specific_column_mapping(self) -> Dict[str, str]:
        """Moto-specific Excel column mapping"""
        return {
            # Vehicle Info
            'BIỂN SỐ XE': 'licensePlates',
            'SỐ KHUNG': 'chassisNumber',
            'SỐ MÁY': 'engineNumber',
            'LOẠI XE': 'packageName',
            'NHÃN HIỆU XE': 'maker',
            
            # Owner/Buyer Info → payer* fields
            'TÊN KHÁCH HÀNG': 'payerName',
            'SỐ ĐIỆN THOẠI': 'payerPhone',
            'SỐ ĐIẸN THOẠI': 'payerPhone',
            'Email': 'payerEmail',
            
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
        """Fields specific to moto insurance"""
        return [
            'payerName', 'payerPhone', 'payerEmail',
            'licensePlates', 'chassisNumber', 'engineNumber',
            'packageName', 'maker',
            'feeMainBenefit', 'feeSideBenefit', 'contractPeriodValue',
            'contractObjectStartDate', 'contractObjectEndDate',
            'issue_date',
        ]
    
    def get_required_fields(self) -> List[str]:
        """Required fields for moto insurance validation"""
        return [
            'contractId', 'peopleName', 'programName', 'companyProviderName',
            'payerName', 'payerPhone', 'payerEmail',
            'feeInsurance',
            'contractObjectStartDate', 'contractObjectEndDate',
            'saleId', 'programCodeMiningChannel', 'termsFeePaymentMethod'
        ]

    def validate_required_fields(self, record: Dict[str, Any]) -> tuple[bool, List[Dict[str, Any]]]:
        """Validate required fields for Moto based on null table summary."""
        is_valid, errors = super().validate_required_fields(record)

        moto_required = [
            'payerName', 'payerPhone', 'payerEmail',
            'feeInsurance',
            'contractObjectStartDate', 'contractObjectEndDate',
            'saleId', 'programCodeMiningChannel', 'termsFeePaymentMethod'
        ]

        for field in moto_required:
            value = record.get(field)
            excel_col = self._get_excel_column_for_field(field)

            if value is None:
                errors.append({
                    'field': field,
                    'excel_column': excel_col,
                    'error_type': 'MISSING',
                    'message': f"Missing data in column '{excel_col}' (required)",
                    'current_value': None
                })
            elif isinstance(value, str) and not value.strip():
                errors.append({
                    'field': field,
                    'excel_column': excel_col,
                    'error_type': 'EMPTY',
                    'message': f"Empty data in column '{excel_col}' (required)",
                    'current_value': value
                })

        return (len(errors) == 0, errors)
    
    def get_name_field(self) -> str:
        """Moto uses 'payerName' for owner/buyer (mirrored to peopleName for business key)"""
        return 'payerName'
    
    @classmethod
    def get_file_keywords(cls) -> List[str]:
        return ["moto", "xe may", "xemay", "xe_may"]
