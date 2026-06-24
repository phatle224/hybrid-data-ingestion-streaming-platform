"""
Event Publisher (Production) - Monitors staging → publishes CDC events to RabbitMQ on PostgreSQL.

This is the standalone producer deployed via rabbitmq_producer/Dockerfile.
It does NOT share consumer/shared/ because of a separate Docker build context.

OOP Restructured (self-contained):
- Extracted config classes (PostgreSQLConfig, RabbitMQConfig)
- Extracted TableMonitorConfig for declarative table definitions
- Separated concerns: CDCEventBuilder, TableChangeMonitor, DuplicateTracker
- Preserved: pytz timezone handling, >= comparison, dedup tracking, autocommit
"""

import pika
import json
import psycopg2
from psycopg2.extras import DictCursor
from psycopg2 import Error as PostgreSQLError
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv
import logging
import pytz
from typing import Dict, List, Optional, Set

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

VN_TIMEZONE = pytz.timezone('Asia/Ho_Chi_Minh')


# =============================================================================
# Configuration Classes (self-contained – separate Docker context)
# =============================================================================

class AppConfig:
    """Centralised environment variable access."""

    @staticmethod
    def env(key: str, default, cast=str):
        val = os.getenv(key)
        if val is None:
            return default
        return cast(val)


class PostgreSQLConfig:
    """PostgreSQL configuration with autocommit support."""

    def __init__(self, database_env: str = 'DB_DATABASE', autocommit: bool = True):
        self.config = {
            'host': AppConfig.env('DB_HOST', AppConfig.env('MYSQL_HOST', 'localhost')),
            'port': AppConfig.env('DB_PORT', AppConfig.env('MYSQL_PORT', 5432, int), int),
            'user': AppConfig.env('DB_USER', AppConfig.env('MYSQL_USER', 'postgres')),
            'password': AppConfig.env('DB_PASSWORD', AppConfig.env('MYSQL_PASSWORD', 'postgres')),
            'database': AppConfig.env(database_env, AppConfig.env('MYSQL_DATABASE', 'postgres')),
        }
        self.autocommit = autocommit

    def get_config(self) -> Dict:
        return self.config.copy()


class RabbitMQConfig:
    """RabbitMQ configuration."""

    def __init__(self):
        self.config = {
            'host': AppConfig.env('RABBITMQ_HOST', 'localhost'),
            'port': AppConfig.env('RABBITMQ_PORT', 5672, int),
            'user': AppConfig.env('RABBITMQ_USER', 'admin'),
            'password': AppConfig.env('RABBITMQ_PASS', 'admin'),
            'vhost': AppConfig.env('RABBITMQ_VHOST', '/affina'),
        }

    def get_config(self) -> Dict:
        return self.config.copy()


# Monitoring config
CHECK_INTERVAL = AppConfig.env('CHECK_INTERVAL', 30, int)
BATCH_SIZE = AppConfig.env('BATCH_SIZE', 100, int)


# =============================================================================
# Table Monitor Configuration
# =============================================================================

class TableMonitorConfig:
    """Declarative config for a table to monitor."""

    def __init__(self, table_name: str, id_column: str, timestamp_column: str, entity_name: str):
        self.table_name = table_name
        self.id_column = id_column
        self.timestamp_column = timestamp_column
        self.entity_name = entity_name


# Tables to monitor
MONITORED_TABLES = [
    TableMonitorConfig('stgInsuranceClaim', 'id', 'modifiedDate', 'claim'),
    TableMonitorConfig('stgInsuranceContract', 'contractId', 'modifiedDate', 'contract'),
]


# =============================================================================
# Duplicate Tracker
# =============================================================================

class DuplicateTracker:
    """
    Tracks already-processed records by ID+timestamp to detect true changes.
    Keeps only the last N entries to bound memory usage.
    """

    def __init__(self, max_entries: int = 1000, trim_to: int = 500):
        self._processed: Set[str] = set()
        self._max_entries = max_entries
        self._trim_to = trim_to

    def is_duplicate(self, record_id, timestamp) -> bool:
        """Check if record_id:timestamp was already processed."""
        key = f"{record_id}:{timestamp}"
        if key in self._processed:
            return True
        self._processed.add(key)
        self._trim()
        return False

    def _trim(self):
        """Trim set if it exceeds max_entries."""
        if len(self._processed) > self._max_entries:
            self._processed = set(list(self._processed)[-self._trim_to:])


