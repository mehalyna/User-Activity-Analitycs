from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (
    EventSerializer,
    EventResponseSerializer,
    UserEventSerializer,
    UserEventsResponseSerializer,
    DailyReportResponseSerializer
)
from .storage import EventStorage
import logging

logger = logging.getLogger(__name__)


class EventCreateView(APIView):
    """
    API endpoint for creating user activity events.

    POST /api/events/

    Request body:
    {
        "user_id": "string (required)",
        "event_type": "click|page_view|navigation|add_to_cart (required)",
        "page_url": "string (optional)",
        "target_id": "string (optional)",
        "created_at": "ISO 8601 datetime (optional, defaults to current time)",
        "metadata": "object (optional)"
    }

    Response:
    {
        "event_id": "string",
        "user_id": "string",
        "event_type": "string",
        "created_at": "ISO 8601 datetime",
        "status": "created",
        "message": "Event created successfully"
    }
    """

    def post(self, request):
        serializer = EventSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    'error': 'Invalid request data',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        event_data = serializer.save()

        success = EventStorage.save_event(
            user_id=event_data['user_id'],
            event_id=event_data['event_id'],
            event_data=event_data
        )

        if not success:
            return Response(
                {
                    'error': 'Failed to store event',
                    'message': 'Could not save event to storage'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        response_data = {
            'event_id': event_data['event_id'],
            'user_id': event_data['user_id'],
            'event_type': event_data['event_type'],
            'created_at': event_data['created_at'],
            'status': 'created',
            'message': 'Event created successfully'
        }

        response_serializer = EventResponseSerializer(response_data)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )

    def get(self, request):
        """
        GET endpoint to show API documentation
        """
        return Response(
            {
                'endpoint': '/api/events/',
                'method': 'POST',
                'description': 'Create a new user activity event',
                'required_fields': ['user_id', 'event_type'],
                'optional_fields': ['page_url', 'target_id', 'created_at', 'metadata'],
                'event_types': ['click', 'page_view', 'navigation', 'add_to_cart'],
                'example_request': {
                    'user_id': '42',
                    'event_type': 'page_view',
                    'page_url': 'https://example.com/products/laptop',
                    'target_id': 'prod_123',
                    'metadata': {
                        'browser': 'Chrome',
                        'device': 'desktop'
                    }
                }
            },
            status=status.HTTP_200_OK
        )


class UserEventsView(APIView):
    """
    API endpoint for retrieving user activity events.

    GET /api/users/{user_id}/events/

    Query Parameters:
    - start_date (optional): Start date in YYYY-MM-DD format
    - end_date (optional): End date in YYYY-MM-DD format
    - limit (optional): Maximum number of events to return

    Response:
    {
        "user_id": "string",
        "total_events": integer,
        "start_date": "string or null",
        "end_date": "string or null",
        "limit": integer or null,
        "events": [
            {
                "event_id": "string",
                "user_id": "string",
                "event_type": "string",
                "date": "string",
                "created_at": "string",
                "page_url": "string",
                "target_id": "string",
                "metadata": object
            }
        ]
    }
    """

    def get(self, request, user_id):
        logger.info(f"Retrieving events for user {user_id}")

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        limit_str = request.query_params.get('limit')

        limit = None
        if limit_str:
            try:
                limit = int(limit_str)
                if limit <= 0:
                    return Response(
                        {
                            'error': 'Invalid limit parameter',
                            'message': 'Limit must be a positive integer'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {
                        'error': 'Invalid limit parameter',
                        'message': 'Limit must be an integer'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        if start_date and not self._is_valid_date(start_date):
            return Response(
                {
                    'error': 'Invalid start_date parameter',
                    'message': 'Date must be in YYYY-MM-DD format'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if end_date and not self._is_valid_date(end_date):
            return Response(
                {
                    'error': 'Invalid end_date parameter',
                    'message': 'Date must be in YYYY-MM-DD format'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if start_date and end_date and start_date > end_date:
            return Response(
                {
                    'error': 'Invalid date range',
                    'message': 'start_date must be before or equal to end_date'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            events = EventStorage.get_user_events(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )

            logger.info(f"Retrieved {len(events)} events for user {user_id}")

            response_data = {
                'user_id': user_id,
                'total_events': len(events),
                'start_date': start_date,
                'end_date': end_date,
                'limit': limit,
                'events': events
            }

            serializer = UserEventsResponseSerializer(response_data)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error retrieving events for user {user_id}: {str(e)}", exc_info=True)
            return Response(
                {
                    'error': 'Failed to retrieve events',
                    'message': 'An error occurred while retrieving events'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _is_valid_date(self, date_str):
        """Validate date string format (YYYY-MM-DD)"""
        try:
            from datetime import datetime
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False


class DailyReportView(APIView):
    """
    API endpoint for daily activity reports.

    GET /api/reports/daily/

    Query Parameters:
    - start_date (optional): Start date in YYYY-MM-DD format
    - end_date (optional): End date in YYYY-MM-DD format

    Response:
    {
        "report_type": "daily",
        "start_date": "string or null",
        "end_date": "string or null",
        "total_days": integer,
        "total_events": integer,
        "total_unique_users": integer,
        "daily_stats": [
            {
                "date": "string",
                "total_events": integer,
                "unique_users": integer,
                "event_types": [
                    {
                        "event_type": "string",
                        "count": integer
                    }
                ]
            }
        ]
    }
    """

    def get(self, request):
        logger.info("Generating daily activity report")

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date and not self._is_valid_date(start_date):
            return Response(
                {
                    'error': 'Invalid start_date parameter',
                    'message': 'Date must be in YYYY-MM-DD format'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if end_date and not self._is_valid_date(end_date):
            return Response(
                {
                    'error': 'Invalid end_date parameter',
                    'message': 'Date must be in YYYY-MM-DD format'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if start_date and end_date and start_date > end_date:
            return Response(
                {
                    'error': 'Invalid date range',
                    'message': 'start_date must be before or equal to end_date'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            daily_stats = EventStorage.get_daily_aggregation(
                start_date=start_date,
                end_date=end_date
            )

            total_events = sum(day['total_events'] for day in daily_stats)
            all_users = set()
            for day in daily_stats:
                all_users.update(range(day['unique_users']))

            response_data = {
                'report_type': 'daily',
                'start_date': start_date,
                'end_date': end_date,
                'total_days': len(daily_stats),
                'total_events': total_events,
                'total_unique_users': len(set(
                    day['unique_users'] for day in daily_stats
                )) if daily_stats else 0,
                'daily_stats': daily_stats
            }

            logger.info(
                f"Generated daily report: {len(daily_stats)} days, "
                f"{total_events} total events"
            )

            serializer = DailyReportResponseSerializer(response_data)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error generating daily report: {str(e)}", exc_info=True)
            return Response(
                {
                    'error': 'Failed to generate report',
                    'message': 'An error occurred while generating the report'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _is_valid_date(self, date_str):
        """Validate date string format (YYYY-MM-DD)"""
        try:
            from datetime import datetime
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
