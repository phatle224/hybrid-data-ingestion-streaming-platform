#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Streaming ETL Consumer - Real-time staging → reporting pipeline on PostgreSQL
================================================================================
Replaces batch ETL scheduler with event-driven streaming.

Architecture:
    Debezium → Kafka (staging topics) → This Consumer → PostgreSQL reporting

Topics consumed:
    - staging.stgInsuranceContract
    - staging.stgInsuranceContractObject (HEALTH)
    - staging.stgInsuranceContractObjectVehicle
    - staging.stgInsuranceContractObjectTravel
    - staging.stgInsuranceContractObjectMoto
    - staging.stgInsuranceContractObjectSocialInsurance
    - staging.stgInsuranceContractObjectMedicalInsurance
    - staging.stgInsuranceContractObjectHouse
    - staging.stgInsuranceContractObjectOffline (Excel uploads)

Inherits BaseKafkaConsumer for standardized lifecycle.
"""
import os
import time
from collections import OrderedDict
from datetime import datetime
from typing import Any, Dict, List, Optional

from shared.logger import create_logger, configure_shared_loggers
from shared.configs import PostgreSQLConfig, KafkaConfig, RedisConfig
from shared.connections import PostgreSQLConnectionManager, RedisConnectionManager
from shared.debezium import DebeziumTransformer
from shared.query_builder import SQLQueryBuilder
from shared.base_consumer import BaseKafkaConsumer


# =============================================================================
# Topic Configuration (insurance type metadata per topic)
# =============================================================================

class TopicConfig:
    """Configuration for a single staging topic."""

    def __init__(self, table: str, insurance_type: str = None,
                 data_source: str = 'online', is_contract_master: bool = False):
        self.table = table
        self.insurance_type = insurance_type
        self.data_source = data_source
        self.is_contract_master = is_contract_master


# Primary key mapping for each staging table
PRIMARY_KEYS = {
    'stgInsuranceContract': 'contractId',
    'stgInsuranceContractObject': 'contractObjectId',
    'stgInsuranceContractObjectVehicle': 'contractObjectId',
    'stgInsuranceContractObjectTravel': 'id',
    'stgInsuranceContractObjectMoto': 'id',
    'stgInsuranceContractObjectSocialInsurance': 'contractObjectId',
    'stgInsuranceContractObjectMedicalInsurance': 'contractObjectId',
    'stgInsuranceContractObjectHouse': 'id',
    'stgInsuranceContractObjectOffline': 'offline_id',
}


# =============================================================================
# Streaming ETL Consumer
# =============================================================================

class StreamingETLConsumer(BaseKafkaConsumer):
    """
    Streaming ETL Consumer: staging CDC → reporting table (real-time).

    Features:
    - Real-time processing (< 1s latency)
    - Redis deduplication check
    - Automatic field mapping from staging to reporting
    - Support both online (CDC) and offline (Excel) data
    - Idempotent upserts using ON CONFLICT DO UPDATE
    - Contract cache for JOIN enrichment
    """

    def __init__(self):
        # ── Configuration ────────────────────────────────────
        self._topic_prefix = os.getenv('STAGING_TOPIC_PREFIX', 'staging')

        self._staging_config = PostgreSQLConfig(database_env='DB_DATABASE').get_config()
        self._reporting_config = PostgreSQLConfig(database_env='DB_DATABASE').get_config()
        self._redis_config = RedisConfig().get_config()
        self._kafka_config = KafkaConfig(
            group_id=os.getenv('CONSUMER_GROUP', 'staging-consumer-v1'),
        ).get_config()

        # Logger
        log_dir = '/app/logs' if os.path.exists('/app/logs') else '.'
        _logger = create_logger('StreamingETL', os.path.join(log_dir, 'streaming_etl.log'))
        configure_shared_loggers(os.path.join(log_dir, 'streaming_etl.log'))
        super().__init__('Streaming ETL Consumer', _logger)

        # ── Topic Configs ────────────────────────────────────
        self._topic_configs = self._build_topic_configs()

        # ── Connections ──────────────────────────────────────
        self._staging_db = PostgreSQLConnectionManager(self._staging_config, 'staging')
        self._reporting_db = PostgreSQLConnectionManager(self._reporting_config, 'reporting')
        self._redis = RedisConnectionManager(self._redis_config)

        # ── Reporting table columns (loaded at startup) ──────
        self._reporting_columns: Optional[set] = None

        # ── Contract cache (for join enrichment) ─────────────
        self._contract_cache_max_size = 10000
        self._contract_cache: OrderedDict[str, Dict] = OrderedDict()
        self._contract_cache_time: Dict[str, float] = {}
        self._contract_cache_ttl = 300  # 5 minutes

    def _build_topic_configs(self) -> Dict[str, TopicConfig]:
        """Build topic → config mapping."""
        p = self._topic_prefix
        return {
            f'{p}.stgInsuranceContract': TopicConfig(
                'stgInsuranceContract', insurance_type=None,
                data_source='online', is_contract_master=True
            ),
            f'{p}.stgInsuranceContractObject': TopicConfig(
                'stgInsuranceContractObject', 'HEALTH', 'online'
            ),
            f'{p}.stgInsuranceContractObjectVehicle': TopicConfig(
                'stgInsuranceContractObjectVehicle', 'VEHICLE', 'online'
            ),
            f'{p}.stgInsuranceContractObjectTravel': TopicConfig(
                'stgInsuranceContractObjectTravel', 'TRAVEL', 'online'
            ),
            f'{p}.stgInsuranceContractObjectMoto': TopicConfig(
                'stgInsuranceContractObjectMoto', 'MOTO', 'online'
            ),
            f'{p}.stgInsuranceContractObjectSocialInsurance': TopicConfig(
                'stgInsuranceContractObjectSocialInsurance', 'SOCIAL', 'online'
            ),
            f'{p}.stgInsuranceContractObjectMedicalInsurance': TopicConfig(
                'stgInsuranceContractObjectMedicalInsurance', 'MEDICAL', 'online'
            ),
            f'{p}.stgInsuranceContractObjectHouse': TopicConfig(
                'stgInsuranceContractObjectHouse', 'HOUSE', 'online'
            ),
            f'{p}.stgInsuranceContractObjectOffline': TopicConfig(
                'stgInsuranceContractObjectOffline', insurance_type=None,
                data_source='offline'
            ),
        }

    # ─── BaseKafkaConsumer Implementation ────────────────────

    def _get_topics(self) -> List[str]:
        return list(self._topic_configs.keys())

    def _get_kafka_config(self) -> Dict[str, Any]:
        return self._kafka_config

    def _setup_connections(self) -> bool:
        self._redis.connect()  # Optional, continue without Redis
        if not self._staging_db.connect():
            return False
        if not self._reporting_db.connect():
            return False
        self._load_reporting_columns()
        return True

    def _cleanup_connections(self):
        self._staging_db.close()
        self._reporting_db.close()
        self._redis.close()

    def _init_stats(self):
        stats = super()._init_stats()
        stats.update({
            'records_inserted': 0,
            'records_updated': 0,
            'records_skipped': 0,
            'by_type': {},
        })
        return stats

    def _print_custom_stats(self):
        self.logger.info("Records inserted: %d", self._stats['records_inserted'])
        self.logger.info("Records updated: %d", self._stats['records_updated'])
        self.logger.info("Records skipped: %d", self._stats['records_skipped'])
        self.logger.info("By insurance type:")
        for ins_type, count in self._stats['by_type'].items():
            self.logger.info("  %s: %d", ins_type, count)

    # ─── Schema Loading ──────────────────────────────────────

    def _load_reporting_columns(self):
        """Load valid column names from reporting.contract table."""
        columns = self._reporting_db.load_table_columns('contract')
        self._reporting_columns = columns or set()

    # ─── Contract Cache ──────────────────────────────────────

    def _get_contract_data(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Get contract master data from staging (with bounded LRU+TTL caching)."""
        if not contract_id:
            return None

        # Check cache
        current_time = time.time()
        if contract_id in self._contract_cache:
            cache_time = self._contract_cache_time.get(contract_id, 0)
            if current_time - cache_time < self._contract_cache_ttl:
                # Move to end (most recently used)
                self._contract_cache.move_to_end(contract_id)
                return self._contract_cache[contract_id]
            else:
                # Expired — remove
                del self._contract_cache[contract_id]
                self._contract_cache_time.pop(contract_id, None)

        # Fetch from database
        result = self._staging_db.fetch_one(
            'SELECT * FROM "stgInsuranceContract" WHERE "contractId" = %s LIMIT 1',
            [contract_id]
        )
        if result:
            # Evict oldest if at capacity
            if len(self._contract_cache) >= self._contract_cache_max_size:
                oldest_key, _ = self._contract_cache.popitem(last=False)
                self._contract_cache_time.pop(oldest_key, None)
            self._contract_cache[contract_id] = result
            self._contract_cache_time[contract_id] = current_time
        return result

    # ─── Deduplication (7 Business Keys — aligned with Portal) ──

    @staticmethod
    def _normalize_bk(*parts: str) -> str:
        """Normalise business key parts (strip + lowercase) — aligned with redis_cache_builder.BusinessKeyBuilder."""
        return ':'.join(str(p).strip().lower() for p in parts)

    @staticmethod
    def _normalize_date(value) -> str:
        """Normalise date value to YYYY-MM-DD string for BK comparison."""
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
        """Normalise fee/amount value to integer string for BK comparison."""
        if not value:
            return '0'
        try:
            return str(int(float(value)))
        except (ValueError, TypeError):
            return str(value).strip()

    def _extract_bk_dates_fee(self, data: Dict[str, Any]) -> tuple:
        """Extract and normalise the 3 new BK fields (startDate, endDate, feeInsurance) from a record."""
        start_date = (
            data.get('contractStartDate')
            or data.get('contractObjectStartDate')
            or data.get('startDateJourney')
            or ''
        )
        end_date = (
            data.get('contractEndDate')
            or data.get('contractObjectEndDate')
            or data.get('endDateJourney')
            or ''
        )
        fee = data.get('feeInsurance') or data.get('amountPay') or 0
        return self._normalize_date(start_date), self._normalize_date(end_date), self._normalize_fee(fee)

    def _build_online_bk_key(self, contract_id, person_name, major_name, company,
                             start_date='', end_date='', fee='0') -> str:
        """Build normalised online business-key Redis key (7 parts)."""
        return f"dedup:online_bk:{self._normalize_bk(contract_id, person_name, major_name, company, start_date, end_date, fee)}"

    def _build_offline_bk_key(self, insurance_type, contract_id, person_name, major_name, company,
                              start_date='', end_date='', fee='0') -> str:
        """Build normalised offline business-key Redis key (7 parts)."""
        return f"dedup:{insurance_type}:{self._normalize_bk(contract_id, person_name, major_name, company, start_date, end_date, fee)}"

    def _check_duplicate(self, insurance_type: str, contract_object_id: str) -> bool:
        """Check if record is duplicate using Redis (offline-vs-offline)."""
        if not self._redis.is_connected or not insurance_type or not contract_object_id:
            return False
        key = f"dedup:{insurance_type}:{contract_object_id}"
        return self._redis.exists(key)

    def _mark_processed(self, insurance_type: str, contract_object_id: str):
        """Mark record as processed in Redis (7-day TTL)."""
        if not self._redis.is_connected or not insurance_type or not contract_object_id:
            return
        key = f"dedup:{insurance_type}:{contract_object_id}"
        self._redis.setex(key, 86400 * 7, "1")

    def _has_online_duplicate(self, data: Dict[str, Any]) -> bool:
        """
        Check if an online record with the same 7 business keys already exists.
        Used for offline-vs-online dedup (online wins policy).
        """
        contract_id = data.get('contractId')
        major_name = data.get('majorName')
        company = data.get('companyProviderName')
        person_name = data.get('peopleName')

        if not all([contract_id, major_name, company, person_name]):
            return False

        start_date, end_date, fee = self._extract_bk_dates_fee(data)

        # Try Redis first
        if self._redis.is_connected:
            bk_key = self._build_online_bk_key(
                contract_id, person_name, major_name, company,
                start_date, end_date, fee,
            )
            if self._redis.exists(bk_key):
                return True

        # Fallback to SQL
        result = self._reporting_db.fetch_one(
            """SELECT 1 FROM "reporting"."contract"
                   WHERE "data_source" = 'online'
                     AND "contractId" = %s
                     AND "peopleName" = %s
                     AND "majorName" = %s
                     AND "companyProviderName" = %s
                     AND (COALESCE(TO_CHAR("contractObjectStartDate", 'YYYY-MM-DD'), '') = %s OR %s = '')
                     AND (COALESCE(TO_CHAR("contractObjectEndDate", 'YYYY-MM-DD'), '') = %s OR %s = '')
                     AND CAST(COALESCE("feeInsurance", 0) AS NUMERIC) = %s
                   LIMIT 1""",
            [
                contract_id, person_name, major_name, company,
                start_date, start_date, end_date, end_date, float(fee)
            ],
        )
        return result is not None

    # Keywords to resolve MEDICAL_SOCIAL → MEDICAL or SOCIAL
    _MEDICAL_SOCIAL_KEYWORDS = {
        'SOCIAL': ['bhxh', 'bảo hiểm xã hội', 'xã hội'],
        'MEDICAL': ['bhyt', 'bảo hiểm y tế', 'y tế'],
    }

    def _resolve_medical_social_type(self, data: Dict[str, Any]) -> str:
        """Resolve 'MEDICAL_SOCIAL' → 'MEDICAL' or 'SOCIAL' by checking majorName."""
        major_name = str(data.get('majorName') or '').lower().strip()
        for ins_type, keywords in self._MEDICAL_SOCIAL_KEYWORDS.items():
            for kw in keywords:
                if kw in major_name:
                    return ins_type
        self.logger.warning(
            "Cannot resolve MEDICAL_SOCIAL sub-type from majorName='%s', keeping MEDICAL_SOCIAL",
            data.get('majorName'),
        )
        return 'MEDICAL_SOCIAL'

    # ─── Message Processing ──────────────────────────────────

    def process_message(self, topic: str, message_value: Dict[str, Any]):
        """Process a single CDC message from staging."""
        topic_cfg = self._topic_configs.get(topic)
        if not topic_cfg:
            self.logger.warning("No config for topic: %s", topic)
            return

        op, data = DebeziumTransformer.extract_operation_and_data(message_value)
        if not op or not data:
            self.logger.debug("Skipping empty message from %s", topic)
            return

        transformed = DebeziumTransformer.transform_data(data)

        if op == 'd':
            self._handle_delete(topic_cfg, transformed)
            return

        record = self._build_reporting_record(topic_cfg, transformed, op)
        if not record:
            return

        if topic_cfg.data_source == 'online':
            self._remove_conflicting_offline(record)

        success = self._upsert_to_reporting(record)
        if success:
            insurance_type = record.get('insuranceType', 'UNKNOWN')
            self._stats['by_type'][insurance_type] = (
                self._stats['by_type'].get(insurance_type, 0) + 1
            )
            if op in ['c', 'r']:
                self._stats['records_inserted'] += 1
            else:
                self._stats['records_updated'] += 1

            # Mark processed in Redis
            bk_name = record.get('peopleName') or ''
            bk_start, bk_end, bk_fee = self._extract_bk_dates_fee(record)

            if record.get('data_source') == 'offline':
                redis_bk_key = self._build_offline_bk_key(
                    insurance_type,
                    record.get('contractId'), bk_name,
                    record.get('majorName'), record.get('companyProviderName'),
                    bk_start, bk_end, bk_fee,
                )
                if self._redis.is_connected:
                    self._redis.setex(redis_bk_key, 86400 * 7, "1")
            else:
                cobj_id = record.get('contractObjectId') or record.get('contractId')
                self._mark_processed(insurance_type, str(cobj_id))

                bk_key = self._build_online_bk_key(
                    record.get('contractId'),
                    bk_name,
                    record.get('majorName'), record.get('companyProviderName'),
                    bk_start, bk_end, bk_fee,
                )
                if self._redis.is_connected:
                    self._redis.setex(bk_key, 86400 * 7, "1")
            self.logger.info(
                "[OK] Processed %s from %s: %s",
                op, topic_cfg.table, insurance_type
            )
        else:
            self._stats['errors'] = self._stats.get('errors', 0) + 1
            self.logger.error("[FAIL] Failed to process from %s", topic)

    def _handle_delete(self, topic_cfg: TopicConfig, data: Dict[str, Any]):
        """Propagate a delete event from staging to reporting.contract."""
        if topic_cfg.is_contract_master:
            contract_id = data.get('contractId')
            if not contract_id:
                return
            self._contract_cache.pop(contract_id, None)
            self._contract_cache_time.pop(contract_id, None)
            rows = self._reporting_db.execute_with_rowcount(
                'DELETE FROM "reporting"."contract" WHERE "contractId" = %s',
                [contract_id],
            )
            self.logger.info(
                "[DELETE] contractId=%s → removed %d row(s) from reporting.contract",
                contract_id, rows or 0,
            )
        else:
            pk_field = PRIMARY_KEYS.get(topic_cfg.table)
            contract_object_id = (
                data.get('contractObjectId')
                or (data.get(pk_field) if pk_field else None)
                or data.get('id')
            )
            if not contract_object_id:
                return
            rows = self._reporting_db.execute_with_rowcount(
                'DELETE FROM "reporting"."contract" WHERE "contractObjectId" = %s',
                [contract_object_id],
            )
            self.logger.info(
                "[DELETE] contractObjectId=%s (%s) → removed %d row(s) from reporting.contract",
                contract_object_id, topic_cfg.table, rows or 0,
            )

    def _build_reporting_record(
        self, topic_cfg: TopicConfig,
        data: Dict[str, Any], operation: str,
    ) -> Optional[Dict[str, Any]]:
        """Build record for reporting table."""
        source_table = topic_cfg.table
        data_source = topic_cfg.data_source

        if topic_cfg.is_contract_master:
            contract_id = data.get('contractId')
            if contract_id:
                self._contract_cache[contract_id] = data
                self._contract_cache_time[contract_id] = time.time()
            self.logger.debug("Updated contract cache for %s", contract_id)
            return None

        insurance_type = topic_cfg.insurance_type
        if not insurance_type and source_table == 'stgInsuranceContractObjectOffline':
            insurance_type = data.get('insuranceType', 'UNKNOWN')

        if insurance_type == 'MEDICAL_SOCIAL':
            insurance_type = self._resolve_medical_social_type(data)

        pk_field = PRIMARY_KEYS.get(source_table)
        cobj_id = (
            data.get(pk_field)
            or data.get('contractObjectId')
            or data.get('id')
        )

        if data_source == 'offline':
            bk_name = data.get('peopleName') or ''
            bk_start, bk_end, bk_fee = self._extract_bk_dates_fee(data)
            redis_bk_key = self._build_offline_bk_key(
                 insurance_type,
                 data.get('contractId'),
                 bk_name,
                 data.get('majorName'), data.get('companyProviderName'),
                 bk_start, bk_end, bk_fee,
            )
            if self._redis.is_connected and self._redis.exists(redis_bk_key):
                self.logger.debug("Duplicate offline (Redis) found: %s", redis_bk_key)
                self._stats['records_skipped'] += 1
                return None

        if data_source == 'offline' and self._has_online_duplicate(data):
            self.logger.info(
                "[DEDUP] Skipped offline record %s — online version already exists "
                "(contractId=%s peopleName=%s majorName=%s)",
                cobj_id, data.get('contractId'),
                data.get('peopleName'), data.get('majorName'),
            )
            self._stats['records_skipped'] += 1
            return None

        record = dict(data)

        if pk_field == 'id' and 'id' in record and 'contractObjectId' not in record:
            record['contractObjectId'] = record['id']
            del record['id']

        if insurance_type:
            record['insuranceType'] = insurance_type

        record['data_source'] = data_source
        record['source_table'] = source_table
        record['etl_batch_id'] = f"streaming_{datetime.now().strftime('%Y%m%d')}"

        if data_source == 'online' and not topic_cfg.is_contract_master:
            contract_id = data.get('contractId')
            if contract_id:
                contract_data = self._get_contract_data(contract_id)
                if contract_data:
                    for field in ['userId', 'contractStatus', 'amount', 'amountPay']:
                        if field in contract_data and field not in record:
                            record[field] = contract_data[field]
                    
                    payer_name = contract_data.get('name')
                    payer_dob = contract_data.get('dob')
                    payer_gender = contract_data.get('gender')
                    payer_license = contract_data.get('license')
                    payer_phone = contract_data.get('phone')
                    payer_email = contract_data.get('email')
                    payer_address = contract_data.get('address')
                    
                    if not record.get('peopleName') and payer_name:
                        record['peopleName'] = payer_name
                        if record.get('peopleRelationship') is None:
                            record['peopleRelationship'] = 0

                    if not record.get('peopleDob') and payer_dob:
                        record['peopleDob'] = payer_dob
                    if record.get('peopleGender') is None and payer_gender is not None:
                        record['peopleGender'] = payer_gender
                    if not record.get('peopleLicense') and payer_license:
                        record['peopleLicense'] = payer_license
                    if not record.get('peoplePhone') and payer_phone:
                        record['peoplePhone'] = payer_phone
                    if not record.get('peopleEmail') and payer_email:
                        record['peopleEmail'] = payer_email
                    if not record.get('peopleAddress') and payer_address:
                        record['peopleAddress'] = payer_address

        if data_source == 'online' and insurance_type in ['TRAVEL', 'MOTO']:
            for src_field, tgt_field in [('name', 'peopleName'), ('dob', 'peopleDob'), ('gender', 'peopleGender'),
                                         ('phone', 'peoplePhone'), ('email', 'peopleEmail'), ('license', 'peopleLicense'), 
                                         ('licenseType', 'peopleLicenseType'), ('licenseFront', 'peopleLicenseFront'),
                                         ('licenseBack', 'peopleLicenseBack'), ('address', 'peopleAddress'),
                                         ('districtsCode', 'peopleDistrictsCode'), ('wardsCode', 'peopleWardsCode'),
                                         ('street', 'peopleStreet')]:
                if src_field in record and not record.get(tgt_field):
                    record[tgt_field] = record.pop(src_field)

        start_date_val = record.get('contractObjectStartDate') or record.pop('contractStartDate', None) or record.pop('startDateJourney', None)
        if start_date_val:
            record['contractObjectStartDate'] = start_date_val

        end_date_val = record.get('contractObjectEndDate') or record.pop('contractEndDate', None) or record.pop('endDateJourney', None)
        if end_date_val:
            record['contractObjectEndDate'] = end_date_val

        return record

    def _remove_conflicting_offline(self, record: Dict[str, Any]):
        """Delete any existing offline row that shares the same business keys as an incoming online record."""
        contract_id = record.get('contractId')
        major_name = record.get('majorName')
        company = record.get('companyProviderName')
        person_name = record.get('peopleName') or record.get('name')

        if not all([contract_id, major_name, company, person_name]):
            return

        start_date, end_date, fee = self._extract_bk_dates_fee(record)

        rows = self._reporting_db.execute_with_rowcount(
            """DELETE FROM "reporting"."contract"
               WHERE "data_source" = 'offline'
                 AND "contractId" = %s
                 AND "peopleName" = %s
                 AND "majorName" = %s
                 AND "companyProviderName" = %s
                 AND (COALESCE(TO_CHAR("contractObjectStartDate", 'YYYY-MM-DD'), '') = %s OR %s = '')
                 AND (COALESCE(TO_CHAR("contractObjectEndDate", 'YYYY-MM-DD'), '') = %s OR %s = '')
                 AND CAST(COALESCE("feeInsurance", 0) AS NUMERIC) = %s""",
            [
                contract_id, person_name, major_name, company,
                start_date, start_date, end_date, end_date, float(fee)
            ],
        )
        if rows and rows > 0:
            self.logger.info(
                "[DEDUP] Removed %d offline row(s) superseded by online: contractId=%s name=%s majorName=%s",
                rows, contract_id, person_name, major_name,
            )

    def _upsert_to_reporting(self, record: Dict[str, Any]) -> bool:
        """Upsert record to reporting.contract."""
        query, values = SQLQueryBuilder.build_reporting_upsert(
            table='reporting.contract',
            data=record,
            allowed_columns=self._reporting_columns,
            key_fields=['contractId', 'contractObjectId'],
            exclude_fields=['id'],
        )
        if not query or not values:
            self.logger.warning("No valid fields to insert after filtering")
            return False

        result = self._reporting_db.execute_with_rowcount(query, values)
        return result > 0

    # ─── Override run() to add architecture info ─────────────

    def run(self):
        """Override to add architecture logging."""
        self.logger.info("Architecture: Debezium → Kafka (staging) → This Consumer → Reporting")
        self.logger.info("Mode: Real-time streaming (< 1s latency)")
        super().run()


def main():
    """Main entry point."""
    consumer = StreamingETLConsumer()
    consumer.run()


if __name__ == '__main__':
    main()
