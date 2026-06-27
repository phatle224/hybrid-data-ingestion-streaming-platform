"""
Medical-Social insurance processor implementation
Inherits from IInsuranceProcessor
"""
import pandas as pd
import re
from datetime import datetime
from typing import List, Dict, Any, Tuple
from services.processors.base_processor import IInsuranceProcessor
from models.contract_model import ContractRecord
from configs.mappings.medical_social_mapping import MedicalSocialMapping


class MedicalSocialProcessor(IInsuranceProcessor):
    """
    Processor for Medical & Social Insurance (BHYT & BHXH)
    
    Processing specifics:
    - Can contain both Medical (BHYT) and Social (BHXH) records
    - Resolves insuranceType from MEDICAL_SOCIAL → MEDICAL or SOCIAL based on majorName
    - Maps 'peopleName' to 'name' for business key
    """

    # Keywords used to resolve MEDICAL_SOCIAL sub-type from majorName
    _MEDICAL_SOCIAL_KEYWORDS = {
        'SOCIAL': ['bhxh', 'bảo hiểm xã hội', 'xã hội'],
        'MEDICAL': ['bhyt', 'bảo hiểm y tế', 'y tế'],
    }

    def __init__(self):
        super().__init__(MedicalSocialMapping())
    
    def pre_process(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pre-process Medical-Social Excel data
        - Remove completely empty rows
        - Clean up duplicate column suffixes (.1)
        """
        # Remove rows where all values are NaN
        df = df.dropna(how='all')
        
        # Reset index
        df = df.reset_index(drop=True)
        
        return df
    
    def post_process(self, records: List[ContractRecord]) -> List[ContractRecord]:
        """
        Post-process Medical-Social records
        - Ensure 'name' is populated from 'peopleName'
        - Convert gender text to integer (Nam=1, Nữ=0)
        - Convert relationship text to integer
        """
        # Gender mapping: Text -> Integer (strict business enum)
        gender_map = {
            'nam': 1,
            'nữ': 0,
            'nu': 0,
        }
        
        # Relationship mapping: Text -> Integer
        relationship_map = {
            'bản thân': 0,
            'bố/mẹ': 1,
            'vợ/chồng': 2,
            'anh/chị/em': 3,
            'con': 4,
            'khác': 5,
            'bố/mẹ vợ/chồng': 6,
        }

        renewal_map = {
            'tái tục': 0,
            'tai tuc': 0,
            'mua mới': 1,
            'mua moi': 1,
        }
        
        for record in records:
            if hasattr(record, '_raw_data'):
                # Resolve MEDICAL_SOCIAL → MEDICAL or SOCIAL based on majorName
                resolved_type = self._resolve_insurance_type(record._raw_data)
                record._raw_data['insuranceType'] = resolved_type
                record.insurance_type = resolved_type
                # Convert peopleGender text to integer
                if 'peopleGender' in record._raw_data:
                    gender_value = record._raw_data['peopleGender']
                    if isinstance(gender_value, str) and gender_value.strip():
                        converted = gender_map.get(gender_value.strip().lower())
                        if converted is not None:
                            record._raw_data['peopleGender'] = converted
                
                # Convert peopleRelationship text to integer
                if 'peopleRelationship' in record._raw_data:
                    rel_value = record._raw_data['peopleRelationship']
                    if isinstance(rel_value, str) and rel_value.strip():
                        converted = relationship_map.get(rel_value.strip().lower())
                        if converted is not None:
                            record._raw_data['peopleRelationship'] = converted

                # Normalize name/address fields
                for f in ['peopleName', 'peopleAddress', 'payerName', 'payerAddress']:
                    if f in record._raw_data and isinstance(record._raw_data.get(f), str):
                        record._raw_data[f] = record._raw_data[f].strip()

                # Normalize license fields (keep only letters and digits)
                for f in ['peopleLicense', 'payerLicense']:
                    if f in record._raw_data:
                        normalized_license = self._normalize_license(record._raw_data.get(f))
                        if normalized_license:
                            record._raw_data[f] = normalized_license

                # Normalize social ID according to current rule (trim + remove special chars)
                if 'socialId' in record._raw_data:
                    normalized_social_id = self._normalize_license(record._raw_data.get('socialId'))
                    if normalized_social_id:
                        record._raw_data['socialId'] = normalized_social_id

                # Normalize phone fields
                for f in ['peoplePhone', 'payerPhone']:
                    if f in record._raw_data:
                        normalized_phone = self._normalize_phone_number(record._raw_data.get(f))
                        if normalized_phone:
                            record._raw_data[f] = normalized_phone

                # Normalize email fields
                for f in ['peopleEmail', 'payerEmail']:
                    if f in record._raw_data and isinstance(record._raw_data.get(f), str):
                        record._raw_data[f] = record._raw_data[f].strip().lower()

                # Normalize renewal text (TRIM)
                if 'renewal' in record._raw_data and isinstance(record._raw_data.get('renewal'), str):
                    renewal_value = record._raw_data['renewal'].strip().lower()
                    converted_renewal = renewal_map.get(renewal_value)
                    record._raw_data['renewal'] = converted_renewal if converted_renewal is not None else record._raw_data['renewal'].strip()

                # Normalize contract status to integer for DB compatibility (nullable field)
                if 'contractStatus' in record._raw_data:
                    normalized_status = self._normalize_contract_status(record._raw_data.get('contractStatus'))
                    if normalized_status is None:
                        # Nullable field: remove unrecognized status text to avoid DB type errors
                        record._raw_data.pop('contractStatus', None)
                    else:
                        record._raw_data['contractStatus'] = normalized_status

                # --- Buyer-as-beneficiary fallback ---
                # When buyer purchases for themselves, insured columns are empty.
                # Fill insured fields from payer fields in that case.
                raw = record._raw_data
                if not raw.get('peopleName') and raw.get('payerName'):
                    raw['peopleName'] = raw['payerName']
                    record.people_name = raw['peopleName']
                    # Set relationship = 0 (self) if not already set
                    if raw.get('peopleRelationship') is None:
                        raw['peopleRelationship'] = 0

                if not raw.get('peopleDob') and raw.get('payerDob'):
                    raw['peopleDob'] = raw['payerDob']

                if not raw.get('peopleLicense') and raw.get('payerLicense'):
                    raw['peopleLicense'] = raw['payerLicense']

                if not raw.get('peopleAddress') and raw.get('payerAddress'):
                    raw['peopleAddress'] = raw['payerAddress']

                if not raw.get('peoplePhone') and raw.get('payerPhone'):
                    raw['peoplePhone'] = raw['payerPhone']

                if not raw.get('peopleEmail') and raw.get('payerEmail'):
                    raw['peopleEmail'] = raw['payerEmail']
        
        return records

    def validate_records(self, records: List[ContractRecord]) -> Tuple[List[ContractRecord], List[Dict[str, Any]]]:
        valid_records_base, detailed_errors = super().validate_records(records)

        errors_by_row = {err['row']: err for err in detailed_errors}

        def add_error(row_idx: int, field: str, error_type: str, message: str, current_value: Any = None):
            excel_col = self.mapping._get_excel_column_for_field(field)
            if row_idx not in errors_by_row:
                record_dict = records[row_idx - 2].to_dict() if len(records) >= row_idx - 1 else {}
                errors_by_row[row_idx] = {
                    'row': row_idx,
                    'excel_row': row_idx,
                    'error_count': 0,
                    'field_errors': [],
                    'record_preview': {
                        'contractId': record_dict.get('contractId', '(trống)'),
                        'peopleName': record_dict.get('peopleName', '(trống)'),
                        'majorName': record_dict.get('majorName', '(trống)'),
                        'companyProviderName': record_dict.get('companyProviderName', '(trống)'),
                    }
                }
            errors_by_row[row_idx]['field_errors'].append({
                'field': field,
                'excel_column': excel_col,
                'error_type': error_type,
                'message': message,
                'current_value': current_value
            })
            errors_by_row[row_idx]['error_count'] += 1

        min_amount_threshold = 1000.0

        for idx, record in enumerate(records, start=1):
            row_number = idx + 1
            raw = record._raw_data if hasattr(record, '_raw_data') else record.to_dict()

            # Gender enum: only Nam/Nu allowed before converting to int
            people_gender = raw.get('peopleGender')
            if people_gender not in (None, '') and people_gender not in (0, 1):
                add_error(row_number, 'peopleGender', 'INVALID_ENUM', 'Giới tính chỉ chấp nhận Nam hoặc Nữ', people_gender)

            # Relationship enum conversion must result in integer code 0..6
            people_relationship = raw.get('peopleRelationship')
            if people_relationship not in (None, '') and people_relationship not in (0, 1, 2, 3, 4, 5, 6):
                add_error(
                    row_number,
                    'peopleRelationship',
                    'INVALID_ENUM',
                    'Mối quan hệ không hợp lệ. Chỉ chấp nhận: Bản thân, Bố/Mẹ, Vợ/Chồng, Anh/Chị/Em, Con, Khác, Bố/Mẹ vợ/chồng',
                    people_relationship,
                )

            # Phone format validation (nullable)
            for f in ['peoplePhone', 'payerPhone']:
                val = raw.get(f)
                if val:
                    val_str = str(val).strip()
                    if not re.match(r'^0\d{9,10}$', val_str):
                        add_error(row_number, f, 'FORMAT_PHONE', 'SĐT phải bắt đầu bằng số 0 và có 10-11 chữ số', val)

            # Email format validation (nullable)
            for f in ['peopleEmail', 'payerEmail']:
                val = raw.get(f)
                if val:
                    val_str = str(val).strip()
                    if '@' not in val_str:
                        add_error(row_number, f, 'FORMAT_EMAIL', 'Email không hợp lệ (phải chứa @)', val)

            # Social ID format: already normalized in post_process (trim + remove special chars)

            # Renewal enum (required): Tái tục -> 0, Mua mới -> 1
            renewal = raw.get('renewal')
            if renewal in (None, ''):
                add_error(row_number, 'renewal', 'MISSING', 'Phương án KH là trường bắt buộc', renewal)
            elif renewal not in (0, 1):
                add_error(row_number, 'renewal', 'INVALID_ENUM', 'Phương án KH chỉ chấp nhận Tái tục hoặc Mua mới', renewal)

            # Fee must be numeric and >= 1,000
            fee_val = raw.get('feeInsurance')
            if fee_val is not None and fee_val != '':
                parsed_fee = self._parse_amount(fee_val)
                if parsed_fee is None:
                    add_error(row_number, 'feeInsurance', 'INVALID_AMOUNT', 'Phí bảo hiểm không đúng định dạng số', fee_val)
                else:
                    raw['feeInsurance'] = parsed_fee
                    if parsed_fee < min_amount_threshold:
                        add_error(row_number, 'feeInsurance', 'INVALID_AMOUNT', 'Phí bảo hiểm phải lớn hơn hoặc bằng 1,000', fee_val)

            # Date range check: contract end date must be greater than start date
            start_dt = self._parse_date(raw.get('contractObjectStartDate'))
            end_dt = self._parse_date(raw.get('contractObjectEndDate'))
            if start_dt and end_dt and end_dt <= start_dt:
                add_error(
                    row_number,
                    'contractObjectEndDate',
                    'INVALID_DATE',
                    'Ngày kết thúc phải lớn hơn ngày bắt đầu',
                    raw.get('contractObjectEndDate'),
                )

        final_errors = list(errors_by_row.values())
        final_valid_records = []
        for idx, record in enumerate(records, start=1):
            excel_row = idx + 1
            if excel_row not in errors_by_row:
                if hasattr(record, '_raw_data'):
                    record._raw_data['_excel_row'] = excel_row
                final_valid_records.append(record)

        return final_valid_records, final_errors

    def _resolve_insurance_type(self, raw_data: Dict[str, Any]) -> str:
        """
        Resolve 'MEDICAL_SOCIAL' → 'MEDICAL' or 'SOCIAL' by checking majorName or programName.
        """
        major_name = str(raw_data.get('majorName') or '').lower().strip()
        program_name = str(raw_data.get('programName') or '').lower().strip()
        combined = f"{major_name} {program_name}"
        for ins_type, keywords in self._MEDICAL_SOCIAL_KEYWORDS.items():
            for kw in keywords:
                if kw in combined:
                    return ins_type
        print(f"WARNING: Cannot resolve MEDICAL_SOCIAL sub-type from majorName='{raw_data.get('majorName')}' and programName='{raw_data.get('programName')}', keeping MEDICAL_SOCIAL")
        return 'MEDICAL_SOCIAL'

    @staticmethod
    def _normalize_phone_number(value: Any) -> Any:
        if value is None:
            return value
        text = str(value).strip()
        if not text:
            return text
        if text.endswith('.0'):
            text = text[:-2]
        digits = re.sub(r'\D', '', text)
        if len(digits) == 9:
            digits = '0' + digits
        return digits

    @staticmethod
    def _normalize_license(value: Any) -> Any:
        if value is None:
            return value
        text = str(value).strip()
        if not text:
            return text
        return re.sub(r'[^0-9A-Za-z]', '', text)

    @staticmethod
    def _parse_amount(value: Any) -> Any:
        if value is None or value == '':
            return None
        try:
            if isinstance(value, (int, float)):
                val_float = float(value)
                if 0 < val_float < 1000:
                    val_float *= 1000
                return val_float
            text = str(value).strip()
            text = text.replace('.', '').replace(',', '.')
            val_float = float(text)
            if 0 < val_float < 1000:
                val_float *= 1000
            return val_float
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _parse_date(value: Any) -> Any:
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        text = str(value).strip()
        if not text:
            return None
        try:
            if '/' in text:
                day, month, year = text.split('/')
                return datetime(int(year), int(month), int(day))
            if '-' in text:
                iso = text.split('T')[0]
                return datetime.fromisoformat(iso)
        except Exception:
            return None
        return None

    @staticmethod
    def _normalize_contract_status(value: Any) -> Any:
        """Normalize contract status to integer codes expected by DB."""
        if value is None:
            return None

        if isinstance(value, bool):
            return int(value)

        if isinstance(value, (int, float)):
            try:
                return int(value)
            except (ValueError, TypeError):
                return None

        text = str(value).strip()
        if not text:
            return None

        # Numeric string
        if text.isdigit():
            return int(text)

        normalized = text.lower()
        status_map = {
            'đã duyệt': 1,
            'da duyet': 1,
            'duyệt': 1,
            'duyet': 1,
            'chờ duyệt': 0,
            'cho duyet': 0,
            'pending': 0,
            'từ chối': 2,
            'tu choi': 2,
            'hủy': 3,
            'huy': 3,
            'đã hủy': 3,
            'da huy': 3,
        }
        return status_map.get(normalized)
