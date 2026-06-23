"""
Base processor interface - Abstract base for insurance type processors.
Mirrors backend services/processors/base_processor.py.

Design Pattern: Strategy Pattern + Template Method Pattern
"""
import logging
from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any
import pandas as pd
from models.contract_model import ContractRecord
from configs.mappings.base_mapping import BaseInsuranceMapping

logger = logging.getLogger(__name__)


class IInsuranceProcessor(ABC):
    """
    Interface/Abstract Base Class for insurance type processors.

    Design Patterns Used:
    - Strategy Pattern: Different processing strategies per insurance type
    - Template Method: process_file() defines the algorithm skeleton

    How to extend:
    1. Create new mapping class inheriting from BaseInsuranceMapping
    2. Create new processor class inheriting from IInsuranceProcessor
    3. Register in processors/__init__.py PROCESSOR_REGISTRY
    """

    def __init__(self, mapping: BaseInsuranceMapping):
        self._mapping = mapping
        self._insurance_type = mapping.insurance_type

    @property
    def mapping(self) -> BaseInsuranceMapping:
        return self._mapping

    @property
    def insurance_type(self) -> str:
        return self._insurance_type

    # ==================== ABSTRACT METHODS ====================

    @abstractmethod
    def pre_process(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pre-process DataFrame before transformation.
        Override for type-specific preprocessing.
        """
        pass

    @abstractmethod
    def post_process(self, records: List[ContractRecord]) -> List[ContractRecord]:
        """
        Post-process records after transformation.
        Override for type-specific post-processing.
        """
        pass

    # ==================== TEMPLATE METHODS ====================

    def parse_excel(self, file_path: str) -> pd.DataFrame:
        """Parse Excel file and rename columns using mapping."""
        df = pd.read_excel(file_path)

        logger.info(
            "[%s] Read %d rows, %d columns from Excel",
            self.insurance_type, len(df), len(df.columns)
        )

        # Rename columns using mapping
        df = df.rename(columns=self.mapping.column_mapping)

        return df

    def transform_records(self, df: pd.DataFrame) -> List[ContractRecord]:
        """Transform DataFrame to ContractRecord objects."""
        records = []

        # Date field names that need conversion
        date_fields = [
            'modifiedAt', 'contractObjectStartDate', 'contractObjectEndDate',
            'payment_date', 'startDateJourney', 'endDateJourney',
            'contractStartDate', 'contractEndDate', 'outsidePaymentAt',
            'dob', 'peopleDob', 'payerDob', 'upload_date',
            'issue_date', 'approval_date', 'refund_date',
        ]

        # Numeric fields
        numeric_fields = [
            'feeInsurance', 'feeMainBenefit', 'feeSideBenefit',
            'totalFee', 'amountPay', 'amount',
        ]

        for _, row in df.iterrows():
            row_dict = {}
            for col, value in row.items():
                if pd.notna(value):
                    if isinstance(value, str):
                        value = value.strip() if value else None
                        if value:
                            if col in numeric_fields:
                                value = self._parse_numeric_string(value)
                            elif col in date_fields:
                                value = self._parse_date_string(value)
                    row_dict[col] = value

            # Add insurance type
            row_dict['insuranceType'] = self.insurance_type

            # Ensure 'name' field exists
            name_field = self.mapping.get_name_field()
            if 'name' not in row_dict or not row_dict.get('name'):
                if name_field in row_dict:
                    row_dict['name'] = row_dict[name_field]

            record = ContractRecord(row_dict)
            records.append(record)

        return records

    def _parse_numeric_string(self, value: str) -> Any:
        """Parse numeric string with thousand separators to float."""
        if not value or not isinstance(value, str):
            return value
        try:
            # Vietnamese format: "2.980.800" → 2980800
            cleaned = value.replace('.', '').replace(',', '.')
            return float(cleaned)
        except (ValueError, AttributeError):
            return value

    def _parse_date_string(self, value: str) -> Any:
        """Parse date string from DD/MM/YYYY to YYYY-MM-DD format for MySQL."""
        if not value or not isinstance(value, str):
            return value
        try:
            if '/' in value and len(value.split('/')) == 3:
                parts = value.split('/')
                if len(parts[0]) <= 2:  # DD/MM/YYYY
                    day, month, year = parts
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            return value
        except (ValueError, AttributeError, IndexError):
            return value

    def validate_records(
        self,
        records: List[ContractRecord],
    ) -> Tuple[List[ContractRecord], List[Dict[str, Any]]]:
        """
        Validate records using mapping's validation rules.
        Returns detailed error information.

        Returns:
            Tuple of (valid_records, detailed_errors)
        """
        valid_records = []
        detailed_errors = []

        for idx, record in enumerate(records, start=1):
            row_number = idx + 1  # Excel row (accounting for header)

            # Model-level validation
            is_valid, error_msg = record.validate()

            if is_valid:
                # Mapping-level validation with detailed errors
                record_dict = record.to_dict()
                is_valid, field_errors = self.mapping.validate_required_fields(record_dict)

                if not is_valid:
                    detailed_errors.append({
                        'row': row_number,
                        'excel_row': row_number,
                        'error_count': len(field_errors),
                        'field_errors': field_errors,
                        'record_preview': {
                            'contractId': record_dict.get('contractId', '(trống)'),
                            'name': record_dict.get('name') or record_dict.get('peopleName', '(trống)'),
                            'majorName': record_dict.get('majorName', '(trống)'),
                            'companyProviderName': record_dict.get('companyProviderName', '(trống)'),
                        },
                    })
            else:
                record_dict = record.to_dict()
                detailed_errors.append({
                    'row': row_number,
                    'excel_row': row_number,
                    'error_count': 1,
                    'field_errors': [{
                        'field': 'model_validation',
                        'excel_column': 'N/A',
                        'error_type': 'VALIDATION_FAILED',
                        'message': error_msg,
                        'current_value': None,
                    }],
                    'record_preview': {
                        'contractId': record_dict.get('contractId', '(trống)'),
                        'name': record_dict.get('name') or record_dict.get('peopleName', '(trống)'),
                        'majorName': record_dict.get('majorName', '(trống)'),
                        'companyProviderName': record_dict.get('companyProviderName', '(trống)'),
                    },
                })

            if is_valid:
                valid_records.append(record)

        return valid_records, detailed_errors

    def get_validation_summary(
        self,
        total_records: int,
        valid_count: int,
        errors: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Generate professional validation summary."""
        error_by_field = {}
        for error in errors:
            for field_error in error.get('field_errors', []):
                field = field_error.get('field', 'unknown')
                if field not in error_by_field:
                    error_by_field[field] = {
                        'field': field,
                        'display_name': self.mapping.get_field_display_name(field),
                        'excel_column': field_error.get('excel_column', 'N/A'),
                        'count': 0,
                        'sample_rows': [],
                    }
                error_by_field[field]['count'] += 1
                if len(error_by_field[field]['sample_rows']) < 5:
                    error_by_field[field]['sample_rows'].append(error.get('row'))

        return {
            'total_records': total_records,
            'valid_records': valid_count,
            'invalid_records': len(errors),
            'success_rate': f"{(valid_count / total_records * 100):.1f}%" if total_records > 0 else "0%",
            'error_summary_by_field': list(error_by_field.values()),
            'all_errors': errors,
            'first_10_errors': errors[:10],
            'has_more_errors': len(errors) > 10,
            'insurance_type': self.insurance_type,
        }

    def process_file(
        self,
        file_path: str,
    ) -> Tuple[List[ContractRecord], List[Dict[str, Any]]]:
        """
        Complete processing workflow using Template Method Pattern.

        Algorithm skeleton:
        1. Parse Excel file
        2. Pre-process DataFrame (type-specific hook)
        3. Transform to ContractRecord objects
        4. Post-process records (type-specific hook)
        5. Validate records

        Returns:
            Tuple of (valid_records, detailed_errors)
        """
        # Step 1: Parse Excel
        df = self.parse_excel(file_path)

        # Step 2: Pre-process (type-specific hook)
        df = self.pre_process(df)

        # Step 3: Transform to records
        records = self.transform_records(df)

        # Step 4: Post-process (type-specific hook)
        records = self.post_process(records)

        # Step 5: Validate
        valid_records, errors = self.validate_records(records)

        return valid_records, errors

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(type={self.insurance_type})"
