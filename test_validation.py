#!/usr/bin/env python
"""
Validation test script
Tests enhanced validation rules for Epic 6
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_activity_analytics.settings')
django.setup()

from rest_framework.test import APIRequestFactory
from events.views import EventCreateView
from events.serializers import EventSerializer


def test_user_id_validation():
    print("Testing user_id validation...")
    print("-" * 60)

    from events.serializers import EventSerializer

    # Valid user IDs
    valid_ids = ['user123', 'test-user', 'user_001', 'ABC-123_test']
    for user_id in valid_ids:
        serializer = EventSerializer(data={
            'user_id': user_id,
            'event_type': 'page_view'
        })
        assert serializer.is_valid(), f"Should accept valid user_id: {user_id}"

    print(f"[OK] Valid user IDs accepted: {', '.join(valid_ids)}")

    # Invalid user IDs
    invalid_ids = [
        ('', 'empty string'),
        ('user@email.com', 'contains @'),
        ('user name', 'contains space'),
        ('user#123', 'contains #'),
        ('a' * 101, 'exceeds 100 chars')
    ]

    for user_id, reason in invalid_ids:
        serializer = EventSerializer(data={
            'user_id': user_id,
            'event_type': 'page_view'
        })
        assert not serializer.is_valid(), f"Should reject user_id: {reason}"
        print(f"[OK] Rejected user_id ({reason})")

    print()


def test_timestamp_validation():
    print("Testing timestamp validation...")
    print("-" * 60)

    from datetime import datetime, timedelta

    # Future timestamp
    future_time = datetime.now() + timedelta(days=1)
    serializer = EventSerializer(data={
        'user_id': 'test',
        'event_type': 'page_view',
        'created_at': future_time.isoformat()
    })
    assert not serializer.is_valid(), "Should reject future timestamp"
    print("[OK] Rejected future timestamp")

    # Very old timestamp (> 1 year)
    old_time = datetime.now() - timedelta(days=400)
    serializer = EventSerializer(data={
        'user_id': 'test',
        'event_type': 'page_view',
        'created_at': old_time.isoformat()
    })
    assert not serializer.is_valid(), "Should reject timestamp > 1 year old"
    print("[OK] Rejected timestamp > 1 year old")

    # Valid timestamps
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    last_week = now - timedelta(days=7)

    for time_val in [now, yesterday, last_week]:
        serializer = EventSerializer(data={
            'user_id': 'test',
            'event_type': 'page_view',
            'created_at': time_val.isoformat() + 'Z'  # Add Z for UTC
        })
        if not serializer.is_valid():
            print(f"Validation errors: {serializer.errors}")
        assert serializer.is_valid(), f"Should accept valid timestamp: {time_val}"

    print("[OK] Accepted valid timestamps (now, yesterday, last week)")
    print()


def test_url_validation():
    print("Testing URL validation...")
    print("-" * 60)

    # Valid URLs
    valid_urls = [
        'https://example.com',
        'http://localhost:8000/page',
        'https://sub.domain.com/path?query=1'
    ]

    for url in valid_urls:
        serializer = EventSerializer(data={
            'user_id': 'test',
            'event_type': 'page_view',
            'page_url': url
        })
        assert serializer.is_valid(), f"Should accept valid URL: {url}"

    print(f"[OK] Valid URLs accepted")

    # URL too long (> 2048 chars)
    long_url = 'https://example.com/' + 'a' * 2050
    serializer = EventSerializer(data={
        'user_id': 'test',
        'event_type': 'page_view',
        'page_url': long_url
    })
    assert not serializer.is_valid(), "Should reject URL > 2048 chars"
    print("[OK] Rejected URL exceeding 2048 characters")

    print()


def test_metadata_validation():
    print("Testing metadata validation...")
    print("-" * 60)

    # Valid metadata
    valid_metadata = {
        'browser': 'Chrome',
        'device': 'desktop',
        'session': {'id': '123', 'duration': 300}
    }

    serializer = EventSerializer(data={
        'user_id': 'test',
        'event_type': 'page_view',
        'metadata': valid_metadata
    })
    assert serializer.is_valid(), "Should accept valid metadata"
    print("[OK] Valid metadata accepted")

    # Metadata too large (> 10KB)
    large_metadata = {'data': 'x' * 11000}
    serializer = EventSerializer(data={
        'user_id': 'test',
        'event_type': 'page_view',
        'metadata': large_metadata
    })
    assert not serializer.is_valid(), "Should reject metadata > 10KB"
    print("[OK] Rejected metadata exceeding 10KB")

    # Deep nesting (> 5 levels)
    deep_metadata = {'l1': {'l2': {'l3': {'l4': {'l5': {'l6': 'too deep'}}}}}}
    serializer = EventSerializer(data={
        'user_id': 'test',
        'event_type': 'page_view',
        'metadata': deep_metadata
    })
    assert not serializer.is_valid(), "Should reject metadata with > 5 levels of nesting"
    print("[OK] Rejected metadata with excessive nesting (> 5 levels)")

    # Not a dictionary
    serializer = EventSerializer(data={
        'user_id': 'test',
        'event_type': 'page_view',
        'metadata': "not a dict"
    })
    assert not serializer.is_valid(), "Should reject non-dict metadata"
    print("[OK] Rejected non-dictionary metadata")

    print()


def test_target_id_validation():
    print("Testing target_id validation...")
    print("-" * 60)

    # Valid target IDs
    serializer = EventSerializer(data={
        'user_id': 'test',
        'event_type': 'click',
        'target_id': 'btn_submit_123'
    })
    assert serializer.is_valid(), "Should accept valid target_id"
    print("[OK] Valid target_id accepted")

    # Target ID too long (> 200 chars)
    long_target = 'a' * 201
    serializer = EventSerializer(data={
        'user_id': 'test',
        'event_type': 'click',
        'target_id': long_target
    })
    assert not serializer.is_valid(), "Should reject target_id > 200 chars"
    print("[OK] Rejected target_id exceeding 200 characters")

    print()


def test_api_validation_integration():
    print("Testing API validation integration...")
    print("-" * 60)

    factory = APIRequestFactory()
    view = EventCreateView.as_view()

    # Valid request
    request = factory.post('/api/events/', {
        'user_id': 'valid_user',
        'event_type': 'page_view'
    }, format='json')
    response = view(request)

    # Should return 201 or 500 (if HBase unavailable)
    assert response.status_code in [201, 500], f"Unexpected status: {response.status_code}"
    print(f"[OK] Valid request handled (status: {response.status_code})")

    # Invalid request - empty user_id
    request = factory.post('/api/events/', {
        'user_id': '',
        'event_type': 'page_view'
    }, format='json')
    response = view(request)

    assert response.status_code == 400, "Should return 400 for empty user_id"
    print("[OK] Empty user_id rejected with 400")

    # Invalid request - invalid characters in user_id
    request = factory.post('/api/events/', {
        'user_id': 'user@example.com',
        'event_type': 'page_view'
    }, format='json')
    response = view(request)

    assert response.status_code == 400, "Should return 400 for invalid user_id"
    print("[OK] Invalid user_id characters rejected with 400")

    print()


def main():
    print("=" * 60)
    print("Validation Tests (Epic 6)")
    print("=" * 60)
    print()

    try:
        test_user_id_validation()
        test_timestamp_validation()
        test_url_validation()
        test_metadata_validation()
        test_target_id_validation()
        test_api_validation_integration()

        print("=" * 60)
        print("[OK] All validation tests passed!")
        print()
        print("Validation Rules Verified:")
        print("  [OK] User ID format and length")
        print("  [OK] Timestamp range (no future, max 1 year old)")
        print("  [OK] URL length limits (max 2048 chars)")
        print("  [OK] Metadata size limits (max 10KB)")
        print("  [OK] Metadata nesting limits (max 5 levels)")
        print("  [OK] Target ID length (max 200 chars)")
        print("  [OK] API integration with validation")
        print()
        print("Demo data generation commands:")
        print("  python manage.py generate_demo_data --scenario default")
        print("  python manage.py generate_demo_data --scenario ecommerce")
        print("  python manage.py generate_demo_data --scenario campaign")
        print("  python manage.py generate_demo_data --scenario minimal")
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
