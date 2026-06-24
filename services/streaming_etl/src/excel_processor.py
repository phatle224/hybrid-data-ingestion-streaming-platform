"""
Excel to Offline Contract Processor on PostgreSQL
Rewritten using Strategy + Factory pattern (mirrors backend architecture).

Uses:
- ProcessorFactory → creates type-specific processor (Strategy Pattern)
- IInsuranceProcessor → Template Method: parse → pre_process → transform → post_process → validate
- ContractRecord model → proper data model instead of raw dicts
- RedisDuplicateService → Redis-based dedup (online wins policy)
- AppSettings → centralized valid_db_columns

Architecture is consistent with cdc_portal_upload/backend.
"""

import os
import logging
from typing import Dict, List, Tuple, Optional

import pandas as pd
import psycopg2

from models.contract_model import ContractRecord
from services.excel_service import ExcelService, ProcessorFactory
from services.duplicate_service import RedisDuplicateService
from configs.app_settings import app_settings
from shared.connections import PostgreSQLConnectionManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ExcelProcessor:
    """
    Process Excel files and upload to offline contract table on PostgreSQL.
    Uses Factory + Strategy pattern consistent with backend portal.

    Orchestration flow:
    1. ExcelService detects type and creates processor (Factory)
    2. Processor parses, transforms, validates (Template Method)
    3. RedisDuplicateService filters duplicates (online wins)
    4. Upload filtered records to staging DB
    """

    def __init__(self, db_config: Dict[str, str], redis_config: Dict[str, str] = None):
        """
        Initialize processor.

        Args:
            db_config: PostgreSQL connection config
            redis_config: Redis connection config (optional, for dedup)
        """
        self.db_config = db_config
        self._excel_service = ExcelService()

        # Initialize Redis dedup service
        redis_client = None
        if redis_config:
            try:
                import redis
                redis_client = redis.Redis(
                    host=redis_config.get('host', 'localhost'),
                    port=redis_config.get('port', 6379),
                    password=redis_config.get('password'),
                    db=redis_config.get('db', 0),
                    decode_responses=True,
                )
                redis_client.ping()
                logger.info("Redis connected - deduplication enabled")
            except Exception as e:
                logger.warning("Redis connection failed: %s. Continuing without dedup.", e)
                redis_client = None

        self._dedup_service = RedisDuplicateService(redis_client)

    def process_excel_file(
        self,
        file_path: str,
        uploaded_by: str,
        insurance_type_override: Optional[str] = None,
    ) -> Dict:
        """
        Main method: Process Excel file end-to-end.

        Args:
            file_path: Path to Excel file
            uploaded_by: User ID who uploads
            insurance_type_override: Force insurance type (optional)

        Returns:
            Summary dict with statistics
        """
        logger.info("Processing file: %s", file_path)
        filename = os.path.basename(file_path)

        try:
            # Step 1: Detect insurance type
            insurance_type = insurance_type_override
            if not insurance_type:
                try:
                    insurance_type = self._excel_service.detect_insurance_type(filename)
                except ValueError as e:
                    return {
                        'status': 'error',
                        'message': str(e),
                        'filename': filename,
                    }

            logger.info("Detected insurance type: %s", insurance_type)

            # Step 2: Process with type-specific processor (Factory + Template Method)
            valid_records, errors = self._excel_service.process_excel_file(
                file_path, insurance_type
            )

            total_rows = len(valid_records) + len(errors)
            logger.info("Valid: %d, Invalid: %d", len(valid_records), len(errors))

            # Step 3: Check for validation errors
            if errors:
                invalid_details = []
                for err in errors[:10]:
                    invalid_details.append({
                        'row_number': err.get('row', '?'),
                        'data': err.get('record_preview', {}),
                        'errors': [
                            fe.get('message', 'Unknown error')
                            for fe in err.get('field_errors', [])
                        ],
                    })

                return {
                    'status': 'validation_error',
                    'message': f'{len(errors)} records failed validation',
                    'filename': filename,
                    'insurance_type': insurance_type,
                    'total_rows': total_rows,
                    'valid_rows': len(valid_records),
                    'invalid_rows': len(errors),
                    'invalid_details': invalid_details,
                    'rejection_reason': 'Missing business key fields',
                }

            # Step 4: Redis dedup (online wins policy)
            new_records, dup_records = self._dedup_service.filter_duplicates(valid_records)
            skipped_count = len(dup_records)
            if skipped_count > 0:
                logger.info("Skipped %d duplicates (online wins)", skipped_count)

            # Step 5: Upload to database
            success, error_count, error_messages = self._upload_to_database(
                new_records, insurance_type, uploaded_by
            )

            return {
                'status': 'success' if error_count == 0 else 'partial_success',
                'message': f'Uploaded {success} records successfully',
                'filename': filename,
                'insurance_type': insurance_type,
                'total_rows': total_rows,
                'success_count': success,
                'error_count': error_count,
                'skipped_duplicates': skipped_count,
                'error_messages': error_messages[:10] if error_messages else [],
            }

        except Exception as e:
            logger.error("Error processing file: %s", e, exc_info=True)
            return {
                'status': 'error',
                'message': str(e),
                'filename': filename,
            }

    def _upload_to_database(
        self,
        records: List[ContractRecord],
        insurance_type: str,
        uploaded_by: str,
    ) -> Tuple[int, int, List[str]]:
        """
        Upload records to staging table.

        Args:
            records: List of validated ContractRecord objects
            insurance_type: Insurance type
            uploaded_by: User ID

        Returns:
            Tuple of (success_count, error_count, error_messages)
        """
        success_count = 0
        error_count = 0
        errors = []

        # Get target table from settings
        target_table = app_settings.staging_table_mapping.get(
            insurance_type, app_settings.staging_table
        )
        logger.info("Target table for %s: %s", insurance_type, target_table)

        db = PostgreSQLConnectionManager(self.db_config, 'staging')
        if not db.connect():
            error_msg = "Database connection error"
            errors.append(error_msg)
            logger.error(error_msg)
            return 0, len(records), errors

        try:
            with db.connection.cursor() as cursor:
                for record in records:
                    try:
                        record_dict = record.to_dict()

                        # Add upload metadata
                        record_dict['createdBy'] = uploaded_by
                        record_dict['modifiedBy'] = uploaded_by

                        # Filter to only valid schema columns (from AppSettings)
                        filtered = {
                            k: v for k, v in record_dict.items()
                            if k in app_settings.valid_db_columns and v is not None
                        }

                        columns = list(filtered.keys())
                        placeholders = ['%s'] * len(columns)
                        values = [filtered[col] for col in columns]

                        quoted_table = f'"{target_table}"'
                        quoted_cols = ', '.join([f'"{col}"' for col in columns])

                        if target_table == 'stgInsuranceContractObjectHouse':
                            # House has "id" as PK/conflict key
                            update_clause = ', '.join([
                                f'"{col}" = EXCLUDED."{col}"'
                                for col in columns
                                if col != 'id'
                            ])
                            query = f"""
                                INSERT INTO {quoted_table} ({quoted_cols})
                                VALUES ({', '.join(placeholders)})
                                ON CONFLICT ("id") DO UPDATE SET {update_clause}, "modifiedDate" = NOW()
                            """
                        else:
                            # Offline table is append-only here because dedup was done by Redis
                            query = f"""
                                INSERT INTO {quoted_table} ({quoted_cols})
                                VALUES ({', '.join(placeholders)})
                            """

                        cursor.execute(query, values)
                        success_count += 1

                    except psycopg2.Error as e:
                        error_count += 1
                        error_msg = f"Record {record.contract_id}: {e}"
                        errors.append(error_msg)
                        logger.error(error_msg)

                db.connection.commit()

        except Exception as e:
            logger.error("Database transaction error: %s", e)
            errors.append(f"Database error: {e}")

        finally:
            db.close()

        return success_count, error_count, errors


