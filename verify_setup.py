#!/usr/bin/env python
"""
Verification script for Epic 1 setup
Run this to verify that all components are properly configured
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_activity_analytics.settings')
django.setup()

from django.conf import settings
from events.hbase_client import HBaseClient


def check_django_config():
    print("✓ Checking Django configuration...")
    print(f"  - DEBUG: {settings.DEBUG}")
    print(f"  - ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"  - Installed apps include 'events': {'events' in settings.INSTALLED_APPS}")
    print(f"  - Installed apps include 'rest_framework': {'rest_framework' in settings.INSTALLED_APPS}")
    return True


def check_hbase_config():
    print("\n✓ Checking HBase configuration...")
    print(f"  - HBASE_HOST: {settings.HBASE_CONFIG['host']}")
    print(f"  - HBASE_PORT: {settings.HBASE_CONFIG['port']}")
    print(f"  - HBASE_TABLE_PREFIX: {settings.HBASE_CONFIG['table_prefix']}")
    return True


def check_hbase_connection():
    print("\n✓ Checking HBase connection...")
    try:
        connection = HBaseClient.get_connection()
        tables = connection.tables()
        print(f"  - Connection successful!")
        print(f"  - Available tables: {[t.decode() for t in tables]}")

        table_name = 'user_activity'
        if HBaseClient.table_exists(table_name):
            print(f"  - Table '{settings.HBASE_CONFIG['table_prefix']}{table_name}' exists ✓")
        else:
            print(f"  - Table '{settings.HBASE_CONFIG['table_prefix']}{table_name}' not found")
            print(f"  - Run 'python manage.py setup_hbase' to create it")

        HBaseClient.close_connection()
        return True
    except Exception as e:
        print(f"  ✗ Connection failed: {str(e)}")
        print(f"  - Make sure HBase Thrift server is running on {settings.HBASE_CONFIG['host']}:{settings.HBASE_CONFIG['port']}")
        return False


def main():
    print("=" * 60)
    print("Epic 1 Setup Verification")
    print("=" * 60)

    checks = [
        check_django_config(),
        check_hbase_config(),
        check_hbase_connection(),
    ]

    print("\n" + "=" * 60)
    if all(checks):
        print("✓ All checks passed!")
        print("\nYou can now:")
        print("  1. Run 'python manage.py setup_hbase' (if table doesn't exist)")
        print("  2. Run 'python manage.py runserver' to start the dev server")
        print("  3. Proceed to Epic 2: Event Collection API")
    else:
        print("✗ Some checks failed. Please review the output above.")
        sys.exit(1)
    print("=" * 60)


if __name__ == '__main__':
    main()
