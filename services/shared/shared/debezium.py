"""
Debezium CDC message transformer.
Shared logic for converting Debezium format values to MySQL-compatible format.

Consolidates duplicated convert_debezium_value() and extract_operation_and_data()
from cdc_consumer.py, streaming_etl_consumer.py, and profiling_consumer.py.
"""
import logging
from datetime import datetime, date, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


# =============================================================================
# Field Classification (merged from all consumers)
# =============================================================================

DATETIME_FIELDS = {
    'createdAt', 'modifiedAt', 'modifiedDate', 'causeDate',
    'outsideCreatedAt', 'outsidePaymentAt', 'admissionDate',
    'createdAt_7', 'modifiedAt_9',
    'topupRegisterDate', 'relateRegisterDate', 'employeeRegisterDate',
    'contractStartDate', 'contractEndDate',
    'contractObjectStartDate', 'contractObjectEndDate',
    'startDate', 'endDate',
}

DATE_FIELDS = {
    'dob', 'peopleDob', 'payerDob',
    'hospitalizedDate', 'hospitalDischargeDate',
    'oldCardStartDate', 'oldCardEndDate',
    'startDateJourney', 'endDateJourney',
    'fiveYearDate', 'oldRegisterDate',
}


# =============================================================================
# Debezium Transformer
# =============================================================================

class DebeziumTransformer:
    """
    Transforms Debezium CDC messages to MySQL-compatible format.

    Handles:
    - Datetime fields (milliseconds since epoch → datetime)
    - Date fields (days or milliseconds since epoch → date)
    - Operation extraction from wrapped/unwrapped messages
    - Full data transformation pipeline

    This class uses only static/class methods — no state needed.
    """

    @staticmethod
    def convert_value(value: Any, field_name: str) -> Any:
        """
        Convert Debezium special format values to MySQL format.

        Args:
            value: Raw value from Debezium message
            field_name: Column name (used to determine conversion type)

        Returns:
            Converted value suitable for MySQL insertion
        """
        if value is None:
            return None

        try:
            # --- Datetime fields (epoch milliseconds → datetime) ---
            if field_name in DATETIME_FIELDS and isinstance(value, (int, float)):
                if value < 100000:
                    # Days since epoch (due to DATE schema mismatch)
                    return datetime(1970, 1, 1) + timedelta(days=int(value))
                else:
                    dt = datetime.fromtimestamp(value / 1000.0, tz=timezone.utc)
                    # Return naive datetime for MySQL compatibility
                    return dt.replace(tzinfo=None)

            # --- Date fields (days/milliseconds/string → date) ---
            elif field_name in DATE_FIELDS:
                if isinstance(value, (int, float)):
                    if value > 100000:
                        # Likely milliseconds since epoch
                        return datetime.fromtimestamp(value / 1000.0).date()
                    else:
                        # Days since epoch
                        return date(1970, 1, 1) + timedelta(days=int(value))
                elif isinstance(value, str):
                    # Try YYYY-MM-DD / YYYY-M-D (strptime %m/%d match 1-2 digits)
                    if '-' in value:
                        try:
                            return datetime.strptime(value, '%Y-%m-%d').date()
                        except ValueError:
                            pass
                    # Try YYYYMMDD
                    if len(value) == 8 and value.isdigit():
                        return datetime.strptime(value, '%Y%m%d').date()
                    # Try DD/MM/YYYY
                    if '/' in value:
                        try:
                            return datetime.strptime(value, '%d/%m/%Y').date()
                        except ValueError:
                            pass
                    logger.warning(
                        "Invalid date string for %s: '%s', storing as NULL",
                        field_name, value
                    )
                    return None
                return value

            # --- All other fields: pass through ---
            return value

        except (ValueError, OSError, OverflowError) as e:
            logger.warning("Failed to convert %s=%s: %s, storing as NULL", field_name, value, e)
            return None
        except Exception as e:
            logger.warning("Unexpected error converting %s=%s: %s", field_name, value, e)
            return None

    @staticmethod
    def extract_operation_and_data(
        message_value: Dict[str, Any]
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Extract operation type and data from Debezium message.

        Supports both wrapped (payload) and unwrapped message formats.

        Returns:
            Tuple of (operation, data)
            operation: 'c' (create), 'u' (update), 'd' (delete), 'r' (read/snapshot)
        """
        try:
            # Unwrapped message (no payload wrapper) → treat as snapshot
            if 'payload' not in message_value:
                return 'r', message_value

            payload = message_value.get('payload', {})
            op = payload.get('op')  # c=create, u=update, d=delete, r=read

            if op in ['c', 'r', 'u']:
                return op, payload.get('after', {})
            elif op == 'd':
                return op, payload.get('before', {})
            else:
                logger.warning("Unknown operation type: %s", op)
                return None, None

        except Exception as e:
            logger.error("Error extracting operation: %s", e)
            return None, None

    @classmethod
    def transform_data(cls, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform all fields in raw data to MySQL-compatible format."""
        transformed = {}
        for key, value in raw_data.items():
            converted = cls.convert_value(value, key)
            if converted is not None:
                transformed[key] = converted
        return transformed

    # -----------------------------------------------------------------
    # Convenience methods for profiling consumer date parsing
    # -----------------------------------------------------------------

    @staticmethod
    def to_date(value: Any) -> Optional[date]:
        """
        Convert various date representations to Python date object.
        Handles: date, datetime, int (epoch ms), str ('YYYY-MM-DD', 'YYYY-M-D').
        """
        if value is None:
            return None
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, (int, float)):
            try:
                return datetime.fromtimestamp(value / 1000).date() if value else None
            except (OSError, OverflowError, ValueError):
                return None
        if isinstance(value, str):
            # Try YYYY-MM-DD / YYYY-M-D (strptime %m/%d match 1-2 digits)
            for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
            return None
        return None

    @staticmethod
    def to_datetime(value: Any) -> Optional[datetime]:
        """
        Convert various datetime representations to Python datetime object.
        Handles: datetime, int (epoch ms), str ('YYYY-MM-DD HH:MM:SS').
        """
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, (int, float)):
            try:
                if value < 100000:
                    # Days since epoch
                    return datetime(1970, 1, 1) + timedelta(days=int(value))
                return datetime.fromtimestamp(value / 1000) if value else None
            except (OSError, OverflowError, ValueError):
                return None
        if isinstance(value, str):
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
        return None
