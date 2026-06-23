"""
Hazard insurance mapping configuration
Inherits from BaseInsuranceMapping
"""
from typing import Dict, List, Any
from configs.mappings.base_mapping import BaseInsuranceMapping


class HazardMapping(BaseInsuranceMapping):
    """
    Hazard Insurance (Bảo hiểm rủi ro) - Hazard.xlsx
    
    Specific characteristics:
    - Offline-only insurance type (not in source database)
    - Uses 'peopleName' for customer name
    - Field 'Trạng thái' maps to termsFeePaymentMethod
    - Stores in stgContractObjectOffline (same as other types)
    """
    
    def get_insurance_type(self) -> str:
        return "HAZARD"
    
    def get_common_column_mapping(self) -> Dict[str, str]:
        """Override common mapping for Hazard-specific Vietnamese headers"""
        return {
            'Ngày cập nhật': 'modifiedAt',
            'Mã hợp đồng': 'contractId',
            'Sản phẩm': 'programName',
            'Đối tác nhà bảo hiểm': 'companyProviderName',
            'Code sale': 'saleId',
            'Channel': 'programCodeMiningChannel',
            # Trạng thái maps to termsFeePaymentMethod (text field)
            'Trạng thái': 'termsFeePaymentMethod',
        }
    
    def get_specific_column_mapping(self) -> Dict[str, str]:
        """Hazard-specific Excel column mapping"""
        return {
            # Customer/Buyer Info → payer* fields
            'Tên khách hàng': 'payerName',
            
            # Financial Info
            'Số tiền thanh toán': 'feeInsurance',
            
            # Contract Dates
            'Ngày bắt đầu': 'contractObjectStartDate',
            'Ngày kết thúc': 'contractObjectEndDate',
            
            # Payment Info
            'Ngày thanh toán': 'payment_date',
            
            # Note - RATE_BONUS and NOTE combined or separate
            'NOTE': 'note',
        }
    
    def get_specific_fields(self) -> List[str]:
        """Fields specific to hazard insurance"""
        return [
            'payerName',
            'feeInsurance',
            'contractObjectStartDate', 'contractObjectEndDate',
            'payment_date',
            'termsFeePaymentMethod',
            'note',
        ]
    
    def get_required_fields(self) -> List[str]:
        """Required fields for hazard insurance validation"""
        return [
            'contractId', 'peopleName', 'programName', 'companyProviderName',
            'feeInsurance',
            'contractObjectStartDate', 'contractObjectEndDate',
            'payment_date',
            'saleId', 'programCodeMiningChannel'
        ]

    def validate_required_fields(self, record: Dict[str, Any]) -> tuple[bool, List[Dict[str, Any]]]:
        """Override to validate all specifically required fields for Hazard."""
        is_valid, errors = super().validate_required_fields(record)

        hazard_required = [
            'feeInsurance',
            'contractObjectStartDate', 'contractObjectEndDate',
            'payment_date',
            'saleId', 'programCodeMiningChannel'
        ]

        for field in hazard_required:
            value = record.get(field)
            excel_col = self._get_excel_column_for_field(field)

            if value is None:
                errors.append({
                    'field': field,
                    'excel_column': excel_col,
                    'error_type': 'MISSING',
                    'message': f"Thiếu dữ liệu tại cột '{excel_col}' (bắt buộc)",
                    'current_value': None
                })
            elif isinstance(value, str) and not value.strip():
                errors.append({
                    'field': field,
                    'excel_column': excel_col,
                    'error_type': 'EMPTY',
                    'message': f"Dữ liệu trống tại cột '{excel_col}' (bắt buộc)",
                    'current_value': value
                })

        return (len(errors) == 0, errors)
    
    def get_name_field(self) -> str:
        """Hazard uses 'payerName' for customer/buyer (mirrored to peopleName for business key)"""
        return 'payerName'
    
    @classmethod
    def get_file_keywords(cls) -> List[str]:
        return ["hazard", "rui ro", "ruiro", "rủi ro", "bao hiem rui ro"]
