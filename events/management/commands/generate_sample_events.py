from django.core.management.base import BaseCommand
from events.storage import EventStorage
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Generate sample events for testing (requires HBase)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=5,
            help='Number of users to generate events for'
        )
        parser.add_argument(
            '--events-per-user',
            type=int,
            default=10,
            help='Number of events per user'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to spread events across'
        )

    def handle(self, *args, **options):
        num_users = options['users']
        events_per_user = options['events_per_user']
        days = options['days']

        self.stdout.write(
            self.style.MIGRATE_HEADING('Generating Sample Events')
        )
        self.stdout.write(f"Users: {num_users}")
        self.stdout.write(f"Events per user: {events_per_user}")
        self.stdout.write(f"Days: {days}")
        self.stdout.write('=' * 60)

        event_types = ['click', 'page_view', 'navigation', 'add_to_cart']
        pages = [
            '/home',
            '/products/laptop',
            '/products/phone',
            '/category/electronics',
            '/cart',
            '/checkout',
        ]

        total_created = 0
        total_failed = 0

        for user_num in range(1, num_users + 1):
            user_id = f"user_{user_num:03d}"
            self.stdout.write(f"\nGenerating events for {user_id}...")

            for event_num in range(events_per_user):
                try:
                    event_type = random.choice(event_types)
                    page_url = f"https://example.com{random.choice(pages)}"

                    days_ago = random.randint(0, days - 1)
                    hours_ago = random.randint(0, 23)
                    minutes_ago = random.randint(0, 59)

                    event_time = datetime.utcnow() - timedelta(
                        days=days_ago,
                        hours=hours_ago,
                        minutes=minutes_ago
                    )

                    event_data = {
                        'event_type': event_type,
                        'page_url': page_url,
                        'target_id': f'target_{random.randint(100, 999)}',
                        'created_at': event_time.isoformat(),
                        'metadata': {
                            'browser': random.choice(['Chrome', 'Firefox', 'Safari', 'Edge']),
                            'device': random.choice(['desktop', 'mobile', 'tablet']),
                            'session_id': f'sess_{random.randint(1000, 9999)}'
                        }
                    }

                    event_id = f"evt_{user_num:03d}_{event_num:03d}_{random.randint(1000, 9999)}"

                    success = EventStorage.save_event(user_id, event_id, event_data)

                    if success:
                        total_created += 1
                    else:
                        total_failed += 1
                        self.stdout.write(
                            self.style.WARNING(f"  Failed to save event {event_id}")
                        )

                except Exception as e:
                    total_failed += 1
                    self.stdout.write(
                        self.style.ERROR(f"  Error: {str(e)}")
                    )

            self.stdout.write(
                self.style.SUCCESS(f"  [OK] {user_id} complete")
            )

        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(
            self.style.SUCCESS(f"\n[OK] Successfully created {total_created} events")
        )

        if total_failed > 0:
            self.stdout.write(
                self.style.WARNING(f"[WARN] Failed to create {total_failed} events")
            )

        self.stdout.write('\nTo view events:')
        self.stdout.write('  python manage.py shell')
        self.stdout.write('  from events.storage import EventStorage')
        self.stdout.write('  events = EventStorage.get_user_events("user_001")')
        self.stdout.write('  print(len(events))')
