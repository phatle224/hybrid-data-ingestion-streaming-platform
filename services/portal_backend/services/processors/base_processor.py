"""
Base processor interface - Abstract base for insurance type processors
Design Pattern: Strategy Pattern + Template Method Pattern
"""
from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any, Optional
import pandas as pd
from models.contract_model import ContractRecord
from configs.mappings.base_mapping import BaseInsuranceMapping


class IInsuranceProcessor(ABC):
    """
    Interface/Abstract Base Class for insurance type processors
    
    Design Patterns Used:
    - Strategy Pattern: Different processing strategies for different insurance types
    - Template Method: process_file() defines the algorithm skeleton
    
    How to extend:
    1. Create new mapping class inheriting from BaseInsuranceMapping
    2. Create new processor class inheriting from IInsuranceProcessor
    3. Register in ProcessorFactory
    """
    
    def __init__(self, mapping: BaseInsuranceMapping):
        """
        Initialize processor with mapping configuration
        
        Args:
            mapping: Insurance type mapping instance
        """
        self._mapping = mapping
        self._insurance_type = mapping.insurance_type
    
    @property
    def mapping(self) -> BaseInsuranceMapping:
        """Get mapping configuration"""
        return self._mapping
    
    @property
    def insurance_type(self) -> str:
        """Get insurance type identifier"""
        return self._insurance_type
    
    # ==================== ABSTRACT METHODS (Must be implemented) ====================
    
    @abstractmethod
    def pre_process(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pre-process DataFrame before transformation
        Override for type-specific preprocessing (e.g., clean headers, remove empty rows)
        
        Args:
            df: Raw DataFrame from Excel
            
        Returns:
            Preprocessed DataFrame
        """
        pass
    
    @abstractmethod
    def post_process(self, records: List[ContractRecord]) -> List[ContractRecord]:
        """
        Post-process records after transformation
        Override for type-specific post-processing (e.g., derived fields)
        
        Args:
            records: List of ContractRecord
            
        Returns:
            Post-processed list of ContractRecord
        """
        pass
    
    # ==================== TEMPLATE METHODS (Common implementation) ====================
    
    def parse_excel(self, file_path: str) -> pd.DataFrame:
        """
        Parse Excel file and return DataFrame
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            Parsed DataFrame with columns renamed according to mapping
        """
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # DEBUG: Print original columns
        print(f"\n{'='*80}")
        print(f"DEBUG [{self.insurance_type}] - Original Excel columns:")
        for i, col in enumerate(df.columns):
            print(f"  [{i}] '{col}' (type: {type(col).__name__}, repr: {repr(col)})")
        print(f"{'='*80}\n")
        
        # Rename columns using mapping
        df = df.rename(columns=self.mapping.column_mapping)
        
        # DEBUG: Print renamed columns
        print(f"\n{'='*80}")
        print(f"DEBUG [{self.insurance_type}] - Renamed columns:")
        for i, col in enumerate(df.columns):
            print(f"  [{i}] '{col}'")
        print(f"{'='*80}\n")
        
        return df
    
    def transform_records(self, df: pd.DataFrame) -> List[ContractRecord]:
        """
        Transform DataFrame to ContractRecord objects
        
        Args:
            df: Parsed DataFrame
            
        Returns:
            List of ContractRecord objects
        """
        records = []
        
        # Date field names that need conversion
        date_fields = [
            'modifiedAt', 'contractObjectStartDate', 'contractObjectEndDate',
            'payment_date', 'startDateJourney', 'endDateJourney',
            'contractStartDate', 'contractEndDate', 'outsidePaymentAt',
            'dob', 'peopleDob', 'payerDob', 'upload_date',
            'issue_date', 'approval_date', 'refund_date'
        ]
        
        for _, row in df.iterrows():
            # Convert row to dictionary and clean NaN values
            row_dict = {}
            for col, value in row.items():
                if pd.notna(value):
                    # Clean string values
                    if isinstance(value, str):
                        value = value.strip() if value else None
                        if value:
                            # Parse numeric strings with thousand separators (e.g., "2.980.800")
                            if col in ['feeInsurance', 'feeMainBenefit', 'feeSideBenefit', 
                                       'totalFee', 'amountPay', 'amount']:
                                value = self._parse_numeric_string(value)
                            # Parse date strings (DD/MM/YYYY -> YYYY-MM-DD)
                            elif col in date_fields:
                                value = self._parse_date_string(value)
                    row_dict[col] = value
            
            # Add insurance type
            row_dict['insuranceType'] = self.insurance_type
            
            # Ensure 'peopleName' field exists for business key.
            # For VEHICLE/MOTO/HAZARD: name_field='payerName', copy to peopleName
            # For HEALTH/MEDICAL_SOCIAL/TRAVEL: peopleName mapped directly from Excel
            name_field = self.mapping.get_name_field()
            if 'peopleName' not in row_dict or not row_dict.get('peopleName'):
                if name_field in row_dict and name_field != 'peopleName':
                    row_dict['peopleName'] = row_dict[name_field]
            
            # Create ContractRecord
            record = ContractRecord(row_dict)
            records.append(record)
        
        return records
    
    def _parse_numeric_string(self, value: str) -> any:
        """Parse numeric string with thousand separators to float"""
        if not value or not isinstance(value, str):
            return value
        try:
            # Remove thousand separators (dots in Vietnamese format)
            # "2.980.800" -> "2980800"
            cleaned = value.replace('.', '').replace(',', '.')
            return float(cleaned)
        except (ValueError, AttributeError):
            return value
    
    def _parse_date_string(self, value: str) -> any:
        """Parse date string from DD/MM/YYYY to YYYY-MM-DD format for MySQL"""
        if not value or not isinstance(value, str):
            return value
        try:
            # Try DD/MM/YYYY format (Vietnamese Excel format)
            if '/' in value and len(value.split('/')) == 3:
                parts = value.split('/')
                if len(parts[0]) <= 2:  # DD/MM/YYYY
                    day, month, year = parts
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            # Return as-is if already in correct format or unrecognized
            return value
        except (ValueError, AttributeError, IndexError):
            return value
    
    def validate_records(
        self, 
        records: List[ContractRecord]
    ) -> Tuple[List[ContractRecord], List[Dict[str, Any]]]:
        """
        Validate records using mapping's validation rules
        Returns detailed error information for professional error reporting
        
        Args:
            records: List of ContractRecord to validate
            
        Returns:
            Tuple of (valid_records, detailed_errors)
            Each error is a dict with: row, field_errors, record_preview
        """
        valid_records = []
        detailed_errors = []
        
        for idx, record in enumerate(records, start=1):
            row_number = idx + 1  # Excel row (accounting for header)
            record_dict = record.to_dict()

            # 1. Start with mapping-level validation (more detailed)
            is_valid_mapping, field_errors = self.mapping.validate_required_fields(record_dict)

            # 2. Validate Channel value
            is_valid_channel, channel_errors = self.mapping.validate_channel_value(record_dict)
            if not is_valid_channel:
                field_errors.extend(channel_errors)
                is_valid_mapping = False

            # 3. Validate Payment Method (termsFeePaymentMethod) - NOT NULL + enum
            is_valid_payment, payment_errors = self.mapping.validate_payment_method(record_dict)
            if not is_valid_payment:
                field_errors.extend(payment_errors)
                is_valid_mapping = False

            # 4. Validate Company Provider (companyProviderName) - enum per insurance type
            is_valid_provider, provider_errors = self.mapping.validate_company_provider(record_dict)
            if not is_valid_provider:
                field_errors.extend(provider_errors)
                is_valid_mapping = False

            # 5. Validate Program Name (programName) - enum per insurance type
            is_valid_program, program_errors = self.mapping.validate_program_name(record_dict)
            if not is_valid_program:
                field_errors.extend(program_errors)
                is_valid_mapping = False

            # 6. Check model-level validation (backup)
            is_valid_model, error_msg = record.validate()
            
            if not is_valid_mapping:
                # Mapping-level failed - use its detailed errors
                detailed_errors.append({
                    'row': row_number,
                    'excel_row': row_number,
                    'error_count': len(field_errors),
                    'field_errors': field_errors,
                    'record_preview': {
                        'contractId': record_dict.get('contractId', '(trống)'),
                        'peopleName': record_dict.get('peopleName', '(trống)'),
                        'programName': record_dict.get('programName', record_dict.get('majorName', '(trống)')),
                        'companyProviderName': record_dict.get('companyProviderName', '(trống)'),
                    }
                })
            elif not is_valid_model:
                # Model-level failed - use its message
                detailed_errors.append({
                    'row': row_number,
                    'excel_row': row_number,
                    'error_count': 1,
                    'field_errors': [{
                        'field': 'model_validation',
                        'excel_column': 'N/A',
                        'error_type': 'VALIDATION_FAILED',
                        'message': error_msg,
                        'current_value': None
                    }],
                    'record_preview': {
                        'contractId': record_dict.get('contractId', '(trống)'),
                        'peopleName': record_dict.get('peopleName', '(trống)'),
                        'programName': record_dict.get('programName', record_dict.get('majorName', '(trống)')),
                        'companyProviderName': record_dict.get('companyProviderName', '(trống)'),
                    }
                })
            
            if is_valid_mapping and is_valid_model:
                # Store Excel row number so it's available in previews
                record._raw_data['_excel_row'] = row_number
                valid_records.append(record)
        
        return valid_records, detailed_errors
    
    def get_validation_summary(
        self,
        total_records: int,
        valid_count: int,
        errors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate professional validation summary for API response
        
        Args:
            total_records: Total number of records processed
            valid_count: Number of valid records
            errors: List of detailed error dictionaries
            
        Returns:
            Summary dictionary with statistics and grouped errors
        """
        # Group errors by field
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
                        'sample_rows': []
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
            'all_errors': errors,  # Return ALL errors for detailed view
            'first_10_errors': errors[:10],  # Keep for backward compatibility
            'has_more_errors': len(errors) > 10,
            'insurance_type': self.insurance_type,
        }
    
    def process_file(
        self, 
        file_path: str
    ) -> Tuple[List[ContractRecord], List[str]]:
        """
        Complete processing workflow using Template Method Pattern
        
        Algorithm skeleton:
        1. Parse Excel file
        2. Pre-process DataFrame (type-specific)
        3. Transform to ContractRecord objects
        4. Post-process records (type-specific)
        5. Validate records
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            Tuple of (valid_records, errors)
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
