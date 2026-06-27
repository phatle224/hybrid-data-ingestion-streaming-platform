"""
Moto insurance processor implementation
Inherits from IInsuranceProcessor
"""
import pandas as pd
from typing import List, Tuple, Dict, Any
import re
from datetime import datetime
from services.processors.base_processor import IInsuranceProcessor
from models.contract_model import ContractRecord
from configs.mappings.moto_mapping import MotoMapping


class MotoProcessor(IInsuranceProcessor):
    """
    Processor for Moto Insurance (Xe máy)
    
    Processing specifics:
    - Handles uppercase Vietnamese headers
    - Calculates total fee from main + side benefits
    """
    
    def __init__(self):
        super().__init__(MotoMapping())

    @staticmethod
    def _normalize_phone_number(value: Any) -> Any:
        if value is None:
            return value
        text = str(value).strip()
        if not text or text.lower() == 'nan':
            return None
        if text.endswith('.0'):
            text = text[:-2]
        digits = ''.join(ch for ch in text if ch.isdigit())
        if not digits:
            return None
        # Excel often drops leading zero for phone columns stored as numeric.
        # Example: 0918397534 -> 918397534, so we restore it when length is 9.
        if len(digits) == 9:
            digits = '0' + digits
        return digits

    @staticmethod
    def _normalize_person_name(value: Any) -> Any:
        if not value or not isinstance(value, str):
            return value
        cleaned = " ".join(value.split())
        if not cleaned:
            return cleaned
        return cleaned

    @staticmethod
    def _parse_vi_date(dt_str: Any) -> Any:
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
        text = dt_str.strip()
        if not text:
            return None
        try:
            if '/' in text:
                parts = text.split('/')
                if len(parts) == 3:
                    day, month, year = (p.strip() for p in parts)
                    return datetime(int(year), int(month), int(day))
            if '-' in text:
                iso_parts = text.split('T')[0].split('-')
                if len(iso_parts) == 3:
                    year, month, day = (p.strip() for p in iso_parts)
                    return datetime(int(year), int(month), int(day))
            return datetime.fromisoformat(text.split('T')[0])
        except Exception:
            return None

    @staticmethod
    def _format_db_date(value: Any) -> Any:
        dt = MotoProcessor._parse_vi_date(value)
        if not dt:
            return value
        # Persist in MySQL-compatible format to avoid INSERT datetime errors.
        return dt.strftime('%Y-%m-%d')

    @staticmethod
    def _clean_license_plate(value: Any) -> Any:
        if value is None:
            return None
        text = str(value).strip().upper()
        if not text or text.lower() == 'nan':
            return None
        # Keep letters, numbers, and dash only.
        return ''.join(ch for ch in text if ch.isalnum() or ch == '-')

    @staticmethod
    def _clean_engine_or_chassis(value: Any) -> Any:
        if value is None:
            return None
        text = str(value).strip().upper()
        if not text or text.lower() == 'nan':
            return None
        # Keep alphanumeric only.
        return ''.join(ch for ch in text if ch.isalnum())
    
    def pre_process(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pre-process Moto Excel data
        - Remove completely empty rows
        - Handle uppercase headers
        """
        # Remove rows where all values are NaN
        df = df.dropna(how='all')
        
        # Reset index
        df = df.reset_index(drop=True)
        
        return df
    
    def post_process(self, records: List[ContractRecord]) -> List[ContractRecord]:
        """
        Post-process Moto records
        - Mirror payer* → people* (buyer = insured for moto)
        - Set peopleRelationship = 0 (self)
        """
        for record in records:
            if hasattr(record, '_raw_data'):
                raw = record._raw_data

                # Mirror payer* → people* (buyer IS the insured)
                raw['payerName'] = self._normalize_person_name(raw.get('payerName'))
                if not raw.get('peopleName') and raw.get('payerName'):
                    raw['peopleName'] = raw['payerName']
                else:
                    raw['peopleName'] = self._normalize_person_name(raw.get('peopleName'))
                if not raw.get('peoplePhone') and raw.get('payerPhone'):
                    raw['peoplePhone'] = raw['payerPhone']
                if not raw.get('peopleEmail') and raw.get('payerEmail'):
                    raw['peopleEmail'] = raw['payerEmail']

                raw['payerPhone'] = self._normalize_phone_number(raw.get('payerPhone'))
                raw['licensePlates'] = self._clean_license_plate(raw.get('licensePlates'))
                raw['chassisNumber'] = self._clean_engine_or_chassis(raw.get('chassisNumber'))
                raw['engineNumber'] = self._clean_engine_or_chassis(raw.get('engineNumber'))
                raw['issue_date'] = self._format_db_date(raw.get('issue_date'))
                start_raw = raw.get('contractObjectStartDate')
                end_raw = raw.get('contractObjectEndDate')
                s_dt = self._parse_vi_date(start_raw)
                e_dt = self._parse_vi_date(end_raw)
                if s_dt and e_dt and s_dt > e_dt:
                    raw['contractObjectStartDate'] = self._format_db_date(end_raw)
                    raw['contractObjectEndDate'] = self._format_db_date(start_raw)
                else:
                    raw['contractObjectStartDate'] = self._format_db_date(start_raw)
                    raw['contractObjectEndDate'] = self._format_db_date(end_raw)

                # Single-person type: buyer = beneficiary = self
                if raw.get('peopleRelationship') is None:
                    raw['peopleRelationship'] = 0

        return records

    def validate_records(self, records: List[ContractRecord]) -> Tuple[List[ContractRecord], List[Dict[str, Any]]]:
        valid_records_base, detailed_errors = super().validate_records(records)

        errors_by_row = {err['row']: err for err in detailed_errors}

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

        def parse_amount(value: Any):
            if value is None:
                return None
            if isinstance(value, (int, float)):
                return float(value)
            amount_str = str(value).strip()
            if not amount_str or amount_str in ['-', '--', 'nan', 'None']:
                return None
            amount_str = amount_str.replace('.', '').replace(',', '.')
            return float(amount_str)

        def build_amount_too_small_message(label: str, parsed_amount: float) -> str:
            base_message = f"{label} phải lớn hơn hoặc bằng 1,000"
            # For positive values below threshold, provide a concrete correction hint.
            if parsed_amount is not None and 0 < parsed_amount < min_amount_threshold:
                suggested = int(round(parsed_amount * 1000))
                suggested_text = f"{suggested:,}".replace(',', '.')
                return f"{base_message}. Có thể sai đơn vị (nghìn đồng). Vui lòng kiểm tra và sửa, ví dụ {parsed_amount:g} -> {suggested_text}"
            return base_message

        for idx, record in enumerate(records, start=1):
            row_number = idx + 1
            raw = record._raw_data if hasattr(record, '_raw_data') else record.to_dict()
            min_amount_threshold = 1000.0

            # Phone format: 0 + 9-10 digits
            payer_phone = self._normalize_phone_number(raw.get('payerPhone'))
            if payer_phone:
                raw['payerPhone'] = payer_phone
                if not re.match(r'^0\d{9,10}$', payer_phone):
                    add_error(row_number, 'payerPhone', 'FORMAT_PHONE', 'SĐT phải bắt đầu bằng số 0, 10-11 số, không khoảng trắng', raw.get('payerPhone'))

            # Email basic format
            payer_email = raw.get('payerEmail')
            if payer_email:
                email_text = str(payer_email).strip().lower()
                raw['payerEmail'] = email_text
                if '@' not in email_text:
                    add_error(row_number, 'payerEmail', 'FORMAT_EMAIL', 'Email không hợp lệ (phải chứa @)', payer_email)

            # At least 2 of 3 vehicle identifiers must exist
            id_fields = ['licensePlates', 'chassisNumber', 'engineNumber']
            id_count = sum(1 for f in id_fields if raw.get(f))
            if id_count < 2:
                add_error(
                    row_number,
                    'licensePlates',
                    'MISSING_VEHICLE_IDENTIFIER',
                    'Cần tối thiểu 2/3 thông tin xe: Biển số, Số khung, Số máy',
                    f"Biển số={raw.get('licensePlates') or '(trống)'}, Số khung={raw.get('chassisNumber') or '(trống)'}, Số máy={raw.get('engineNumber') or '(trống)'}"
                )

            # Fee validation
            fee_main = raw.get('feeMainBenefit')
            fee_main_val = None
            if fee_main is not None:
                try:
                    fee_main_val = parse_amount(fee_main)
                    if fee_main_val is not None and 0 < fee_main_val < min_amount_threshold:
                        add_error(
                            row_number,
                            'feeMainBenefit',
                            'INVALID_AMOUNT',
                            build_amount_too_small_message('Phí bảo hiểm TNDS', fee_main_val),
                            fee_main
                        )
                    elif fee_main_val is not None:
                        raw['feeMainBenefit'] = fee_main_val
                except (ValueError, TypeError):
                    add_error(row_number, 'feeMainBenefit', 'INVALID_AMOUNT', 'Phí bảo hiểm TNDS phải là số hợp lệ', fee_main)

            fee_side = raw.get('feeSideBenefit')
            fee_side_val = None
            if fee_side is not None:
                try:
                    fee_side_val = parse_amount(fee_side)
                    if fee_side_val is not None and 0 < fee_side_val < min_amount_threshold:
                        add_error(
                            row_number,
                            'feeSideBenefit',
                            'INVALID_AMOUNT',
                            build_amount_too_small_message('Phí bảo hiểm tai nạn', fee_side_val),
                            fee_side
                        )
                    elif fee_side_val is not None:
                        raw['feeSideBenefit'] = fee_side_val
                except (ValueError, TypeError):
                    add_error(row_number, 'feeSideBenefit', 'INVALID_AMOUNT', 'Phí bảo hiểm tai nạn phải là số hợp lệ', fee_side)

            if fee_main_val is None and fee_side_val is None:
                add_error(
                    row_number,
                    'feeMainBenefit',
                    'MISSING',
                    'Cần nhập ít nhất 1 trong 2 trường: PHÍ BẢO HIỂM TNDS BẮT BUỘC hoặc PHÍ BẢO HIỂM TAI NẠN NNTX',
                    None
                )

            fee_total = raw.get('feeInsurance')
            fee_total_val = None
            if fee_total is not None:
                try:
                    fee_total_val = parse_amount(fee_total)
                    if fee_total_val is None or fee_total_val < min_amount_threshold:
                        add_error(
                            row_number,
                            'feeInsurance',
                            'INVALID_AMOUNT',
                            build_amount_too_small_message('Tổng phí bảo hiểm', fee_total_val),
                            fee_total
                        )
                    else:
                        raw['feeInsurance'] = fee_total_val
                except (ValueError, TypeError):
                    add_error(row_number, 'feeInsurance', 'INVALID_AMOUNT', 'Tổng phí bảo hiểm phải là số hợp lệ', fee_total)

            # Date validation
            start_dt = self._parse_vi_date(raw.get('contractObjectStartDate'))
            end_dt = self._parse_vi_date(raw.get('contractObjectEndDate'))
            if start_dt and end_dt and end_dt < start_dt:
                add_error(row_number, 'contractObjectEndDate', 'INVALID_DATE', 'Ngày kết thúc phải >= Ngày bắt đầu', raw.get('contractObjectEndDate'))

            # Contract period value must be positive if present
            period_value = raw.get('contractPeriodValue')
            if period_value is not None:
                try:
                    period_int = int(float(period_value))
                    if period_int <= 0:
                        add_error(row_number, 'contractPeriodValue', 'INVALID_VALUE', 'Số năm bảo hiểm phải > 0', period_value)
                    else:
                        raw['contractPeriodValue'] = period_int
                except (ValueError, TypeError):
                    add_error(row_number, 'contractPeriodValue', 'INVALID_VALUE', 'Số năm bảo hiểm phải là số nguyên hợp lệ', period_value)

        final_valid_records = []
        final_errors = list(errors_by_row.values())
        for idx, record in enumerate(records, start=1):
            if idx + 1 not in errors_by_row:
                record._raw_data['_excel_row'] = idx + 1
                final_valid_records.append(record)

        return final_valid_records, final_errors
