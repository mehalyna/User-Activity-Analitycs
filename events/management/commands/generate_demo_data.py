from django.core.management.base import BaseCommand
from events.storage import EventStorage
from datetime import datetime, timedelta
import random
import json


class Command(BaseCommand):
    help = 'Generate realistic demo data for presentation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--scenario',
            type=str,
            default='default',
            choices=['default', 'ecommerce', 'campaign', 'minimal'],
            help='Demo scenario to generate'
        )

    def handle(self, *args, **options):
        scenario = options['scenario']

        self.stdout.write(
            self.style.MIGRATE_HEADING(f'Generating Demo Data: {scenario.upper()} Scenario')
        )
        self.stdout.write('=' * 60)

        if scenario == 'default':
            self.generate_default_scenario()
        elif scenario == 'ecommerce':
            self.generate_ecommerce_scenario()
        elif scenario == 'campaign':
            self.generate_campaign_scenario()
        elif scenario == 'minimal':
            self.generate_minimal_scenario()

    def generate_default_scenario(self):
        """Generate balanced demo data across all event types"""
        self.stdout.write("\nScenario: Balanced user activity over 7 days")
        self.stdout.write("Users: 10, Events per user: ~30")

        users = [f"demo_user_{i:03d}" for i in range(1, 11)]
        pages = [
            '/home', '/products', '/products/laptop', '/products/phone',
            '/cart', '/checkout', '/account', '/search'
        ]
        browsers = ['Chrome', 'Firefox', 'Safari', 'Edge']
        devices = ['desktop', 'mobile', 'tablet']

        total_created = 0
        total_failed = 0

        for user_id in users:
            self.stdout.write(f"\nGenerating events for {user_id}...")

            for day in range(7):
                events_today = random.randint(3, 6)
                date = datetime.utcnow() - timedelta(days=day)

                for _ in range(events_today):
                    event_type = random.choice([
                        'page_view', 'page_view', 'page_view',  # More page views
                        'click', 'click',
                        'navigation',
                        'add_to_cart'
                    ])

                    page_url = f"https://demo.example.com{random.choice(pages)}"
                    target_id = f"elem_{random.randint(100, 999)}"

                    event_time = date - timedelta(
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59)
                    )

                    event_data = {
                        'event_type': event_type,
                        'page_url': page_url,
                        'target_id': target_id,
                        'created_at': event_time.isoformat(),
                        'metadata': {
                            'browser': random.choice(browsers),
                            'device': random.choice(devices),
                            'session_id': f'sess_{random.randint(10000, 99999)}'
                        }
                    }

                    event_id = f"demo_{user_id}_{int(event_time.timestamp())}_{random.randint(100, 999)}"

                    if EventStorage.save_event(user_id, event_id, event_data):
                        total_created += 1
                    else:
                        total_failed += 1

            self.stdout.write(self.style.SUCCESS(f"  [OK] {user_id} complete"))

        self._print_summary(total_created, total_failed)

    def generate_ecommerce_scenario(self):
        """Generate e-commerce shopping journey demo data"""
        self.stdout.write("\nScenario: E-commerce shopping journeys")
        self.stdout.write("Users: 5 shoppers with complete purchase funnels")

        users = [f"shopper_{i:03d}" for i in range(1, 6)]

        products = [
            {'id': 'prod_laptop_001', 'name': 'Gaming Laptop', 'price': 1299.99},
            {'id': 'prod_phone_002', 'name': 'Smartphone', 'price': 899.99},
            {'id': 'prod_tablet_003', 'name': 'Tablet', 'price': 599.99},
            {'id': 'prod_watch_004', 'name': 'Smartwatch', 'price': 399.99},
        ]

        total_created = 0
        total_failed = 0

        for user_id in users:
            self.stdout.write(f"\nGenerating shopping journey for {user_id}...")

            product = random.choice(products)
            base_time = datetime.utcnow() - timedelta(hours=random.randint(1, 72))

            # Journey: Home -> Browse -> Product -> Add to Cart -> Checkout
            journey = [
                ('page_view', '/home', None, {}),
                ('page_view', '/products', None, {}),
                ('page_view', f'/products/{product["id"]}', product['id'], {
                    'product_name': product['name'],
                    'product_price': product['price']
                }),
                ('click', f'/products/{product["id"]}', 'btn_add_to_cart', {
                    'button_text': 'Add to Cart'
                }),
                ('add_to_cart', f'/products/{product["id"]}', product['id'], {
                    'product_name': product['name'],
                    'price': product['price'],
                    'quantity': 1
                }),
                ('page_view', '/cart', None, {'cart_total': product['price']}),
                ('click', '/cart', 'btn_checkout', {'button_text': 'Proceed to Checkout'}),
                ('page_view', '/checkout', None, {'step': 'payment'}),
            ]

            for idx, (event_type, page, target, meta) in enumerate(journey):
                event_time = base_time + timedelta(minutes=idx * 2)

                event_data = {
                    'event_type': event_type,
                    'page_url': f'https://demo-shop.example.com{page}',
                    'target_id': target or '',
                    'created_at': event_time.isoformat(),
                    'metadata': {
                        'browser': 'Chrome',
                        'device': random.choice(['desktop', 'mobile']),
                        'session_id': f'shop_sess_{random.randint(10000, 99999)}',
                        **meta
                    }
                }

                event_id = f"shop_{user_id}_{int(event_time.timestamp())}_{idx}"

                if EventStorage.save_event(user_id, event_id, event_data):
                    total_created += 1
                else:
                    total_failed += 1

            self.stdout.write(self.style.SUCCESS(f"  [OK] {user_id} journey complete"))

        self._print_summary(total_created, total_failed)

    def generate_campaign_scenario(self):
        """Generate data showing campaign impact"""
        self.stdout.write("\nScenario: Marketing campaign impact analysis")
        self.stdout.write("Before campaign: Low activity, After: High activity")

        users = [f"campaign_user_{i:03d}" for i in range(1, 16)]

        total_created = 0
        total_failed = 0

        # Before campaign (7-14 days ago): Low activity
        self.stdout.write("\nGenerating pre-campaign activity...")
        for user_id in users[:10]:  # Only 10 users active
            for day in range(7, 14):
                if random.random() < 0.3:  # 30% chance of activity
                    date = datetime.utcnow() - timedelta(days=day)

                    event_data = {
                        'event_type': 'page_view',
                        'page_url': 'https://campaign.example.com/home',
                        'target_id': '',
                        'created_at': date.isoformat(),
                        'metadata': {
                            'browser': 'Chrome',
                            'device': 'desktop',
                            'campaign': 'none'
                        }
                    }

                    event_id = f"campaign_{user_id}_{int(date.timestamp())}"

                    if EventStorage.save_event(user_id, event_id, event_data):
                        total_created += 1

        # During campaign (last 7 days): High activity
        self.stdout.write("\nGenerating campaign period activity...")
        for user_id in users:  # All 15 users active
            for day in range(7):
                events_today = random.randint(5, 10)  # More events
                date = datetime.utcnow() - timedelta(days=day)

                for _ in range(events_today):
                    event_type = random.choice([
                        'page_view', 'page_view', 'click', 'add_to_cart'
                    ])

                    pages = ['/home', '/campaign/spring-sale', '/products', '/cart']

                    event_time = date - timedelta(
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59)
                    )

                    event_data = {
                        'event_type': event_type,
                        'page_url': f'https://campaign.example.com{random.choice(pages)}',
                        'target_id': f'campaign_elem_{random.randint(100, 999)}',
                        'created_at': event_time.isoformat(),
                        'metadata': {
                            'browser': random.choice(['Chrome', 'Safari', 'Firefox']),
                            'device': random.choice(['desktop', 'mobile']),
                            'campaign': 'spring_sale_2026',
                            'campaign_source': random.choice(['email', 'social', 'banner'])
                        }
                    }

                    event_id = f"campaign_{user_id}_{int(event_time.timestamp())}_{random.randint(100, 999)}"

                    if EventStorage.save_event(user_id, event_id, event_data):
                        total_created += 1
                    else:
                        total_failed += 1

        self._print_summary(total_created, total_failed)

    def generate_minimal_scenario(self):
        """Generate minimal demo data for quick testing"""
        self.stdout.write("\nScenario: Minimal data for quick demo")
        self.stdout.write("Users: 3, Events: ~15 total")

        users = ['alice', 'bob', 'charlie']
        total_created = 0
        total_failed = 0

        for idx, user_id in enumerate(users):
            self.stdout.write(f"\nGenerating events for {user_id}...")

            # Each user has 5 events today
            for i in range(5):
                event_time = datetime.utcnow() - timedelta(hours=i)

                event_types = ['page_view', 'click', 'page_view', 'click', 'add_to_cart']

                event_data = {
                    'event_type': event_types[i],
                    'page_url': f'https://minimal.example.com/page{i}',
                    'target_id': f'elem_{i}',
                    'created_at': event_time.isoformat(),
                    'metadata': {
                        'browser': 'Chrome',
                        'device': 'desktop',
                        'demo': 'minimal'
                    }
                }

                event_id = f"minimal_{user_id}_{i}"

                if EventStorage.save_event(user_id, event_id, event_data):
                    total_created += 1
                else:
                    total_failed += 1

            self.stdout.write(self.style.SUCCESS(f"  [OK] {user_id} complete"))

        self._print_summary(total_created, total_failed)

    def _print_summary(self, created, failed):
        """Print generation summary"""
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(
            self.style.SUCCESS(f"\n[OK] Successfully created {created} events")
        )

        if failed > 0:
            self.stdout.write(
                self.style.WARNING(f"[WARN] Failed to create {failed} events")
            )

        self.stdout.write('\nDemo data ready! Try these endpoints:')
        self.stdout.write('  GET  /api/reports/daily/')
        self.stdout.write('  GET  /api/users/demo_user_001/events/')
        self.stdout.write('  POST /api/events/')
        self.stdout.write('=' * 60)
