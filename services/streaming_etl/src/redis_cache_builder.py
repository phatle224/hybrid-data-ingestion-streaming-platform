#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis Deduplication Cache Builder
Build cache from CDC staging tables for duplicate detection against online data.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from shared.configs import PostgreSQLConfig, RedisConfig
from shared.connections import PostgreSQLConnectionManager, RedisConnectionManager
from shared.logger import create_logger

logger = create_logger('redis_cache', 'logs/redis_cache.log')

# Default cache TTL: 7 days (aligned with streaming ETL)
DEFAULT_CACHE_TTL = 86400 * 7


# =============================================================================
# Cache Query Registry
# =============================================================================

class CacheQueryRegistry:
    """
    Registry of SQL queries per insurance type for building Redis dedup cache.
    Each query selects the 7 business key fields:
        contractId, name, majorName, companyProviderName,
        startDate, endDate, feeInsurance
    and metadata from the corresponding staging table.
    """

    QUERIES: Dict[str, str] = {
        'TRAVEL': """
        SELECT
            cot."id" as "contractObjectId",
            c."contractId",
            cot."name",
            cot."programName" as "majorName",
            cot."companyProviderName",
            cot."startDateJourney" as "startDate",
            cot."endDateJourney" as "endDate",
            cot."feeInsurance",
            'TRAVEL' as "insuranceType",
            cot."modifiedAt"
        FROM "stgInsuranceContractObjectTravel" cot
        INNER JOIN "stgInsuranceContract" c ON cot."contractId" = c."contractId"
        WHERE c."contractId" IS NOT NULL
          AND c."contractId" != ''
          AND cot."name" IS NOT NULL
          AND cot."name" != ''
          AND cot."programName" IS NOT NULL
          AND cot."programName" != ''
          AND cot."companyProviderName" IS NOT NULL
          AND cot."companyProviderName" != ''
        """,

        'VEHICLE': """
        SELECT
            cov."contractObjectId",
            c."contractId",
            cov."peopleName" as "name",
            cov."programName" as "majorName",
            cov."companyProviderName",
            cov."contractObjectStartDate" as "startDate",
            cov."contractObjectEndDate" as "endDate",
            cov."feeInsurance",
            'VEHICLE' as "insuranceType",
            cov."modifiedAt"
        FROM "stgInsuranceContractObjectVehicle" cov
        INNER JOIN "stgInsuranceContract" c ON cov."contractId" = c."contractId"
        WHERE c."contractId" IS NOT NULL
          AND c."contractId" != ''
          AND cov."peopleName" IS NOT NULL
          AND cov."peopleName" != ''
          AND cov."programName" IS NOT NULL
          AND cov."programName" != ''
          AND cov."companyProviderName" IS NOT NULL
          AND cov."companyProviderName" != ''
        """,

        'MOTO': """
        SELECT
            com."id" as "contractObjectId",
            c."contractId",
            com."name",
            com."programName" as "majorName",
            com."companyProviderName",
            com."startDate" as "startDate",
            com."endDate" as "endDate",
            com."feeInsurance",
            'MOTO' as "insuranceType",
            com."modifiedAt"
        FROM "stgInsuranceContractObjectMoto" com
        INNER JOIN "stgInsuranceContract" c ON com."contractId" = c."contractId"
        WHERE c."contractId" IS NOT NULL
          AND c."contractId" != ''
          AND com."name" IS NOT NULL
          AND com."name" != ''
          AND com."programName" IS NOT NULL
          AND com."programName" != ''
          AND com."companyProviderName" IS NOT NULL
          AND com."companyProviderName" != ''
        """,

        'HEALTH': """
        SELECT
            coh."contractObjectId",
            c."contractId",
            coh."peopleName" as "name",
            coh."programName" as "majorName",
            coh."companyProviderName",
            c."contractStartDate" as "startDate",
            c."contractEndDate" as "endDate",
            coh."feeInsurance",
            'HEALTH' as "insuranceType",
            coh."modifiedAt"
        FROM "stgInsuranceContractObject" coh
        INNER JOIN "stgInsuranceContract" c ON coh."contractId" = c."contractId"
        WHERE c."contractId" IS NOT NULL
          AND c."contractId" != ''
          AND coh."peopleName" IS NOT NULL
          AND coh."peopleName" != ''
          AND coh."programName" IS NOT NULL
          AND coh."programName" != ''
          AND coh."companyProviderName" IS NOT NULL
          AND coh."companyProviderName" != ''
        """,

        'SOCIAL': """
        SELECT
            cos."contractObjectId",
            c."contractId",
            cos."peopleName" as "name",
            cos."programName" as "majorName",
            cos."companyProviderName",
            cos."contractObjectStartDate" as "startDate",
            cos."contractObjectEndDate" as "endDate",
            cos."feeInsurance",
            'SOCIAL' as "insuranceType",
            cos."modifiedAt"
        FROM "stgInsuranceContractObjectSocialInsurance" cos
        INNER JOIN "stgInsuranceContract" c ON cos."contractId" = c."contractId"
        WHERE c."contractId" IS NOT NULL
          AND c."contractId" != ''
          AND cos."peopleName" IS NOT NULL
          AND cos."peopleName" != ''
          AND cos."programName" IS NOT NULL
          AND cos."programName" != ''
          AND cos."companyProviderName" IS NOT NULL
          AND cos."companyProviderName" != ''
        """,

        'MEDICAL': """
        SELECT
            com."contractObjectId",
            c."contractId",
            com."peopleName" as "name",
            com."programName" as "majorName",
            com."companyProviderName",
            com."contractObjectStartDate" as "startDate",
            com."contractObjectEndDate" as "endDate",
            com."feeInsurance",
            'MEDICAL' as "insuranceType",
            com."modifiedAt"
        FROM "stgInsuranceContractObjectMedicalInsurance" com
        INNER JOIN "stgInsuranceContract" c ON com."contractId" = c."contractId"
        WHERE c."contractId" IS NOT NULL
          AND c."contractId" != ''
          AND com."peopleName" IS NOT NULL
          AND com."peopleName" != ''
          AND com."programName" IS NOT NULL
          AND com."programName" != ''
          AND com."companyProviderName" IS NOT NULL
          AND com."companyProviderName" != ''
        """,

        'HOUSE': """
        SELECT
            coh."id" as "contractObjectId",
            c."contractId",
            coh."name",
            coh."majorName",
            coh."companyProviderName",
            coh."contractObjectStartDate" as "startDate",
            coh."contractObjectEndDate" as "endDate",
            coh."feeInsurance",
            'HOUSE' as "insuranceType",
            coh."modifiedAt"
        FROM "stgInsuranceContractObjectHouse" coh
        INNER JOIN "stgInsuranceContract" c ON coh."contractId" = c."contractId"
        WHERE c."contractId" IS NOT NULL
          AND c."contractId" != ''
          AND coh."name" IS NOT NULL
          AND coh."name" != ''
          AND coh."majorName" IS NOT NULL
          AND coh."majorName" != ''
          AND coh."companyProviderName" IS NOT NULL
          AND coh."companyProviderName" != ''
        """,

        'OFFLINE': """
        SELECT
            "offline_id" as "contractObjectId",
            "contractId",
            "peopleName" as "name",
            "majorName",
            "companyProviderName",
            "contractObjectStartDate" as "startDate",
            "contractObjectEndDate" as "endDate",
            "feeInsurance",
            "insuranceType",
            "modifiedAt"
        FROM "stgInsuranceContractObjectOffline"
        """
    }

    @classmethod
    def get_types(cls) -> List[str]:
        """Return all registered insurance types."""
        return list(cls.QUERIES.keys())


