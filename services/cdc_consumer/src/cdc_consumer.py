"""
CDC Consumer - Debezium Source → Kafka → MySQL Staging
======================================================
Routes CDC events from source database to staging tables.

Architecture:
    Debezium → Kafka (source topics) → This Consumer → insustream_staging

Inherits from BaseKafkaConsumer for standardized lifecycle management.
Uses shared DebeziumTransformer and SQLQueryBuilder to eliminate code duplication.
"""
import os
from typing import Any, Dict, List

import logging

from shared.logger import create_logger, configure_shared_loggers
from shared.configs import PostgreSQLConfig, KafkaConfig
from shared.connections import PostgreSQLConnectionManager
from shared.debezium import DebeziumTransformer
from shared.query_builder import SQLQueryBuilder
from shared.base_consumer import BaseKafkaConsumer


class CDCConsumer(BaseKafkaConsumer):
    """
    CDC Consumer: Source Debezium → Kafka → PostgreSQL Staging.

    Processes CDC events from source database and writes to staging tables.
    Supports insert (UPSERT), update (UPDATE trigger), and delete operations.
    """

    def __init__(self):
        # ── Configuration ────────────────────────────────────
        self._topic_prefix = os.getenv('TOPIC_PREFIX', 'source.source')

        self._db_config = PostgreSQLConfig(
            database_env='DB_DATABASE',
        ).get_config()

        self._kafka_config = KafkaConfig(
            group_id=os.getenv('CONSUMER_GROUP', 'source-consumer-v1'),
        ).get_config()

        # Logger — also route shared module loggers to stdout
        _logger = create_logger('CDCConsumer', 'server.log')
        configure_shared_loggers('server.log')
        super().__init__('CDC Consumer', _logger)

        # ── Topic → Table Mapping ────────────────────────────
        self._topic_table_mapping = {
            f'{self._topic_prefix}.insuranceContract': 'stgInsuranceContract',
            f'{self._topic_prefix}.insuranceContractObject': 'stgInsuranceContractObject',
            f'{self._topic_prefix}.insuranceContractObjectVehicle': 'stgInsuranceContractObjectVehicle',
            f'{self._topic_prefix}.insuranceContractObjectTravel': 'stgInsuranceContractObjectTravel',
            f'{self._topic_prefix}.insuranceContractObjectMoto': 'stgInsuranceContractObjectMoto',
            f'{self._topic_prefix}.insuranceContractObjectSocialInsurance': 'stgInsuranceContractObjectSocialInsurance',
            f'{self._topic_prefix}.insuranceContractObjectMedicalInsurance': 'stgInsuranceContractObjectMedicalInsurance',
            f'{self._topic_prefix}.insuranceContractObjectHouse': 'stgInsuranceContractObjectHouse',
            f'{self._topic_prefix}.insuranceClaim': 'stgInsuranceClaim',
        }

        # ── Primary Key Mapping ──────────────────────────────
        self._primary_keys = {
            'stgInsuranceContract': 'contractId',
            'stgInsuranceContractObject': 'contractObjectId',
            'stgInsuranceContractObjectVehicle': 'contractObjectId',
            'stgInsuranceContractObjectTravel': 'id',
            'stgInsuranceContractObjectMoto': 'id',
            'stgInsuranceContractObjectSocialInsurance': 'contractObjectId',
            'stgInsuranceContractObjectMedicalInsurance': 'contractObjectId',
            'stgInsuranceContractObjectHouse': 'id',
            'stgInsuranceClaim': 'id',
        }

        # ── State ────────────────────────────────────────────
        self._table_columns: Dict[str, set] = {}
        self._db = PostgreSQLConnectionManager(self._db_config, 'staging')

    # ─── BaseKafkaConsumer Implementation ────────────────────

    def _get_topics(self) -> List[str]:
        return list(self._topic_table_mapping.keys())

    def _get_kafka_config(self) -> Dict[str, Any]:
        return self._kafka_config

    def _setup_connections(self) -> bool:
        if not self._db.connect():
            return False
        self._load_all_schemas()
        return True

    def _cleanup_connections(self):
        self._db.close()

    def _init_stats(self):
        stats = super()._init_stats()
        stats.update({
            'inserts': 0,
            'updates': 0,
            'deletes': 0,
            'snapshots': 0,
        })
        return stats

    def _print_custom_stats(self):
        self.logger.info("Inserts: %d", self._stats.get('inserts', 0))
        self.logger.info("Updates: %d", self._stats.get('updates', 0))
        self.logger.info("Deletes: %d", self._stats.get('deletes', 0))
        self.logger.info("Snapshots: %d", self._stats.get('snapshots', 0))

    # ─── Schema Loading ──────────────────────────────────────

    def _load_all_schemas(self):
        """Load column names from all staging tables."""
        for table_name in set(self._topic_table_mapping.values()):
            columns = self._db.load_table_columns(table_name)
            self._table_columns[table_name] = columns

    # ─── Message Processing ──────────────────────────────────

    def process_message(self, topic: str, message_value: Dict[str, Any]):
        """Process a single CDC message from source."""
        table = self._topic_table_mapping.get(topic)
        if not table:
            self.logger.warning("No table mapping for topic: %s", topic)
            return

        pk_field = self._primary_keys.get(table)
        if not pk_field:
            self.logger.warning("No primary key for table: %s", table)
            return

        # Extract operation and data using shared transformer
        op, data = DebeziumTransformer.extract_operation_and_data(message_value)

        if not op:
            self.logger.warning("[%s] Skipped: op is None", table)
            return
        if not data:
            self.logger.warning(
                "[%s] Skipped: data is empty - op=%s, keys=%s",
                table, op, list(message_value.keys())
            )
            return

        # Transform Debezium values using shared transformer
        transformed = DebeziumTransformer.transform_data(data)
        allowed_columns = self._table_columns.get(table)

        if op in ['c', 'r']:
            self._handle_insert(table, transformed, pk_field, allowed_columns, op, data)
        elif op == 'u':
            self._handle_update(table, transformed, pk_field, allowed_columns, data)
        elif op == 'd':
            self._handle_delete(table, pk_field, data)

    def _handle_insert(self, table, transformed, pk_field, allowed_columns, op, data):
        """Handle INSERT or SNAPSHOT (UPSERT)."""
        query, values = SQLQueryBuilder.build_upsert(
            table, transformed, pk_field, allowed_columns
        )
        if not query or not values:
            # Log raw data preview to help diagnose why build_upsert returned None
            pk_val = data.get(pk_field)
            preview = {k: v for k, v in data.items() if v is not None}  # non-None fields
            self.logger.error(
                "[SKIP] build_upsert returned None for %s, op=%s, PK field=%s, PK value=%s, "
                "non-null fields: %s",
                table, op, pk_field, pk_val, list(preview.keys())
            )
            self._stats['errors'] += 1
            return
        try:
            if self._db.execute(query, values):
                op_name = 'snapshot' if op == 'r' else 'insert'
                self.logger.info("[OK] %s \u2192 %s, PK: %s", op_name, table, data.get(pk_field))
                self._stats['snapshots' if op == 'r' else 'inserts'] += 1
            else:
                self.logger.error("[FAIL] execute returned False for %s \u2192 %s, PK: %s", op, table, data.get(pk_field))
                self._stats['errors'] += 1
        except Exception as e:
            self.logger.error("[ERROR] %s \u2192 %s, PK: %s — %s", op, table, data.get(pk_field), e)
            raise

    def _handle_update(self, table, transformed, pk_field, allowed_columns, data):
        """Handle UPDATE (separate UPDATE to fire triggers)."""
        query, values = SQLQueryBuilder.build_update(
            table, transformed, pk_field, allowed_columns
        )
        if not query or not values:
            self.logger.warning("[SKIP] build_update returned None for update → %s, PK: %s", table, data.get(pk_field))
            return
        try:
            self._db.execute(query, values)
            self.logger.info("[OK] update → %s, PK: %s", table, data.get(pk_field))
            self._stats['updates'] += 1
        except Exception as e:
            self.logger.error("[ERROR] update → %s, PK: %s — %s", table, data.get(pk_field), e)
            raise

    def _handle_delete(self, table, pk_field, data):
        """Handle DELETE."""
        pk_value = data.get(pk_field)
        if not pk_value:
            return
        query, values = SQLQueryBuilder.build_delete(table, pk_field, pk_value)
        try:
            self._db.execute(query, values)
            self.logger.info("[OK] delete → %s, PK: %s", table, pk_value)
            self._stats['deletes'] += 1
        except Exception as e:
            self.logger.error("[ERROR] delete → %s, PK: %s — %s", table, pk_value, e)
            raise


if __name__ == "__main__":
    consumer = CDCConsumer()
    consumer.run()
