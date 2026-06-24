"""
Connection managers for MySQL, Kafka, Redis, and RabbitMQ.
Provides retry logic, auto-reconnection, and resource cleanup.

Following reporting-main patterns:
- CConns → MySQLConnectionManager
- KafkaConfig → KafkaConsumerFactory
- RedisClusterConnection → RedisConnectionManager
- RabbitMQ → RabbitMQConnectionManager
"""
import json
import logging
import time
from typing import Any, Dict, List, Optional, Set

import mysql.connector
from mysql.connector import Error as MySQLError
import psycopg2
from psycopg2 import Error as PostgreSQLError
from psycopg2.extras import RealDictCursor
from kafka import KafkaConsumer
import redis
import pika

logger = logging.getLogger(__name__)


# =============================================================================
# MySQL Connection Manager
# =============================================================================

class MySQLConnectionManager:
    """
    MySQL connection with automatic reconnection and retry logic.
    Follows backend DatabaseConnection pattern with context manager support.

    Usage (persistent - for Kafka consumers):
        db = MySQLConnectionManager(config, 'staging')
        db.connect()
        db.execute("INSERT INTO ...", [values])
        result = db.fetch_one("SELECT * FROM ... WHERE id=%s", [1])
        db.close()

    Usage (context manager - for batch ETL):
        with MySQLConnectionManager(config, 'batch') as db:
            db.execute("INSERT INTO ...", [values])
            result = db.fetch_one("SELECT * FROM ...")
            # auto-commit on success, rollback on error
    """

    def __init__(self, config: Dict[str, Any], name: str = 'default'):
        self._config = config
        self._name = name
        self._connection = None

    # ── Context Manager (mirrors backend DatabaseConnection) ───

    def __enter__(self):
        """Enter context manager: connect and return self."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager: commit on success, rollback on error, close."""
        try:
            if exc_type is not None:
                if self._connection and self._connection.is_connected():
                    self._connection.rollback()
                    logger.warning("[%s] Transaction rolled back due to: %s", self._name, exc_val)
            else:
                if self._connection and self._connection.is_connected():
                    self._connection.commit()
        finally:
            self.close()
        return False  # Don't suppress exceptions

    @property
    def connection(self):
        """Raw mysql.connector connection (for advanced use)."""
        return self._connection

    @property
    def is_connected(self) -> bool:
        return self._connection is not None and self._connection.is_connected()

    def connect(self, max_retries: int = 3, retry_delay: int = 5) -> bool:
        """Establish MySQL connection with retry."""
        for attempt in range(max_retries):
            try:
                if self._connection and self._connection.is_connected():
                    self._connection.close()
                self._connection = mysql.connector.connect(**self._config)
                logger.info(
                    "[%s] Connected to MySQL: %s",
                    self._name, self._config.get('database')
                )
                return True
            except MySQLError as e:
                logger.error(
                    "[%s] Connection failed (attempt %d/%d): %s",
                    self._name, attempt + 1, max_retries, e
                )
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        return False

    def ensure_connected(self):
        """Ensure connection is alive, reconnect if needed."""
        if not self.is_connected:
            logger.warning("[%s] Connection lost, reconnecting...", self._name)
            try:
                if self._connection:
                    self._connection.reconnect(attempts=3, delay=5)
                else:
                    self.connect()
            except MySQLError:
                self.connect()

    def execute(self, query: str, values: list = None, commit: bool = True) -> bool:
        """Execute a query with auto-reconnect. Raises MySQLError on failure."""
        try:
            self.ensure_connected()
            cursor = self._connection.cursor()
            cursor.execute(query, values)
            if commit:
                self._connection.commit()
            cursor.close()
            return True
        except MySQLError as e:
            logger.error("[%s] Query failed: %s", self._name, e)
            logger.error("[%s] Query: %s...", self._name, query[:200])
            try:
                self._connection.rollback()
            except Exception:
                pass
            raise  # re-raise so callers (cdc_consumer._handle_insert) can catch & log

    def execute_with_rowcount(self, query: str, values: list = None) -> int:
        """Execute query and return affected row count. Returns -1 on error."""
        try:
            self.ensure_connected()
            cursor = self._connection.cursor()
            cursor.execute(query, values)
            affected = cursor.rowcount
            self._connection.commit()
            cursor.close()
            return affected
        except MySQLError as e:
            logger.error("[%s] Query failed: %s", self._name, e)
            return -1

    def fetch_one(self, query: str, values: list = None) -> Optional[Dict]:
        """Fetch a single row as dictionary."""
        try:
            self.ensure_connected()
            cursor = self._connection.cursor(dictionary=True)
            cursor.execute(query, values)
            result = cursor.fetchone()
            cursor.close()
            return result
        except MySQLError as e:
            logger.error("[%s] Fetch failed: %s", self._name, e)
            return None

    def fetch_all(self, query: str, values: list = None) -> List[Dict]:
        """Fetch all rows as dictionaries."""
        try:
            self.ensure_connected()
            cursor = self._connection.cursor(dictionary=True)
            cursor.execute(query, values)
            results = cursor.fetchall()
            cursor.close()
            return results
        except MySQLError as e:
            logger.error("[%s] Fetch all failed: %s", self._name, e)
            return []

    def load_table_columns(self, table_name: str) -> Optional[Set[str]]:
        """Load column names for a specific table."""
        try:
            self.ensure_connected()
            cursor = self._connection.cursor()
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = {row[0] for row in cursor.fetchall()}
            cursor.close()
            logger.info(
                "[%s] Loaded %d columns for %s",
                self._name, len(columns), table_name
            )
            return columns
        except MySQLError as e:
            logger.error(
                "[%s] Failed to load schema for %s: %s",
                self._name, table_name, e
            )
            return None

    def create_cursor(self, dictionary: bool = True):
        """Create a cursor for manual operations."""
        self.ensure_connected()
        return self._connection.cursor(dictionary=dictionary)

    def commit(self):
        """Commit current transaction."""
        if self._connection:
            self._connection.commit()

    def close(self):
        """Close the connection."""
        if self.is_connected:
            self._connection.close()
            logger.info("[%s] MySQL connection closed", self._name)


