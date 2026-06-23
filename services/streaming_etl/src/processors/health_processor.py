"""
Health insurance processor implementation.
Mirrors backend services/processors/health_processor.py

Updated to align with Portal changes:
- 2-phase gender/relationship processing (parse → validate → convert)
- Name normalization to Title Case
- Phone normalization (prepend 0 if Excel lost it)
- Buyer-as-beneficiary fallback
"""
import logging
import re
import pandas as pd
from typing import Any, List
from processors.base_processor import IInsuranceProcessor
from models.contract_model import ContractRecord
from configs.mappings.health_mapping import HealthMapping

logger = logging.getLogger(__name__)


class HealthProcessor(IInsuranceProcessor):
    """
    Processor for Health Insurance (Sức khỏe).

    Processing specifics:
    - Handles multiline Vietnamese headers
    - Has detailed benefit columns
    - Maps 'peopleName' to 'name' for business key
    - Parses gender text → canonical form → int (2-phase, aligned with Portal)
    - Parses relationship text → canonical form → int (2-phase, aligned with Portal)
    - Normalizes names to Title Case
    - Normalizes phone numbers (prepend 0 if 9 digits)
    - Buyer-as-beneficiary fallback
    """

    # Gender mapping: Canonical Text → Integer
    GENDER_MAP = {
        'Nam': 1,
        'Nữ': 0,
    }

    # Relationship mapping: Canonical Text → Integer
    # SELF(0), PARENTS(1), COUPLE(2), SIBLINGS(3), CHILDREN(4),
    # OTHER(5), WIFE_HUSBAND_PARENTS(6), GRANDCHILDREN(7), EMPLOYEE(8)
    RELATIONSHIP_MAP = {
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

    def __init__(self):
        super().__init__(HealthMapping())

    def pre_process(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.dropna(how='all')
        df = df.reset_index(drop=True)
        return df

    # ── Parse methods (Phase 1: text → canonical form) ────────────

    @staticmethod
    def _parse_gender(value: str) -> str:
        """
        Parse and normalize gender input.
        Examples: 'nam' -> 'Nam', 'FEMALE' -> 'Nữ', 'M' -> 'Nam'

        Returns standardized gender text that maps to a DB value.
        Returns original value if parsing fails.
        """
        if not value or not isinstance(value, str):
            return value

        normalized = value.strip().lower()

        # Direct canonical match
        if normalized == 'nam':
            return 'Nam'
        if normalized in ('nữ', 'nu'):
            return 'Nữ'

        # Keyword matching
        if normalized in ('male', 'm'):
            return 'Nam'
        if normalized in ('female', 'f', 'n', 'woman'):
            return 'Nữ'

        return value

    @staticmethod
    def _parse_relationship(value: str) -> str:
        """
        Parse and normalize relationship input.
        Examples: 'MẸ' -> 'Mẹ', 'chị gái' -> 'Chị', 'Con đẻ' -> 'Con'

        Returns standardized relationship text that maps to a DB value.
        Returns original value if parsing fails.
        """
        if not value or not isinstance(value, str):
            return value

        normalized = value.strip().lower()

        # Keyword matching (priority order — specific before generic)
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

        return value

    # ── Normalize methods ─────────────────────────────────────────

    @staticmethod
    def _normalize_person_name(value: Any) -> Any:
        """Normalize full name to Vietnamese-friendly Title Case.
        Example: 'trịnh bảo ngọc' → 'Trịnh Bảo Ngọc'
        """
        if not value or not isinstance(value, str):
            return value

        # Collapse repeated spaces and trim
        cleaned = " ".join(value.split())
        if not cleaned:
            return cleaned

        # Title-case each token
        return " ".join(token.capitalize() for token in cleaned.split(" "))

    @staticmethod
    def _normalize_phone_number(value: Any) -> Any:
        """Normalize phone values read from Excel, preserving/repairing leading zero.
        Excel often stores phone as number → loses leading 0 and adds .0 suffix.
        """
        if value is None:
            return value

        text = str(value).strip()
        if not text or text.lower() == 'nan':
            return None

        # Excel float suffix: 969090278.0 → 969090278
        if text.endswith('.0'):
            text = text[:-2]

        digits = ''.join(ch for ch in text if ch.isdigit())
        if not digits:
            return None

        # Common case: leading zero lost → 9 digits → prepend 0
        if len(digits) == 9:
            digits = '0' + digits

        return digits

    # ── Post-process (Phase 2: normalize + convert) ───────────────

    def post_process(self, records: List[ContractRecord]) -> List[ContractRecord]:
        """
        Post-process Health records:
        - Normalize names to Title Case
        - Normalize phone numbers
        - Buyer-as-beneficiary fallback
        - Convert gender/relationship text → int (2-phase approach)
        """
        for record in records:
            # Ensure name field is set from peopleName
            if not record.name and record.people_name:
                record.name = record.people_name

            if hasattr(record, '_raw_data'):
                raw = record._raw_data

                # ── Name normalization (Title Case) ──
                raw['payerName'] = self._normalize_person_name(raw.get('payerName'))
                raw['peopleName'] = self._normalize_person_name(raw.get('peopleName'))
                record.payer_name = raw.get('payerName')
                record.people_name = raw.get('peopleName')

                # ── Phone normalization ──
                raw['payerPhone'] = self._normalize_phone_number(raw.get('payerPhone'))
                raw['leadPhone'] = self._normalize_phone_number(raw.get('leadPhone'))
                raw['customerPhone'] = self._normalize_phone_number(raw.get('customerPhone'))
                raw['peoplePhone'] = self._normalize_phone_number(raw.get('peoplePhone'))

                # Phone fallback: prefer customerPhone, then leadPhone
                if not raw.get('payerPhone'):
                    raw['payerPhone'] = raw.get('customerPhone') or raw.get('leadPhone')

                # ── Buyer-as-beneficiary fallback ──
                if not raw.get('peopleName') and raw.get('payerName'):
                    raw['peopleName'] = raw['payerName']
                    record.people_name = raw['peopleName']
                    if raw.get('peopleRelationship') is None:
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

                # ── Convert gender: parse → canonical → int ──
                if 'peopleGender' in raw:
                    gender_value = raw['peopleGender']
                    if isinstance(gender_value, str) and gender_value.strip():
                        parsed_gender = self._parse_gender(gender_value.strip())
                        converted = self.GENDER_MAP.get(parsed_gender)
                        if converted is not None:
                            raw['peopleGender'] = converted
                        else:
                            logger.warning("Unknown gender value: '%s' - removing field", gender_value)
                            raw.pop('peopleGender', None)

                # ── Convert relationship: parse → canonical → int ──
                if 'peopleRelationship' in raw:
                    rel_value = raw['peopleRelationship']
                    if isinstance(rel_value, str) and rel_value.strip():
                        parsed_rel = self._parse_relationship(rel_value.strip())
                        converted = self.RELATIONSHIP_MAP.get(parsed_rel)
                        if converted is not None:
                            raw['peopleRelationship'] = converted
                        else:
                            logger.warning("Unknown relationship value: '%s' - removing field", rel_value)
                            raw.pop('peopleRelationship', None)

                # Update record name after all normalization
                if raw.get('peopleName') and not record.name:
                    record.name = raw['peopleName']

        return records
