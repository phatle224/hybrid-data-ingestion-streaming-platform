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
        
        # Rename columns using mapping
        df = df.rename(columns=self.mapping.column_mapping)
        
        # Propagate merged/partially filled batch-level columns
        for col in ['majorName', 'companyProviderName', 'termsFeePaymentMethod', 'programCodeMiningChannel']:
            if col in df.columns:
                df[col] = df[col].ffill().bfill()
        
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
                    else:
                        # For numeric fields that are already float/int but may have thousand-unit representation
                        if col in ['feeInsurance', 'feeMainBenefit', 'feeSideBenefit', 
                                   'totalFee', 'amountPay', 'amount']:
                            if isinstance(value, (int, float)):
                                val_float = float(value)
                                if 0 < val_float < 1000:
                                    val_float *= 1000
                                value = val_float
                    row_dict[col] = value
            
            # Skip empty/dummy/incomplete rows that lack sufficient critical fields
            critical_fields = ['payment_date', 'feeInsurance', 'contractStartDate', 'contractObjectStartDate', 'payerPhone', 'peoplePhone', 'contractId']
            present_critical = [f for f in critical_fields if row_dict.get(f) is not None]
            if 'contractId' not in present_critical or len(present_critical) < 3:
                continue
                
            # Add insurance type
            row_dict['insuranceType'] = self.insurance_type
            
            # Ensure 'peopleName' field exists for business key.
            # For VEHICLE/MOTO: name_field='payerName', copy to peopleName
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
                        'contractId': record_dict.get('contractId', '(empty)'),
                        'peopleName': record_dict.get('peopleName', '(empty)'),
                        'majorName': record_dict.get('majorName', '(empty)'),
                        'programName': record_dict.get('programName', record_dict.get('majorName', '(empty)')),
                        'companyProviderName': record_dict.get('companyProviderName', '(empty)'),
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
                        'contractId': record_dict.get('contractId', '(empty)'),
                        'peopleName': record_dict.get('peopleName', '(empty)'),
                        'majorName': record_dict.get('majorName', '(empty)'),
                        'programName': record_dict.get('programName', record_dict.get('majorName', '(empty)')),
                        'companyProviderName': record_dict.get('companyProviderName', '(empty)'),
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
        5. Normalize records (common)
        6. Validate records
        
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
        
        # Step 5: Normalize records (common normalization)
        records = self.normalize_records(records)
        
        # Step 6: Validate
        valid_records, errors = self.validate_records(records)
        
        return valid_records, errors

    def normalize_records(self, records: List[ContractRecord]) -> List[ContractRecord]:
        """
        Common normalization step for all records before validation:
        - Normalizes companyProviderName (case-insensitive + defaults)
        - Normalizes termsFeePaymentMethod (maps numeric codes and text deviations)
        - Normalizes programName (case-insensitive + B-One sub-plan mapping)
        - Normalizes programCodeMiningChannel (case-insensitive lookup)
        """
        for record in records:
            raw = record._raw_data if hasattr(record, '_raw_data') else {}
            
            # --- 1. Normalize payment method ---
            pm_val = raw.get('termsFeePaymentMethod')
            if pm_val is not None:
                normalized_pm = self._normalize_payment_method_value(pm_val)
                if normalized_pm:
                    raw['termsFeePaymentMethod'] = normalized_pm
            else:
                if self.insurance_type == 'HEALTH':
                    raw['termsFeePaymentMethod'] = 'Nhà bảo hiểm'
            
            # --- 2. Normalize company provider ---
            provider_val = record.company_provider_name or raw.get('companyProviderName')
            normalized_provider = self._normalize_provider_value(provider_val)
            if normalized_provider:
                record.company_provider_name = normalized_provider
                raw['companyProviderName'] = normalized_provider
                
            # --- 2.1 Default majorName / fallback programName ---
            major_val = raw.get('majorName')
            if major_val is None or (isinstance(major_val, str) and not major_val.strip()):
                if self.insurance_type == 'TRAVEL':
                    raw['majorName'] = 'Du lịch'
                elif self.insurance_type == 'MOTO':
                    raw['majorName'] = 'BHXM'
                elif self.insurance_type == 'HEALTH':
                    raw['majorName'] = 'Sức khỏe'
                elif self.insurance_type == 'VEHICLE':
                    raw['majorName'] = 'ô tô'
                elif self.insurance_type == 'MEDICAL_SOCIAL':
                    raw['majorName'] = 'Bảo hiểm y tế'
                    
            if self.insurance_type == 'MEDICAL_SOCIAL':
                if not raw.get('programName') and raw.get('majorName'):
                    raw['programName'] = raw.get('majorName')
                elif not raw.get('majorName') and raw.get('programName'):
                    raw['majorName'] = 'Bảo hiểm y tế'

            # --- 3. Normalize program name ---
            program_val = record.program_name or raw.get('programName')
            normalized_program = self._normalize_program_value(program_val, record.company_provider_name)
            if normalized_program:
                record.program_name = normalized_program
                raw['programName'] = normalized_program
                
            # --- 4. Normalize channel ---
            channel_val = raw.get('programCodeMiningChannel')
            if channel_val is not None:
                normalized_channel = self._normalize_channel_value(channel_val)
                if normalized_channel:
                    raw['programCodeMiningChannel'] = normalized_channel
                    if hasattr(record, 'channel_id'):
                        record.channel_id = normalized_channel
            else:
                if self.insurance_type == 'HEALTH':
                    raw['programCodeMiningChannel'] = 'HO'
                    if hasattr(record, 'channel_id'):
                        record.channel_id = 'HO'
            
            # Ensure _raw_data is synchronized
            if hasattr(record, '_raw_data'):
                record._raw_data.update(raw)
                
            # Ensure instance attributes match raw data for business keys and metadata
            record.contract_id = raw.get('contractId')
            record.payer_name = raw.get('payerName')
            record.major_name = raw.get('majorName')
            record.company_provider_name = raw.get('companyProviderName')
            record.insurance_type = raw.get('insuranceType')
            
        return records

    def _normalize_payment_method_value(self, val: Any) -> Optional[str]:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            if self.insurance_type == 'HEALTH':
                return 'Nhà bảo hiểm'
            return None
        val_str = str(val).strip()
        if not val_str:
            if self.insurance_type == 'HEALTH':
                return 'Nhà bảo hiểm'
            return None
            
        val_lower = val_str.lower()
        
        # Handle numeric values
        if val_lower in ['1', '1.0']:
            return 'OCB'
        elif val_lower in ['2', '2.0']:
            return 'Payoo'
        elif val_lower in ['3', '3.0']:
            return 'Bảo Kim'
        elif val_lower in ['4', '4.0']:
            return 'VietcomBank'
        elif val_lower in ['5', '5.0']:
            return 'Nhà bảo hiểm'
        elif val_lower in ['6', '6.0']:
            return 'InsuStream'
            
        # Handle insurer transfers and other string deviations
        if any(k in val_lower for k in [
            'chuyển khoản', 'chuyen khoan', 'chuyển về', 'chuyen ve',
            'nhà bh', 'nha bh', 'nhà bảo hiểm', 'nha bao hiem',
            'liberty', 'vbi', 'bảo minh', 'baominh', 'bảo việt', 'baoviet',
            'tasc', 'tasco', 'pvi', 'mic', 'pti', 'aaa', 'gic', 'opes'
        ]):
            if 'insustream' in val_lower:
                return 'InsuStream'
            return 'Nhà bảo hiểm'
            
        if 'insustream' in val_lower:
            return 'InsuStream'
            
        if 'online' in val_lower or 'gateway' in val_lower or 'gate' in val_lower or 'payoo' in val_lower:
            return 'Payoo'
            
        # Case-insensitive lookup
        for method in self.mapping.VALID_PAYMENT_METHODS:
            if method.lower() == val_lower:
                return method
                
        return val_str

    def _normalize_provider_value(self, val: Any) -> Optional[str]:
        # If health, default empty to 'BHV'
        if val is None or (isinstance(val, float) and pd.isna(val)):
            if self.insurance_type == 'HEALTH':
                return 'BHV'
            return None
        val_str = str(val).strip()
        if not val_str:
            if self.insurance_type == 'HEALTH':
                return 'BHV'
            return None
            
        val_lower = val_str.lower()
        valid_set = self.mapping.VALID_COMPANY_PROVIDERS.get(self.insurance_type, set())
        
        # Case-insensitive direct match against valid set
        for provider in valid_set:
            if provider.lower() == val_lower:
                return provider
                
        # Common fuzzy mappings
        if 'liberty' in val_lower:
            for provider in valid_set:
                if 'liberty' in provider.lower():
                    return provider
        if 'vbi' in val_lower:
            for provider in valid_set:
                if 'vbi' in provider.lower():
                    return provider
        if 'pvi' in val_lower:
            if 'digital' in val_lower:
                for provider in valid_set:
                    if 'digital' in provider.lower():
                        return provider
            for provider in valid_set:
                if 'pvi' in provider.lower():
                    return provider
        if 'tasco' in val_lower:
            for provider in valid_set:
                if 'tasco' in provider.lower():
                    return provider
                    
        return val_str

    def _normalize_program_value(self, val: Any, provider: Optional[str]) -> Optional[str]:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            if self.insurance_type == 'HEALTH' and provider == 'BHV':
                return 'SKTA_new'
            return None
        val_str = str(val).strip()
        if not val_str:
            if self.insurance_type == 'HEALTH' and provider == 'BHV':
                return 'SKTA_new'
            return None
            
        val_lower = val_str.lower()
        
        # Health specific plan mapping
        if self.insurance_type == 'HEALTH':
            # Map sub-plans B3, B5, B9 to B-One
            if val_lower in ['b3', 'b5', 'b9', 'b 3', 'b 5', 'b 9']:
                return 'B-One'
            # If the value is "sức khỏe" or similar, map to SKTA_new
            if val_lower == 'sức khỏe' or val_lower == 'suc khoe':
                return 'SKTA_new'
                
        valid_set = self.mapping.VALID_PROGRAM_NAMES.get(self.insurance_type, set())
        
        # Case-insensitive lookup
        for program in valid_set:
            if program.lower() == val_lower:
                return program
                
        # Fuzzy match
        for program in valid_set:
            p_clean = ''.join(c for c in program.lower() if c.isalnum())
            v_clean = ''.join(c for c in val_lower if c.isalnum())
            if p_clean == v_clean:
                return program
                
        return val_str

    def _normalize_channel_value(self, val: Any) -> Optional[str]:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            if self.insurance_type == 'HEALTH':
                return 'HO'
            return None
        val_str = str(val).strip()
        if not val_str:
            if self.insurance_type == 'HEALTH':
                return 'HO'
            return None
            
        val_lower = val_str.lower()
        
        # Norms
        if 'h.o_renew' in val_lower or 'ho_renew' in val_lower or 'ho-renew' in val_lower:
            return 'Renew'
        if 'dsa_neo_renew' in val_lower or 'dsa-neo-renew' in val_lower:
            return 'DSA_NEO/Renew'
        if 'dsa_renew' in val_lower or 'dsa-renew' in val_lower:
            return 'DSA/Renew'
        if 'ctv_tsa' in val_lower or 'ctv-tsa' in val_lower or 'ctv tsa' in val_lower:
            if 'renew' in val_lower:
                return 'CTV_TSA (TSA 2)/Renew'
            return 'CTV_TSA (TSA 2)'
        if val_lower in ['ho', 'h.o']:
            return 'HO'
            
        for channel in self.mapping.VALID_CHANNELS:
            if channel.lower() == val_lower:
                return channel
            c_clean = ''.join(c for c in channel.lower() if c.isalnum())
            v_clean = ''.join(c for c in val_lower if c.isalnum())
            if c_clean == v_clean:
                return channel
                
        return val_str

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(type={self.insurance_type})"