# =============================================================================
# PostgreSQL Connection Manager
# =============================================================================

class PostgreSQLConnectionManager:
    """
    PostgreSQL connection with automatic reconnection and retry logic.
    Provides identical API to MySQLConnectionManager for easy drop-in replacement.
    """

    def __init__(self, config: Dict[str, Any], name: str = 'default'):
        self._config = config
        self._name = name
        self._connection = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                if self._connection and not self._connection.closed:
                    self._connection.rollback()
                    logger.warning("[%s] Transaction rolled back due to: %s", self._name, exc_val)
            else:
                if self._connection and not self._connection.closed:
                    self._connection.commit()
        finally:
            self.close()
        return False

    @property
    def connection(self):
        return self._connection

    @property
    def is_connected(self) -> bool:
        return self._connection is not None and not self._connection.closed

    def connect(self, max_retries: int = 3, retry_delay: int = 5) -> bool:
        """Establish PostgreSQL connection with retry."""
        pg_config = {
            'host': self._config.get('host'),
            'port': self._config.get('port'),
            'user': self._config.get('user') or self._config.get('username'),
            'password': self._config.get('password'),
            'database': self._config.get('database') or self._config.get('dbname'),
        }
        pg_config = {k: v for k, v in pg_config.items() if v is not None}

        for attempt in range(max_retries):
            try:
                if self._connection and not self._connection.closed:
                    self._connection.close()
                self._connection = psycopg2.connect(**pg_config)
                
                # Automatically set search path if name is specified (e.g. 'staging')
                if self._name and self._name != 'default':
                    with self._connection.cursor() as cursor:
                        cursor.execute(f'SET search_path TO "{self._name}", public;')
                        self._connection.commit()
                
                logger.info(
                    "[%s] Connected to PostgreSQL: %s",
                    self._name, pg_config.get('database')
                )
                return True
            except PostgreSQLError as e:
                logger.error(
                    "[%s] PostgreSQL Connection failed (attempt %d/%d): %s",
                    self._name, attempt + 1, max_retries, e
                )
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        return False

    def ensure_connected(self):
        """Ensure connection is alive, reconnect if needed."""
        if not self.is_connected:
            logger.warning("[%s] PostgreSQL connection lost, reconnecting...", self._name)
            self.connect()

    def execute(self, query: str, values: list = None, commit: bool = True) -> bool:
        """Execute a query with auto-reconnect. Raises PostgreSQLError on failure."""
        try:
            self.ensure_connected()
            with self._connection.cursor() as cursor:
                cursor.execute(query, values)
                if commit:
                    self._connection.commit()
            return True
        except PostgreSQLError as e:
            logger.error("[%s] Query failed: %s", self._name, e)
            logger.error("[%s] Query: %s...", self._name, query[:200])
            try:
                self._connection.rollback()
            except Exception:
                pass
            raise

    def execute_with_rowcount(self, query: str, values: list = None) -> int:
        """Execute query and return affected row count. Returns -1 on error."""
        try:
            self.ensure_connected()
            with self._connection.cursor() as cursor:
                cursor.execute(query, values)
                affected = cursor.rowcount
                self._connection.commit()
            return affected
        except PostgreSQLError as e:
            logger.error("[%s] Query failed: %s", self._name, e)
            return -1

    def fetch_one(self, query: str, values: list = None) -> Optional[Dict]:
        """Fetch a single row as dictionary."""
        try:
            self.ensure_connected()
            with self._connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, values)
                result = cursor.fetchone()
                if result is not None:
                    result = dict(result)
                return result
        except PostgreSQLError as e:
            logger.error("[%s] Fetch failed: %s", self._name, e)
            return None

    def fetch_all(self, query: str, values: list = None) -> List[Dict]:
        """Fetch all rows as dictionaries."""
        try:
            self.ensure_connected()
            with self._connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, values)
                results = [dict(row) for row in cursor.fetchall()]
                return results
        except PostgreSQLError as e:
            logger.error("[%s] Fetch all failed: %s", self._name, e)
            return []

    def load_table_columns(self, table_name: str) -> Optional[Set[str]]:
        """Load column names for a specific table from PostgreSQL information_schema."""
        try:
            self.ensure_connected()
            schema_name = self._name if self._name != 'default' else 'public'
            query = """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s 
                  AND table_schema = %s
            """
            with self._connection.cursor() as cursor:
                cursor.execute(query, (table_name, schema_name))
                columns = {row[0] for row in cursor.fetchall()}
            logger.info(
                "[%s] Loaded %d columns for %s",
                self._name, len(columns), table_name
            )
            return columns
        except PostgreSQLError as e:
            logger.error(
                "[%s] Failed to load schema for %s: %s",
                self._name, table_name, e
            )
            return None

    def create_cursor(self, dictionary: bool = True):
        self.ensure_connected()
        if dictionary:
            return self._connection.cursor(cursor_factory=RealDictCursor)
        return self._connection.cursor()

    def commit(self):
        if self._connection:
            self._connection.commit()

    def close(self):
        if self.is_connected:
            self._connection.close()
            logger.info("[%s] PostgreSQL connection closed", self._name)


