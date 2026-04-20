import happybase
import logging
import time
from django.conf import settings
from typing import Optional, Dict, Any
from thrift.transport.TTransport import TTransportException

logger = logging.getLogger(__name__)


class HBaseConnectionError(Exception):
    """Custom exception for HBase connection errors"""
    pass


class HBaseClient:
    _connection: Optional[happybase.Connection] = None
    _pool: Optional[happybase.ConnectionPool] = None
    _connection_attempts = 0
    _max_retries = 3
    _retry_delay = 1

    @classmethod
    def get_connection(cls, retry=True) -> happybase.Connection:
        """
        Get or create HBase connection with retry logic.

        Args:
            retry: Whether to retry on connection failure

        Returns:
            happybase.Connection instance

        Raises:
            HBaseConnectionError: If connection fails after retries
        """
        if cls._connection is None:
            for attempt in range(cls._max_retries if retry else 1):
                try:
                    logger.info(f"Attempting to connect to HBase at {settings.HBASE_CONFIG['host']}:{settings.HBASE_CONFIG['port']}")
                    cls._connection = happybase.Connection(
                        host=settings.HBASE_CONFIG['host'],
                        port=settings.HBASE_CONFIG['port'],
                        timeout=10000
                    )
                    cls._connection_attempts = 0
                    logger.info("Successfully connected to HBase")
                    return cls._connection

                except TTransportException as e:
                    cls._connection_attempts += 1
                    logger.warning(
                        f"HBase connection attempt {attempt + 1}/{cls._max_retries} failed: {str(e)}"
                    )

                    if attempt < cls._max_retries - 1:
                        time.sleep(cls._retry_delay * (attempt + 1))
                    else:
                        error_msg = f"Failed to connect to HBase after {cls._max_retries} attempts"
                        logger.error(error_msg)
                        raise HBaseConnectionError(error_msg) from e

                except Exception as e:
                    logger.error(f"Unexpected error connecting to HBase: {str(e)}")
                    raise HBaseConnectionError(f"HBase connection error: {str(e)}") from e

        return cls._connection

    @classmethod
    def get_pool(cls, size=10) -> happybase.ConnectionPool:
        """
        Get or create connection pool for high-concurrency scenarios.

        Args:
            size: Maximum number of connections in the pool

        Returns:
            happybase.ConnectionPool instance
        """
        if cls._pool is None:
            try:
                logger.info(f"Creating HBase connection pool with size {size}")
                cls._pool = happybase.ConnectionPool(
                    size=size,
                    host=settings.HBASE_CONFIG['host'],
                    port=settings.HBASE_CONFIG['port'],
                    timeout=10000
                )
                logger.info("Connection pool created successfully")
            except Exception as e:
                logger.error(f"Failed to create connection pool: {str(e)}")
                raise HBaseConnectionError(f"Connection pool error: {str(e)}") from e

        return cls._pool

    @classmethod
    def close_connection(cls):
        """Close the singleton connection"""
        if cls._connection:
            try:
                cls._connection.close()
                logger.info("HBase connection closed")
            except Exception as e:
                logger.warning(f"Error closing connection: {str(e)}")
            finally:
                cls._connection = None

    @classmethod
    def close_pool(cls):
        """Close the connection pool"""
        if cls._pool:
            try:
                cls._pool._close_connections()
                logger.info("Connection pool closed")
            except Exception as e:
                logger.warning(f"Error closing pool: {str(e)}")
            finally:
                cls._pool = None

    @classmethod
    def get_table(cls, table_name: str, use_pool=False):
        """
        Get a table instance.

        Args:
            table_name: Name of the table (without prefix)
            use_pool: Whether to use connection pool

        Returns:
            happybase.Table instance
        """
        prefix = settings.HBASE_CONFIG.get('table_prefix', '')
        full_table_name = f"{prefix}{table_name}"

        try:
            if use_pool:
                pool = cls.get_pool()
                return pool.table(full_table_name)
            else:
                connection = cls.get_connection()
                return connection.table(full_table_name)
        except Exception as e:
            logger.error(f"Failed to get table {full_table_name}: {str(e)}")
            raise

    @classmethod
    def create_table(cls, table_name: str, families: Dict[str, Dict]) -> bool:
        """
        Create a table if it doesn't exist.

        Args:
            table_name: Name of the table (without prefix)
            families: Dictionary of column families and their properties

        Returns:
            True if table was created, False if it already exists
        """
        prefix = settings.HBASE_CONFIG.get('table_prefix', '')
        full_table_name = f"{prefix}{table_name}"

        try:
            connection = cls.get_connection()

            if full_table_name.encode() not in connection.tables():
                logger.info(f"Creating table {full_table_name} with families: {families}")
                connection.create_table(full_table_name, families)
                logger.info(f"Table {full_table_name} created successfully")
                return True
            else:
                logger.info(f"Table {full_table_name} already exists")
                return False

        except Exception as e:
            logger.error(f"Error creating table {full_table_name}: {str(e)}")
            raise

    @classmethod
    def table_exists(cls, table_name: str) -> bool:
        """
        Check if a table exists.

        Args:
            table_name: Name of the table (without prefix)

        Returns:
            True if table exists, False otherwise
        """
        prefix = settings.HBASE_CONFIG.get('table_prefix', '')
        full_table_name = f"{prefix}{table_name}"

        try:
            connection = cls.get_connection()
            exists = full_table_name.encode() in connection.tables()
            logger.debug(f"Table {full_table_name} exists: {exists}")
            return exists
        except Exception as e:
            logger.error(f"Error checking if table exists: {str(e)}")
            return False

    @classmethod
    def is_connected(cls) -> bool:
        """
        Check if HBase is currently connected.

        Returns:
            True if connected, False otherwise
        """
        try:
            if cls._connection is None:
                return False
            cls._connection.tables()
            return True
        except Exception:
            cls._connection = None
            return False

    @classmethod
    def health_check(cls) -> Dict[str, Any]:
        """
        Perform a health check on the HBase connection.

        Returns:
            Dictionary with health check results
        """
        result = {
            'connected': False,
            'host': settings.HBASE_CONFIG['host'],
            'port': settings.HBASE_CONFIG['port'],
            'tables_count': 0,
            'error': None
        }

        try:
            connection = cls.get_connection(retry=False)
            tables = connection.tables()
            result['connected'] = True
            result['tables_count'] = len(tables)
            logger.info("HBase health check: OK")
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"HBase health check failed: {str(e)}")

        return result
