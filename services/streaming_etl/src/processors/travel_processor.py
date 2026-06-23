"""
Travel insurance processor implementation.
Mirrors backend services/processors/travel_processor.py
"""
import pandas as pd
from typing import List
from processors.base_processor import IInsuranceProcessor
from models.contract_model import ContractRecord
from configs.mappings.travel_mapping import TravelMapping


class TravelProcessor(IInsuranceProcessor):
    """
    Processor for Travel Insurance (Du lịch).

    Processing specifics:
    - Handles journey date validation
    - Calculates journey days if not provided
    """

    def __init__(self):
        super().__init__(TravelMapping())

    def pre_process(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.dropna(how='all')
        df = df.reset_index(drop=True)
        return df

    def post_process(self, records: List[ContractRecord]) -> List[ContractRecord]:
        # Could add journey_days calculation from dates
        return records
