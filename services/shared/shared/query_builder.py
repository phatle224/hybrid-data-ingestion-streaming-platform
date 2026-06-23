"""
SQL Query Builder for staging and reporting tables.

Generates parameterized UPSERT, UPDATE, and DELETE queries.
Consolidates duplicated query-building logic from:
- cdc_consumer.py (build_upsert_query, build_update_query, build_delete_query)
- streaming_etl_consumer.py (upsert_to_reporting)
- merge_etl.py (_insert_to_reporting)
"""
import logging
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class SQLQueryBuilder:
    """
    Builds parameterized SQL queries for CDC operations.

    All methods are static — no state needed.
    """

    @staticmethod
    def build_upsert(
        table: str,
        data: Dict[str, Any],
        pk_field: str,
        allowed_columns: Optional[Set[str]] = None,
    ) -> Tuple[Optional[str], Optional[list]]:
        """
        Build INSERT ... ON DUPLICATE KEY UPDATE query.

        Args:
            table: Target table name (e.g., 'stgContract')
            data: Data dictionary (already transformed)
            pk_field: Primary key field name
            allowed_columns: Set of allowed column names (from DESCRIBE)

        Returns:
            Tuple of (query_string, values_list) or (None, None) on error.
        """
        # Filter to allowed columns, exclude None values and modifiedDate
        filtered = {}
        for k, v in data.items():
            if v is None:
                continue
            if k == 'modifiedDate':
                continue
            if allowed_columns is not None and k not in allowed_columns:
                continue
            filtered[k] = v

        if not filtered or pk_field not in filtered:
            logger.warning("No valid data or missing PK for %s", table)
            return None, None

        columns = list(filtered.keys())
        placeholders = ['%s'] * len(columns)
        values = [filtered[col] for col in columns]

        # Build UPDATE clause (exclude PK)
        update_cols = [col for col in columns if col != pk_field]
        update_clause = ', '.join(
            [f"`{col}` = VALUES(`{col}`)" for col in update_cols]
        )

        # CRITICAL: Always update modifiedDate to track CDC sync time
        if update_clause:
            update_clause += ", `modifiedDate` = NOW()"
        else:
            update_clause = "`modifiedDate` = NOW()"

        query = f"""
            INSERT INTO `{table}` ({', '.join([f'`{col}`' for col in columns])})
            VALUES ({', '.join(placeholders)})
            ON DUPLICATE KEY UPDATE {update_clause}
        """
        return query, values

    @staticmethod
    def build_update(
        table: str,
        data: Dict[str, Any],
        pk_field: str,
        allowed_columns: Optional[Set[str]] = None,
    ) -> Tuple[Optional[str], Optional[list]]:
        """
        Build UPDATE query (separate from INSERT to fire UPDATE triggers).

        Args:
            table: Target table name
            data: Data dictionary (already transformed)
            pk_field: Primary key field name
            allowed_columns: Set of allowed column names

        Returns:
            Tuple of (query_string, values_list) or (None, None) on error.
        """
        # Filter data
        filtered = {}
        for k, v in data.items():
            if v is None or k == 'modifiedDate':
                continue
            if allowed_columns is not None and k not in allowed_columns:
                continue
            filtered[k] = v

        if not filtered or pk_field not in filtered:
            return None, None

        pk_value = filtered.pop(pk_field)
        if not filtered:
            return None, None

        set_clause = ', '.join([f"`{col}` = %s" for col in filtered.keys()])
        values = list(filtered.values())
        values.append(pk_value)  # For WHERE clause

        query = f"UPDATE `{table}` SET {set_clause} WHERE `{pk_field}` = %s"
        return query, values

    @staticmethod
    def build_delete(
        table: str,
        pk_field: str,
        pk_value: Any,
    ) -> Tuple[str, list]:
        """Build DELETE query."""
        query = f"DELETE FROM `{table}` WHERE `{pk_field}` = %s"
        return query, [pk_value]

    @staticmethod
    def build_reporting_upsert(
        table: str,
        data: Dict[str, Any],
        allowed_columns: Optional[Set[str]] = None,
        key_fields: List[str] = None,
        exclude_fields: List[str] = None,
        add_etl_timestamp: bool = True,
    ) -> Tuple[Optional[str], Optional[list]]:
        """
        Build upsert for reporting tables (e.g., insuranceReporting.contract).

        Args:
            table: Full table name (e.g., 'insuranceReporting.contract')
            data: Data dictionary
            allowed_columns: Set of valid columns in target table
            key_fields: Fields to exclude from UPDATE (primary/unique keys)
            exclude_fields: Fields to completely exclude (e.g., 'id' for auto-increment)
            add_etl_timestamp: Whether to add etl_loaded_at = NOW()

        Returns:
            Tuple of (query_string, values_list) or (None, None) on error.
        """
        exclude_set = set(exclude_fields or [])
        fields = {
            k: v for k, v in data.items()
            if v is not None
            and k not in exclude_set
            and (allowed_columns is None or k in allowed_columns)
        }

        if not fields:
            logger.warning("No valid fields for reporting upsert into %s", table)
            return None, None

        columns = list(fields.keys())
        placeholders = ['%s'] * len(columns)
        values = [fields[col] for col in columns]

        key_set = set(key_fields or ['contractId', 'contractObjectId'])
        update_cols = [col for col in columns if col not in key_set]
        update_clauses = [f"`{col}` = VALUES(`{col}`)" for col in update_cols]

        if add_etl_timestamp:
            update_clauses.append("etl_loaded_at = NOW()")

        query = f"""
            INSERT INTO {table}
            ({', '.join([f'`{col}`' for col in columns])})
            VALUES ({', '.join(placeholders)})
            ON DUPLICATE KEY UPDATE
                {', '.join(update_clauses)}
        """
        return query, values
