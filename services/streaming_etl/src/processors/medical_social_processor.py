"""
Medical-Social insurance processor implementation.
Mirrors backend services/processors/medical_social_processor.py
"""
import logging
import pandas as pd
from typing import List
from processors.base_processor import IInsuranceProcessor
from models.contract_model import ContractRecord
from configs.mappings.medical_social_mapping import MedicalSocialMapping

logger = logging.getLogger(__name__)


class MedicalSocialProcessor(IInsuranceProcessor):
    """
    Processor for Medical & Social Insurance (BHYT & BHXH).

    Processing specifics:
    - Can contain both Medical (BHYT) and Social (BHXH) records
    - Detects sub-type from 'Loại sản phẩm' column
    - Maps 'peopleName' to 'name' for business key
    - Converts gender/relationship text to integers
    """

    # Gender mapping: Text → Integer
    GENDER_MAP = {
        'Nam': 1, 'nam': 1, 'NAM': 1, 'Male': 1, 'male': 1, 'M': 1, 'm': 1,
        'Nữ': 0, 'nữ': 0, 'NỮ': 0, 'Female': 0, 'female': 0, 'F': 0, 'f': 0,
    }

    # Insurance sub-type keywords: used to resolve MEDICAL or SOCIAL from 'Loại sản phẩm'
    INSURANCE_TYPE_KEYWORDS = {
        'SOCIAL': ['bhxh', 'bảo hiểm xã hội', 'xã hội'],
        'MEDICAL': ['bhyt', 'bảo hiểm y tế', 'y tế'],
    }

    # Relationship mapping: Text → Integer
    RELATIONSHIP_MAP = {
        'Bản thân': 0, 'Bản Thân': 0, 'BẢN THÂN': 0, 'bản thân': 0, 'BT': 0, 'SELF': 0,
        'Bố': 1, 'Mẹ': 1, 'Cha': 1, 'Ba': 1, 'Má': 1, 'Bố/Mẹ đẻ': 1, 'Bố/Mẹ': 1, 'BM': 1, 'PARENT': 1,
        'Vợ': 2, 'Chồng': 2, 'Vợ/Chồng': 2, 'VC': 2, 'COUPLE': 2,
        'Anh': 3, 'Chị': 3, 'Em': 3, 'Anh/Chị/Em ruột': 3, 'Anh/Chị/Em': 3, 'ACE': 3, 'SIBLING': 3,
        'Con': 4, 'Con đẻ': 4, 'Con nuôi': 4, 'Con đẻ/nuôi hợp pháp': 4, 'CON': 4, 'CHILDREN': 4,
        'Khác': 5, 'OTHER': 5,
        'Bố/Mẹ của vợ/chồng': 6, 'Bố vợ': 6, 'Mẹ vợ': 6, 'Bố chồng': 6, 'Mẹ chồng': 6,
    }

    @classmethod
    def _resolve_insurance_type(cls, type_text: str) -> str:
        """Resolve 'Loại sản phẩm' text → 'MEDICAL' or 'SOCIAL'. Falls back to 'MEDICAL_SOCIAL'."""
        text_lower = type_text.lower().strip()
        for insurance_type, keywords in cls.INSURANCE_TYPE_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    return insurance_type
        logger.warning("Cannot resolve insurance type from text: '%s', defaulting to MEDICAL_SOCIAL", type_text)
        return 'MEDICAL_SOCIAL'

    def __init__(self):
        super().__init__(MedicalSocialMapping())

    def pre_process(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.dropna(how='all')
        df = df.reset_index(drop=True)
        return df

    def post_process(self, records: List[ContractRecord]) -> List[ContractRecord]:
        for record in records:
            # Ensure name field is set from peopleName
            if not record.name and record.people_name:
                record.name = record.people_name

            if hasattr(record, '_raw_data'):
                # Resolve actual insurance type (MEDICAL or SOCIAL) from 'Loại sản phẩm' column
                type_text = record._raw_data.pop('insuranceType_text', None)
                if type_text is not None:
                    actual_type = self._resolve_insurance_type(str(type_text))
                    record._raw_data['insuranceType'] = actual_type
                    record.insurance_type = actual_type

                # Convert peopleGender text to integer
                if 'peopleGender' in record._raw_data:
                    gender_value = record._raw_data['peopleGender']
                    if isinstance(gender_value, str) and gender_value.strip():
                        converted = self.GENDER_MAP.get(gender_value.strip())
                        if converted is not None:
                            record._raw_data['peopleGender'] = converted
                        else:
                            record._raw_data.pop('peopleGender', None)

                # Convert peopleRelationship text to integer
                if 'peopleRelationship' in record._raw_data:
                    rel_value = record._raw_data['peopleRelationship']
                    if isinstance(rel_value, str) and rel_value.strip():
                        converted = self.RELATIONSHIP_MAP.get(rel_value.strip())
                        if converted is not None:
                            record._raw_data['peopleRelationship'] = converted
                        else:
                            logger.warning("Unknown relationship value: '%s'", rel_value)
                            record._raw_data.pop('peopleRelationship', None)

        return records
