"""
Abstract base class for all Kafka CDC consumers.
Implements Template Method pattern for consumer lifecycle.

Inspired by reporting-main CKafka2MySQLConsumerTemplate.

Usage:
    class MyConsumer(BaseKafkaConsumer):
        def _get_topics(self): return ['topic1']
        def _get_kafka_config(self): return {...}
        def _setup_connections(self): ...
        def process_message(self, topic, msg): ...
        def _cleanup_connections(self): ...

    consumer = MyConsumer('My Consumer')
    consumer.run()
"""
import json
import logging
import signal
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List

from shared.connections import KafkaConsumerFactory

logger = logging.getLogger(__name__)


class BaseKafkaConsumer(ABC):
    """
    Abstract base for Kafka consumers.

    Implements Template Method pattern:
        1. setup()  → _setup_connections() + _create_kafka_consumer()
        2. run()    → loops over messages → process_message()
        3. cleanup() → close all resources

    Subclasses MUST implement:
        - _get_topics()          → list of Kafka topics
        - _get_kafka_config()    → dict with bootstrap_servers, group_id, etc.
        - _setup_connections()   → set up DB connections, return bool
        - process_message()      → handle a single message
        - _cleanup_connections() → close DB connections
    """

    # Maximum consecutive failures before a message is sent to DLQ
    MAX_RETRIES_PER_MESSAGE = 3

    def __init__(self, name: str, logger_instance: logging.Logger = None):
        self.name = name
        self.logger = logger_instance or logging.getLogger(name)
        self._kafka_consumer = None
        self._running = True
        self._stats = self._init_stats()

    # ── Stats Management ───────────────────────────────────────

    def _init_stats(self) -> Dict[str, Any]:
        """Initialize statistics dictionary. Override to add custom stats."""
        return {
            'messages_processed': 0,
            'errors': 0,
            'start_time': None,
        }

    def _print_custom_stats(self):
        """Override to print additional statistics in subclasses."""
        pass

    # ── Abstract Methods (must be implemented by subclasses) ───

    @abstractmethod
    def _get_topics(self) -> List[str]:
        """Return list of Kafka topics to subscribe to."""
        pass

    @abstractmethod
    def _get_kafka_config(self) -> Dict[str, Any]:
        """Return Kafka consumer configuration dict."""
        pass

    @abstractmethod
    def _setup_connections(self) -> bool:
        """Set up all required connections (PostgreSQL, MySQL, etc.)."""
        pass

    @abstractmethod
    def process_message(self, topic: str, message_value: Dict[str, Any]):
        """Process a single Kafka message."""
        pass

    def _cleanup_connections(self):
        """Override to close specific connections."""
        pass

    # ── Lifecycle (Template Method) ────────────────────────────

    def setup(self) -> bool:
        """Template method: set up all resources before consuming."""
        if not self._setup_connections():
            self.logger.error("Failed to set up connections.")
            return False

        if not self._create_kafka_consumer():
            self.logger.error("Failed to create Kafka consumer.")
            return False

        return True

    def _create_kafka_consumer(self) -> bool:
        """Create Kafka consumer from config (auto_commit disabled for at-least-once)."""
        topics = self._get_topics()
        config = self._get_kafka_config()

        self._kafka_consumer = KafkaConsumerFactory.create(
            topics=topics,
            bootstrap_servers=config['bootstrap_servers'],
            group_id=config['group_id'],
            auto_offset_reset=config.get('auto_offset_reset', 'earliest'),
            enable_auto_commit=False,  # FIX 3.3: manual commit after successful processing
            max_poll_interval_ms=config.get('max_poll_interval_ms', 300000),
            session_timeout_ms=config.get('session_timeout_ms', 30000),
        )
        return self._kafka_consumer is not None

    def _setup_signal_handlers(self):
        """FIX 3.5: Handle SIGTERM for graceful Docker stop."""
        def _signal_handler(signum, frame):
            sig_name = signal.Signals(signum).name
            self.logger.info("Received %s — initiating graceful shutdown...", sig_name)
            self._running = False

        signal.signal(signal.SIGTERM, _signal_handler)
        signal.signal(signal.SIGINT, _signal_handler)

    def _send_to_dlq(self, topic: str, message_value: Any, error: Exception):
        """
        FIX 3.4: Dead Letter Queue handler for poison messages.
        Logs failed messages to a DLQ log file for manual review / replay.
        """
        dlq_record = {
            'original_topic': topic,
            'error': str(error),
            'error_type': type(error).__name__,
            'timestamp': datetime.now().isoformat(),
            'consumer': self.name,
            'message_value': message_value,
        }
        # Log to dedicated DLQ logger so it goes to a separate file
        self.logger.error(
            "[DLQ] Message sent to dead letter queue: topic=%s error=%s",
            topic, error,
        )
        # Also write structured JSON to DLQ log file
        try:
            import os
            dlq_dir = '/app/logs' if os.path.exists('/app/logs') else '.'
            dlq_path = os.path.join(dlq_dir, f'{self.name.lower().replace(" ", "_")}_dlq.jsonl')
            with open(dlq_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(dlq_record, ensure_ascii=False, default=str) + '\n')
        except Exception as dlq_err:
            self.logger.error("Failed to write DLQ record: %s", dlq_err)

    def run(self):
        """Main consumer loop (Template Method)."""
        self.logger.info("=" * 60)
        self.logger.info("STARTING %s", self.name.upper())
        self.logger.info("=" * 60)

        if not self.setup():
            self.logger.error("Setup failed. Exiting.")
            return

        self._setup_signal_handlers()  # FIX 3.5: graceful shutdown
        self._stats['start_time'] = datetime.now()
        self.logger.info("%s started. Waiting for messages...", self.name)

        try:
            while self._running:
                # Poll with timeout so we can check _running flag
                records = self._kafka_consumer.poll(timeout_ms=1000)
                if not records:
                    continue

                for tp, messages in records.items():
                    for message in messages:
                        if not self._running:
                            break
                        if not message.value:
                            continue

                        retries = 0
                        success = False
                        while retries < self.MAX_RETRIES_PER_MESSAGE:
                            try:
                                self.process_message(message.topic, message.value)
                                success = True
                                break
                            except Exception as e:
                                retries += 1
                                if retries >= self.MAX_RETRIES_PER_MESSAGE:
                                    self.logger.error(
                                        "Message failed after %d retries from %s: %s",
                                        retries, message.topic, e,
                                    )
                                    self.logger.exception("Full traceback:")
                                    self._send_to_dlq(message.topic, message.value, e)
                                    self._stats['errors'] += 1
                                else:
                                    self.logger.warning(
                                        "Retry %d/%d for message from %s: %s",
                                        retries, self.MAX_RETRIES_PER_MESSAGE,
                                        message.topic, e,
                                    )

                        self._stats['messages_processed'] += 1

                # FIX 3.3: commit offset AFTER successful processing of the batch
                try:
                    self._kafka_consumer.commit()
                except Exception as commit_err:
                    self.logger.error("Kafka commit failed: %s", commit_err)

                if (self._stats['messages_processed'] % 100 == 0
                        and self._stats['messages_processed'] > 0):
                    self.print_stats()

        except KeyboardInterrupt:
            self.logger.info("Consumer interrupted by user")
        except Exception as e:
            self.logger.error("Unexpected error in consumer loop: %s", e)
            self.logger.exception("Full traceback:")
        finally:
            self.cleanup()

    # ── Output & Cleanup ───────────────────────────────────────

    def print_stats(self):
        """Print consumer statistics."""
        elapsed = 0
        if self._stats['start_time']:
            elapsed = (datetime.now() - self._stats['start_time']).total_seconds()

        self.logger.info("=" * 60)
        self.logger.info("%s STATISTICS", self.name.upper())
        self.logger.info("=" * 60)
        self.logger.info("Running time: %.0fs", elapsed)
        self.logger.info("Messages processed: %d", self._stats['messages_processed'])
        self.logger.info("Errors: %d", self._stats['errors'])
        self._print_custom_stats()
        self.logger.info("=" * 60)

    def cleanup(self):
        """Cleanup all resources."""
        self.logger.info("Cleaning up resources...")
        self.print_stats()

        if self._kafka_consumer:
            self._kafka_consumer.close()
            self.logger.info("Kafka consumer closed")

        self._cleanup_connections()
        self.logger.info("%s stopped", self.name)