# =============================================================================
# Business Key Builder
# =============================================================================

class BusinessKeyBuilder:
    """
    Builds and normalises Redis dedup keys from 7 business key components.

    Key format: dedup:online_bk:{contractId}:{name}:{majorName}:{companyProviderName}:{startDate}:{endDate}:{fee}
    Values are stripped and lowercased for case-insensitive matching.
    """

    KEY_PREFIX = 'dedup:online_bk'

    @staticmethod
    def _normalize_date(value) -> str:
        """Normalise date value to YYYY-MM-DD string."""
        if not value:
            return ''
        s = str(value).strip()
        if 'T' in s:
            s = s.split('T')[0]
        if ' ' in s:
            s = s.split(' ')[0]
        try:
            if s.isdigit() and len(s) <= 6:
                from datetime import date, timedelta
                d = date(1970, 1, 1) + timedelta(days=int(s))
                return d.isoformat()
        except Exception:
            pass
        return s

    @staticmethod
    def _normalize_fee(value) -> str:
        """Normalise fee/amount to integer string (strip decimal precision)."""
        if not value:
            return '0'
        try:
            return str(int(float(value)))
        except (ValueError, TypeError):
            return str(value).strip()

    @classmethod
    def build(
        cls,
        contract_id: str,
        name: str,
        major_name: str,
        company_provider: str,
        start_date: str = '',
        end_date: str = '',
        fee: str = '0',
        prefix: str = None,
    ) -> str:
        """
        Build normalised Redis key from 7 business key components.
        """
        norm_start = cls._normalize_date(start_date)
        norm_end = cls._normalize_date(end_date)
        norm_fee = cls._normalize_fee(fee)

        parts = [
            str(contract_id).strip(),
            str(name).strip().lower(),
            str(major_name).strip().lower(),
            str(company_provider).strip().lower(),
            norm_start,
            norm_end,
            norm_fee,
        ]
        
        effective_prefix = prefix if prefix is not None else cls.KEY_PREFIX
        return f"{effective_prefix}:{':'.join(parts)}"