# =============================================================================
# CDC Event Builder
# =============================================================================

class CDCEventBuilder:
    """Builds CDC event payloads."""

    EXCHANGE = 'affina.cdc.events'
    HEADERS = {'source': 'affina_reporting', 'producer': 'cdc_event_publisher'}

    @staticmethod
    def build(table_name: str, operation: str, record_id, row: Dict) -> Dict:
        return {
            'event_type': 'cdc',
            'table': table_name,
            'operation': operation,
            'record_id': record_id,
            'timestamp': datetime.now(VN_TIMEZONE).isoformat(),
            'data': dict(row),
        }

    @staticmethod
    def determine_operation(row: Dict, timestamp_column: str) -> str:
        if 'createdAt' in row and row['createdAt'] == row.get(timestamp_column):
            return 'insert'
        return 'update'


# =============================================================================
# PostgreSQL Connection Manager (self-contained)
# =============================================================================

class PostgreSQLConnectionManager:
    """PostgreSQL connection with reconnect."""

    def __init__(self, config: Dict, name: str = 'default', autocommit: bool = True):
        self._config = config
        self._name = name
        self._conn = None
        self._autocommit = autocommit

    @property
    def is_connected(self) -> bool:
        if self._conn is None:
            return False
        try:
            with self._conn.cursor() as cur:
                cur.execute('SELECT 1')
            return True
        except Exception:
            return False

    def connect(self, max_retries: int = 3):
        for attempt in range(max_retries):
            try:
                if self._conn:
                    try:
                        self._conn.close()
                    except Exception:
                        pass
                self._conn = psycopg2.connect(
                    **self._config,
                    cursor_factory=DictCursor
                )
                self._conn.autocommit = self._autocommit
                with self._conn.cursor() as cur:
                    if self._name == 'staging':
                        cur.execute('SET search_path TO staging, public')
                    elif self._name == 'reporting':
                        cur.execute('SET search_path TO reporting, public')
                logger.info("[OK] Connected to PostgreSQL: %s (role: %s)",
                            self._config.get('database'), self._name)
                return
            except Exception as e:
                logger.error("[ERROR] PostgreSQL %s failed (attempt %d/%d): %s",
                             self._name, attempt + 1, max_retries, e)
                if attempt < max_retries - 1:
                    time.sleep(5)
                else:
                    raise

    def ensure_connected(self):
        if not self.is_connected:
            self.connect()

    def cursor(self):
        self.ensure_connected()
        return self._conn.cursor()

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
            logger.info("[OK] PostgreSQL %s closed", self._name)


# =============================================================================
# RabbitMQ Connection Manager (self-contained)
# =============================================================================

class RabbitMQConnectionManager:
    """RabbitMQ connection with reconnect and publish retry."""

    def __init__(self, config: Dict):
        self._config = config
        self._conn = None
        self._channel = None

    def connect(self, max_retries: int = 3):
        for attempt in range(max_retries):
            try:
                if self._conn and not self._conn.is_closed:
                    self._conn.close()
                credentials = pika.PlainCredentials(self._config['user'], self._config['password'])
                params = pika.ConnectionParameters(
                    host=self._config['host'],
                    port=self._config['port'],
                    virtual_host=self._config['vhost'],
                    credentials=credentials,
                    heartbeat=600,
                    blocked_connection_timeout=300,
                )
                self._conn = pika.BlockingConnection(params)
                self._channel = self._conn.channel()
                logger.info("[OK] Connected to RabbitMQ: %s", self._config['host'])
                return
            except Exception as e:
                logger.error("[ERROR] RabbitMQ failed (attempt %d/%d): %s",
                             attempt + 1, max_retries, e)
                if attempt < max_retries - 1:
                    time.sleep(5)
                else:
                    raise

    def ensure_connected(self) -> bool:
        try:
            if (self._conn is None or self._conn.is_closed or
                    self._channel is None or self._channel.is_closed):
                self.connect()
            return True
        except Exception as e:
            logger.error("[ERROR] RabbitMQ ensure_connected failed: %s", e)
            return False

    def publish(self, exchange: str, routing_key: str, event_data: Dict,
                headers: Dict = None, max_retries: int = 3) -> bool:
        for attempt in range(max_retries):
            try:
                if not self.ensure_connected():
                    time.sleep(1)
                    continue

                body = json.dumps(event_data, default=str)
                self._channel.basic_publish(
                    exchange=exchange,
                    routing_key=routing_key,
                    body=body,
                    properties=pika.BasicProperties(
                        delivery_mode=2,
                        content_type='application/json',
                        timestamp=int(time.time()),
                        headers=headers or {},
                    ),
                )
                logger.info("[PUBLISHED] %s | ID: %s", routing_key, event_data.get('record_id'))
                return True
            except (pika.exceptions.ChannelClosedByBroker,
                    pika.exceptions.ChannelWrongStateError,
                    pika.exceptions.StreamLostError,
                    pika.exceptions.AMQPConnectionError) as e:
                logger.error("[ERROR] RabbitMQ error for %s: %s", routing_key, e)
                self._conn = None
                self._channel = None
                if attempt < max_retries - 1:
                    time.sleep(2)
            except Exception as e:
                logger.error("[ERROR] Publish error for %s: %s", routing_key, e)
                return False

        logger.error("[ERROR] Max retries reached for %s", routing_key)
        return False

    def close(self):
        if self._conn and not self._conn.is_closed:
            self._conn.close()
            logger.info("[OK] RabbitMQ connection closed")


