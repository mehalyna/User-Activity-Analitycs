import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from .hbase_client import HBaseClient, HBaseConnectionError

logger = logging.getLogger(__name__)


class EventStorageError(Exception):
    """Custom exception for event storage errors"""
    pass


class EventStorage:
    TABLE_NAME = 'user_activity'
    COLUMN_FAMILY = 'cf'
    BATCH_SIZE = 100

    @classmethod
    def _build_row_key(cls, user_id: str, date: str, event_id: str) -> str:
        """
        Build HBase row key from user_id, date, and event_id.

        Format: user_id#date#event_id
        Example: 42#2026-04-20#evt_a1b2c3d4e5f6

        This format enables:
        - Fast user-specific queries (scan by user_id prefix)
        - Efficient date-range queries (date in key)
        - Natural ordering by time
        """
        return f"{user_id}#{date}#{event_id}"

    @classmethod
    def _parse_row_key(cls, row_key: str) -> Dict[str, str]:
        """
        Parse HBase row key into components.

        Args:
            row_key: Row key string

        Returns:
            Dictionary with user_id, date, and event_id
        """
        parts = row_key.split('#')
        if len(parts) == 3:
            return {
                'user_id': parts[0],
                'date': parts[1],
                'event_id': parts[2]
            }
        logger.warning(f"Invalid row key format: {row_key}")
        return {}

    @classmethod
    def _prepare_event_data(cls, event_data: dict) -> Dict[bytes, bytes]:
        """
        Prepare event data for HBase storage.

        Args:
            event_data: Event data dictionary

        Returns:
            Dictionary with encoded column names and values
        """
        created_at = event_data.get('created_at', datetime.utcnow().isoformat())

        data = {
            f'{cls.COLUMN_FAMILY}:event_type'.encode():
                event_data.get('event_type', '').encode('utf-8'),
            f'{cls.COLUMN_FAMILY}:page_url'.encode():
                event_data.get('page_url', '').encode('utf-8'),
            f'{cls.COLUMN_FAMILY}:target_id'.encode():
                event_data.get('target_id', '').encode('utf-8'),
            f'{cls.COLUMN_FAMILY}:created_at'.encode():
                created_at.encode('utf-8'),
            f'{cls.COLUMN_FAMILY}:metadata'.encode():
                json.dumps(event_data.get('metadata', {})).encode('utf-8'),
        }

        return data

    @classmethod
    def save_event(cls, user_id: str, event_id: str, event_data: dict) -> bool:
        """
        Save a single event to HBase.

        Args:
            user_id: User identifier
            event_id: Event identifier
            event_data: Event data dictionary

        Returns:
            True if successful, False otherwise

        Raises:
            EventStorageError: If storage operation fails critically
        """
        try:
            logger.debug(f"Saving event {event_id} for user {user_id}")

            table = HBaseClient.get_table(cls.TABLE_NAME)
            created_at = event_data.get('created_at', datetime.utcnow().isoformat())
            date = created_at.split('T')[0]

            row_key = cls._build_row_key(user_id, date, event_id)
            data = cls._prepare_event_data(event_data)

            table.put(row_key.encode('utf-8'), data)

            logger.info(f"Successfully saved event {event_id} for user {user_id}")
            return True

        except HBaseConnectionError as e:
            logger.error(f"HBase connection error saving event {event_id}: {str(e)}")
            return False

        except Exception as e:
            logger.error(f"Unexpected error saving event {event_id}: {str(e)}", exc_info=True)
            return False

    @classmethod
    def save_events_batch(cls, events: List[Tuple[str, str, dict]]) -> Tuple[int, int]:
        """
        Save multiple events in a batch operation.

        Args:
            events: List of tuples (user_id, event_id, event_data)

        Returns:
            Tuple of (successful_count, failed_count)
        """
        if not events:
            logger.warning("save_events_batch called with empty event list")
            return 0, 0

        success_count = 0
        failed_count = 0

        try:
            table = HBaseClient.get_table(cls.TABLE_NAME)
            batch = table.batch()

            logger.info(f"Starting batch save of {len(events)} events")

            for user_id, event_id, event_data in events:
                try:
                    created_at = event_data.get('created_at', datetime.utcnow().isoformat())
                    date = created_at.split('T')[0]

                    row_key = cls._build_row_key(user_id, date, event_id)
                    data = cls._prepare_event_data(event_data)

                    batch.put(row_key.encode('utf-8'), data)
                    success_count += 1

                except Exception as e:
                    logger.error(f"Error preparing event {event_id} for batch: {str(e)}")
                    failed_count += 1

            batch.send()
            logger.info(f"Batch save completed: {success_count} successful, {failed_count} failed")

        except HBaseConnectionError as e:
            logger.error(f"HBase connection error during batch save: {str(e)}")
            failed_count = len(events) - success_count

        except Exception as e:
            logger.error(f"Unexpected error during batch save: {str(e)}", exc_info=True)
            failed_count = len(events) - success_count

        return success_count, failed_count

    @classmethod
    def get_user_events(
        cls,
        user_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Retrieve events for a specific user.

        Args:
            user_id: User identifier
            start_date: Start date (YYYY-MM-DD format), inclusive
            end_date: End date (YYYY-MM-DD format), inclusive
            limit: Maximum number of events to return

        Returns:
            List of event dictionaries
        """
        try:
            logger.debug(f"Retrieving events for user {user_id}, date range: {start_date} to {end_date}")

            table = HBaseClient.get_table(cls.TABLE_NAME)
            events = []

            start_row = f"{user_id}#{start_date if start_date else ''}".encode('utf-8')
            if end_date:
                stop_row = f"{user_id}#{end_date}~".encode('utf-8')
            else:
                stop_row = f"{user_id}#~".encode('utf-8')

            scan_limit = limit if limit else None

            for row_key, data in table.scan(row=start_row, stop=stop_row, limit=scan_limit):
                try:
                    row_key_str = row_key.decode('utf-8')
                    parsed_key = cls._parse_row_key(row_key_str)

                    event = {
                        'user_id': parsed_key.get('user_id'),
                        'event_id': parsed_key.get('event_id'),
                        'date': parsed_key.get('date'),
                    }

                    for col, value in data.items():
                        col_name = col.decode('utf-8').split(':')[1]
                        if col_name == 'metadata':
                            try:
                                event[col_name] = json.loads(value.decode('utf-8'))
                            except json.JSONDecodeError as e:
                                logger.warning(f"Invalid JSON in metadata for event {parsed_key.get('event_id')}: {str(e)}")
                                event[col_name] = {}
                        else:
                            event[col_name] = value.decode('utf-8')

                    events.append(event)

                except Exception as e:
                    logger.error(f"Error parsing event row: {str(e)}")
                    continue

            logger.info(f"Retrieved {len(events)} events for user {user_id}")
            return events

        except HBaseConnectionError as e:
            logger.error(f"HBase connection error retrieving events for user {user_id}: {str(e)}")
            return []

        except Exception as e:
            logger.error(f"Unexpected error retrieving events for user {user_id}: {str(e)}", exc_info=True)
            return []

    @classmethod
    def get_event(cls, user_id: str, date: str, event_id: str) -> Optional[Dict]:
        """
        Retrieve a specific event by its identifiers.

        Args:
            user_id: User identifier
            date: Event date (YYYY-MM-DD)
            event_id: Event identifier

        Returns:
            Event dictionary or None if not found
        """
        try:
            logger.debug(f"Retrieving specific event {event_id} for user {user_id} on {date}")

            table = HBaseClient.get_table(cls.TABLE_NAME)
            row_key = cls._build_row_key(user_id, date, event_id)

            data = table.row(row_key.encode('utf-8'))

            if not data:
                logger.info(f"Event not found: {row_key}")
                return None

            event = {
                'user_id': user_id,
                'event_id': event_id,
                'date': date,
            }

            for col, value in data.items():
                col_name = col.decode('utf-8').split(':')[1]
                if col_name == 'metadata':
                    try:
                        event[col_name] = json.loads(value.decode('utf-8'))
                    except json.JSONDecodeError:
                        event[col_name] = {}
                else:
                    event[col_name] = value.decode('utf-8')

            logger.info(f"Successfully retrieved event {event_id}")
            return event

        except HBaseConnectionError as e:
            logger.error(f"HBase connection error retrieving event {event_id}: {str(e)}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error retrieving event {event_id}: {str(e)}", exc_info=True)
            return None

    @classmethod
    def count_user_events(cls, user_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> int:
        """
        Count events for a specific user.

        Args:
            user_id: User identifier
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)

        Returns:
            Number of events
        """
        try:
            events = cls.get_user_events(user_id, start_date, end_date)
            count = len(events)
            logger.info(f"User {user_id} has {count} events in date range")
            return count
        except Exception as e:
            logger.error(f"Error counting events for user {user_id}: {str(e)}")
            return 0

    @classmethod
    def ensure_table_exists(cls) -> bool:
        """
        Ensure the events table exists, creating it if necessary.

        Returns:
            True if table exists or was created successfully
        """
        try:
            if not HBaseClient.table_exists(cls.TABLE_NAME):
                logger.warning(f"Table {cls.TABLE_NAME} does not exist, attempting to create")
                families = {cls.COLUMN_FAMILY: dict()}
                HBaseClient.create_table(cls.TABLE_NAME, families)
                return True
            return True
        except Exception as e:
            logger.error(f"Failed to ensure table exists: {str(e)}")
            return False

    @classmethod
    def get_daily_aggregation(
        cls,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict]:
        """
        Get aggregated event counts by date and event type.

        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)

        Returns:
            List of daily aggregation dictionaries with:
            - date: Date string
            - total_events: Total events for that date
            - unique_users: Number of unique users
            - event_types: Dict of event_type -> count
        """
        try:
            logger.info(f"Aggregating events by date, range: {start_date} to {end_date}")

            table = HBaseClient.get_table(cls.TABLE_NAME)

            start_row = b''
            stop_row = b'~'

            if start_date:
                start_row = f"#{start_date}".encode('utf-8')
            if end_date:
                stop_row = f"#{end_date}~".encode('utf-8')

            daily_data = {}

            for row_key, data in table.scan(row=start_row, stop=stop_row):
                try:
                    row_key_str = row_key.decode('utf-8')
                    parsed_key = cls._parse_row_key(row_key_str)

                    if not parsed_key:
                        continue

                    date = parsed_key.get('date')
                    user_id = parsed_key.get('user_id')

                    if not date:
                        continue

                    if date not in daily_data:
                        daily_data[date] = {
                            'total_events': 0,
                            'users': set(),
                            'event_types': {}
                        }

                    event_type = None
                    for col, value in data.items():
                        col_name = col.decode('utf-8').split(':')[1]
                        if col_name == 'event_type':
                            event_type = value.decode('utf-8')
                            break

                    if event_type:
                        daily_data[date]['total_events'] += 1
                        daily_data[date]['users'].add(user_id)

                        if event_type not in daily_data[date]['event_types']:
                            daily_data[date]['event_types'][event_type] = 0
                        daily_data[date]['event_types'][event_type] += 1

                except Exception as e:
                    logger.warning(f"Error processing row for aggregation: {str(e)}")
                    continue

            result = []
            for date, stats in sorted(daily_data.items()):
                event_types = [
                    {'event_type': et, 'count': count}
                    for et, count in sorted(stats['event_types'].items())
                ]

                result.append({
                    'date': date,
                    'total_events': stats['total_events'],
                    'unique_users': len(stats['users']),
                    'event_types': event_types
                })

            logger.info(f"Aggregated {len(result)} days of data")
            return result

        except HBaseConnectionError as e:
            logger.error(f"HBase connection error during aggregation: {str(e)}")
            return []

        except Exception as e:
            logger.error(f"Unexpected error during aggregation: {str(e)}", exc_info=True)
            return []

    @classmethod
    def get_event_type_summary(
        cls,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Get summary of event counts by event type across all dates.

        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)

        Returns:
            Dictionary mapping event_type to total count
        """
        try:
            logger.info(f"Getting event type summary, range: {start_date} to {end_date}")

            daily_stats = cls.get_daily_aggregation(start_date, end_date)

            summary = {}
            for day_stat in daily_stats:
                for et_stat in day_stat['event_types']:
                    event_type = et_stat['event_type']
                    count = et_stat['count']

                    if event_type not in summary:
                        summary[event_type] = 0
                    summary[event_type] += count

            logger.info(f"Event type summary: {summary}")
            return summary

        except Exception as e:
            logger.error(f"Error generating event type summary: {str(e)}")
            return {}
