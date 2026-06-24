"""
Centralized configuration classes.
Following reporting-main pattern: BaseConfig → specific config classes.

All configs read from environment variables with sensible defaults.
Supports explicit parameter overrides for flexibility.
"""
import os
from typing import Any, Dict


class BaseConfig:
    """
    Base configuration class with env variable support.
    Inspired by reporting-main Configs pattern.
    """

    def __init__(self):
        self._config: Dict[str, Any] = {}

    def get_config(self) -> Dict[str, Any]:
        """Get a copy of the configuration dictionary."""
        return self._config.copy()

    def to_dict(self) -> Dict[str, Any]:
        """Get config as dictionary (alias for get_config, matches backend pattern)."""
        return self.get_config()

    @staticmethod
    def env(key: str, default: Any = None, cast: type = str) -> Any:
        """
        Get environment variable with optional type casting.

        Args:
            key: Environment variable name
            default: Default value if not set
            cast: Type to cast the value to (str, int, float, bool)
        """
        value = os.getenv(key, None)
        if value is None:
            return default
        if cast == int:
            return int(value)
        if cast == float:
            return float(value)
        if cast == bool:
            return value.lower() in ('true', '1', 'yes')
        return value


class MySQLConfig(BaseConfig):
    """
    MySQL database configuration.

    Supports multiple database connections by customizing env variable prefixes.
    Example:
        staging = MySQLConfig(database='affina_staging')
        reporting = MySQLConfig(database='affina_reporting')
        profiling_staging = MySQLConfig(host_env='STAGING_DB_HOST', user_env='STAGING_DB_USER', ...)
    """

    def __init__(
        self,
        database: str = None,
        host: str = None,
        port: int = None,
        user: str = None,
        password: str = None,
        host_env: str = 'MYSQL_HOST',
        port_env: str = 'MYSQL_PORT',
        user_env: str = 'MYSQL_USER',
        password_env: str = 'MYSQL_PASSWORD',
        database_env: str = 'MYSQL_DATABASE',
        charset: str = None,
        autocommit: bool = None,
    ):
        super().__init__()
        self._config = {
            'host': host or self.env(host_env, '172.16.10.32'),
            'port': port or self.env(port_env, 3306, int),
            'user': user or self.env(user_env, 'aff_admin'),
            'password': password or self.env(password_env, 'affina_poOB7G9A51'),
            'database': database or self.env(database_env, 'affina_staging'),
        }
        if charset:
            self._config['charset'] = charset
        if autocommit is not None:
            self._config['autocommit'] = autocommit

    # ── Property access (matches backend DatabaseConfig pattern) ──

    @property
    def host(self) -> str:
        return self._config['host']

    @property
    def port(self) -> int:
        return self._config['port']

    @property
    def user(self) -> str:
        return self._config['user']

    @property
    def password(self) -> str:
        return self._config['password']

    @property
    def database(self) -> str:
        return self._config['database']


class KafkaConfig(BaseConfig):
    """Kafka consumer configuration."""

    def __init__(
        self,
        bootstrap_servers: str = None,
        group_id: str = None,
        auto_offset_reset: str = 'earliest',
        enable_auto_commit: bool = True,
        max_poll_interval_ms: int = 300000,
        session_timeout_ms: int = 30000,
    ):
        super().__init__()
        self._config = {
            'bootstrap_servers': bootstrap_servers or self.env(
                'KAFKA_BOOTSTRAP_SERVERS', 'kafka:9093'
            ),
            'group_id': group_id or self.env('CONSUMER_GROUP', 'default-consumer-v1'),
            'auto_offset_reset': auto_offset_reset,
            'enable_auto_commit': enable_auto_commit,
            'max_poll_interval_ms': max_poll_interval_ms,
            'session_timeout_ms': session_timeout_ms,
        }


class RedisConfig(BaseConfig):
    """Redis configuration."""

    def __init__(
        self,
        host: str = None,
        port: int = None,
        password: str = None,
        db: int = None,
    ):
        super().__init__()
        self._config = {
            'host': host or self.env('REDIS_HOST', 'cdc_redis'),
            'port': port or self.env('REDIS_PORT', 6379, int),
            'password': password or self.env('REDIS_PASSWORD', 'admin'),
            'db': db if db is not None else self.env('REDIS_DB', 0, int),
        }


class RabbitMQConfig(BaseConfig):
    """RabbitMQ configuration."""

    def __init__(
        self,
        host: str = None,
        port: int = None,
        user: str = None,
        password: str = None,
        vhost: str = None,
    ):
        super().__init__()
        self._config = {
            'host': host or self.env('RABBITMQ_HOST', 'localhost'),
            'port': port or self.env('RABBITMQ_PORT', 5672, int),
            'user': user or self.env('RABBITMQ_USER', 'admin'),
            'password': password or self.env('RABBITMQ_PASS', 'admin'),
            'vhost': vhost or self.env('RABBITMQ_VHOST', '/affina'),
            'heartbeat': self.env('RABBITMQ_HEARTBEAT', 600, int),
            'blocked_connection_timeout': self.env('RABBITMQ_BLOCKED_TIMEOUT', 300, int),
        }


class PostgreSQLConfig(BaseConfig):
    """
    PostgreSQL database configuration.
    """

    def __init__(
        self,
        database: str = None,
        host: str = None,
        port: int = None,
        user: str = None,
        password: str = None,
        host_env: str = 'DB_HOST',
        port_env: str = 'DB_PORT',
        user_env: str = 'DB_USER',
        password_env: str = 'DB_PASSWORD',
        database_env: str = 'DB_DATABASE',
    ):
        super().__init__()
        self._config = {
            'host': host or self.env(host_env, 'localhost'),
            'port': port or self.env(port_env, 5432, int),
            'user': user or self.env(user_env, 'postgres'),
            'password': password or self.env(password_env, 'postgres'),
            'database': database or self.env(database_env, 'postgres'),
        }

    @property
    def host(self) -> str:
        return self._config['host']

    @property
    def port(self) -> int:
        return self._config['port']

    @property
    def user(self) -> str:
        return self._config['user']

    @property
    def password(self) -> str:
        return self._config['password']

    @property
    def database(self) -> str:
        return self._config['database']
