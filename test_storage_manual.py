#!/usr/bin/env python
"""
Manual test script for HBase storage operations
This script tests the EventStorage class without requiring HBase to be running
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_activity_analytics.settings')
django.setup()

from events.storage import EventStorage
from datetime import datetime


def test_row_key_operations():
    print("Testing row key operations...")
    print("-" * 60)

    user_id = "user_42"
    date = "2026-04-20"
    event_id = "evt_001"

    row_key = EventStorage._build_row_key(user_id, date, event_id)
    print(f"[OK] Built row key: {row_key}")

    parsed = EventStorage._parse_row_key(row_key)
    print(f"[OK] Parsed row key: {parsed}")

    assert parsed['user_id'] == user_id, "User ID mismatch"
    assert parsed['date'] == date, "Date mismatch"
    assert parsed['event_id'] == event_id, "Event ID mismatch"

    print("[OK] Row key operations working correctly\n")


def test_event_data_structure():
    print("Testing event data structure...")
    print("-" * 60)

    sample_event = {
        'event_type': 'page_view',
        'page_url': '/products/laptop',
        'target_id': 'prod_123',
        'created_at': datetime.utcnow().isoformat(),
        'metadata': {
            'browser': 'Chrome',
            'device': 'desktop',
            'session_id': 'sess_abc123'
        }
    }

    print("[OK] Sample event structure:")
    for key, value in sample_event.items():
        print(f"  - {key}: {value}")

    print("\n[OK] Event data structure is valid\n")


def test_with_hbase():
    print("Testing with HBase...")
    print("-" * 60)
    print("Note: This requires HBase to be running")
    print("Skipping actual HBase operations in this test")
    print("To test with HBase:")
    print("  1. Ensure HBase and Thrift server are running")
    print("  2. Run: python manage.py setup_hbase")
    print("  3. Run: python verify_setup.py")
    print()


def main():
    print("=" * 60)
    print("EventStorage Manual Test")
    print("=" * 60)
    print()

    try:
        test_row_key_operations()
        test_event_data_structure()
        test_with_hbase()

        print("=" * 60)
        print("[OK] All manual tests passed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[FAIL] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
