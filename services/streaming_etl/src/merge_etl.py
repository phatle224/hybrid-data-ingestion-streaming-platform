#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merge ETL Script - insuranceWarehouse → insuranceReporting
Merge online (CDC) + offline (Excel) data into ODS contract table.

OOP Restructured:
- Config-driven insurance type queries (eliminates 6 repetitive methods)
- Uses shared MySQLConnectionManager for connection management
- Uses shared RedisConnectionManager for optional dedup
- Follows Template Method pattern for extract-and-load flow
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional

from shared.configs import MySQLConfig, RedisConfig
from shared.connections import MySQLConnectionManager, RedisConnectionManager
from shared.logger import create_logger

logger = create_logger('merge_etl', 'logs/merge_etl.log')


# =============================================================================
# Insurance Type Query Registry
# =============================================================================

class InsuranceTypeQueryRegistry:
    """
    Registry of SQL extract queries per insurance type.
    Centralises the 6 insurance-type-specific queries that were previously
    duplicated across separate methods.

    Each entry maps an insurance type to its SELECT query joining the
    staging contract-object table with stgContract.
    """

    QUERIES: Dict[str, str] = {
        'TRAVEL': """
        SELECT
            cot.id as contractObjectId,
            c.contractId,
            cot.name,
            cot.companyProviderName,
            'TRAVEL' as insuranceType,
            cot.cardNumber,
            cot.certificateNumberProvider,
            cot.accountTPA,
            c.userId,
            cot.startDate as contractObjectStartDate,
            cot.endDate as contractObjectEndDate,
            cot.idProvider as contractObjectIdProvider,
            cot.url as contractObjectUrl,
            cot.programTypeName,
            cot.programTypeId,
            cot.programId,
            cot.programName,
            cot.packageId,
            cot.packageName,
            cot.feeMainBenefit,
            cot.feeInsurance,
            cot.termsId,
            cot.majorName,
            cot.dob,
            cot.gender,
            cot.phone,
            cot.email,
            cot.license,
            cot.address,
            cot.nationality,
            cot.destination,
            cot.journey,
            cot.startDateJourney,
            cot.endDateJourney,
            cot.adults,
            cot.children,
            cot.payerName,
            cot.createdAt,
            cot.modifiedAt
        FROM insuranceWarehouse.stgContractObjectTravel cot
        INNER JOIN insuranceWarehouse.stgContract c ON cot.contractId = c.contractId
        """,

        'VEHICLE': """
        SELECT
            cov.contractObjectId,
            c.contractId,
            cov.peopleName,
            cov.companyProviderName,
            'VEHICLE' as insuranceType,
            cov.cardNumber,
            cov.certificateNumberProvider,
            cov.accountTPA,
            c.userId,
            cov.contractObjectStartDate,
            cov.contractObjectEndDate,
            cov.contractObjectIdProvider,
            cov.contractObjectUrl,
            cov.contractObjectSmeStatus,
            cov.programTypeName,
            cov.programTypeId,
            cov.programId,
            cov.programName,
            cov.packageId,
            cov.packageName,
            cov.feeMainBenefit,
            cov.feeInsurance,
            cov.termsId,
            cov.majorName,
            cov.peopleRelationship,
            cov.peopleDob,
            cov.peopleGender,
            cov.peoplePhone,
            cov.peopleEmail,
            cov.peopleLicense,
            cov.peopleAddress,
            cov.vehicleId,
            cov.createdAt,
            cov.modifiedAt
        FROM insuranceWarehouse.stgContractObjectVehicle cov
        INNER JOIN insuranceWarehouse.stgContract c ON cov.contractId = c.contractId
        """,

        'MOTO': """
        SELECT
            com.id as contractObjectId,
            c.contractId,
            com.name,
            com.companyProviderName,
            'MOTO' as insuranceType,
            com.cardNumber,
            com.certificateNumberProvider,
            com.accountTPA,
            c.userId,
            com.startDate as contractObjectStartDate,
            com.endDate as contractObjectEndDate,
            com.idProvider as contractObjectIdProvider,
            com.url as contractObjectUrl,
            com.programTypeName,
            com.programTypeId,
            com.programId,
            com.programName,
            com.packageId,
            com.packageName,
            com.feeMainBenefit,
            com.feeInsurance,
            com.termsId,
            com.majorName,
            com.dob,
            com.gender,
            com.phone,
            com.email,
            com.license,
            com.address,
            com.licensePlates,
            com.chassisNumber,
            com.engineNumber,
            com.type,
            com.createdAt,
            com.modifiedAt
        FROM insuranceWarehouse.stgContractObjectMoto com
        INNER JOIN insuranceWarehouse.stgContract c ON com.contractId = c.contractId
        """,

        'HEALTH': """
        SELECT
            coh.contractObjectId,
            c.contractId,
            coh.peopleName,
            coh.companyProviderName,
            'HEALTH' as insuranceType,
            coh.cardNumber,
            coh.certificateNumberProvider,
            coh.accountTPA,
            c.userId,
            coh.contractObjectStartDate,
            coh.contractObjectEndDate,
            coh.contractObjectSmeStatus,
            coh.contractIndividualStatus,
            coh.programTypeName,
            coh.programTypeId,
            coh.programId,
            coh.programName,
            coh.packageId,
            coh.packageName,
            coh.feeMainBenefit,
            coh.feeSideBenefit,
            coh.feeInsurance,
            coh.fromAge,
            coh.toAge,
            coh.termsId,
            coh.majorName,
            coh.peopleDob,
            coh.peopleGender,
            coh.peoplePhone,
            coh.peopleEmail,
            coh.peopleLicense,
            coh.peopleAddress,
            coh.peopleRelationship,
            coh.createdAt,
            coh.modifiedAt,
            c.contractStatus,
            c.contractStartDate,
            c.contractEndDate,
            c.amount,
            c.amountPay
        FROM insuranceWarehouse.stgContractObject coh
        INNER JOIN insuranceWarehouse.stgContract c ON coh.contractId = c.contractId
        """,

        'SOCIAL': """
        SELECT
            cos.contractObjectId,
            c.contractId,
            cos.peopleName,
            cos.companyProviderName,
            'SOCIAL' as insuranceType,
            cos.cardNumber,
            cos.certificateNumberProvider,
            cos.accountTPA,
            c.userId,
            cos.contractObjectStartDate,
            cos.contractObjectEndDate,
            cos.contractObjectSmeStatus,
            cos.contractIndividualStatus,
            cos.programTypeName,
            cos.programTypeId,
            cos.programId,
            cos.programName,
            cos.packageId,
            cos.packageName,
            cos.feeMainBenefit,
            cos.feeSideBenefit,
            cos.feeInsurance,
            cos.fromAge,
            cos.toAge,
            cos.termsId,
            cos.majorName,
            cos.peopleDob,
            cos.peopleGender,
            cos.peoplePhone,
            cos.peopleEmail,
            cos.peopleLicense,
            cos.peopleAddress,
            cos.peopleRelationship,
            cos.socialId,
            cos.monthlyIncome,
            cos.paymentPeriod,
            cos.createdAt,
            cos.modifiedAt
        FROM insuranceWarehouse.stgContractObjectSocialInsurance cos
        INNER JOIN insuranceWarehouse.stgContract c ON cos.contractId = c.contractId
        """,

        'MEDICAL': """
        SELECT
            com.contractObjectId,
            c.contractId,
            com.peopleName,
            com.companyProviderName,
            'MEDICAL' as insuranceType,
            com.cardNumber,
            com.certificateNumberProvider,
            com.accountTPA,
            c.userId,
            com.contractObjectStartDate,
            com.contractObjectEndDate,
            com.contractObjectSmeStatus,
            com.contractIndividualStatus,
            com.programTypeName,
            com.programTypeId,
            com.programId,
            com.programName,
            com.packageId,
            com.packageName,
            com.feeMainBenefit,
            com.feeSideBenefit,
            com.feeInsurance,
            com.fromAge,
            com.toAge,
            com.termsId,
            com.majorName,
            com.peopleDob,
            com.peopleGender,
            com.peoplePhone,
            com.peopleEmail,
            com.peopleLicense,
            com.peopleAddress,
            com.peopleRelationship,
            com.medicalId,
            com.hospitalCode,
            com.hospitalName,
            com.nation,
            com.createdAt,
            com.modifiedAt
        FROM insuranceWarehouse.stgContractObjectMedicalInsurance com
        INNER JOIN insuranceWarehouse.stgContract c ON com.contractId = c.contractId
        """,
    }

    # Map insurance type → source table name (for ETL metadata)
    SOURCE_TABLES: Dict[str, str] = {
        'TRAVEL': 'stgContractObjectTravel',
        'VEHICLE': 'stgContractObjectVehicle',
        'MOTO': 'stgContractObjectMoto',
        'HEALTH': 'stgContractObject',
        'SOCIAL': 'stgContractObjectSocialInsurance',
        'MEDICAL': 'stgContractObjectMedicalInsurance',
    }

    @classmethod
    def get_types(cls) -> List[str]:
        """Return all registered insurance types."""
        return list(cls.QUERIES.keys())


