from django.core.management.base import BaseCommand
from events.hbase_client import HBaseClient
from events.storage import EventStorage
import json


class Command(BaseCommand):
    help = 'Test HBase connection and display diagnostic information'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('HBase Connection Test'))
        self.stdout.write('=' * 60)

        health = HBaseClient.health_check()

        self.stdout.write(f"\nHost: {health['host']}")
        self.stdout.write(f"Port: {health['port']}")
        self.stdout.write(f"Connected: {health['connected']}")

        if health['connected']:
            self.stdout.write(
                self.style.SUCCESS(f"\n[OK] HBase is available")
            )
            self.stdout.write(f"Total tables: {health['tables_count']}")

            table_exists = HBaseClient.table_exists(EventStorage.TABLE_NAME)
            self.stdout.write(
                f"\nTable '{EventStorage.TABLE_NAME}' exists: {table_exists}"
            )

            if table_exists:
                self.stdout.write(
                    self.style.SUCCESS(f"[OK] Events table is ready")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"\n[WARN] Events table not found"
                    )
                )
                self.stdout.write(
                    "Run 'python manage.py setup_hbase' to create it"
                )

            try:
                connection = HBaseClient.get_connection()
                tables = connection.tables()
                self.stdout.write(f"\nAvailable tables:")
                for table in tables:
                    self.stdout.write(f"  - {table.decode()}")
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error listing tables: {str(e)}")
                )

        else:
            self.stdout.write(
                self.style.ERROR(f"\n[FAIL] HBase connection failed")
            )
            self.stdout.write(f"Error: {health.get('error', 'Unknown error')}")
            self.stdout.write(
                "\nTroubleshooting steps:"
            )
            self.stdout.write("1. Ensure HBase is running")
            self.stdout.write("2. Start the Thrift server:")
            self.stdout.write("   hbase thrift start")
            self.stdout.write(f"3. Verify port {health['port']} is accessible")
            self.stdout.write("4. Check .env configuration")

        self.stdout.write('\n' + '=' * 60)
