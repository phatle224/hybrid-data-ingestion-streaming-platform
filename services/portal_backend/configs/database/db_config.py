"""
Database configuration module
"""
import os
import mysql.connector
from typing import Optional


class DatabaseConfig:
    """Database configuration class"""
    
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", "3306"))
        self.user = os.getenv("DB_USER", "")
        self.password = os.getenv("DB_PASSWORD", "")
        self.database = os.getenv("DB_NAME", "")
    
    def to_dict(self) -> dict:
        """Convert config to dictionary"""
        return {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            "database": self.database
        }
    
    def get_connection(self):
        """Create and return a database connection"""
        return mysql.connector.connect(**self.to_dict())


class DatabaseConnection:
    """Database connection manager with context manager support"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connection: Optional[mysql.connector.MySQLConnection] = None
        self.cursor = None
    
    def __enter__(self):
        """Enter context manager"""
        self.connection = self.config.get_connection()
        self.cursor = self.connection.cursor(dictionary=True)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            if exc_type is None:
                self.connection.commit()
            else:
                self.connection.rollback()
            self.connection.close()
    
    def execute(self, query: str, params: tuple = None):
        """Execute a query"""
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        return self.cursor
    
    def fetchall(self):
        """Fetch all results"""
        return self.cursor.fetchall()
    
    def fetchone(self):
        """Fetch one result"""
        return self.cursor.fetchone()
    
    def commit(self):
        """Commit transaction"""
        if self.connection:
            self.connection.commit()


# Global database config instance
db_config = DatabaseConfig()
