"""
Contract repository - handles database operations
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from decimal import Decimal
from models.contract_model import ContractRecord
from configs.database.db_config import DatabaseConfig, DatabaseConnection
from configs.app.settings import app_settings


class ContractRepository:
    """Repository for contract database operations"""
    
    # Allowed table names (whitelist for SQL injection prevention)
    ALLOWED_TABLES = {"stgInsuranceContractObjectOffline"}

    @staticmethod
    def _normalize_fee_key(value: Any) -> Any:
        if value is None or value == "":
            return None
        try:
            if isinstance(value, (int, float, Decimal)):
                num = float(value)
            else:
                text = str(value).strip()
                if not text:
                    return None
                text = text.replace('.', '').replace(',', '.')
                num = float(text)
            return f"{num:.6f}".rstrip('0').rstrip('.')
        except (ValueError, TypeError):
            return str(value).strip() or None

    @staticmethod
    def _normalize_date_key(value: Any) -> Any:
        """Normalize date/datetime value to YYYY-MM-DD for duplicate key comparison."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")
        if isinstance(value, date):
            return value.strftime("%Y-%m-%d")

        text = str(value).strip()
        if not text:
            return None

        if " " in text:
            text = text.split(" ")[0]
        if "T" in text:
            text = text.split("T")[0]

        try:
            return datetime.fromisoformat(text).strftime("%Y-%m-%d")
        except ValueError:
            return text
    
    def __init__(self, db_config: DatabaseConfig):
        """
        Initialize repository with database config
        
        Args:
            db_config: Database configuration instance
        """
        self.db_config = db_config
        self.table_name = app_settings.staging_table
        
        # Validate table name against whitelist
        if self.table_name not in self.ALLOWED_TABLES:
            raise ValueError(f"Invalid table name: {self.table_name}. Allowed: {self.ALLOWED_TABLES}")
    
    def get_existing_business_keys_batch(self, records: List[ContractRecord]) -> set:
        """
        Get all existing business keys that match any of the records in ONE query
        This is much faster than checking each record individually
        
        Args:
            records: List of ContractRecord to check
            
        Returns:
            Set of tuples (contractId, peopleName, majorName, companyProviderName, startDate, endDate, feeInsurance)
        """
        if not records:
            return set()
        
        # Collect unique 4-key combinations for database query
        keys_to_check = set()
        for record in records:
            bk = record.get_business_keys()
            keys_to_check.add((
                bk.get("contractId"),
                bk.get("peopleName"),
                bk.get("majorName"),
                bk.get("companyProviderName")
            ))
        
        if not keys_to_check:
            return set()
        
        existing_keys = set()
        
        # Query database for records matching the 4 core business keys
        # Then we'll normalize dates/fees and build 7-key tuples in Python
        with DatabaseConnection(self.db_config) as db:
            # Build query for all combinations of 4-key groups
            # This is more efficient than multiple queries
            conditions = []
            params = []
            
            for contract_id, people_name, major_name, company_provider in keys_to_check:
                conditions.append('("contractId" = %s AND "peopleName" = %s AND "majorName" = %s AND "companyProviderName" = %s)')
                params.extend([
                    str(contract_id) if contract_id is not None else None,
                    str(people_name) if people_name is not None else None,
                    str(major_name) if major_name is not None else None,
                    str(company_provider) if company_provider is not None else None
                ])
            
            where_clause = " OR ".join(conditions)
            
            query = f"""
                SELECT 
                    "contractId", "peopleName", "majorName", "companyProviderName",
                    "feeInsurance",
                    "contractObjectStartDate", "contractObjectEndDate",
                    "startDateJourney", "endDateJourney",
                    "contractStartDate", "contractEndDate"
                FROM "{self.table_name}"
                WHERE {where_clause}
            """
            
            db.execute(query, tuple(params))
            rows = db.fetchall()
            
            print(f"\nDUPLICATE CHECK: Query found {len(rows)} existing records with matching 4-key groups")
            
            # Build set of 7-key tuples from database results
            for idx, row in enumerate(rows):
                # NORMALIZE core business keys
                contract_id = str(row.get("contractId") or "").strip() or None
                people_name = str(row.get("peopleName") or "").strip() or None
                major_name = str(row.get("majorName") or "").strip() or None
                company_provider = str(row.get("companyProviderName") or "").strip() or None
                
                # NORMALIZE dates using same logic as ContractRecord
                # Try fields in priority order: journey > contractObject > contract > insurance
                start_date = self._normalize_date_key(
                    row.get("startDateJourney") or 
                    row.get("contractObjectStartDate") or 
                    row.get("contractStartDate") or 
                    ""
                )
                
                end_date = self._normalize_date_key(
                    row.get("endDateJourney") or 
                    row.get("contractObjectEndDate") or 
                    row.get("contractEndDate") or 
                    ""
                )
                
                # NORMALIZE fee using same method as ContractRecord
                fee_insurance = self._normalize_fee_key(row.get("feeInsurance"))
                
                # Build 7-key tuple
                key = (contract_id, people_name, major_name, company_provider, start_date, end_date, fee_insurance)
                existing_keys.add(key)
                
                if idx < 3:
                    print(f"  Found existing 7-key: contractId={contract_id}, peopleName={people_name}, "
                          f"startDate={start_date}, endDate={end_date}, fee={fee_insurance}")
        
        print(f"Total unique existing 7-key tuples: {len(existing_keys)}\n")
        return existing_keys
    
    def check_duplicate(self, record: ContractRecord) -> bool:
        """
        Check if record exists based on business keys
        
        Args:
            record: ContractRecord to check
            
        Returns:
            True if duplicate exists, False otherwise
        """
        business_keys = record.get_business_keys()
        
        with DatabaseConnection(self.db_config) as db:
            # Check using peopleName as business key
            query = f"""
                SELECT 
                    "feeInsurance",
                    "contractObjectStartDate", "contractObjectEndDate",
                    "startDateJourney", "endDateJourney",
                    "contractStartDate", "contractEndDate"
                FROM "{self.table_name}"
                WHERE "contractId" = %s 
                AND "peopleName" = %s
                AND "majorName" = %s 
                AND "companyProviderName" = %s
            """
            
            db.execute(query, (
                business_keys["contractId"],
                business_keys["peopleName"],
                business_keys["majorName"],
                business_keys["companyProviderName"]
            ))
            
            rows = db.fetchall()
            target_start = self._normalize_date_key(business_keys.get("startDate"))
            target_end = self._normalize_date_key(business_keys.get("endDate"))
            target_fee = self._normalize_fee_key(business_keys.get("feeInsurance"))
            
            for row in rows:
                db_start = self._normalize_date_key(
                    row.get("startDateJourney") or row.get("contractObjectStartDate") or row.get("contractStartDate")
                )
                db_end = self._normalize_date_key(
                    row.get("endDateJourney") or row.get("contractObjectEndDate") or row.get("contractEndDate")
                )
                db_fee = self._normalize_fee_key(row.get("feeInsurance"))
                if db_start == target_start and db_end == target_end and db_fee == target_fee:
                    return True
                    
            return False
    
    def check_duplicates_batch(self, records: List[ContractRecord]) -> List[bool]:
        """
        Check duplicates for multiple records efficiently
        
        Args:
            records: List of ContractRecord to check
            
        Returns:
            List of boolean indicating duplicate status for each record
        """
        if not records:
            return []
        
        results = []
        with DatabaseConnection(self.db_config) as db:
            for record in records:
                is_duplicate = self.check_duplicate(record)
                results.append(is_duplicate)
        
        return results
    
    def insert_record(self, record: ContractRecord) -> bool:
        """
        Insert a single record into database
        
        Args:
            record: ContractRecord to insert
            
        Returns:
            True if successful, False otherwise
        """
        record_dict = record.to_dict()
        valid_columns = app_settings.valid_db_columns
        
        # Filter to ONLY include valid DB schema columns
        filtered_data = {}
        for k, v in record_dict.items():
            if v is not None and k in valid_columns:
                filtered_data[k] = v
        
        if not filtered_data:
            return False
        
        # Escape column names with double quotes for PostgreSQL
        columns = ", ".join([f'"{k}"' for k in filtered_data.keys()])
        placeholders = ", ".join(["%s"] * len(filtered_data))
        values = tuple(filtered_data.values())
        
        with DatabaseConnection(self.db_config) as db:
            query = f"""
                INSERT INTO "{self.table_name}" ({columns})
                VALUES ({placeholders})
            """
            db.execute(query, values)
            db.commit()
        
        return True
    
    def insert_records_batch(self, records: List[ContractRecord]) -> tuple:
        """
        Insert multiple records into database
        
        Args:
            records: List of ContractRecord to insert
            
        Returns:
            Tuple of (inserted_list, failed_list) where each failed item is
            (record, error_message)
        """
        if not records:
            return [], []
        
        inserted_records = []
        failed_records = []
        valid_columns = app_settings.valid_db_columns
        
        with DatabaseConnection(self.db_config) as db:
            for record in records:
                try:
                    record_dict = record.to_dict()
                    
                    # Filter to ONLY include valid DB schema columns
                    filtered_data = {}
                    for k, v in record_dict.items():
                        if v is not None and k in valid_columns:
                            filtered_data[k] = v
                    
                    if not filtered_data:
                        error_msg = "Record has no valid columns after filtering"
                        print(f"Warning: {error_msg}")
                        failed_records.append((record, error_msg))
                        continue
                    
                    # Escape column names with double quotes for PostgreSQL
                    columns = ", ".join([f'"{k}"' for k in filtered_data.keys()])
                    placeholders = ", ".join(["%s"] * len(filtered_data))
                    values = tuple(filtered_data.values())
                    
                    query = f"""
                        INSERT INTO "{self.table_name}" ({columns})
                        VALUES ({placeholders})
                    """
                    db.execute(query, values)
                    inserted_records.append(record)
                except Exception as e:
                    error_msg = str(e)
                    print(f"Error inserting record (contractId={record.contract_id}, peopleName={record.people_name}): {error_msg}")
                    failed_records.append((record, error_msg))
                    continue
            
            db.commit()
        
        return inserted_records, failed_records
    
    def get_all_records(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve all records from database
        
        Args:
            limit: Optional limit on number of records
            
        Returns:
            List of record dictionaries
        """
        with DatabaseConnection(self.db_config) as db:
            query = f'SELECT * FROM "{self.table_name}"'
            if limit:
                query += f" LIMIT {limit}"
            
            db.execute(query)
            return db.fetchall()
    
    def delete_all_records(self) -> int:
        """
        Delete all records from table (use with caution!)
        
        Returns:
            Number of deleted records
        """
        with DatabaseConnection(self.db_config) as db:
            db.execute(f'SELECT COUNT(*) as count FROM "{self.table_name}"')
            result = db.fetchone()
            count = result["count"] if result else 0
            
            db.execute(f'DELETE FROM "{self.table_name}"')
            db.commit()
            
            return count
