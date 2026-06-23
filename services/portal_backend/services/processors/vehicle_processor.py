"""
Vehicle insurance processor implementation
Inherits from IInsuranceProcessor
"""
import re
from datetime import datetime, date
from typing import Any, Dict, List, Tuple

import pandas as pd

from configs.mappings.vehicle_mapping import VehicleMapping
from models.contract_model import ContractRecord
from services.processors.base_processor import IInsuranceProcessor


class VehicleProcessor(IInsuranceProcessor):
    """
    Processor for Vehicle Insurance.

    Processing specifics:
    - Mirror payer info to people info (vehicle owner = insured person)
    - Normalize phone/email and vehicle identifiers
    - Merge date + time fields into datetime fields
    - Validate fee and contact data
    """

    def __init__(self):
        super().__init__(VehicleMapping())

    @staticmethod
    def _normalize_phone_number(value: Any) -> Any:
        if value is None:
            return value
        text = str(value).strip()
        if not text or text.lower() == "nan":
            return None
        if text.endswith(".0"):
            text = text[:-2]
        digits = "".join(ch for ch in text if ch.isdigit())
        if not digits:
            return None
        # Excel often drops leading zero for phone columns stored as numeric.
        # Example: 0918397534 -> 918397534, so we restore it when length is 9.
        if len(digits) == 9:
            digits = f"0{digits}"
        return digits

    @staticmethod
    def _normalize_person_name(value: Any) -> Any:
        if not value or not isinstance(value, str):
            return value
        return " ".join(value.split())

    @staticmethod
    def _clean_license_plate(value: Any) -> Any:
        if value is None:
            return None
        text = str(value).strip().upper()
        if not text or text.lower() == "nan":
            return None
        return "".join(ch for ch in text if ch.isalnum() or ch == "-")

    @staticmethod
    def _clean_engine_or_chassis(value: Any) -> Any:
        if value is None:
            return None
        text = str(value).strip().upper()
        if not text or text.lower() == "nan":
            return None
        return "".join(ch for ch in text if ch.isalnum())

    @staticmethod
    def _parse_vi_date(value: Any) -> Any:
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime(value.year, value.month, value.day)
        if hasattr(value, "to_pydatetime"):
            try:
                return value.to_pydatetime()
            except Exception:
                return None
        if not isinstance(value, str):
            return None

        text = value.strip()
        if not text:
            return None

        try:
            # Common DB-like datetime strings: "YYYY-MM-DD HH:MM:SS".
            if " " in text:
                text = text.split(" ")[0]

            # ISO datetime strings: "YYYY-MM-DDTHH:MM:SS".
            if "T" in text:
                text = text.split("T")[0]

            if "/" in text:
                parts = [p.strip() for p in text.split("/") if p.strip()]
                if len(parts) == 3:
                    day, month, year = parts
                    if len(year) == 2:
                        year = f"20{year}"
                    return datetime(int(year), int(month), int(day))
                # Handle malformed values like "21/1/2/2024" -> "21/12/2024"
                if len(parts) == 4 and len(parts[1]) == 1 and len(parts[2]) == 1:
                    day = parts[0]
                    month = f"{parts[1]}{parts[2]}"
                    year = parts[3]
                    return datetime(int(year), int(month), int(day))
                return None

            if "-" in text:
                iso = text
                iso_parts = [p.strip() for p in iso.split("-") if p.strip()]
                if len(iso_parts) != 3:
                    return None

                # Support both YYYY-MM-DD and DD-MM-YY/DD-MM-YYYY.
                if len(iso_parts[0]) == 4:
                    year, month, day = iso_parts
                else:
                    day, month, year = iso_parts
                    if len(year) == 2:
                        year = f"20{year}"
                return datetime(int(year), int(month), int(day))

            return datetime.fromisoformat(text.split("T")[0])
        except Exception:
            return None

    @staticmethod
    def _parse_time_hhmm(value: Any) -> Tuple[int, int]:
        if value is None:
            return None, None
        text = str(value).strip()
        if not text:
            return None, None
        parts = text.split(":")
        if len(parts) < 2:
            return None, None
        try:
            hour = int(parts[0])
            minute = int(parts[1])
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return hour, minute
            return None, None
        except Exception:
            return None, None

    @staticmethod
    def _format_db_date(value: Any) -> Any:
        dt = VehicleProcessor._parse_vi_date(value)
        return dt.strftime("%Y-%m-%d") if dt else value

    @staticmethod
    def _merge_date_time_to_db_datetime(date_value: Any, time_value: Any) -> Any:
        date_dt = VehicleProcessor._parse_vi_date(date_value)
        if not date_dt:
            return date_value

        hour, minute = VehicleProcessor._parse_time_hhmm(time_value)
        if hour is None:
            return date_dt.strftime("%Y-%m-%d")

        merged = date_dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
        return merged.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _parse_amount(value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        text = str(value).strip()
        if not text or text in ["-", "--", "nan", "None"]:
            return None
        text = text.replace(".", "").replace(",", ".")
        return float(text)

    @staticmethod
    def _parse_contract_period_value(value: Any) -> Any:
        """Parse contract period to positive integer (e.g. '1 năm' -> 1)."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            parsed = int(float(value))
            return parsed if parsed > 0 else None

        text = str(value).strip().lower()
        if not text or text in ["nan", "none", "-"]:
            return None

        # Extract first numeric token from text formats like: "1 năm", "12 tháng", "365 ngày".
        match = re.search(r"\d+(?:[\.,]\d+)?", text)
        if not match:
            return None

        number_text = match.group(0).replace(",", ".")
        try:
            parsed = int(float(number_text))
            return parsed if parsed > 0 else None
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _build_amount_too_small_message(label: str, parsed_amount: float) -> str:
        base_message = f"{label} phải lớn hơn hoặc bằng 1.000"
        if parsed_amount is not None and 0 < parsed_amount < 1000:
            suggested = int(round(parsed_amount * 1000))
            suggested_text = f"{suggested:,}".replace(",", ".")
            return f"{base_message}. Có thể sai đơn vị (nghìn đồng). Vui lòng kiểm tra, ví dụ {parsed_amount:g} -> {suggested_text}"
        return base_message

    def pre_process(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.dropna(how="all")
        df = df.reset_index(drop=True)
        return df

    def post_process(self, records: List[ContractRecord]) -> List[ContractRecord]:
        for record in records:
            if not hasattr(record, "_raw_data"):
                continue
            raw = record._raw_data

            raw["payerName"] = self._normalize_person_name(raw.get("payerName"))

            if not raw.get("peopleName") and raw.get("payerName"):
                raw["peopleName"] = raw.get("payerName")
            else:
                raw["peopleName"] = self._normalize_person_name(raw.get("peopleName"))

            if not raw.get("peoplePhone") and raw.get("payerPhone"):
                raw["peoplePhone"] = raw.get("payerPhone")
            if not raw.get("peopleEmail") and raw.get("payerEmail"):
                raw["peopleEmail"] = raw.get("payerEmail")
            if not raw.get("peopleAddress") and raw.get("payerAddress"):
                raw["peopleAddress"] = raw.get("payerAddress")

            raw["payerPhone"] = self._normalize_phone_number(raw.get("payerPhone"))
            raw["peoplePhone"] = self._normalize_phone_number(raw.get("peoplePhone"))

            if raw.get("payerEmail"):
                raw["payerEmail"] = str(raw.get("payerEmail")).strip().lower()
            if raw.get("peopleEmail"):
                raw["peopleEmail"] = str(raw.get("peopleEmail")).strip().lower()

            raw["licensePlate"] = self._clean_license_plate(raw.get("licensePlate"))
            raw["chassisNumber"] = self._clean_engine_or_chassis(raw.get("chassisNumber"))
            raw["engineNumber"] = self._clean_engine_or_chassis(raw.get("engineNumber"))

            raw["payment_date"] = self._format_db_date(raw.get("payment_date"))
            raw["contractObjectStartDate"] = self._merge_date_time_to_db_datetime(
                raw.get("contractObjectStartDate"), raw.get("start_time")
            )
            raw["contractObjectEndDate"] = self._merge_date_time_to_db_datetime(
                raw.get("contractObjectEndDate"), raw.get("end_time")
            )

            # start_time/end_time are helper fields only, do not persist separately
            raw.pop("start_time", None)
            raw.pop("end_time", None)

            if raw.get("peopleRelationship") is None:
                raw["peopleRelationship"] = 0

        return records

    def validate_records(self, records: List[ContractRecord]) -> Tuple[List[ContractRecord], List[Dict[str, Any]]]:
        valid_records_base, detailed_errors = super().validate_records(records)
        errors_by_row = {err["row"]: err for err in detailed_errors}

        def add_error(row_idx: int, field: str, error_type: str, message: str, current_value: Any = None):
            excel_col = self.mapping._get_excel_column_for_field(field)
            if row_idx not in errors_by_row:
                record_dict = records[row_idx - 2].to_dict() if len(records) >= row_idx - 1 else {}
                errors_by_row[row_idx] = {
                    "row": row_idx,
                    "excel_row": row_idx,
                    "error_count": 0,
                    "field_errors": [],
                    "record_preview": {
                        "contractId": record_dict.get("contractId", "(trống)"),
                        "peopleName": record_dict.get("peopleName", "(trống)"),
                        "majorName": record_dict.get("majorName", "(trống)"),
                        "companyProviderName": record_dict.get("companyProviderName", "(trống)"),
                    },
                }
            errors_by_row[row_idx]["field_errors"].append(
                {
                    "field": field,
                    "excel_column": excel_col,
                    "error_type": error_type,
                    "message": message,
                    "current_value": current_value,
                }
            )
            errors_by_row[row_idx]["error_count"] += 1

        for idx, record in enumerate(records, start=1):
            row_number = idx + 1
            raw = record._raw_data if hasattr(record, "_raw_data") else record.to_dict()

            payer_phone = self._normalize_phone_number(raw.get("payerPhone"))
            if payer_phone:
                raw["payerPhone"] = payer_phone
                if not re.match(r"^0\d{9,10}$", payer_phone):
                    add_error(
                        row_number,
                        "payerPhone",
                        "FORMAT_PHONE",
                        "SĐT phải bắt đầu bằng số 0, 10-11 số, không khoảng trắng",
                        raw.get("payerPhone"),
                    )

            payer_email = raw.get("payerEmail")
            if payer_email:
                email_text = str(payer_email).strip().lower()
                raw["payerEmail"] = email_text
                if "@" not in email_text:
                    add_error(
                        row_number,
                        "payerEmail",
                        "FORMAT_EMAIL",
                        "Email không hợp lệ (phải chứa @)",
                        payer_email,
                    )

            fee_total = raw.get("feeInsurance")
            if fee_total is not None:
                try:
                    fee_value = self._parse_amount(fee_total)
                    if fee_value is None or fee_value < 1000:
                        add_error(
                            row_number,
                            "feeInsurance",
                            "INVALID_AMOUNT",
                            self._build_amount_too_small_message("Phí bảo hiểm", fee_value),
                            fee_total,
                        )
                    else:
                        raw["feeInsurance"] = fee_value
                except (ValueError, TypeError):
                    add_error(
                        row_number,
                        "feeInsurance",
                        "INVALID_AMOUNT",
                        "Phí bảo hiểm phải là số hợp lệ",
                        fee_total,
                    )

            period_value = raw.get("contractPeriodValue")
            if period_value is not None:
                period_int = self._parse_contract_period_value(period_value)
                if period_int is None:
                    add_error(
                        row_number,
                        "contractPeriodValue",
                        "INVALID_VALUE",
                        "Số ngày/năm bảo hiểm phải là số nguyên dương hợp lệ",
                        period_value,
                    )
                else:
                    raw["contractPeriodValue"] = period_int

            payment_raw = raw.get("payment_date")
            payment_dt = self._parse_vi_date(payment_raw)
            if payment_raw not in (None, "") and payment_dt is None:
                add_error(
                    row_number,
                    "payment_date",
                    "INVALID_DATE",
                    "Ngày thanh toán không đúng định dạng ngày hợp lệ",
                    payment_raw,
                )

            start_raw = raw.get("contractObjectStartDate")
            end_raw = raw.get("contractObjectEndDate")
            start_dt = self._parse_vi_date(start_raw)
            end_dt = self._parse_vi_date(end_raw)

            if start_raw not in (None, "") and start_dt is None:
                add_error(
                    row_number,
                    "contractObjectStartDate",
                    "INVALID_DATE",
                    "Ngày bắt đầu hiệu lực không đúng định dạng ngày hợp lệ",
                    start_raw,
                )

            if end_raw not in (None, "") and end_dt is None:
                add_error(
                    row_number,
                    "contractObjectEndDate",
                    "INVALID_DATE",
                    "Ngày kết thúc hiệu lực không đúng định dạng ngày hợp lệ",
                    end_raw,
                )

            if start_dt and end_dt and end_dt < start_dt:
                add_error(
                    row_number,
                    "contractObjectEndDate",
                    "INVALID_DATE",
                    "Ngày kết thúc phải >= Ngày bắt đầu",
                    raw.get("contractObjectEndDate"),
                )

        all_errors = sorted(errors_by_row.values(), key=lambda e: e["row"])

        invalid_rows = {err["row"] for err in all_errors}
        valid_records = [record for idx, record in enumerate(records, start=1) if (idx + 1) not in invalid_rows]

        return valid_records, all_errors
