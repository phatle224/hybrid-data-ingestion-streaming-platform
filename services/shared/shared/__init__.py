"""
Shared OOP base package for CDC Reporting consumers.

Provides reusable base classes, connection managers, transformers,
and utilities following the reporting-main architecture patterns.

Usage:
    from shared import MySQLConfig, DebeziumTransformer, BaseKafkaConsumer
    from shared.connections import MySQLConnectionManager
"""
from shared.logger import create_logger
from shared.configs import BaseConfig, MySQLConfig, PostgreSQLConfig, KafkaConfig, RedisConfig
from shared.connections import (
    MySQLConnectionManager,
    PostgreSQLConnectionManager,
    KafkaConsumerFactory,
    RedisConnectionManager,
)
from shared.debezium import DebeziumTransformer
from shared.query_builder import SQLQueryBuilder
from shared.base_consumer import BaseKafkaConsumer

__all__ = [
    'create_logger',
    'BaseConfig', 'MySQLConfig', 'PostgreSQLConfig', 'KafkaConfig', 'RedisConfig',
    'MySQLConnectionManager', 'PostgreSQLConnectionManager', 'KafkaConsumerFactory',
    'RedisConnectionManager',
    'DebeziumTransformer', 'SQLQueryBuilder', 'BaseKafkaConsumer',
]
