from django.core.management.base import BaseCommand
from events.hbase_client import HBaseClient


class Command(BaseCommand):
    help = 'Set up HBase tables for user activity tracking'

    def handle(self, *args, **options):
        self.stdout.write('Setting up HBase tables...')

        try:
            table_name = 'user_activity'
            families = {
                'cf': dict()
            }

            if HBaseClient.table_exists(table_name):
                self.stdout.write(
                    self.style.WARNING(f'Table {table_name} already exists')
                )
            else:
                HBaseClient.create_table(table_name, families)
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created table: {table_name}')
                )

            self.stdout.write(self.style.SUCCESS('HBase setup completed'))

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error setting up HBase: {str(e)}')
            )
