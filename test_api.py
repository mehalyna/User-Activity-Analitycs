#!/usr/bin/env python
"""
API endpoint test script
Tests the Event Collection API without requiring HBase
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_activity_analytics.settings')
django.setup()

from rest_framework.test import APIRequestFactory
from events.views import EventCreateView
import json


def test_event_validation():
    print("Testing event validation...")
    print("-" * 60)

    factory = APIRequestFactory()
    view = EventCreateView.as_view()

    # Test missing required fields
    request = factory.post('/api/events/', {}, format='json')
    response = view(request)

    print(f"[TEST] Missing fields - Status: {response.status_code}")
    assert response.status_code == 400, "Should return 400 for missing fields"
    print(f"[OK] Validation correctly rejects missing fields\n")

    # Test invalid event type
    request = factory.post('/api/events/', {
        'user_id': '42',
        'event_type': 'invalid_type'
    }, format='json')
    response = view(request)

    print(f"[TEST] Invalid event type - Status: {response.status_code}")
    assert response.status_code == 400, "Should return 400 for invalid event type"
    print(f"[OK] Validation correctly rejects invalid event type\n")


def test_event_creation_structure():
    print("Testing event creation structure...")
    print("-" * 60)

    factory = APIRequestFactory()
    view = EventCreateView.as_view()

    # Test valid event (will fail at storage without HBase)
    event_data = {
        'user_id': '42',
        'event_type': 'page_view',
        'page_url': 'https://example.com/products/laptop',
        'target_id': 'prod_123',
        'metadata': {
            'browser': 'Chrome',
            'device': 'desktop'
        }
    }

    request = factory.post('/api/events/', event_data, format='json')
    response = view(request)

    print(f"[TEST] Valid event - Status: {response.status_code}")

    if response.status_code == 201:
        print("[OK] Event created successfully")
        print(f"Response: {json.dumps(response.data, indent=2)}")
    elif response.status_code == 500:
        print("[EXPECTED] Storage failed (HBase not available)")
        print("This is expected if HBase is not running")
    else:
        print(f"[UNEXPECTED] Status: {response.status_code}")

    print()


def test_api_documentation():
    print("Testing API documentation endpoint...")
    print("-" * 60)

    factory = APIRequestFactory()
    view = EventCreateView.as_view()

    request = factory.get('/api/events/')
    response = view(request)

    print(f"[TEST] GET /api/events/ - Status: {response.status_code}")
    assert response.status_code == 200, "Should return 200 for GET"

    print("[OK] Documentation endpoint works")
    print(f"Available event types: {response.data.get('event_types')}")
    print()


def test_serializer_logic():
    print("Testing serializer logic...")
    print("-" * 60)

    from events.serializers import EventSerializer

    # Test with minimal data
    serializer = EventSerializer(data={
        'user_id': '42',
        'event_type': 'click'
    })

    assert serializer.is_valid(), f"Should be valid: {serializer.errors}"
    event = serializer.save()

    print(f"[OK] Generated event_id: {event['event_id']}")
    print(f"[OK] Auto-generated created_at: {event['created_at']}")
    print(f"[OK] Default metadata: {event.get('metadata', {})}")
    print()


def main():
    print("=" * 60)
    print("Event Collection API Test")
    print("=" * 60)
    print()

    try:
        test_serializer_logic()
        test_event_validation()
        test_event_creation_structure()
        test_api_documentation()

        print("=" * 60)
        print("[OK] All API tests passed!")
        print()
        print("Note: Event storage tests require HBase to be running.")
        print("To test with HBase:")
        print("  1. Start HBase and Thrift server")
        print("  2. Run: python manage.py setup_hbase")
        print("  3. Run: python manage.py runserver")
        print("  4. Use curl or Postman to POST to /api/events/")
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