# =============================================================================
# Cache Record Value
# =============================================================================

class CacheRecordValue:
    """Builds the JSON value stored alongside each Redis key."""

    @staticmethod
    def from_row(row: Dict) -> str:
        """
        Serialise a staging row into a JSON string for Redis storage.
        """
        modified_at = row.get('modifiedAt')
        value = {
            'source': 'online',
            'contractObjectId': row['contractObjectId'],
            'insuranceType': row['insuranceType'],
            'modifiedAt': modified_at.isoformat() if modified_at and hasattr(modified_at, 'isoformat') else str(modified_at) if modified_at else None,
            'cachedAt': datetime.now().isoformat(),
        }
        return json.dumps(value, ensure_ascii=False)


# =============================================================================
# Main Cache Builder
# =============================================================================

class RedisDeduplicationCache:
    """
    Builds and manages the Redis dedup cache on PostgreSQL.
    """

    def __init__(self, redis_config: Dict, db_config: Dict, cache_ttl: int = DEFAULT_CACHE_TTL):
        self._redis = RedisConnectionManager(redis_config)
        self._db = PostgreSQLConnectionManager(db_config, 'staging')
        self._cache_ttl = cache_ttl

        # Connect eagerly
        if not self._redis.connect():
            raise ConnectionError("Redis connection failed")

    def build_cache_for_type(self, insurance_type: str) -> int:
        """
        Build cache for a single insurance type.
        """
        query = CacheQueryRegistry.QUERIES.get(insurance_type)
        if not query:
            logger.warning("Unknown insurance type: %s", insurance_type)
            return 0

        count = 0

        try:
            self._db.ensure_connected()
            rows = self._db.fetch_all(query)

            for row in rows:
                prefix = None
                if insurance_type == 'OFFLINE':
                    row_ins_type = row.get('insuranceType', 'UNKNOWN')
                    prefix = f"dedup:{row_ins_type}"
                
                business_key = BusinessKeyBuilder.build(
                    contract_id=row['contractId'],
                    name=row['name'],
                    major_name=row['majorName'],
                    company_provider=row['companyProviderName'],
                    start_date=row.get('startDate', ''),
                    end_date=row.get('endDate', ''),
                    fee=row.get('feeInsurance', 0),
                    prefix=prefix
                )
                value = CacheRecordValue.from_row(row)
                self._redis.setex(business_key, self._cache_ttl, value)
                count += 1

            logger.info("%s: Added %d keys to Redis", insurance_type, count)
            return count

        except Exception as e:
            logger.error("Error building cache for %s: %s", insurance_type, e)
            raise

    def rebuild_all_caches(self) -> Dict[str, int]:
        logger.info("Starting full cache rebuild...")
        start_time = datetime.now()

        self._db.connect()

        results: Dict[str, int] = {}
        for insurance_type in CacheQueryRegistry.get_types():
            results[insurance_type] = self.build_cache_for_type(insurance_type)

        total = sum(results.values())
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info("Cache rebuild complete: %d total keys in %.2fs", total, elapsed)
        logger.info("  Breakdown: %s", results)

        self._db.close()
        return results

    def check_duplicate(
        self,
        contract_id: str,
        name: str,
        major_name: str,
        company_provider: str,
        start_date: str = '',
        end_date: str = '',
        fee: str = '0',
    ) -> Tuple[bool, Dict]:
        business_key = BusinessKeyBuilder.build(
            contract_id, name, major_name, company_provider,
            start_date, end_date, fee,
        )
        raw = self._redis.get(business_key)
        if raw:
            return True, json.loads(raw)
        return False, {}

    def get_cache_stats(self) -> Dict:
        info = self._redis.info()
        total_keys = sum(1 for _ in self._redis.scan_iter(match=f"{BusinessKeyBuilder.KEY_PREFIX}:*"))
        return {
            'total_keys': total_keys,
            'used_memory_human': info.get('used_memory_human'),
            'uptime_days': info.get('uptime_in_days'),
            'connected_clients': info.get('connected_clients'),
        }

    def close(self):
        self._redis.close()
        self._db.close()


def main():
    redis_config = RedisConfig().get_config()
    db_config = PostgreSQLConfig(database_env='DB_DATABASE').get_config()

    cache = RedisDeduplicationCache(redis_config, db_config)

    try:
        results = cache.rebuild_all_caches()
        stats = cache.get_cache_stats()
        print("\nRedis Cache Statistics:")
        print(f"  Total Keys: {stats['total_keys']}")
        print(f"  Memory Used: {stats['used_memory_human']}")
        print(f"  Uptime: {stats['uptime_days']} days")
    finally:
        cache.close()


if __name__ == '__main__':
    main()
