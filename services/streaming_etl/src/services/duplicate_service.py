"""
Redis-based duplicate checking service for ETL consumer.
Consumer version: uses Redis cache (online data wins over offline).
Backend version: uses DB-based dedup (see backend/services/duplicate_service.py).
"""
import json
import logging
from typing import List, Tuple, Optional, Dict
from models.contract_model import ContractRecord

logger = logging.getLogger(__name__)


class RedisDuplicateService:
    """
    Service for checking duplicate records against Redis cache.
    Implements "online wins" policy: if a record exists in Redis (from CDC online),
    the offline Excel record is treated as a duplicate and skipped.
    """

    REDIS_KEY_PREFIX = "contract:dedup"

    def __init__(self, redis_client=None):
        """
        Initialize service with optional Redis client.

        Args:
            redis_client: redis.Redis instance (or None to disable dedup)
        """
        self._redis = redis_client
        self._enabled = redis_client is not None

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def _build_business_key(self, record: ContractRecord) -> str:
        """
        Build Redis key from business key components.
        Format: contract:dedup:{contractId}:{name}:{majorName}:{companyProviderName}
        """
        keys = record.get_business_keys()
        contract_id = str(keys.get('contractId') or '').strip()
        name = str(keys.get('name') or '').strip().lower()
        major_name = str(keys.get('majorName') or '').strip().lower()
        company_provider = str(keys.get('companyProviderName') or '').strip().lower()

        return f"{self.REDIS_KEY_PREFIX}:{contract_id}:{name}:{major_name}:{company_provider}"

    def filter_duplicates(
        self,
        records: List[ContractRecord],
    ) -> Tuple[List[ContractRecord], List[ContractRecord]]:
        """
        Filter records into new and duplicate lists using Redis cache.

        Args:
            records: List of ContractRecord to check

        Returns:
            Tuple of (new_records, duplicate_records)
        """
        if not records:
            return [], []

        if not self._enabled:
            logger.info("Redis dedup disabled - all records treated as new")
            return records, []

        new_records = []
        duplicate_records = []

        for record in records:
            business_key = self._build_business_key(record)

            try:
                if self._redis.exists(business_key):
                    online_data_str = self._redis.get(business_key)
                    online_data = json.loads(online_data_str) if online_data_str else {}
                    logger.debug(
                        "Duplicate with online data (contractObjectId: %s) - skipping offline",
                        online_data.get('contractObjectId', 'unknown')
                    )
                    duplicate_records.append(record)
                else:
                    new_records.append(record)
            except Exception as e:
                logger.warning("Redis check failed for key %s: %s", business_key, e)
                new_records.append(record)  # On error, treat as new

        logger.info(
            "Dedup result: %d new, %d duplicates (online wins)",
            len(new_records), len(duplicate_records)
        )

        return new_records, duplicate_records

    def get_duplicate_summary(
        self,
        total_count: int,
        new_count: int,
        duplicate_count: int,
    ) -> Dict:
        """Generate summary of duplicate checking results."""
        return {
            "total": total_count,
            "new": new_count,
            "duplicates": duplicate_count,
            "duplicate_rate": f"{(duplicate_count / total_count * 100):.2f}%" if total_count > 0 else "0%",
        }
