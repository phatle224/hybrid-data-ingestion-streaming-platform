"""
Duplicate checking service
"""
from typing import List, Tuple, Set
from models.contract_model import ContractRecord
from repositories.contract_repository import ContractRepository


class DuplicateService:
    """Service for checking duplicate records"""
    
    def __init__(self, repository: ContractRepository):
        """
        Initialize service with repository
        
        Args:
            repository: ContractRepository instance
        """
        self.repository = repository
    
    def filter_duplicates(
        self, 
        records: List[ContractRecord]
    ) -> Tuple[List[ContractRecord], List[ContractRecord]]:
        """
        Filter records into new and duplicate lists using batch query.
        Uses 7-key deduplication: contractId, peopleName, majorName, companyProviderName, startDate, endDate, feeInsurance
        """
        if not records:
            return [], []
        
        # Get all existing business keys in ONE query
        # This returns set of 7-key tuples from database
        existing_keys = self.repository.get_existing_business_keys_batch(records)
        
        print(f"\n{'='*80}")
        print(f"DUPLICATE CHECK: Found {len(existing_keys)} existing 7-key tuples in database")
        print(f"Checking {len(records)} records from current upload")
        print(f"{'='*80}\n")
        
        new_records = []
        duplicate_records = []
        seen_in_batch: Set[tuple] = set()  # Track keys already seen in this upload
        
        for idx, record in enumerate(records):
            # Get 7-key business key using same normalization as repository
            business_keys = record.get_business_keys()
            
            # Build 7-key tuple - use exact same normalization as repository
            key = (
                str(business_keys.get("contractId") or "").strip() or None,
                str(business_keys.get("peopleName") or "").strip() or None,
                str(business_keys.get("majorName") or "").strip() or None,
                str(business_keys.get("companyProviderName") or "").strip() or None,
                business_keys.get("startDate"),  # Already returns None or str
                business_keys.get("endDate"),      # Already returns None or str
                business_keys.get("feeInsurance"), # Already returns None or str
            )
            
            if key in existing_keys:
                # Found duplicate in database
                duplicate_records.append(record)
                if idx < 3:
                    record_id = business_keys.get("contractId", "?")
                    person_name = business_keys.get("peopleName", "?")
                    print(f"  DUPLICATE (in DB): contractId={record_id}, peopleName={person_name}")
            elif key in seen_in_batch:
                # Found duplicate within current file
                duplicate_records.append(record)
                if idx < 3:
                    record_id = business_keys.get("contractId", "?")
                    person_name = business_keys.get("peopleName", "?")
                    print(f"  DUPLICATE (in file): contractId={record_id}, peopleName={person_name}")
            else:
                # New record
                new_records.append(record)
                seen_in_batch.add(key)
                if idx < 3:
                    record_id = business_keys.get("contractId", "?")
                    person_name = business_keys.get("peopleName", "?")
                    print(f"  NEW record: contractId={record_id}, peopleName={person_name}")
        
        print(f"\nResult: {len(new_records)} new, {len(duplicate_records)} duplicates\n")
        
        return new_records, duplicate_records
    
    def get_duplicate_summary(
        self,
        total_count: int,
        new_count: int,
        duplicate_count: int
    ) -> dict:
        """
        Generate summary of duplicate checking results
        
        Args:
            total_count: Total records processed
            new_count: Number of new records
            duplicate_count: Number of duplicate records
            
        Returns:
            Dictionary with summary information
        """
        return {
            "total": total_count,
            "new": new_count,
            "duplicates": duplicate_count,
            "duplicate_rate": f"{(duplicate_count / total_count * 100):.2f}%" if total_count > 0 else "0%"
        }
