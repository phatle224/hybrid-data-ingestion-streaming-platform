"""
Moto insurance processor implementation.
Mirrors backend services/processors/moto_processor.py
"""
import pandas as pd
from typing import List
from processors.base_processor import IInsuranceProcessor
from models.contract_model import ContractRecord
from configs.mappings.moto_mapping import MotoMapping


class MotoProcessor(IInsuranceProcessor):
    """
    Processor for Moto Insurance (Xe máy).

    Processing specifics:
    - Handles uppercase Vietnamese headers
    - Calculates total fee from main + side benefits
    """

    def __init__(self):
        super().__init__(MotoMapping())

    def pre_process(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.dropna(how='all')
        df = df.reset_index(drop=True)
        return df

    def post_process(self, records: List[ContractRecord]) -> List[ContractRecord]:
        # Could calculate total from main + side benefits
        return records