# =============================================================================
# Reporting Record Loader
# =============================================================================

class ReportingRecordLoader:
    """
    Handles INSERT INTO insuranceReporting.contract with ON DUPLICATE KEY UPDATE.
    Encapsulates the SQL generation for idempotent upserts into the reporting table.
    """

    # Columns excluded from the UPDATE clause (primary keys / immutable)
    IMMUTABLE_COLUMNS = frozenset(['contractId', 'contractObjectId', 'id'])

    @staticmethod
    def insert(cursor, record: Dict):
        """
        Insert record into insuranceReporting.contract.
        Uses ON DUPLICATE KEY UPDATE for idempotent inserts.

        Args:
            cursor: MySQL cursor
            record: Dict of column -> value
        """
        # Filter out None values and the offline_id helper field
        fields = {k: v for k, v in record.items() if v is not None and k != 'offline_id'}

        columns = list(fields.keys())
        placeholders = ['%s'] * len(columns)
        values = [fields[col] for col in columns]

        update_clauses = [
            f"`{col}` = VALUES(`{col}`)"
            for col in columns
            if col not in ReportingRecordLoader.IMMUTABLE_COLUMNS
        ]

        query = f"""
            INSERT INTO insuranceReporting.contract
            ({', '.join(f'`{col}`' for col in columns)})
            VALUES ({', '.join(placeholders)})
            ON DUPLICATE KEY UPDATE
                {', '.join(update_clauses)},
                etl_loaded_at = NOW()
        """
        cursor.execute(query, values)


