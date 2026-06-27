"""
Health insurance processor implementation
Inherits from IInsuranceProcessor
"""
import pandas as pd
from typing import List, Tuple, Dict, Any
import re
from datetime import datetime
from services.processors.base_processor import IInsuranceProcessor
from models.contract_model import ContractRecord
from configs.mappings.health_mapping import HealthMapping


class HealthProcessor(IInsuranceProcessor):
    """
    Processor for Health Insurance (Sức khỏe)
    
    Processing specifics:
    - Handles multiline Vietnamese headers
    - Has detailed benefit columns (outpatient, dental, maternity, topup)
    - Maps 'peopleName' to 'name' for business key
    """
    
    def __init__(self):
        super().__init__(HealthMapping())

        # After parsing with _parse_relationship(), we only need canonical forms
        # Parser handles variations like 'MẸ', 'chị gái', 'Con đẻ', etc.
        self._gender_map = {
            'Nam': 1,
            'Nữ': 0,
        }
        self._relationship_map = {
            'Bản thân': 0,
            'Bố': 1, 'Mẹ': 1,
            'Vợ': 2, 'Chồng': 2,
            'Anh': 3, 'Chị': 3, 'Em': 3,
            'Con': 4,
            'Khác': 5,
            'Bố/Mẹ của vợ/chồng': 6,
            'Cháu': 7,
            'Nhân viên': 8,
        }
        # Removed _relationship_keywords dict - now handled by _parse_relationship() directly
    
    def pre_process(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pre-process Health Excel data
        - Remove completely empty rows
        - Handle multiline headers (already handled by pandas)
        """
        # Remove rows where all values are NaN
        df = df.dropna(how='all')
        
        # Reset index
        df = df.reset_index(drop=True)
        
        return df
    
    def _parse_relationship(self, value: str) -> str:
        """
        Parse and normalize relationship input.
        Examples: 'MẸ' -> 'Mẹ', 'chị gái' -> 'Chị', 'Con đẻ' -> 'Con'
        
        Returns standardized relationship text that maps to a DB value.
        Returns original value if parsing fails.
        """
        if not value or not isinstance(value, str):
            return value
        
        normalized = value.strip().lower()
        
        # First, check if it's already a valid key in the map
        for key in self._relationship_map.keys():
            if key.lower() == normalized:
                return key
        
        # If not found, try intelligent keyword matching with priority order
        # Check for specific keywords before generic ones
        if 'mẹ' in normalized or 'má' in normalized:
            return 'Mẹ'
        if 'bố' in normalized or 'ba' in normalized or 'cha' in normalized:
            return 'Bố'
        if 'chồng' in normalized:
            return 'Chồng'
        if 'vợ' in normalized:
            return 'Vợ'
        if 'chị' in normalized:
            return 'Chị'
        if 'anh' in normalized:
            return 'Anh'
        if 'em' in normalized:
            return 'Em'
        if 'con' in normalized:
            return 'Con'
        if 'cháu' in normalized:
            return 'Cháu'
        if 'nhân viên' in normalized or 'nv' in normalized or 'staff' in normalized or 'employee' in normalized:
            return 'Nhân viên'
        if 'khác' in normalized or 'other' in normalized:
            return 'Khác'
        if 'bản thân' in normalized or 'bt' in normalized or 'self' in normalized:
            return 'Bản thân'
        
        # If no match found, return original value
        return value
    
    def _parse_gender(self, value: str) -> str:
        """
        Parse and normalize gender input.
        Examples: 'nam' -> 'Nam', 'FEMALE' -> 'Nữ', 'M' -> 'Nam'
        
        Returns standardized gender text that maps to a DB value.
        Returns original value if parsing fails.
        """
        if not value or not isinstance(value, str):
            return value
        
        normalized = value.strip().lower()
        
        # First, check if it's already a valid key in the map
        for key in self._gender_map.keys():
            if key.lower() == normalized:
                return key
        
        # If not found, try intelligent keyword matching
        if 'nam' in normalized or 'm' in normalized:
            return 'Nam'
        if 'nữ' in normalized or 'n' in normalized or 'f' in normalized or 'female' in normalized or 'woman' in normalized:
            return 'Nữ'
        
        # If no match found, return original value
        return value
    
    def _parse_date_string(self, value: str) -> Any:
        # Override to prevent converting DD/MM/YYYY to YYYY-MM-DD
        if not value or not isinstance(value, str):
            return value
        return value.strip()

    @staticmethod
    def _normalize_person_name(value: Any) -> Any:
        """Normalize full name to Vietnamese-friendly title case."""
        if not value or not isinstance(value, str):
            return value

        # Collapse repeated spaces and trim first.
        cleaned = " ".join(value.split())
        if not cleaned:
            return cleaned

        # Title-case each token: "trịnh bảo ngọc" -> "Trịnh Bảo Ngọc"
        return " ".join(token.capitalize() for token in cleaned.split(" "))

    @staticmethod
    def _normalize_phone_number(value: Any) -> Any:
        """Normalize phone values read from Excel, preserving/repairing leading zero when possible."""
        if value is None:
            return value

        text = str(value).strip()
        if not text or text.lower() == 'nan':
            return None

        # Excel often reads phone numbers as floats like 969090278.0
        if text.endswith('.0'):
            text = text[:-2]

        digits = ''.join(ch for ch in text if ch.isdigit())
        if not digits:
            return None

        # Common case in source files: leading zero is lost because Excel stores phone as number.
        if len(digits) == 9:
            digits = '0' + digits

        return digits
        
    def post_process(self, records: List[ContractRecord]) -> List[ContractRecord]:
        """
        Post-process Health records
        - Buyer-as-beneficiary fallback
        """
        for record in records:
            if hasattr(record, '_raw_data'):
                raw = record._raw_data

                # Normalize buyer/insured names to title case (no full UPPER requirement).
                raw['payerName'] = self._normalize_person_name(raw.get('payerName'))
                raw['peopleName'] = self._normalize_person_name(raw.get('peopleName'))
                record.payer_name = raw.get('payerName')
                record.people_name = raw.get('peopleName')
                raw['payerPhone'] = self._normalize_phone_number(raw.get('payerPhone'))
                raw['leadPhone'] = self._normalize_phone_number(raw.get('leadPhone'))
                raw['customerPhone'] = self._normalize_phone_number(raw.get('customerPhone'))
                raw['peoplePhone'] = self._normalize_phone_number(raw.get('peoplePhone'))

                # HEALTH source files often leave 'Số điện thoại' empty while phone exists in
                # 'Phone Khách hàng' or 'Phone trên lead'. Prefer customer phone, then lead phone.
                if not raw.get('payerPhone'):
                    raw['payerPhone'] = raw.get('customerPhone') or raw.get('leadPhone')
                
                # --- Buyer-as-beneficiary fallback ---
                # When buyer purchases for themselves, insured columns are empty.
                if not raw.get('peopleName') and raw.get('payerName'):
                    raw['peopleName'] = raw['payerName']
                    record.people_name = raw['peopleName']
                    if raw.get('peopleRelationship') is None or (isinstance(raw.get('peopleRelationship'), float) and pd.isna(raw.get('peopleRelationship'))):
                        raw['peopleRelationship'] = 'Bản thân'
                elif raw.get('peopleName') and raw.get('payerName') and str(raw.get('peopleName')).strip().lower() == str(raw.get('payerName')).strip().lower():
                    if raw.get('peopleRelationship') is None or (isinstance(raw.get('peopleRelationship'), float) and pd.isna(raw.get('peopleRelationship'))):
                        raw['peopleRelationship'] = 'Bản thân'

                if not raw.get('peopleDob') and raw.get('payerDob'):
                    raw['peopleDob'] = raw['payerDob']

                if not raw.get('peopleLicense') and raw.get('payerLicense'):
                    raw['peopleLicense'] = raw['payerLicense']

                if not raw.get('peopleAddress') and raw.get('payerAddress'):
                    raw['peopleAddress'] = raw['payerAddress']

                if not raw.get('peopleEmail') and raw.get('payerEmail'):
                    raw['peopleEmail'] = raw['payerEmail']

                if not raw.get('peoplePhone') and raw.get('payerPhone'):
                    raw['peoplePhone'] = raw['payerPhone']
        
        return records

    def validate_records(self, records: List[ContractRecord]) -> Tuple[List[ContractRecord], List[Dict[str, Any]]]:
        valid_records_base, detailed_errors = super().validate_records(records)
        
        errors_by_row = {err['row']: err for err in detailed_errors}
        final_valid_records = []
        
        def add_error(row_idx, field, error_type, message, current_value=None):
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

        for idx, record in enumerate(records, start=1):
            row_number = idx + 1
            raw = record._raw_data if hasattr(record, '_raw_data') else record.to_dict()
            min_amount_threshold = 1000.0

            def build_amount_too_small_message(label: str, parsed_amount: float) -> str:
                base_message = f"{label} phải lớn hơn hoặc bằng 1,000"
                if parsed_amount is not None and 0 < parsed_amount < min_amount_threshold:
                    suggested = int(round(parsed_amount * 1000))
                    suggested_text = f"{suggested:,}".replace(',', '.')
                    return f"{base_message}. Có thể sai đơn vị (nghìn đồng). Vui lòng kiểm tra và sửa, ví dụ {parsed_amount:g} -> {suggested_text}"
                return base_message

            gender_value = raw.get('peopleGender')
            if gender_value is not None:
                gender_text = str(gender_value).strip()
                if not gender_text:
                    add_error(row_number, 'peopleGender', 'EMPTY', 'Giới tính không được để trống', gender_value)
                else:
                    # Parse and normalize the gender value
                    parsed_gender = self._parse_gender(gender_text)
                    if parsed_gender not in self._gender_map:
                        # Still invalid after parsing
                        add_error(row_number, 'peopleGender', 'INVALID_ENUM', f'Giới tính không hợp lệ: {gender_text}', gender_value)
                    else:
                        # Update raw data with parsed value for consistency
                        raw['peopleGender'] = parsed_gender

            relationship_value = raw.get('peopleRelationship')
            if relationship_value is not None:
                relationship_text = str(relationship_value).strip()
                if not relationship_text:
                    add_error(row_number, 'peopleRelationship', 'EMPTY', 'Mối quan hệ không được để trống', relationship_value)
                else:
                    # Parse and normalize the relationship value
                    parsed_relationship = self._parse_relationship(relationship_text)
                    if parsed_relationship not in self._relationship_map:
                        # Still invalid after parsing
                        add_error(row_number, 'peopleRelationship', 'INVALID_ENUM', f'Mối quan hệ không hợp lệ: {relationship_text}', relationship_value)
                    else:
                        # Update raw data with parsed value for consistency
                        raw['peopleRelationship'] = parsed_relationship
            
            # 1. License & Passport (allow special characters per updated business rules)
            # CCCD, hộ chiếu có thể chứa ký tự đặc biệt - no validation required
            
            # 2. Phone numbers
            for f in ['payerPhone', 'leadPhone', 'customerPhone']:
                val = raw.get(f)
                if val:
                    val_str = str(val).split('.')[0].strip()
                    if not re.match(r'^0\d{9,10}$', val_str):
                        add_error(row_number, f, 'FORMAT_PHONE', 'SĐT phải bắt đầu bằng số 0, 10-11 số, không khoảng trắng', val)
                        
            # 3. Email format
            for f in ['peopleEmail', 'payerEmail']:
                val = raw.get(f)
                if val:
                    val_str = str(val).strip()
                    if '@' not in val_str:
                        add_error(row_number, f, 'FORMAT_EMAIL', 'Email không hợp lệ (phải chứa @)', val_str)
                        
            # 4. Amount check (remove thousand separators: 2.980.800 -> 2980800)
            feeMain = raw.get('feeInsurance')
            amtPay = raw.get('amountPay')
            
            f_val = None
            if feeMain is not None:
                try:
                    if isinstance(feeMain, (int, float)):
                        f_val = float(feeMain)
                    else:
                        fee_str = str(feeMain).strip()
                        # Remove thousand separators (VN format: 2.980.800 -> 2980800, or 2.980.800,50 -> 2980800.50)
                        fee_str = fee_str.replace('.', '').replace(',', '.')
                        f_val = float(fee_str)
                    if f_val < min_amount_threshold:
                        add_error(
                            row_number,
                            'feeInsurance',
                            'INVALID_AMOUNT',
                            build_amount_too_small_message('Phí bảo hiểm', f_val),
                            feeMain
                        )
                    else:
                        raw['feeInsurance'] = f_val
                except ValueError:
                    pass
            
            a_val = None
            if amtPay is not None:
                try:
                    if isinstance(amtPay, (int, float)):
                        a_val = float(amtPay)
                    else:
                        amt_str = str(amtPay).strip()
                        # Remove thousand separators (VN format: 2.980.800 -> 2980800, or 2.980.800,50 -> 2980800.50)
                        amt_str = amt_str.replace('.', '').replace(',', '.')
                        a_val = float(amt_str)
                    if a_val < min_amount_threshold:
                        add_error(
                            row_number,
                            'amountPay',
                            'INVALID_AMOUNT',
                            build_amount_too_small_message('Số tiền thanh toán', a_val),
                            amtPay
                        )
                    else:
                        raw['amountPay'] = a_val
                except ValueError:
                    pass
                    
            if f_val is not None and a_val is not None:
                if a_val > f_val:
                    add_error(row_number, 'amountPay', 'INVALID_AMOUNT', 'Số tiền thanh toán phải <= Phí bảo hiểm', f"{amtPay} > {feeMain}")
            
            # 5. Dates check
            def _parse_vi_date(dt_str):
                if not dt_str:
                    return None
                if isinstance(dt_str, datetime):
                    return dt_str
                if hasattr(dt_str, 'to_pydatetime'):
                    try:
                        return dt_str.to_pydatetime()
                    except Exception:
                        return None
                if not isinstance(dt_str, str):
                    return None
                try:
                    text = dt_str.strip()
                    if not text:
                        return None

                    # Input chuẩn: DD/MM/YYYY
                    if '/' in text:
                        parts = text.split('/')
                        if len(parts) == 3:
                            day, month, year = (p.strip() for p in parts)
                            return datetime(int(year), int(month), int(day))

                    # Hỗ trợ thêm dữ liệu đã ở ISO
                    if '-' in text:
                        iso_parts = text.split('T')[0].split('-')
                        if len(iso_parts) == 3:
                            year, month, day = (p.strip() for p in iso_parts)
                            return datetime(int(year), int(month), int(day))

                    return datetime.fromisoformat(text.split('T')[0])
                except Exception:
                    return None
                    
            start_dt = _parse_vi_date(raw.get('contractStartDate'))
            pay_dt = _parse_vi_date(raw.get('payment_date'))
            end_dt = _parse_vi_date(raw.get('contractEndDate'))
            dob_dt = _parse_vi_date(raw.get('peopleDob'))
            now_dt = datetime.now()
            
            if pay_dt and pay_dt > now_dt:
                add_error(row_number, 'payment_date', 'INVALID_DATE', 'Ngày thanh toán không được lớn hơn ngày hiện tại', raw.get('payment_date'))
                
            if start_dt and pay_dt and start_dt < pay_dt:
                add_error(row_number, 'contractStartDate', 'INVALID_DATE', 'Ngày hiệu lực phải >= Ngày thanh toán', raw.get('contractStartDate'))
                
            if dob_dt and start_dt:
                age_days = (start_dt - dob_dt).days
                if age_days < 30:
                    add_error(row_number, 'contractStartDate', 'INVALID_DATE', f'Người được bảo hiểm chưa đủ 30 ngày tuổi bắt đầu hiệu lực (mới {age_days} ngày)', raw.get('contractStartDate'))
                
            if end_dt and start_dt and end_dt <= start_dt:
                add_error(row_number, 'contractEndDate', 'INVALID_DATE', 'Ngày kết thúc phải > Ngày bắt đầu (hiệu lực)', raw.get('contractEndDate'))
        
        # Re-build valid_records based on the newly accumulated errors
        final_valid_records = []
        final_errors = list(errors_by_row.values())
        for idx, record in enumerate(records, start=1):
            if idx + 1 not in errors_by_row:
                raw = record._raw_data if hasattr(record, '_raw_data') else None
                if raw is not None:
                    gender_text = raw.get('peopleGender')
                    if isinstance(gender_text, str):
                        parsed = self._parse_gender(gender_text.strip())
                        if parsed in self._gender_map:
                            raw['peopleGender'] = self._gender_map[parsed]

                    relationship_text = raw.get('peopleRelationship')
                    if isinstance(relationship_text, str):
                        parsed = self._parse_relationship(relationship_text.strip())
                        if parsed in self._relationship_map:
                            raw['peopleRelationship'] = self._relationship_map[parsed]

                record._raw_data['_excel_row'] = idx + 1
                final_valid_records.append(record)
                
        return final_valid_records, final_errors
