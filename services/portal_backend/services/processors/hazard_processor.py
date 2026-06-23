"""
Hazard insurance processor implementation
Inherits from IInsuranceProcessor
"""
import pandas as pd
from typing import List, Tuple, Dict, Any
from datetime import datetime
from services.processors.base_processor import IInsuranceProcessor
from models.contract_model import ContractRecord
from configs.mappings.hazard_mapping import HazardMapping


class HazardProcessor(IInsuranceProcessor):
    """
    Processor for Hazard Insurance (Bảo hiểm rủi ro)
    
    Processing specifics:
    - Handles offline-only insurance data
    - Maps status (Trạng thái) to termsFeePaymentMethod
    - Stores in stgContractObjectOffline
    """
    
    def __init__(self):
        super().__init__(HazardMapping())
    
    def pre_process(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pre-process Hazard Excel data
        - Remove completely empty rows
        - Clean whitespace in string columns
        """
        # Remove rows where all values are NaN
        df = df.dropna(how='all')
        
        # Reset index
        df = df.reset_index(drop=True)
        
        return df

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
    
    def post_process(self, records: List[ContractRecord]) -> List[ContractRecord]:
        """
        Post-process Hazard records
        - Mirror payerName → peopleName (buyer = insured for hazard)
        - Set peopleRelationship = 0 (self)
        """
        for record in records:
            if hasattr(record, '_raw_data'):
                raw = record._raw_data

                # Mirror payer* → people* (buyer IS the insured)
                if not raw.get('peopleName') and raw.get('payerName'):
                    raw['peopleName'] = raw['payerName']

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

            amount = raw.get('feeInsurance')
            amount_val = None
            if amount is not None:
                try:
                    if isinstance(amount, (int, float)):
                        amount_val = float(amount)
                    else:
                        amount_str = str(amount).strip().replace('.', '').replace(',', '.')
                        amount_val = float(amount_str)
                    if amount_val < min_amount_threshold:
                        add_error(
                            row_number,
                            'feeInsurance',
                            'INVALID_AMOUNT',
                            build_amount_too_small_message('Phí bảo hiểm', amount_val),
                            amount
                        )
                    else:
                        raw['feeInsurance'] = amount_val
                except (ValueError, TypeError):
                    add_error(row_number, 'feeInsurance', 'INVALID_AMOUNT', 'Phí bảo hiểm phải là số hợp lệ', amount)

            start_dt = self._parse_vi_date(raw.get('contractObjectStartDate'))
            end_dt = self._parse_vi_date(raw.get('contractObjectEndDate'))
            pay_dt = self._parse_vi_date(raw.get('payment_date'))
            now_dt = datetime.now()

            if pay_dt and pay_dt > now_dt:
                add_error(row_number, 'payment_date', 'INVALID_DATE', 'Ngày thanh toán không được lớn hơn ngày hiện tại', raw.get('payment_date'))

            if start_dt and end_dt and end_dt <= start_dt:
                add_error(row_number, 'contractObjectEndDate', 'INVALID_DATE', 'Ngày kết thúc phải > Ngày bắt đầu', raw.get('contractObjectEndDate'))

        final_valid_records = []
        final_errors = list(errors_by_row.values())
        for idx, record in enumerate(records, start=1):
            if idx + 1 not in errors_by_row:
                record._raw_data['_excel_row'] = idx + 1
                final_valid_records.append(record)

        return final_valid_records, final_errors