# =============================================================================
# ETL Executor
# =============================================================================

class ETLExecutor:
    """
    Executes extract-and-load for a single insurance type.
    Reads rows from staging via a cursor and writes them to the reporting
    table using ReportingRecordLoader.
    """

    def __init__(self, staging_db: MySQLConnectionManager, reporting_db: MySQLConnectionManager, batch_id: str):
        self._staging_db = staging_db
        self._reporting_db = reporting_db
        self._batch_id = batch_id

    def extract_and_load(self, insurance_type: str, query: str, source_table: str) -> int:
        """
        Run an extract query on staging and load results into reporting.

        Args:
            insurance_type: e.g. 'TRAVEL', 'HEALTH'
            query: SQL SELECT to run against staging
            source_table: staging table name (for ETL metadata)

        Returns:
            Number of records inserted
        """
        count = 0
        staging_cursor = None
        reporting_cursor = None

        try:
            self._staging_db.ensure_connected()
            self._reporting_db.ensure_connected()

            staging_cursor = self._staging_db.create_cursor(dictionary=True)
            staging_cursor.execute(query)

            reporting_cursor = self._reporting_db.create_cursor(dictionary=False)

            for row in staging_cursor:
                try:
                    # Add ETL metadata
                    row['data_source'] = 'online'
                    row['source_table'] = source_table
                    row['etl_batch_id'] = self._batch_id

                    ReportingRecordLoader.insert(reporting_cursor, row)
                    count += 1
                except Exception as e:
                    logger.error("Error inserting %s record: %s", insurance_type, e)

            self._reporting_db.commit()
            logger.info("  %s (%s): %d records", insurance_type, source_table, count)
            return count

        except Exception as e:
            logger.error("Error in extract_and_load for %s: %s", insurance_type, e)
            raise
        finally:
            if staging_cursor:
                staging_cursor.close()
            if reporting_cursor:
                reporting_cursor.close()


# =============================================================================
# Main ETL Orchestrator
# =============================================================================