# =============================================================================
# Kafka Consumer Factory
# =============================================================================

class KafkaConsumerFactory:
    """
    Factory for creating Kafka consumers with retry logic.
    Inspired by reporting-main CKafka2MySQLConsumerTemplate pattern.

    Usage:
        consumer = KafkaConsumerFactory.create(
            topics=['topic1', 'topic2'],
            bootstrap_servers='kafka:9093',
            group_id='my-group-v1'
        )
    """

    @staticmethod
    def create(
        topics: List[str],
        bootstrap_servers: str,
        group_id: str,
        auto_offset_reset: str = 'earliest',
        enable_auto_commit: bool = True,
        max_poll_interval_ms: int = 300000,
        session_timeout_ms: int = 30000,
        max_retries: int = 10,
        retry_delay: int = 5,
    ) -> Optional[KafkaConsumer]:
        """Create a Kafka consumer with retry logic."""
        for attempt in range(max_retries):
            try:
                consumer = KafkaConsumer(
                    *topics,
                    bootstrap_servers=bootstrap_servers,
                    auto_offset_reset=auto_offset_reset,
                    enable_auto_commit=enable_auto_commit,
                    group_id=group_id,
                    value_deserializer=lambda x: json.loads(
                        x.decode('utf-8')
                    ) if x else None,
                    max_poll_interval_ms=max_poll_interval_ms,
                    session_timeout_ms=session_timeout_ms,
                )
                logger.info(
                    "Kafka consumer created. Subscribed to %d topics:",
                    len(topics)
                )
                for topic in topics:
                    logger.info("  - %s", topic)
                return consumer
            except Exception as e:
                logger.error(
                    "Attempt %d/%d - Kafka connection failed: %s",
                    attempt + 1, max_retries, e
                )
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)

        logger.error("Max retries reached. Could not connect to Kafka.")
        return None


