"""
Health insurance mapping configuration
Inherits from BaseInsuranceMapping
"""
from typing import Dict, List, Any
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
        """Override common mapping for Health-specific Vietnamese headers"""
        return {
            'Ngày cập nhật': 'modifiedAt',
            'STT': 'row_number',
            'Sản phẩm': 'majorName',
            'Số hợp đồng': 'contractId',
            'Nhà bảo hiểm': 'companyProviderName',
            'Code sale': 'saleId',
            'Chương trình\nbảo hiểm': 'programName',
            'Channel': 'programCodeMiningChannel',
            'Hình thức \nthanh toán': 'termsFeePaymentMethod',
            'Phí bảo hiểm': 'feeInsurance',
        }
    
    def get_specific_column_mapping(self) -> Dict[str, str]:
        """Health-specific Excel column mapping"""
        return {
            # Insured Person Info (with multiline headers)
            'Thông tin \nNgười được bảo hiểm': 'peopleName',
            'Ngày tháng\nnăm sinh': 'peopleDob',
            'Giới tính': 'peopleGender',
            'Email': 'peopleEmail',
            'Passport': 'passport',
            'CCCD': 'peopleLicense',
            'Địa chỉ liên hệ': 'peopleAddress',
            
            # Payer Info (Bên mua BH)
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
            'Ngày hiệu lực': 'contractStartDate',
            'Ngày kết thúc': 'contractEndDate',
            'Số GCNBH': 'certificateNumberProvider',
            
            # Other Info
            'Thông tin xuất hóa đơn': 'invoiceInfo',
            'Phone trên lead': 'leadPhone',
            'Phone\nKhách hàng': 'customerPhone',
            'Tên liên hệ': 'contactName',
            'NOTE': 'note',
        }
    
    def get_specific_fields(self) -> List[str]:
        """Fields specific to health insurance"""
        return [
            'peopleName', 'peopleDob', 'peopleGender', 'peopleEmail',
            'passport', 'peopleLicense', 'peopleAddress',
            'payerName', 'payerDob', 'payerLicense', 'payerPhone',
            'payerAddress', 'payerEmail', 'peopleRelationship',
            'outpatient_benefit', 'dental_benefit', 'maternity_benefit',
            'topup_benefit', 'feeInsurance', 'feeAdjustment', 'amountPay',
            'contractStartDate', 'contractEndDate',
            'payment_date', 'certificateNumberProvider',
            'invoiceInfo', 'leadPhone', 'customerPhone', 'contactName', 'note',
        ]
    
    def get_required_fields(self) -> List[str]:
        """Required fields for health insurance validation"""
        return [
            'contractId', 'peopleName', 'programName', 'companyProviderName',
            'contractStartDate', 'contractEndDate',
            'peopleDob', 'peopleGender', 'payerName', 'peopleRelationship',
            'payerPhone', 'payerEmail', 'feeInsurance',
            'amountPay', 'payment_date', 'saleId', 'programCodeMiningChannel',
            'termsFeePaymentMethod',
        ]
        
    def validate_required_fields(self, record: Dict[str, Any]) -> tuple[bool, List[Dict[str, Any]]]:
        """Override to validate all specifically required fields for Health"""
        is_valid, errors = super().validate_required_fields(record)
        
        health_required = [
            'contractStartDate', 'contractEndDate',
            'peopleDob', 'peopleGender',
            'payerName', 'peopleRelationship', 'payerPhone', 'payerEmail',
            'programName', 'feeInsurance', 'amountPay', 'payment_date',
            'saleId', 'programCodeMiningChannel', 'termsFeePaymentMethod'
        ]
        
        for field in health_required:
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
                
        # 1 trong 2 không được null (CCCD hoặc Passport)
        pp_license = record.get('peopleLicense')
        pp_passport = record.get('passport')
        def is_empty(val):
            return val is None or (isinstance(val, str) and not val.strip())
            
        if is_empty(pp_license) and is_empty(pp_passport):
            errors.append({
                'field': 'peopleLicense',
                'excel_column': 'CCCD / Passport NĐBH',
                'error_type': 'MISSING',
                'message': "Either CCCD or Passport must be provided for the insured person",
                'current_value': None
            })
                
        return (len(errors) == 0, errors)
    
    def get_name_field(self) -> str:
        """Health uses 'peopleName' for insured person"""
        return 'peopleName'
    
    @classmethod
    def get_file_keywords(cls) -> List[str]:
        return ["health", "suc khoe", "suckhoe", "suc_khoe"]