# =============================================================================
# Table Change Monitor
# =============================================================================

class TableChangeMonitor:
    """Monitors a single table for CDC changes using >= comparison and dedup tracking."""

    def __init__(self, db: PostgreSQLConnectionManager, config: TableMonitorConfig,
                 batch_size: int = 100):
        self._db = db
        self._config = config
        self._batch_size = batch_size
        self._last_sync: Optional[datetime] = None
        self._dedup = DuplicateTracker()

    @property
    def entity_name(self) -> str:
        return self._config.entity_name

    def check_changes(self) -> List[Dict]:
        """Poll table for changes. Returns list of {routing_key, event} dicts."""
        self._db.ensure_connected()
        cursor = self._db.cursor()
        events = []

        try:
            # Check existence in current schema
            cursor.execute(
                """SELECT 1 FROM information_schema.tables 
                   WHERE table_schema = %s AND table_name = %s""",
                [self._db._name, self._config.table_name]
            )
            if not cursor.fetchone():
                cursor.close()
                return events

            last_sync = self._last_sync or (datetime.now() - timedelta(hours=1))
            if hasattr(last_sync, 'tzinfo') and last_sync.tzinfo is not None:
                last_sync = last_sync.replace(tzinfo=None)

            logger.info("[QUERY] %s | last_sync = %s",
                        self._config.table_name, last_sync)

            # Use >= to catch records with same timestamp and double quote identifiers
            query = f"""
            SELECT *
            FROM "{self._db._name}"."{self._config.table_name}"
            WHERE "{self._config.timestamp_column}" >= %s
            ORDER BY "{self._config.timestamp_column}" ASC
            LIMIT {self._batch_size}
            """
            cursor.execute(query, (last_sync,))
            rows = cursor.fetchall()
            logger.info("[QUERY] %s | Found %d rows", self._config.table_name, len(rows))

            new_rows = []
            for row in rows:
                record_id = row.get(self._config.id_column)
                record_ts = row.get(self._config.timestamp_column)
                if self._dedup.is_duplicate(record_id, record_ts):
                    continue
                new_rows.append(row)

            logger.info("[QUERY] %s | New rows after dedup: %d",
                        self._config.table_name, len(new_rows))

            for row in new_rows:
                operation = CDCEventBuilder.determine_operation(row, self._config.timestamp_column)
                routing_key = f"{self._config.entity_name}.{operation}"

                record_id = row.get(self._config.id_column)
                if record_id is None:
                    logger.warning("[WARNING] %s: ID column '%s' is NULL. Keys: %s",
                                   self._config.table_name, self._config.id_column,
                                   list(row.keys())[:10])

                event = CDCEventBuilder.build(
                    self._config.table_name, operation, record_id, row,
                )
                events.append({'routing_key': routing_key, 'event': event})

                row_ts = row.get(self._config.timestamp_column)
                if row_ts:
                    self._last_sync = row_ts

        except Exception as e:
            logger.error("[ERROR] Error checking %s: %s", self._config.table_name, e)
        finally:
            cursor.close()

        return events