class ContractMergeETL:
    """
    ETL class to merge data from staging → reporting.

    Flow:
        1. Extract online data: JOIN stgContract + stgContractObject* per type
        2. Extract offline data: stgContractObjectOffline (post-Redis dedup)
        3. Transform: Map fields to reporting schema
        4. Load: INSERT into insuranceReporting.contract

    OOP improvements over original:
        - Config-driven insurance type queries (InsuranceTypeQueryRegistry)
        - Separated record loading (ReportingRecordLoader)
        - Separated execution (ETLExecutor)
        - Uses shared connection managers
    """

    def __init__(
        self,
        staging_config: Dict,
        reporting_config: Dict,
        redis_config: Optional[Dict] = None,
    ):
        self._staging_db = MySQLConnectionManager(staging_config, 'staging')
        self._reporting_db = MySQLConnectionManager(reporting_config, 'reporting')
        self._redis = None
        self._batch_id = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Optional Redis client
        if redis_config:
            self._redis = RedisConnectionManager(redis_config)
            self._redis.connect()

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def run_full_merge(self) -> Dict:
        """
        Run complete merge ETL process.

        Returns:
            Dict with batch statistics
        """
        logger.info("Starting full merge ETL - Batch ID: %s", self._batch_id)
        start_time = datetime.now()

        stats = {
            'batch_id': self._batch_id,
            'start_time': start_time.isoformat(),
            'online': {t: 0 for t in InsuranceTypeQueryRegistry.get_types()},
            'offline': {},
            'total_inserted': 0,
            'errors': [],
        }

        try:
            self._staging_db.connect()
            self._reporting_db.connect()

            # 1. Online data (CDC staging)
            logger.info("Processing online data (CDC staging)...")
            stats['online'] = self._process_online_data()

            # 2. Offline data (Excel uploads)
            logger.info("Processing offline data (Excel uploads)...")
            stats['offline'] = self._process_offline_data()

            stats['total_inserted'] = sum(stats['online'].values()) + sum(stats['offline'].values())
            elapsed = (datetime.now() - start_time).total_seconds()
            stats['end_time'] = datetime.now().isoformat()
            stats['elapsed_seconds'] = elapsed

            logger.info(
                "Merge ETL complete in %.2fs | Online: %d | Offline: %d | Total: %d",
                elapsed, sum(stats['online'].values()), sum(stats['offline'].values()), stats['total_inserted'],
            )
            return stats

        except Exception as e:
            logger.error("ETL failed: %s", e)
            stats['errors'].append(str(e))
            raise
        finally:
            self._staging_db.close()
            self._reporting_db.close()
            if self._redis:
                self._redis.close()

    # -----------------------------------------------------------------
    # Online Data Processing (config-driven loop)
    # -----------------------------------------------------------------

    def _process_online_data(self) -> Dict[str, int]:
        """
        Process all insurance types from staging via config-driven loop.
        Replaces 6 separate _extract_and_load_XXX() methods.
        """
        executor = ETLExecutor(self._staging_db, self._reporting_db, self._batch_id)
        stats: Dict[str, int] = {}

        for insurance_type in InsuranceTypeQueryRegistry.get_types():
            query = InsuranceTypeQueryRegistry.QUERIES[insurance_type]
            source_table = InsuranceTypeQueryRegistry.SOURCE_TABLES[insurance_type]
            stats[insurance_type] = executor.extract_and_load(insurance_type, query, source_table)

        return stats

    # -----------------------------------------------------------------
    # Offline Data Processing
    # -----------------------------------------------------------------

    def _process_offline_data(self) -> Dict[str, int]:
        """
        Process offline data from stgContractObjectOffline.

        Returns:
            Dict with count per insurance type
        """
        stats: Dict[str, int] = {}

        try:
            self._staging_db.ensure_connected()
            self._reporting_db.ensure_connected()

            staging_cursor = self._staging_db.create_cursor(dictionary=True)
            staging_cursor.execute("SELECT * FROM insuranceWarehouse.stgContractObjectOffline")

            reporting_cursor = self._reporting_db.create_cursor(dictionary=False)

            for row in staging_cursor:
                try:
                    insurance_type = row.get('insuranceType', 'UNKNOWN')

                    # Transform: add ETL metadata
                    row['data_source'] = 'offline'
                    row['source_table'] = 'stgContractObjectOffline'
                    row['etl_batch_id'] = self._batch_id

                    ReportingRecordLoader.insert(reporting_cursor, row)
                    stats[insurance_type] = stats.get(insurance_type, 0) + 1

                except Exception as e:
                    logger.error("Error processing offline record %s: %s", row.get('offline_id'), e)

            self._reporting_db.commit()
            staging_cursor.close()
            reporting_cursor.close()

            logger.info("  Offline loaded: %s", stats)
            return stats

        except Exception as e:
            logger.error("Error processing offline data: %s", e)
            raise

    # -----------------------------------------------------------------
    # Utility
    # -----------------------------------------------------------------

    def truncate_reporting_table(self):
        """Truncate reporting table (use with caution!)."""
        self._reporting_db.ensure_connected()
        self._reporting_db.execute("TRUNCATE TABLE insuranceReporting.contract")
        logger.warning("Reporting table truncated")


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    """Main function for running merge ETL."""
    staging_config = MySQLConfig(database='insuranceWarehouse').get_config()
    reporting_config = MySQLConfig(database='insuranceReporting').get_config()
    redis_config = RedisConfig().get_config()

    etl = ContractMergeETL(staging_config, reporting_config, redis_config)
    stats = etl.run_full_merge()

    # Print summary
    print("\n" + "=" * 80)
    print("MERGE ETL SUMMARY")
    print("=" * 80)
    print(f"Batch ID: {stats['batch_id']}")
    print(f"Start Time: {stats['start_time']}")
    print(f"End Time: {stats['end_time']}")
    print(f"Elapsed: {stats['elapsed_seconds']:.2f} seconds")
    print(f"\nOnline Data:")
    for ins_type, count in stats['online'].items():
        print(f"  {ins_type}: {count} records")
    print(f"\nOffline Data:")
    for ins_type, count in stats['offline'].items():
        print(f"  {ins_type}: {count} records")
    print(f"\nTotal Inserted: {stats['total_inserted']} records")
    if stats['errors']:
        print(f"\nErrors: {len(stats['errors'])}")
        for err in stats['errors']:
            print(f"  - {err}")
    print("=" * 80)


if __name__ == '__main__':
    main()
