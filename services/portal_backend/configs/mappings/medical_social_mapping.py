"""
Medical & Social insurance mapping configuration
Inherits from BaseInsuranceMapping
"""
from typing import Dict, List, Any
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
        """Override common mapping for Medical-Social-specific Vietnamese headers"""
        return {
            'Ngày update': 'modifiedAt',
            'Sản phẩm': 'programName',
            'Loại sản phẩm': 'majorName',
            'Mã tờ khai': 'contractId',  # Mã tờ khai = Mã hợp đồng
            'Đối tác NBH': 'companyProviderName',
            'Code sales': 'saleId',
            'Channel': 'programCodeMiningChannel',
            'Phí Bảo hiểm': 'feeInsurance',
            'Hình thức thanh toán': 'termsFeePaymentMethod',
        }
    
    def get_specific_column_mapping(self) -> Dict[str, str]:
        """Medical-Social-specific Excel column mapping"""
        return {
            # Insured Person Info (Người được BH)
            'Họ tên NĐBH': 'peopleName',
            'Ngày sinh': 'peopleDob',
            'Giới tính': 'peopleGender',
            'CCCD': 'peopleLicense',
            'Địa chỉ': 'peopleAddress',
            'SĐT': 'peoplePhone',
            'Email': 'peopleEmail',
            
            # Payer Info (Bên mua BH)
            'Họ tên BMBH': 'payerName',
            'Ngày sinh.1': 'payerDob',
            'CCCD.1': 'payerLicense',
            'Mối quan hệ với NĐBH': 'peopleRelationship',
            'Địa chỉ.1': 'payerAddress',
            'SĐT ': 'payerPhone',  # Note: có space sau SĐT
            'Email.1': 'payerEmail',
            
            # Insurance Info
            'Mã BHXH': 'socialId',
            'Phương án KH': 'renewal',
            
            # Contract Info
            'Ngày thanh toán': 'payment_date',
            'Ngày bắt đầu': 'contractObjectStartDate',
            'Ngày kết thúc': 'contractObjectEndDate',
            'Trạng thái': 'contractStatus',
        }
    
    def get_specific_fields(self) -> List[str]:
        """Fields specific to medical-social insurance"""
        return [
            'peopleName', 'peopleDob', 'peopleGender', 'peopleLicense',
            'peopleAddress', 'peoplePhone', 'peopleEmail',
            'payerName', 'payerDob', 'payerLicense', 'payerAddress',
            'payerPhone', 'payerEmail', 'peopleRelationship',
            'socialId', 'renewal',
            'contractObjectStartDate', 'contractObjectEndDate',
            'payment_date', 'contractStatus',
        ]
    
    def get_required_fields(self) -> List[str]:
        """Required fields based on Medical-Social null table."""
        return [
            'contractId',
            'peopleName',
            'majorName',
            'companyProviderName',
            'peopleDob',
            'peopleGender',
            'peopleLicense',
            'peopleAddress',
            'peopleRelationship',
            'socialId',
            'renewal',
            'feeInsurance',
            'payment_date',
            'contractObjectStartDate',
            'contractObjectEndDate',
            'saleId',
            'programCodeMiningChannel',
            'termsFeePaymentMethod',
        ]

    def validate_required_fields(self, record: Dict[str, Any]) -> tuple[bool, List[Dict[str, Any]]]:
        """Validate all required fields from the Medical-Social null table."""
        errors: List[Dict[str, Any]] = []

        for field in self.get_required_fields():
            value = record.get(field)
            excel_col = self._get_excel_column_for_field(field)

            if value is None:
                errors.append({
                    'field': field,
                    'excel_column': excel_col,
                    'error_type': 'MISSING',
                    'message': f"Missing data in column '{excel_col}' (required)",
                    'current_value': None,
                })
                continue

            if isinstance(value, str) and not value.strip():
                errors.append({
                    'field': field,
                    'excel_column': excel_col,
                    'error_type': 'EMPTY',
                    'message': f"Empty data in column '{excel_col}' (required)",
                    'current_value': value,
                })

        return (len(errors) == 0, errors)
    
    def get_name_field(self) -> str:
        """Medical-Social uses 'payerName' for buyer; peopleName (insured) is the business key"""
        return 'payerName'
    
    @classmethod
    def get_file_keywords(cls) -> List[str]:
        return ["medical", "social", "bhyt", "bhxh", "medical-social", "medical_social"]
