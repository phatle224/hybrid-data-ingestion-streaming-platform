"""
Travel insurance mapping configuration
Inherits from BaseInsuranceMapping
"""
from typing import Dict, List, Any
from configs.mappings.base_mapping import BaseInsuranceMapping


class TravelMapping(BaseInsuranceMapping):
    """
    Travel Insurance (Du lịch) - Travel.xlsx
    
    Specific characteristics:
    - Has journey dates (startDateJourney, endDateJourney)
    - Has destination and scope (domestic/international)
    - Has payer information separate from insured person
    """
    
    def get_insurance_type(self) -> str:
        return "TRAVEL"
    
    def get_common_column_mapping(self) -> Dict[str, str]:
        """Override common mapping for Travel-specific Vietnamese headers"""
        return {
            'Ngày': 'upload_date',
            'Sản phẩm': 'programName',
            'Số hợp đồng': 'contractId',
            'Đối tác nhà BH': 'companyProviderName',
            'Tên sale': 'saleId',
            'Channel': 'programCodeMiningChannel',
            'Hình thức thanh toán': 'termsFeePaymentMethod',
            'Phí bảo hiểm': 'feeInsurance',
        }
    
    def get_specific_column_mapping(self) -> Dict[str, str]:
        """Travel-specific Excel column mapping"""
        return {
            # Insured Person Info → people* fields
            'Họ Và Tên': 'peopleName',
            'Ngày sinh': 'peopleDob',
            'CCCD/CMND/Pasport ID': 'peopleLicense',      # With 'r'
            'CCCD/CMND/Paspost ID': 'peopleLicense',      # Without 'r' (typo in some Excel files)
            
            # Journey Info
            'Ngày thanh toán': 'payment_date',
            'Ngày đi': 'startDateJourney',
            'Ngày về': 'endDateJourney',
            'Số ngày': 'journey_days',
            'Nơi đến': 'destination_text',
            'Phạm vi': 'domesticOrInternational_text',
            
            # Program Info
            'Gói tham gia': 'packageName',
            'Plan tham gia': 'packageName',
            
            # Payer Info (người mua BH)
            'Họ tên người mua': 'payerName',
            'Ngày sinh.1': 'payerDob',
            'CCCD/CMND/Pasport ID người mua': 'payerLicense',   # With 'r'
            'CCCD/CMND/Paspost ID người mua': 'payerLicense',   # Without 'r' (typo)
            'Số Điện thoại NMBH': 'payerPhone',
        }
    
    def get_specific_fields(self) -> List[str]:
        """Fields specific to travel insurance"""
        return [
            'peopleName', 'peopleDob', 'peopleLicense',
            'startDateJourney', 'endDateJourney', 'journey_days',
            'destination_text', 'domesticOrInternational_text',
            'packageName',
            'payerName', 'payerDob', 'payerLicense', 'payerPhone',
            'payment_date', 'upload_date',
        ]
    
    def get_required_fields(self) -> List[str]:
        """Required fields for travel insurance validation (updated null rules)."""
        return [
            'contractId', 'peopleName', 'programName', 'companyProviderName',
            'peopleDob', 'peopleLicense',
            'payerName', 'payerLicense',
            'startDateJourney', 'endDateJourney', 'journey_days',
            'feeInsurance', 'payment_date', 'packageName',
            'saleId', 'programCodeMiningChannel', 'termsFeePaymentMethod'
        ]

    def validate_required_fields(self, record: Dict[str, Any]) -> tuple[bool, List[Dict[str, Any]]]:
        """Override to validate Travel required fields with detailed error output."""
        is_valid, errors = super().validate_required_fields(record)

        for field in self.get_required_fields():
            if field in ['contractId', 'peopleName', 'majorName', 'companyProviderName']:
                continue

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
        """Travel uses 'payerName' for buyer; peopleName (insured) is the business key"""
        return 'payerName'
    
    @classmethod
    def get_file_keywords(cls) -> List[str]:
        return ["travel", "du lich", "dulich", "du_lich"]
