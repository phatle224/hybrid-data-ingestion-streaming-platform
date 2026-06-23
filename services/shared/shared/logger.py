"""
Centralized logging utility.
Following reporting-main pattern with Logger factory function.
"""
import logging
import logging.handlers
import os
import sys


def create_logger(
    name: str,
    log_file: str = None,
    log_level: str = None,
    max_mb: int = 50,
    backup_count: int = 3
) -> logging.Logger:
    """
    Create a configured logger instance.

    Args:
        name: Logger name (typically class or module name)
        log_file: Optional log file path (auto-creates directory)
        log_level: Override log level (DEBUG, INFO, WARNING, ERROR)
        max_mb: Max log file size in MB before rotation
        backup_count: Number of rotated log files to keep

    Returns:
        Configured logging.Logger instance
    """
    logger = logging.getLogger(name)
    logger.propagate = False

    # Clear existing handlers to avoid duplicates on re-init
    if logger.hasHandlers():
        logger.handlers.clear()

    level_str = (log_level or os.getenv('LOG_LEVEL', 'INFO')).upper()
    level = getattr(logging, level_str, logging.INFO)
    logger.setLevel(level)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console handler (always)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        os.makedirs(os.path.dirname(log_file) or '.', exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_mb * 1024 * 1024,
            backupCount=backup_count,
            mode='a'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def configure_shared_loggers(log_file: str = None, log_level: str = None) -> None:
    """
    Configure module-level loggers in shared package to output to stdout.

    Call this once at consumer startup so that errors from shared.connections,
    shared.query_builder, shared.debezium, etc. are visible in docker logs
    instead of being silently swallowed.

    Args:
        log_file: Optional log file to also write shared logs to
        log_level: Override log level (default: INFO)
    """
    shared_modules = [
        'shared.connections',
        'shared.query_builder',
        'shared.debezium',
        'shared.base_consumer',
        'shared.configs',
    ]
    level_str = (log_level or os.getenv('LOG_LEVEL', 'INFO')).upper()
    level = getattr(logging, level_str, logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    file_handler = None
    if log_file:
        os.makedirs(os.path.dirname(log_file) or '.', exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=50 * 1024 * 1024,
            backupCount=3,
            mode='a',
        )
        file_handler.setFormatter(formatter)

    for module_name in shared_modules:
        module_logger = logging.getLogger(module_name)
        module_logger.setLevel(level)
        module_logger.propagate = False
        if not module_logger.hasHandlers():
            module_logger.addHandler(console_handler)
            if file_handler:
                module_logger.addHandler(file_handler)
