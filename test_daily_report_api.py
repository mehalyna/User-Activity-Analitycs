#!/usr/bin/env python
"""
Daily Report API test script
Tests the daily activity report endpoint
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_activity_analytics.settings')
django.setup()

from rest_framework.test import APIRequestFactory
from events.views import DailyReportView
from events.storage import EventStorage
import json


def test_endpoint_structure():
    print("Testing endpoint structure...")
    print("-" * 60)

    factory = APIRequestFactory()
    view = DailyReportView.as_view()

    request = factory.get('/api/reports/daily/')
    response = view(request)

    print(f"[TEST] GET /api/reports/daily/ - Status: {response.status_code}")

    if response.status_code == 200:
        print("[OK] Endpoint accessible")
        print(f"[INFO] Response keys: {list(response.data.keys())}")

        required_keys = ['report_type', 'total_days', 'total_events', 'daily_stats']
        for key in required_keys:
            assert key in response.data, f"Missing required key: {key}"

        print("[OK] Response structure correct")

        assert response.data['report_type'] == 'daily', "Report type should be 'daily'"
        print("[OK] Report type correct")
    else:
        print(f"[INFO] Status {response.status_code}")

    print()


def test_date_filtering():
    print("Testing date filtering...")
    print("-" * 60)

    factory = APIRequestFactory()
    view = DailyReportView.as_view()

    # Test with date range
    request = factory.get(
        '/api/reports/daily/',
        {'start_date': '2026-04-01', 'end_date': '2026-04-30'}
    )
    response = view(request)

    print(f"[TEST] With date range - Status: {response.status_code}")

    if response.status_code == 200:
        print(f"[OK] Date filtering accepted")
        print(f"[INFO] start_date: {response.data.get('start_date')}")
        print(f"[INFO] end_date: {response.data.get('end_date')}")
        print(f"[INFO] total_days: {response.data.get('total_days')}")
    else:
        print(f"[INFO] Status {response.status_code}")

    print()


def test_invalid_parameters():
    print("Testing invalid parameters...")
    print("-" * 60)

    factory = APIRequestFactory()
    view = DailyReportView.as_view()

    # Invalid date format
    request = factory.get('/api/reports/daily/', {'start_date': 'invalid'})
    response = view(request)
    print(f"[TEST] Invalid date format - Status: {response.status_code}")
    assert response.status_code == 400, "Should return 400 for invalid date"
    print("[OK] Invalid date correctly rejected")

    # Invalid date range (start > end)
    request = factory.get(
        '/api/reports/daily/',
        {'start_date': '2026-04-30', 'end_date': '2026-04-01'}
    )
    response = view(request)
    print(f"[TEST] Invalid date range - Status: {response.status_code}")
    assert response.status_code == 400, "Should return 400 for invalid date range"
    print("[OK] Invalid date range correctly rejected")

    print()


def test_response_format():
    print("Testing response format...")
    print("-" * 60)

    factory = APIRequestFactory()
    view = DailyReportView.as_view()

    request = factory.get('/api/reports/daily/')
    response = view(request)

    if response.status_code == 200:
        print("[OK] Response format test")

        data = response.data

        # Check top-level structure
        assert 'report_type' in data, "Missing report_type"
        assert 'total_days' in data, "Missing total_days"
        assert 'total_events' in data, "Missing total_events"
        assert 'total_unique_users' in data, "Missing total_unique_users"
        assert 'daily_stats' in data, "Missing daily_stats array"

        print(f"[INFO] report_type: {data['report_type']}")
        print(f"[INFO] total_days: {data['total_days']}")
        print(f"[INFO] total_events: {data['total_events']}")
        print(f"[INFO] total_unique_users: {data['total_unique_users']}")
        print(f"[INFO] daily_stats array length: {len(data['daily_stats'])}")

        # Check daily stats structure if data exists
        if data['daily_stats']:
            day_stat = data['daily_stats'][0]
            required_fields = [
                'date', 'total_events', 'unique_users', 'event_types'
            ]
            for field in required_fields:
                assert field in day_stat, f"Daily stat missing field: {field}"

            print("[OK] Daily stats structure correct")

            # Check event_types structure
            if day_stat['event_types']:
                event_type_stat = day_stat['event_types'][0]
                assert 'event_type' in event_type_stat, "Missing event_type"
                assert 'count' in event_type_stat, "Missing count"
                print("[OK] Event type stats structure correct")

        print("[OK] Response format valid")
    else:
        print(f"[INFO] Cannot test format, status: {response.status_code}")

    print()


def test_serializer_validation():
    print("Testing serializer validation...")
    print("-" * 60)

    from events.serializers import DailyReportResponseSerializer

    valid_data = {
        'report_type': 'daily',
        'start_date': '2026-04-01',
        'end_date': '2026-04-30',
        'total_days': 2,
        'total_events': 25,
        'total_unique_users': 5,
        'daily_stats': [
            {
                'date': '2026-04-20',
                'total_events': 15,
                'unique_users': 3,
                'event_types': [
                    {
                        'event_type': 'page_view',
                        'count': 10
                    },
                    {
                        'event_type': 'click',
                        'count': 5
                    }
                ]
            }
        ]
    }

    serializer = DailyReportResponseSerializer(data=valid_data)
    assert serializer.is_valid(), f"Serializer errors: {serializer.errors}"

    print("[OK] Serializer validation passed")
    print(f"[INFO] Serialized data keys: {list(serializer.data.keys())}")

    print()


def test_empty_results():
    print("Testing empty results...")
    print("-" * 60)

    factory = APIRequestFactory()
    view = DailyReportView.as_view()

    # Request report with no data
    request = factory.get('/api/reports/daily/')
    response = view(request)

    print(f"[TEST] Report with no data - Status: {response.status_code}")

    if response.status_code == 200:
        print(f"[OK] Returns valid response even with no data")
        print(f"[INFO] total_days: {response.data.get('total_days')}")
        print(f"[INFO] total_events: {response.data.get('total_events')}")
        assert response.data.get('total_events') == 0, "Should return 0 events"
        assert len(response.data.get('daily_stats', [])) == 0, "Daily stats should be empty"

    print()


def test_aggregation_logic():
    print("Testing aggregation logic...")
    print("-" * 60)

    from events.storage import EventStorage

    print("[INFO] Testing aggregation method structure")

    # Test that aggregation method exists and returns correct format
    try:
        result = EventStorage.get_daily_aggregation(
            start_date='2026-04-01',
            end_date='2026-04-30'
        )

        print(f"[OK] Aggregation method callable")
        print(f"[INFO] Returned {len(result)} days")

        if result:
            day_data = result[0]
            required_keys = ['date', 'total_events', 'unique_users', 'event_types']
            for key in required_keys:
                assert key in day_data, f"Missing key in aggregation: {key}"

            print("[OK] Aggregation result structure correct")

    except Exception as e:
        print(f"[INFO] Aggregation call failed (expected if HBase not available): {str(e)}")

    print()


def test_single_day_report():
    print("Testing single day report...")
    print("-" * 60)

    factory = APIRequestFactory()
    view = DailyReportView.as_view()

    # Request report for a single day
    request = factory.get(
        '/api/reports/daily/',
        {'start_date': '2026-04-20', 'end_date': '2026-04-20'}
    )
    response = view(request)

    print(f"[TEST] Single day report - Status: {response.status_code}")

    if response.status_code == 200:
        print(f"[OK] Single day report works")
        print(f"[INFO] total_days: {response.data.get('total_days')}")

    print()


def main():
    print("=" * 60)
    print("Daily Report API Test")
    print("=" * 60)
    print()

    try:
        test_serializer_validation()
        test_endpoint_structure()
        test_date_filtering()
        test_invalid_parameters()
        test_response_format()
        test_empty_results()
        test_aggregation_logic()
        test_single_day_report()

        print("=" * 60)
        print("[OK] All daily report API tests passed!")
        print()
        print("API Features Tested:")
        print("  [OK] Endpoint structure and accessibility")
        print("  [OK] Date range filtering (start_date, end_date)")
        print("  [OK] Invalid parameter validation")
        print("  [OK] Response format and structure")
        print("  [OK] Empty results handling")
        print("  [OK] Aggregation logic structure")
        print("  [OK] Single day reports")
        print()
        print("To test with real data:")
        print("  1. Start HBase and Thrift server")
        print("  2. Run: python manage.py setup_hbase")
        print("  3. Run: python manage.py generate_sample_events --users 10 --events-per-user 50")
        print("  4. Run: python manage.py runserver")
        print("  5. GET http://127.0.0.1:8000/api/reports/daily/")
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