# =============================================================================
# Redis Connection Manager
# =============================================================================

class RedisConnectionManager:
    """
    Redis connection manager with graceful degradation.

    Usage:
        redis_mgr = RedisConnectionManager(config)
        redis_mgr.connect()
        redis_mgr.setex('key', 3600, 'value')
        exists = redis_mgr.exists('key')
    """

    def __init__(self, config: Dict[str, Any]):
        self._config = config
        self._client: Optional[redis.Redis] = None

    @property
    def client(self) -> Optional[redis.Redis]:
        return self._client

    @property
    def is_connected(self) -> bool:
        return self._client is not None

    def connect(self) -> bool:
        """Connect to Redis. Returns False gracefully on failure."""
        try:
            self._client = redis.Redis(
                host=self._config['host'],
                port=self._config['port'],
                password=self._config.get('password'),
                db=self._config.get('db', 0),
                decode_responses=True,
            )
            self._client.ping()
            logger.info(
                "Connected to Redis at %s:%s",
                self._config['host'], self._config['port']
            )
            return True
        except Exception as e:
            logger.warning("Redis connection failed: %s. Continuing without Redis.", e)
            self._client = None
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self._client:
            return False
        try:
            return self._client.exists(key) > 0
        except Exception as e:
            logger.warning("Redis exists check failed: %s", e)
            return False

    def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        if not self._client:
            return None
        try:
            return self._client.get(key)
        except Exception:
            return None

    def setex(self, key: str, ttl: int, value: str):
        """Set key with TTL expiry."""
        if not self._client:
            return
        try:
            self._client.setex(key, ttl, value)
        except Exception as e:
            logger.warning("Redis setex failed: %s", e)

    def keys(self, pattern: str) -> List[str]:
        """Get keys matching pattern. WARNING: O(N) — blocks Redis. Use scan_iter() instead."""
        if not self._client:
            return []
        try:
            return self._client.keys(pattern)
        except Exception:
            return []

    def scan_iter(self, match: str = '*', count: int = 500):
        """Iterate keys matching pattern using SCAN (non-blocking, cursor-based)."""
        if not self._client:
            return iter([])
        try:
            return self._client.scan_iter(match=match, count=count)
        except Exception as e:
            logger.warning("Redis scan_iter failed: %s", e)
            return iter([])

    def info(self) -> Dict:
        """Get Redis server info."""
        if not self._client:
            return {}
        return self._client.info()

    def close(self):
        """Close Redis connection."""
        if self._client:
            self._client.close()
            logger.info("Redis connection closed")


