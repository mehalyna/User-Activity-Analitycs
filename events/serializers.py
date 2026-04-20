from rest_framework import serializers
from datetime import datetime
import uuid


class EventSerializer(serializers.Serializer):
    EVENT_TYPES = [
        ('click', 'Click'),
        ('page_view', 'Page View'),
        ('navigation', 'Navigation'),
        ('add_to_cart', 'Add to Cart'),
    ]

    user_id = serializers.CharField(
        max_length=100,
        required=True,
        help_text="Unique identifier for the user"
    )
    event_type = serializers.ChoiceField(
        choices=EVENT_TYPES,
        required=True,
        help_text="Type of event"
    )
    page_url = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="URL where the event occurred"
    )
    target_id = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
        help_text="Optional target identifier (e.g., product ID, button ID)"
    )
    created_at = serializers.DateTimeField(
        required=False,
        help_text="Timestamp of the event (ISO 8601 format). Defaults to current UTC time."
    )
    metadata = serializers.JSONField(
        required=False,
        help_text="Optional JSON object with additional event data"
    )

    def validate_user_id(self, value):
        """Validate user_id format"""
        if not value or not value.strip():
            raise serializers.ValidationError(
                "User ID cannot be empty"
            )

        if len(value) > 100:
            raise serializers.ValidationError(
                "User ID cannot exceed 100 characters"
            )

        # Check for valid characters (alphanumeric, underscore, hyphen)
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', value):
            raise serializers.ValidationError(
                "User ID must contain only alphanumeric characters, underscores, and hyphens"
            )

        return value

    def validate_created_at(self, value):
        """Validate event timestamp"""
        if not value:
            return value

        from datetime import timedelta

        # Make timestamps comparable
        now = datetime.utcnow() if value.tzinfo is None else datetime.now(value.tzinfo)

        if value > now:
            raise serializers.ValidationError(
                "Event timestamp cannot be in the future"
            )

        # Check if timestamp is not too old (e.g., more than 1 year)
        one_year_ago = now - timedelta(days=365)
        if value < one_year_ago:
            raise serializers.ValidationError(
                "Event timestamp cannot be more than 1 year in the past"
            )

        return value

    def validate_page_url(self, value):
        """Validate page URL"""
        if value and len(value) > 2048:
            raise serializers.ValidationError(
                "Page URL cannot exceed 2048 characters"
            )
        return value

    def validate_target_id(self, value):
        """Validate target ID"""
        if value and len(value) > 200:
            raise serializers.ValidationError(
                "Target ID cannot exceed 200 characters"
            )
        return value

    def validate_metadata(self, value):
        """Validate metadata structure and size"""
        if value is not None and not isinstance(value, dict):
            raise serializers.ValidationError(
                "Metadata must be a JSON object"
            )

        # Check metadata size (limit to prevent abuse)
        if value:
            import json
            metadata_str = json.dumps(value)
            if len(metadata_str) > 10000:
                raise serializers.ValidationError(
                    "Metadata size cannot exceed 10KB"
                )

            # Check nesting depth
            def check_depth(obj, depth=0, max_depth=5):
                if depth > max_depth:
                    raise serializers.ValidationError(
                        f"Metadata nesting cannot exceed {max_depth} levels"
                    )
                if isinstance(obj, dict):
                    for value in obj.values():
                        check_depth(value, depth + 1, max_depth)
                elif isinstance(obj, list):
                    for item in obj:
                        check_depth(item, depth + 1, max_depth)

            check_depth(value)

        return value or {}

    def create(self, validated_data):
        if 'created_at' not in validated_data or validated_data['created_at'] is None:
            validated_data['created_at'] = datetime.utcnow()

        if isinstance(validated_data['created_at'], datetime):
            validated_data['created_at'] = validated_data['created_at'].isoformat()

        event_id = self._generate_event_id()
        validated_data['event_id'] = event_id

        return validated_data

    def _generate_event_id(self):
        return f"evt_{uuid.uuid4().hex[:12]}"


class EventResponseSerializer(serializers.Serializer):
    event_id = serializers.CharField()
    user_id = serializers.CharField()
    event_type = serializers.CharField()
    created_at = serializers.CharField()
    status = serializers.CharField(default='created')
    message = serializers.CharField(default='Event created successfully')


class UserEventSerializer(serializers.Serializer):
    """Serializer for displaying user events"""
    event_id = serializers.CharField()
    user_id = serializers.CharField()
    event_type = serializers.CharField()
    date = serializers.CharField()
    created_at = serializers.CharField()
    page_url = serializers.CharField(required=False, allow_blank=True)
    target_id = serializers.CharField(required=False, allow_blank=True)
    metadata = serializers.JSONField(required=False)


class UserEventsResponseSerializer(serializers.Serializer):
    """Serializer for user events list response"""
    user_id = serializers.CharField()
    total_events = serializers.IntegerField()
    start_date = serializers.CharField(required=False, allow_null=True)
    end_date = serializers.CharField(required=False, allow_null=True)
    limit = serializers.IntegerField(required=False, allow_null=True)
    events = UserEventSerializer(many=True)


class EventTypeCountSerializer(serializers.Serializer):
    """Serializer for event type count"""
    event_type = serializers.CharField()
    count = serializers.IntegerField()


class DailyStatsSerializer(serializers.Serializer):
    """Serializer for daily statistics"""
    date = serializers.CharField()
    total_events = serializers.IntegerField()
    unique_users = serializers.IntegerField()
    event_types = EventTypeCountSerializer(many=True)


class DailyReportResponseSerializer(serializers.Serializer):
    """Serializer for daily report response"""
    report_type = serializers.CharField(default='daily')
    start_date = serializers.CharField(required=False, allow_null=True)
    end_date = serializers.CharField(required=False, allow_null=True)
    total_days = serializers.IntegerField()
    total_events = serializers.IntegerField()
    total_unique_users = serializers.IntegerField()
    daily_stats = DailyStatsSerializer(many=True)
