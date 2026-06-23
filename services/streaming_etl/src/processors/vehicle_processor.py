"""
Vehicle insurance processor implementation.
Mirrors backend services/processors/vehicle_processor.py
"""
import pandas as pd
from typing import List
from processors.base_processor import IInsuranceProcessor
from models.contract_model import ContractRecord
from configs.mappings.vehicle_mapping import VehicleMapping


class VehicleProcessor(IInsuranceProcessor):
    """
    Processor for Vehicle Insurance (Ô tô).

    Processing specifics:
    - Maps 'peopleName' to 'name' for business key
    - Handles vehicle-specific field validations
    """

    def __init__(self):
        super().__init__(VehicleMapping())

    def pre_process(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.dropna(how='all')
        df = df.reset_index(drop=True)
        return df

    def post_process(self, records: List[ContractRecord]) -> List[ContractRecord]:
        for record in records:
            if not record.name and record.people_name:
                record.name = record.people_name
        return records
