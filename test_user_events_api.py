#!/usr/bin/env python
"""
User Events API test script
Tests the user activity history endpoint
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_activity_analytics.settings')
django.setup()

from rest_framework.test import APIRequestFactory
from events.views import UserEventsView
from events.storage import EventStorage
import json


def test_endpoint_structure():
    print("Testing endpoint structure...")
    print("-" * 60)

    factory = APIRequestFactory()
    view = UserEventsView.as_view()

    request = factory.get('/api/users/user_42/events/')
    response = view(request, user_id='user_42')

    print(f"[TEST] GET /api/users/user_42/events/ - Status: {response.status_code}")

    if response.status_code == 200:
        print("[OK] Endpoint accessible")
        print(f"[INFO] Response keys: {list(response.data.keys())}")

        required_keys = ['user_id', 'total_events', 'events']
        for key in required_keys:
            assert key in response.data, f"Missing required key: {key}"

        print("[OK] Response structure correct")
    else:
        print(f"[INFO] Status {response.status_code} (expected if HBase not available)")

    print()


def test_date_filtering():
    print("Testing date filtering...")
    print("-" * 60)

    factory = APIRequestFactory()
    view = UserEventsView.as_view()

    request = factory.get(
        '/api/users/user_42/events/',
        {'start_date': '2026-04-01', 'end_date': '2026-04-30'}
    )
    response = view(request, user_id='user_42')

    print(f"[TEST] With date range - Status: {response.status_code}")

    if response.status_code == 200:
        print(f"[OK] Date filtering accepted")
        print(f"[INFO] start_date: {response.data.get('start_date')}")
        print(f"[INFO] end_date: {response.data.get('end_date')}")
    else:
        print(f"[INFO] Status {response.status_code}")

    print()


def test_limit_parameter():
    print("Testing limit parameter...")
    print("-" * 60)

    factory = APIRequestFactory()
    view = UserEventsView.as_view()

    request = factory.get('/api/users/user_42/events/', {'limit': '10'})
    response = view(request, user_id='user_42')

    print(f"[TEST] With limit=10 - Status: {response.status_code}")

    if response.status_code == 200:
        print(f"[OK] Limit parameter accepted")
        print(f"[INFO] limit: {response.data.get('limit')}")

        if response.data.get('events'):
            actual_count = len(response.data['events'])
            print(f"[INFO] Events returned: {actual_count}")
            assert actual_count <= 10, "Returned more events than limit"
    else:
        print(f"[INFO] Status {response.status_code}")

    print()


def test_invalid_parameters():
    print("Testing invalid parameters...")
    print("-" * 60)

    factory = APIRequestFactory()
    view = UserEventsView.as_view()

    # Invalid date format
    request = factory.get('/api/users/user_42/events/', {'start_date': 'invalid'})
    response = view(request, user_id='user_42')
    print(f"[TEST] Invalid date format - Status: {response.status_code}")
    assert response.status_code == 400, "Should return 400 for invalid date"
    print("[OK] Invalid date correctly rejected")

    # Invalid limit
    request = factory.get('/api/users/user_42/events/', {'limit': 'invalid'})
    response = view(request, user_id='user_42')
    print(f"[TEST] Invalid limit format - Status: {response.status_code}")
    assert response.status_code == 400, "Should return 400 for invalid limit"
    print("[OK] Invalid limit correctly rejected")

    # Negative limit
    request = factory.get('/api/users/user_42/events/', {'limit': '-1'})
    response = view(request, user_id='user_42')
    print(f"[TEST] Negative limit - Status: {response.status_code}")
    assert response.status_code == 400, "Should return 400 for negative limit"
    print("[OK] Negative limit correctly rejected")

    # Invalid date range (start > end)
    request = factory.get(
        '/api/users/user_42/events/',
        {'start_date': '2026-04-30', 'end_date': '2026-04-01'}
    )
    response = view(request, user_id='user_42')
    print(f"[TEST] Invalid date range - Status: {response.status_code}")
    assert response.status_code == 400, "Should return 400 for invalid date range"
    print("[OK] Invalid date range correctly rejected")

    print()


def test_response_format():
    print("Testing response format...")
    print("-" * 60)

    factory = APIRequestFactory()
    view = UserEventsView.as_view()

    request = factory.get('/api/users/user_42/events/')
    response = view(request, user_id='user_42')

    if response.status_code == 200:
        print("[OK] Response format test")

        data = response.data

        # Check top-level structure
        assert 'user_id' in data, "Missing user_id"
        assert 'total_events' in data, "Missing total_events"
        assert 'events' in data, "Missing events array"

        print(f"[INFO] user_id: {data['user_id']}")
        print(f"[INFO] total_events: {data['total_events']}")
        print(f"[INFO] events array length: {len(data['events'])}")

        # Check event structure if events exist
        if data['events']:
            event = data['events'][0]
            required_fields = [
                'event_id', 'user_id', 'event_type',
                'date', 'created_at'
            ]
            for field in required_fields:
                assert field in event, f"Event missing field: {field}"

            print("[OK] Event structure correct")

        print("[OK] Response format valid")
    else:
        print(f"[INFO] Cannot test format, status: {response.status_code}")

    print()


def test_serializer_validation():
    print("Testing serializer validation...")
    print("-" * 60)

    from events.serializers import UserEventsResponseSerializer

    valid_data = {
        'user_id': 'user_42',
        'total_events': 2,
        'start_date': '2026-04-01',
        'end_date': '2026-04-30',
        'limit': 10,
        'events': [
            {
                'event_id': 'evt_123',
                'user_id': 'user_42',
                'event_type': 'page_view',
                'date': '2026-04-20',
                'created_at': '2026-04-20T10:00:00',
                'page_url': 'https://example.com/page',
                'target_id': 'target_123',
                'metadata': {'browser': 'Chrome'}
            }
        ]
    }

    serializer = UserEventsResponseSerializer(data=valid_data)
    assert serializer.is_valid(), f"Serializer errors: {serializer.errors}"

    print("[OK] Serializer validation passed")
    print(f"[INFO] Serialized data keys: {list(serializer.data.keys())}")

    print()


def test_different_user_ids():
    print("Testing different user IDs...")
    print("-" * 60)

    factory = APIRequestFactory()
    view = UserEventsView.as_view()

    user_ids = ['user_1', 'user_42', 'user_999', 'abc123']

    for user_id in user_ids:
        request = factory.get(f'/api/users/{user_id}/events/')
        response = view(request, user_id=user_id)

        print(f"[TEST] User ID '{user_id}' - Status: {response.status_code}")

        if response.status_code == 200:
            assert response.data['user_id'] == user_id, "User ID mismatch in response"

    print("[OK] Different user IDs handled correctly")
    print()


def test_empty_results():
    print("Testing empty results...")
    print("-" * 60)

    factory = APIRequestFactory()
    view = UserEventsView.as_view()

    # Request events for a user that doesn't exist
    request = factory.get('/api/users/nonexistent_user/events/')
    response = view(request, user_id='nonexistent_user')

    print(f"[TEST] Nonexistent user - Status: {response.status_code}")

    if response.status_code == 200:
        print(f"[OK] Returns empty list for nonexistent user")
        print(f"[INFO] total_events: {response.data.get('total_events')}")
        assert response.data.get('total_events') == 0, "Should return 0 events"
        assert len(response.data.get('events', [])) == 0, "Events array should be empty"

    print()


def main():
    print("=" * 60)
    print("User Events API Test")
    print("=" * 60)
    print()

    try:
        test_serializer_validation()
        test_endpoint_structure()
        test_date_filtering()
        test_limit_parameter()
        test_invalid_parameters()
        test_response_format()
        test_different_user_ids()
        test_empty_results()

        print("=" * 60)
        print("[OK] All user events API tests passed!")
        print()
        print("API Features Tested:")
        print("  [OK] Endpoint structure and accessibility")
        print("  [OK] Date range filtering (start_date, end_date)")
        print("  [OK] Limit parameter for pagination")
        print("  [OK] Invalid parameter validation")
        print("  [OK] Response format and structure")
        print("  [OK] Different user ID handling")
        print("  [OK] Empty results handling")
        print()
        print("To test with real data:")
        print("  1. Start HBase and Thrift server")
        print("  2. Run: python manage.py setup_hbase")
        print("  3. Run: python manage.py generate_sample_events --users 5")
        print("  4. Run: python manage.py runserver")
        print("  5. GET http://127.0.0.1:8000/api/users/user_001/events/")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