# =============================================================================
# RabbitMQ Connection Manager
# =============================================================================

class RabbitMQConnectionManager:
    """
    RabbitMQ connection manager with retry logic.
    Inspired by reporting-main RabbitMQ + RabbitMQProCon patterns.

    Usage:
        rmq = RabbitMQConnectionManager(config)
        rmq.connect()
        rmq.publish('exchange', 'routing.key', {'data': 'value'})
        rmq.close()
    """

    def __init__(self, config: Dict[str, Any]):
        self._config = config
        self._connection = None
        self._channel = None

    @property
    def channel(self):
        return self._channel

    def connect(self, max_retries: int = 3, retry_delay: int = 5) -> bool:
        """Connect to RabbitMQ with retry."""
        for attempt in range(max_retries):
            try:
                if self._connection and not self._connection.is_closed:
                    self._connection.close()

                credentials = pika.PlainCredentials(
                    self._config['user'], self._config['password']
                )
                parameters = pika.ConnectionParameters(
                    host=self._config['host'],
                    port=self._config['port'],
                    virtual_host=self._config['vhost'],
                    credentials=credentials,
                    heartbeat=self._config.get('heartbeat', 600),
                    blocked_connection_timeout=self._config.get(
                        'blocked_connection_timeout', 300
                    ),
                )
                self._connection = pika.BlockingConnection(parameters)
                self._channel = self._connection.channel()
                logger.info("Connected to RabbitMQ: %s", self._config['host'])
                return True
            except Exception as e:
                logger.error(
                    "RabbitMQ connection failed (attempt %d/%d): %s",
                    attempt + 1, max_retries, e
                )
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        return False

    def ensure_connected(self) -> bool:
        """Ensure connection and channel are open."""
        try:
            if (self._connection is None or self._connection.is_closed or
                    self._channel is None or self._channel.is_closed):
                logger.warning("RabbitMQ connection/channel not ready, reconnecting...")
                return self.connect()
            return True
        except Exception as e:
            logger.error("Failed to ensure RabbitMQ connection: %s", e)
            return False

    def publish(
        self,
        exchange: str,
        routing_key: str,
        message: Dict,
        headers: Dict = None,
        max_retries: int = 3,
    ) -> bool:
        """Publish message to exchange with retry logic."""
        for attempt in range(max_retries):
            try:
                if not self.ensure_connected():
                    time.sleep(1)
                    continue

                body = json.dumps(message, default=str)
                properties = pika.BasicProperties(
                    delivery_mode=2,  # Persistent
                    content_type='application/json',
                    timestamp=int(time.time()),
                    headers=headers or {},
                )

                self._channel.basic_publish(
                    exchange=exchange,
                    routing_key=routing_key,
                    body=body,
                    properties=properties,
                )
                logger.info(
                    "[PUBLISHED] %s | ID: %s",
                    routing_key, message.get('record_id')
                )
                return True

            except (pika.exceptions.ChannelClosedByBroker,
                    pika.exceptions.ChannelWrongStateError,
                    pika.exceptions.StreamLostError,
                    pika.exceptions.AMQPConnectionError) as e:
                logger.error("RabbitMQ error for %s: %s", routing_key, e)
                self._connection = None
                self._channel = None
                if attempt < max_retries - 1:
                    time.sleep(2)

            except Exception as e:
                logger.error("Publish error for %s: %s", routing_key, e)
                return False

        logger.error("Max retries reached for %s", routing_key)
        return False

    def close(self):
        """Close RabbitMQ connection."""
        if self._connection and not self._connection.is_closed:
            self._connection.close()
            logger.info("RabbitMQ connection closed")