# ==============================================================================
# CLI Usage
# ==============================================================================
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Upload Excel to Offline Contract')
    parser.add_argument('file', help='Path to Excel file')
    parser.add_argument('--user', default='admin', help='User ID who uploads')
    parser.add_argument(
        '--type',
        choices=ProcessorFactory.get_supported_types(),
        help='Force insurance type (optional, auto-detect from filename)',
    )

    args = parser.parse_args()

    # Use shared configs
    from shared.configs import PostgreSQLConfig, RedisConfig

    db_config = PostgreSQLConfig(database_env='DB_DATABASE').get_config()
    redis_config = RedisConfig().get_config()

    processor = ExcelProcessor(db_config, redis_config)
    result = processor.process_excel_file(args.file, args.user, args.type)

    print("\n" + "=" * 80)
    print("UPLOAD SUMMARY")
    print("=" * 80)
    print(f"Status: {result['status']}")
    print(f"File: {result['filename']}")
    if 'insurance_type' in result:
        print(f"Insurance Type: {result['insurance_type']}")
    print(f"Message: {result['message']}")

    if 'total_rows' in result:
        print(f"\nTotal Rows: {result['total_rows']}")
        print(f"Success: {result.get('success_count', 0)}")
        print(f"Errors: {result.get('error_count', 0)}")
        print(f"Skipped (duplicates): {result.get('skipped_duplicates', 0)}")

    if result.get('error_messages'):
        print("\nError Details:")
        for err in result['error_messages']:
            print(f"  - {err}")

    if result.get('invalid_details'):
        print("\nValidation Errors:")
        for inv in result['invalid_details']:
            row_num = inv.get('row_number', '?')
            print(f"  Row {row_num}: {', '.join(inv.get('errors', []))}")

    print("=" * 80)