# =============================================================================
# Main Event Publisher
# =============================================================================

class AffinaEventPublisher:
    """
    Production event publisher: monitors staging → RabbitMQ on PostgreSQL.

    Preserved from original:
    - pytz VN_TIMEZONE for timestamps
    - >= comparison in change queries
    - Dedup tracking per table via DuplicateTracker
    - autocommit=True in configs
    """

    def __init__(self):
        staging_cfg = PostgreSQLConfig('DB_DATABASE', autocommit=True).get_config()
        reporting_cfg = PostgreSQLConfig('DB_DATABASE', autocommit=True).get_config()
        rmq_cfg = RabbitMQConfig().get_config()

        self._staging_db = PostgreSQLConnectionManager(staging_cfg, 'staging', autocommit=True)
        self._reporting_db = PostgreSQLConnectionManager(reporting_cfg, 'reporting', autocommit=True)
        self._rmq = RabbitMQConnectionManager(rmq_cfg)

        self._monitors = [
            TableChangeMonitor(self._staging_db, cfg, BATCH_SIZE)
            for cfg in MONITORED_TABLES
        ]
        self._event_counts = {cfg.entity_name: 0 for cfg in MONITORED_TABLES}

    def run(self):
        """Main polling loop."""
        logger.info("=" * 60)
        logger.info("AFFINA EVENT PUBLISHER STARTED")
        logger.info("=" * 60)
        logger.info("Monitoring: staging + reporting (PostgreSQL)")
        logger.info("Check interval: %ds", CHECK_INTERVAL)
        logger.info("Tables: %s", [m.entity_name for m in self._monitors])
        logger.info("=" * 60)

        try:
            self._staging_db.connect()
            self._reporting_db.connect()
            self._rmq.connect()

            while True:
                try:
                    self._ensure_connections()
                    self._poll_cycle()
                    logger.info("[INFO] Sleeping %ds until next poll...", CHECK_INTERVAL)
                    time.sleep(CHECK_INTERVAL)

                except PostgreSQLError as e:
                    logger.error("[ERROR] PostgreSQL error: %s", e)
                    time.sleep(5)
                    self._reconnect_all()

                except pika.exceptions.AMQPError as e:
                    logger.error("[ERROR] RabbitMQ error: %s", e)
                    time.sleep(5)
                    self._reconnect_all()

                except Exception as e:
                    logger.error("[ERROR] Unexpected error: %s", e)
                    time.sleep(10)
                    self._reconnect_all()

        except KeyboardInterrupt:
            logger.info("Shutting down gracefully...")
        finally:
            self._cleanup()

    def _poll_cycle(self):
        """Execute one polling cycle."""
        start = time.time()
        total = 0

        for monitor in self._monitors:
            events = monitor.check_changes()
            for item in events:
                self._rmq.publish(
                    CDCEventBuilder.EXCHANGE,
                    item['routing_key'],
                    item['event'],
                    headers=CDCEventBuilder.HEADERS,
                )
                self._event_counts[monitor.entity_name] = \
                    self._event_counts.get(monitor.entity_name, 0) + 1
                total += 1

        elapsed = time.time() - start
        if total > 0:
            logger.info("[OK] Published %d events in %.2fs", total, elapsed)
            logger.info("[INFO] Total counts: %s", self._event_counts)
        else:
            logger.info("[INFO] No new events in this cycle")

    def _ensure_connections(self):
        if not self._staging_db.is_connected:
            self._staging_db.connect()
        if not self._reporting_db.is_connected:
            self._reporting_db.connect()
        self._rmq.ensure_connected()

    def _reconnect_all(self):
        for label, db in [('staging', self._staging_db), ('reporting', self._reporting_db)]:
            try:
                db.connect()
            except Exception as e:
                logger.error("Failed to reconnect %s: %s", label, e)
        try:
            self._rmq.connect()
        except Exception as e:
            logger.error("Failed to reconnect RabbitMQ: %s", e)

    def _cleanup(self):
        self._staging_db.close()
        self._reporting_db.close()
        self._rmq.close()


if __name__ == '__main__':
    publisher = AffinaEventPublisher()
    publisher.run()
