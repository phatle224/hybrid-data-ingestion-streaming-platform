"""
Travel insurance processor implementation
Inherits from IInsuranceProcessor
"""
import pandas as pd
from typing import List, Tuple, Dict, Any
import re
from datetime import datetime
from services.processors.base_processor import IInsuranceProcessor
from models.contract_model import ContractRecord
from configs.mappings.travel_mapping import TravelMapping


class TravelProcessor(IInsuranceProcessor):
    """
    Processor for Travel Insurance (Du lịch)
    
    Processing specifics:
    - Handles journey date validation
    - Calculates journey days if not provided
    """
    
    def __init__(self):
        super().__init__(TravelMapping())

    @staticmethod
    def _normalize_person_name(value: Any) -> Any:
        if not value or not isinstance(value, str):
            return value
        cleaned = " ".join(value.split())
        if not cleaned:
            return cleaned
        return " ".join(token.capitalize() for token in cleaned.split(" "))

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
        if len(digits) == 9:
            digits = '0' + digits
        return digits

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
    
    def pre_process(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pre-process Travel Excel data
        - Remove completely empty rows
        - Clean whitespace in string columns
        """
        # Remove rows where all values are NaN
        df = df.dropna(how='all')
        
        # Reset index
        df = df.reset_index(drop=True)
        
        return df
    
    def post_process(self, records: List[ContractRecord]) -> List[ContractRecord]:
        """
        Post-process Travel records
        - Buyer-as-beneficiary fallback: fill people* from payer* when buyer purchases for themselves
        """
        for record in records:
            if not hasattr(record, '_raw_data'):
                continue
            raw = record._raw_data

            raw['peopleName'] = self._normalize_person_name(raw.get('peopleName'))
            raw['payerName'] = self._normalize_person_name(raw.get('payerName'))
            raw['payerPhone'] = self._normalize_phone_number(raw.get('payerPhone'))
            raw['peoplePhone'] = self._normalize_phone_number(raw.get('peoplePhone'))

            # --- Two-way fallback for Travel ---
            # 1) Buyer-as-beneficiary: people* <- payer*
            # 2) Beneficiary-only files: payer* <- people*
            if not raw.get('peopleName') and raw.get('payerName'):
                raw['peopleName'] = raw['payerName']
            if not raw.get('payerName') and raw.get('peopleName'):
                raw['payerName'] = raw['peopleName']

            record.people_name = raw.get('peopleName')
            record.payer_name = raw.get('payerName')

            if not raw.get('peopleDob') and raw.get('payerDob'):
                raw['peopleDob'] = raw['payerDob']
            if not raw.get('payerDob') and raw.get('peopleDob'):
                raw['payerDob'] = raw['peopleDob']

            if not raw.get('peopleLicense') and raw.get('payerLicense'):
                raw['peopleLicense'] = raw['payerLicense']
            if not raw.get('payerLicense') and raw.get('peopleLicense'):
                raw['payerLicense'] = raw['peopleLicense']

            if not raw.get('peoplePhone') and raw.get('payerPhone'):
                raw['peoplePhone'] = raw['payerPhone']
            if not raw.get('payerPhone') and raw.get('peoplePhone'):
                raw['payerPhone'] = raw['peoplePhone']

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

            # Shared rule from Health: if phone exists, must match 0 + 9-10 digits
            payer_phone = self._normalize_phone_number(raw.get('payerPhone'))
            if payer_phone:
                raw['payerPhone'] = payer_phone
                if not re.match(r'^0\d{9,10}$', payer_phone):
                    add_error(row_number, 'payerPhone', 'FORMAT_PHONE', 'SĐT phải bắt đầu bằng số 0, 10-11 số, không khoảng trắng', raw.get('payerPhone'))

            # Fee must be > 1000 (remove thousand separators: 2.980.800 -> 2980800)
            fee = raw.get('feeInsurance')
            if fee is not None:
                try:
                    if isinstance(fee, (int, float)):
                        fee_val = float(fee)
                    else:
                        fee_str = str(fee).strip()
                        # Remove thousand separators (VN format: 2.980.800 -> 2980800, or 2.980.800,50 -> 2980800.50)
                        fee_str = fee_str.replace('.', '').replace(',', '.')
                        fee_val = float(fee_str)
                    if fee_val < min_amount_threshold:
                        add_error(
                            row_number,
                            'feeInsurance',
                            'INVALID_AMOUNT',
                            build_amount_too_small_message('Phí bảo hiểm', fee_val),
                            fee
                        )
                    else:
                        raw['feeInsurance'] = fee_val
                except (ValueError, TypeError):
                    add_error(row_number, 'feeInsurance', 'INVALID_AMOUNT', 'Phí bảo hiểm phải là số hợp lệ', fee)

            start_dt = self._parse_vi_date(raw.get('startDateJourney'))
            end_dt = self._parse_vi_date(raw.get('endDateJourney'))
            pay_dt = self._parse_vi_date(raw.get('payment_date'))
            now_dt = datetime.now()

            # Shared rule from Health: payment date must not be in the future
            if pay_dt and pay_dt > now_dt:
                add_error(row_number, 'payment_date', 'INVALID_DATE', 'Ngày thanh toán không được lớn hơn ngày hiện tại', raw.get('payment_date'))

            # Shared date-order rule (relaxed for historical offline imports where records can be logged post-journey)
            # if start_dt and pay_dt and start_dt < pay_dt:
            #     add_error(row_number, 'startDateJourney', 'INVALID_DATE', 'Ngày đi phải >= Ngày thanh toán', raw.get('startDateJourney'))

            if start_dt and end_dt and end_dt <= start_dt:
                add_error(row_number, 'endDateJourney', 'INVALID_DATE', 'Ngày về phải > Ngày đi', raw.get('endDateJourney'))

            # journey_days only needs to be a positive integer
            days_value = raw.get('journey_days')
            if days_value is not None:
                try:
                    days_int = int(float(days_value))
                    if days_int <= 0:
                        add_error(row_number, 'journey_days', 'INVALID_VALUE', 'Số ngày phải > 0', days_value)
                except (ValueError, TypeError):
                    add_error(row_number, 'journey_days', 'INVALID_VALUE', 'Số ngày phải là số nguyên hợp lệ', days_value)

        final_valid_records = []
        final_errors = list(errors_by_row.values())
        for idx, record in enumerate(records, start=1):
            if idx + 1 not in errors_by_row:
                record._raw_data['_excel_row'] = idx + 1
                final_valid_records.append(record)

        return final_valid_records, final_errors
