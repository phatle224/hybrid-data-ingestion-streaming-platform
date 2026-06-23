"""
Base mapping class - Abstract base for insurance type mappings.
Mirrors backend configs/mappings/base_mapping.py exactly.

Design Pattern: Template Method Pattern
- Define skeleton of algorithm in base class
- Let subclasses override specific steps
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class BaseInsuranceMapping(ABC):
    """
    Abstract base class for insurance type column mappings.
    Defines common fields and structure that all insurance types must have.
    """

    # ==================== COMMON FIELDS (All insurance types) ====================
    COMMON_DB_FIELDS = {
        'contractId': str,
        'majorName': str,
        'companyProviderName': str,
        'programName': str,
        'saleId': str,
        'channelId': str,
        'termsFeePaymentMethod': str,
        'feeInsurance': float,
        'modifiedAt': str,
    }

    # Business keys for duplicate checking (4-key combination)
    BUSINESS_KEYS = ['contractId', 'peopleName', 'majorName', 'companyProviderName']

    # Required fields = Business Keys
    BASE_REQUIRED_FIELDS = ['contractId', 'peopleName', 'majorName', 'companyProviderName']

    def __init__(self):
        self._column_mapping: Optional[Dict[str, str]] = None
        self._insurance_type: Optional[str] = None

    @property
    def column_mapping(self) -> Dict[str, str]:
        """Lazy load column mapping."""
        if self._column_mapping is None:
            self._column_mapping = self._build_column_mapping()
        return self._column_mapping

    @property
    def insurance_type(self) -> str:
        """Get insurance type identifier."""
        if self._insurance_type is None:
            self._insurance_type = self.get_insurance_type()
        return self._insurance_type

    def _build_column_mapping(self) -> Dict[str, str]:
        """Build complete column mapping by merging common and specific mappings."""
        mapping = {}
        mapping.update(self.get_common_column_mapping())
        mapping.update(self.get_specific_column_mapping())
        return mapping

    # ==================== ABSTRACT METHODS ====================

    @abstractmethod
    def get_insurance_type(self) -> str:
        """Get the insurance type identifier (TRAVEL, VEHICLE, etc.)."""
        pass

    @abstractmethod
    def get_specific_column_mapping(self) -> Dict[str, str]:
        """Get Excel column to DB field mapping specific to this insurance type."""
        pass

    @abstractmethod
    def get_specific_fields(self) -> List[str]:
        """Get database fields specific to this insurance type."""
        pass

    @abstractmethod
    def get_required_fields(self) -> List[str]:
        """Get required fields for this insurance type."""
        pass

    # ==================== COMMON METHODS ====================

    def get_common_column_mapping(self) -> Dict[str, str]:
        """
        Get common column mappings shared by all insurance types.
        Override this if your type has different Vietnamese headers.
        """
        return {
            'Sản phẩm': 'majorName',
            'Channel': 'channelId',
            'Hình thức thanh toán': 'termsFeePaymentMethod',
        }

    def get_name_field(self) -> str:
        """
        Get the field name used for 'name' in business key.
        """
        return 'peopleName'

    @classmethod
    def get_file_keywords(cls) -> List[str]:
        """Get filename keywords that identify this insurance type."""
        return []

    # ==================== UTILITY METHODS ====================

    def get_all_db_fields(self) -> List[str]:
        """Get all database fields for this insurance type."""
        common = list(self.COMMON_DB_FIELDS.keys())
        specific = self.get_specific_fields()
        return list(set(common + specific))

    def get_business_key_values(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Extract business key values from record for duplicate checking."""
        name_field = self.get_name_field()
        return {
            'contractId': record.get('contractId'),
            'peopleName': record.get('peopleName') or record.get(name_field),
            'majorName': record.get('majorName'),
            'companyProviderName': record.get('companyProviderName'),
        }

    def validate_required_fields(self, record: Dict[str, Any]) -> tuple:
        """
        Validate that all required fields (4 business keys) are present and not empty.

        Returns:
            Tuple of (is_valid, list_of_error_details)
        """
        errors = []

        for field in ['contractId', 'majorName', 'companyProviderName']:
            value = record.get(field)
            excel_col = self._get_excel_column_for_field(field)

            if value is None:
                errors.append({
                    'field': field,
                    'excel_column': excel_col,
                    'error_type': 'MISSING',
                    'message': f"Thiếu dữ liệu tại cột '{excel_col}' (field: {field})",
                    'current_value': None,
                })
            elif isinstance(value, str) and not value.strip():
                errors.append({
                    'field': field,
                    'excel_column': excel_col,
                    'error_type': 'EMPTY',
                    'message': f"Dữ liệu trống tại cột '{excel_col}' (field: {field})",
                    'current_value': value,
                })

        # Check name field
        name_field = self.get_name_field()
        name_value = record.get('peopleName') or record.get(name_field)
        excel_col = self._get_excel_column_for_field(name_field)

        if not name_value:
            errors.append({
                'field': name_field,
                'excel_column': excel_col,
                'error_type': 'MISSING',
                'message': f"Thiếu tên khách hàng tại cột '{excel_col}'",
                'current_value': None,
            })
        elif isinstance(name_value, str) and not name_value.strip():
            errors.append({
                'field': name_field,
                'excel_column': excel_col,
                'error_type': 'EMPTY',
                'message': f"Tên khách hàng trống tại cột '{excel_col}'",
                'current_value': name_value,
            })

        return (len(errors) == 0, errors)

    def _get_excel_column_for_field(self, db_field: str) -> str:
        """Reverse lookup: get Excel column name from database field name."""
        for excel_col, field in self.column_mapping.items():
            if field == db_field:
                return excel_col.replace('\n', ' ')
        return db_field

    def get_field_display_name(self, db_field: str) -> str:
        """Get human-readable display name for a database field (Vietnamese)."""
        display_names = {
            'contractId': 'Số hợp đồng/Số GCN/Mã tờ khai',
            'name': 'Họ và tên người được BH',
            'peopleName': 'Tên khách hàng/Họ tên NĐBH',
            'majorName': 'Sản phẩm (Loại BH)',
            'companyProviderName': 'Đối tác nhà bảo hiểm',
            'contractObjectStartDate': 'Ngày bắt đầu hiệu lực',
            'contractObjectEndDate': 'Ngày kết thúc hiệu lực',
            'feeInsurance': 'Phí bảo hiểm',
            'feeMainBenefit': 'Phí bảo hiểm chính',
        }
        return display_names.get(db_field, db_field)

    def map_excel_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Map a single Excel row to database fields."""
        mapped_row = {}

        for excel_col, db_field in self.column_mapping.items():
            if excel_col in row:
                value = row[excel_col]
                if isinstance(value, str):
                    value = value.strip() if value else None
                mapped_row[db_field] = value

        mapped_row['insuranceType'] = self.insurance_type

        # Ensure 'peopleName' field exists
        if 'peopleName' not in mapped_row or not mapped_row.get('peopleName'):
            name_field = self.get_name_field()
            if name_field in mapped_row:
                mapped_row['peopleName'] = mapped_row[name_field]

        return mapped_row

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(type={self.insurance_type})"
