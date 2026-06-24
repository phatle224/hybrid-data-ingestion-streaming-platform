#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merge ETL Script - staging → reporting
Merge online (CDC) + offline (Excel) data into ODS contract table on PostgreSQL.
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional

from shared.configs import PostgreSQLConfig, RedisConfig
from shared.connections import PostgreSQLConnectionManager, RedisConnectionManager
from shared.query_builder import SQLQueryBuilder
from shared.logger import create_logger

logger = create_logger('merge_etl', 'logs/merge_etl.log')


# =============================================================================
# Insurance Type Query Registry
# =============================================================================

class InsuranceTypeQueryRegistry:
    """
    Registry of SQL extract queries per insurance type.
    """

    QUERIES: Dict[str, str] = {
        'TRAVEL': """
        SELECT
            cot."id" as "contractObjectId",
            c."contractId",
            cot."name",
            cot."companyProviderName",
            'TRAVEL' as "insuranceType",
            cot."cardNumber",
            cot."certificateNumberProvider",
            cot."accountTPA",
            c."userId",
            cot."startDate" as "contractObjectStartDate",
            cot."endDate" as "contractObjectEndDate",
            cot."idProvider" as "contractObjectIdProvider",
            cot."url" as "contractObjectUrl",
            cot."programTypeName",
            cot."programTypeId",
            cot."programId",
            cot."programName",
            cot."packageId",
            cot."packageName",
            cot."feeMainBenefit",
            cot."feeInsurance",
            cot."termsId",
            cot."majorName",
            cot."dob",
            cot."gender",
            cot."phone",
            cot."email",
            cot."license",
            cot."address",
            cot."nationality",
            cot."destination",
            cot."journey",
            cot."startDateJourney",
            cot."endDateJourney",
            cot."adults",
            cot."children",
            cot."payerName",
            cot."createdAt",
            cot."modifiedAt"
        FROM "stgInsuranceContractObjectTravel" cot
        INNER JOIN "stgInsuranceContract" c ON cot."contractId" = c."contractId"
        """,

        'VEHICLE': """
        SELECT
            cov."contractObjectId",
            c."contractId",
            cov."peopleName",
            cov."companyProviderName",
            'VEHICLE' as "insuranceType",
            cov."cardNumber",
            cov."certificateNumberProvider",
            cov."accountTPA",
            c."userId",
            cov."contractObjectStartDate",
            cov."contractObjectEndDate",
            cov."contractObjectIdProvider",
            cov."contractObjectUrl",
            cov."contractObjectSmeStatus",
            cov."programTypeName",
            cov."programTypeId",
            cov."programId",
            cov."programName",
            cov."packageId",
            cov."packageName",
            cov."feeMainBenefit",
            cov."feeInsurance",
            cov."termsId",
            cov."majorName",
            cov."peopleRelationship",
            cov."peopleDob",
            cov."peopleGender",
            cov."peoplePhone",
            cov."peopleEmail",
            cov."peopleLicense",
            cov."peopleAddress",
            cov."vehicleId",
            cov."createdAt",
            cov."modifiedAt"
        FROM "stgInsuranceContractObjectVehicle" cov
        INNER JOIN "stgInsuranceContract" c ON cov."contractId" = c."contractId"
        """,

        'MOTO': """
        SELECT
            com."id" as "contractObjectId",
            c."contractId",
            com."name",
            com."companyProviderName",
            'MOTO' as "insuranceType",
            com."cardNumber",
            com."certificateNumberProvider",
            com."accountTPA",
            c."userId",
            com."startDate" as "contractObjectStartDate",
            com."endDate" as "contractObjectEndDate",
            com."idProvider" as "contractObjectIdProvider",
            com."url" as "contractObjectUrl",
            com."programTypeName",
            com."programTypeId",
            com."programId",
            com."programName",
            com."packageId",
            com."packageName",
            com."feeMainBenefit",
            com."feeInsurance",
            com."termsId",
            com."majorName",
            com."dob",
            com."gender",
            com."phone",
            com."email",
            com."license",
            com."address",
            com."licensePlates",
            com."chassisNumber",
            com."engineNumber",
            com."type",
            com."createdAt",
            com."modifiedAt"
        FROM "stgInsuranceContractObjectMoto" com
        INNER JOIN "stgInsuranceContract" c ON com."contractId" = c."contractId"
        """,

        'HEALTH': """
        SELECT
            coh."contractObjectId",
            c."contractId",
            coh."peopleName",
            coh."companyProviderName",
            'HEALTH' as "insuranceType",
            coh."cardNumber",
            coh."certificateNumberProvider",
            coh."accountTPA",
            c."userId",
            coh."contractObjectStartDate",
            coh."contractObjectEndDate",
            coh."contractObjectSmeStatus",
            coh."contractIndividualStatus",
            coh."programTypeName",
            coh."programTypeId",
            coh."programId",
            coh."programName",
            coh."packageId",
            coh."packageName",
            coh."feeMainBenefit",
            coh."feeSideBenefit",
            coh."feeInsurance",
            coh."fromAge",
            coh."toAge",
            coh."termsId",
            coh."majorName",
            coh."peopleDob",
            coh."peopleGender",
            coh."peoplePhone",
            coh."peopleEmail",
            coh."peopleLicense",
            coh."peopleAddress",
            coh."peopleRelationship",
            coh."createdAt",
            coh."modifiedAt",
            c."contractStatus",
            c."contractStartDate",
            c."contractEndDate",
            c."amount",
            c."amountPay"
        FROM "stgInsuranceContractObject" coh
        INNER JOIN "stgInsuranceContract" c ON coh."contractId" = c."contractId"
        """,

        'SOCIAL': """
        SELECT
            cos."contractObjectId",
            c."contractId",
            cos."peopleName",
            cos."companyProviderName",
            'SOCIAL' as "insuranceType",
            cos."cardNumber",
            cos."certificateNumberProvider",
            cos."accountTPA",
            c."userId",
            cos."contractObjectStartDate",
            cos."contractObjectEndDate",
            cos."contractObjectSmeStatus",
            cos."contractIndividualStatus",
            cos."programTypeName",
            cos."programTypeId",
            cos."programId",
            cos."programName",
            cos."packageId",
            cos."packageName",
            cos."feeMainBenefit",
            cos."feeSideBenefit",
            cos."feeInsurance",
            cos."fromAge",
            cos."toAge",
            cos."termsId",
            cos."majorName",
            cos."peopleDob",
            cos."peopleGender",
            cos."peoplePhone",
            cos."peopleEmail",
            cos."peopleLicense",
            cos."peopleAddress",
            cos."peopleRelationship",
            cos."socialId",
            cos."monthlyIncome",
            cos."paymentPeriod",
            cos."createdAt",
            cos."modifiedAt"
        FROM "stgInsuranceContractObjectSocialInsurance" cos
        INNER JOIN "stgInsuranceContract" c ON cos."contractId" = c."contractId"
        """,

        'MEDICAL': """
        SELECT
            com."contractObjectId",
            c."contractId",
            com."peopleName",
            com."companyProviderName",
            'MEDICAL' as "insuranceType",
            com."cardNumber",
            com."certificateNumberProvider",
            com."accountTPA",
            c."userId",
            com."contractObjectStartDate",
            com."contractObjectEndDate",
            com."contractObjectSmeStatus",
            com."contractIndividualStatus",
            com."programTypeName",
            com."programTypeId",
            com."programId",
            com."programName",
            com."packageId",
            com."packageName",
            com."feeMainBenefit",
            com."feeSideBenefit",
            com."feeInsurance",
            com."fromAge",
            com."toAge",
            com."termsId",
            com."majorName",
            com."peopleDob",
            com."peopleGender",
            com."peoplePhone",
            com."peopleEmail",
            com."peopleLicense",
            com."peopleAddress",
            com."peopleRelationship",
            com."medicalId",
            com."hospitalCode",
            com."hospitalName",
            com."nation",
            com."createdAt",
            com."modifiedAt"
        FROM "stgInsuranceContractObjectMedicalInsurance" com
        INNER JOIN "stgInsuranceContract" c ON com."contractId" = c."contractId"
        """,
    }

    SOURCE_TABLES: Dict[str, str] = {
        'TRAVEL': 'stgInsuranceContractObjectTravel',
        'VEHICLE': 'stgInsuranceContractObjectVehicle',
        'MOTO': 'stgInsuranceContractObjectMoto',
        'HEALTH': 'stgInsuranceContractObject',
        'SOCIAL': 'stgInsuranceContractObjectSocialInsurance',
        'MEDICAL': 'stgInsuranceContractObjectMedicalInsurance',
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
    Handles INSERT INTO reporting.contract with ON CONFLICT.
    """

    @staticmethod
    def insert(cursor, record: Dict):
        """
        Insert record into reporting.contract.
        """
        # Filter out None values and offline_id helper field
        fields = {k: v for k, v in record.items() if v is not None and k != 'offline_id'}

        query, values = SQLQueryBuilder.build_reporting_upsert(
            table='reporting.contract',
            data=fields,
            key_fields=['contractId', 'contractObjectId'],
            exclude_fields=['id'],
            add_etl_timestamp=True
        )
        if query:
            cursor.execute(query, values)


# =============================================================================
# ETL Executor
# =============================================================================

class ETLExecutor:
    """
    Executes extract-and-load for a single insurance type on PostgreSQL.
    """

    def __init__(self, staging_db: PostgreSQLConnectionManager, reporting_db: PostgreSQLConnectionManager, batch_id: str):
        self._staging_db = staging_db
        self._reporting_db = reporting_db
        self._batch_id = batch_id

    def extract_and_load(self, insurance_type: str, query: str, source_table: str) -> int:
        count = 0
        try:
            self._staging_db.ensure_connected()
            self._reporting_db.ensure_connected()

            rows = self._staging_db.fetch_all(query)

            with self._reporting_db.connection.cursor() as cursor:
                for row in rows:
                    try:
                        row['data_source'] = 'online'
                        row['source_table'] = source_table
                        row['etl_batch_id'] = self._batch_id

                        ReportingRecordLoader.insert(cursor, row)
                        count += 1
                    except Exception as e:
                        logger.error("Error inserting %s record: %s", insurance_type, e)

                self._reporting_db.connection.commit()

            logger.info("  %s (%s): %d records", insurance_type, source_table, count)
            return count

        except Exception as e:
            logger.error("Error in extract_and_load for %s: %s", insurance_type, e)
            raise


# =============================================================================
# Main ETL Orchestrator
# =============================================================================

class ContractMergeETL:
    """
    ETL class to merge data from staging → reporting in PostgreSQL.
    """

    def __init__(
        self,
        staging_config: Dict,
        reporting_config: Dict,
        redis_config: Optional[Dict] = None,
    ):
        self._staging_db = PostgreSQLConnectionManager(staging_config, 'staging')
        self._reporting_db = PostgreSQLConnectionManager(reporting_config, 'reporting')
        self._redis = None
        self._batch_id = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Optional Redis client
        if redis_config:
            self._redis = RedisConnectionManager(redis_config)
            self._redis.connect()

    def run_full_merge(self) -> Dict:
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

    def _process_online_data(self) -> Dict[str, int]:
        executor = ETLExecutor(self._staging_db, self._reporting_db, self._batch_id)
        stats: Dict[str, int] = {}

        for insurance_type in InsuranceTypeQueryRegistry.get_types():
            query = InsuranceTypeQueryRegistry.QUERIES[insurance_type]
            source_table = InsuranceTypeQueryRegistry.SOURCE_TABLES[insurance_type]
            stats[insurance_type] = executor.extract_and_load(insurance_type, query, source_table)

        return stats

    def _process_offline_data(self) -> Dict[str, int]:
        stats: Dict[str, int] = {}

        try:
            self._staging_db.ensure_connected()
            self._reporting_db.ensure_connected()

            rows = self._staging_db.fetch_all('SELECT * FROM "stgInsuranceContractObjectOffline"')

            with self._reporting_db.connection.cursor() as cursor:
                for row in rows:
                    try:
                        insurance_type = row.get('insuranceType', 'UNKNOWN')

                        # Transform: add ETL metadata
                        row['data_source'] = 'offline'
                        row['source_table'] = 'stgInsuranceContractObjectOffline'
                        row['etl_batch_id'] = self._batch_id

                        ReportingRecordLoader.insert(cursor, row)
                        stats[insurance_type] = stats.get(insurance_type, 0) + 1

                    except Exception as e:
                        logger.error("Error processing offline record %s: %s", row.get('offline_id'), e)

                self._reporting_db.connection.commit()

            logger.info("  Offline loaded: %s", stats)
            return stats

        except Exception as e:
            logger.error("Error processing offline data: %s", e)
            raise

    def truncate_reporting_table(self):
        """Truncate reporting table (use with caution!)."""
        self._reporting_db.ensure_connected()
        self._reporting_db.execute('TRUNCATE TABLE "reporting"."contract"')
        logger.warning("Reporting table truncated")


def main():
    staging_config = PostgreSQLConfig(database_env='DB_DATABASE').get_config()
    reporting_config = PostgreSQLConfig(database_env='DB_DATABASE').get_config()
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
