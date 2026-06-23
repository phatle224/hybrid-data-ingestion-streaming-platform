"""
Hazard insurance processor implementation.
Mirrors backend services/processors/hazard_processor.py
"""
import pandas as pd
from typing import List
from processors.base_processor import IInsuranceProcessor
from models.contract_model import ContractRecord
from configs.mappings.hazard_mapping import HazardMapping


class HazardProcessor(IInsuranceProcessor):
    """
    Processor for Hazard Insurance (Bảo hiểm rủi ro).

    Processing specifics:
    - Handles offline-only insurance data
    - Maps status (Trạng thái) to termsFeePaymentMethod
    """

    def __init__(self):
        super().__init__(HazardMapping())

    def pre_process(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.dropna(how='all')
        df = df.reset_index(drop=True)
        return df

    def post_process(self, records: List[ContractRecord]) -> List[ContractRecord]:
        # Could add derived field calculations
        return records
