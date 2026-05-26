from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import UserProfile, Product


class Command(BaseCommand):
    help = 'Seeds the database with a manager account and sample products'

    def handle(self, *args, **kwargs):
        # ── Create manager ────────────────────────────────────────────────────
        if not User.objects.filter(username='manager').exists():
            manager = User.objects.create_user(
                username='manager',
                password='Manager1234',
                first_name='Store',
                last_name='Manager',
            )
            manager.profile.role = 'manager'
            manager.profile.save()
            self.stdout.write(self.style.SUCCESS('Manager created: manager / Manager1234'))
        else:
            self.stdout.write('Manager already exists — skipping.')

        # ── Create cashier ────────────────────────────────────────────────────
        if not User.objects.filter(username='cashier1').exists():
            cashier = User.objects.create_user(
                username='cashier1',
                password='Cashier1234',
                first_name='John',
                last_name='Doe',
            )
            # Profile is auto-created as 'cashier' by the signal — no need to set role
            self.stdout.write(self.style.SUCCESS('Cashier created: cashier1 / Cashier1234'))
        else:
            self.stdout.write('Cashier already exists — skipping.')

        # ── Seed sample products ──────────────────────────────────────────────
        products = [
            {'name': 'Dangote Rice (50kg)', 'category': 'groceries', 'price': 72000, 'quantity': 30, 'restock_threshold': 5},
            {'name': 'Golden Penny Semolina', 'category': 'groceries', 'price': 4500, 'quantity': 4, 'restock_threshold': 5},
            {'name': 'Peak Milk (400g)', 'category': 'dairy', 'price': 3500, 'quantity': 60, 'restock_threshold': 10},
            {'name': 'Coca-Cola (60cl)', 'category': 'beverages', 'price': 500, 'quantity': 120, 'restock_threshold': 20},
            {'name': 'Indomie Chicken (70g)', 'category': 'groceries', 'price': 250, 'quantity': 200, 'restock_threshold': 30},
            {'name': 'Lipton Yellow Label Tea', 'category': 'beverages', 'price': 1800, 'quantity': 3, 'restock_threshold': 10},
            {'name': 'Sunlight Dish Soap', 'category': 'household', 'price': 800, 'quantity': 45, 'restock_threshold': 8},
            {'name': 'Digestive Biscuits', 'category': 'snacks', 'price': 1200, 'quantity': 0, 'restock_threshold': 5},
            {'name': 'Vaseline Body Lotion', 'category': 'personal', 'price': 2200, 'quantity': 22, 'restock_threshold': 5},
            {'name': 'Agege Bread', 'category': 'bakery', 'price': 700, 'quantity': 2, 'restock_threshold': 5},
        ]

        created = 0
        for p in products:
            if not Product.objects.filter(name=p['name']).exists():
                Product.objects.create(**p)
                created += 1

        self.stdout.write(self.style.SUCCESS(f'{created} products seeded.'))

        from django.core.management import call_command
        self.stdout.write('\nBackfilling 7-day sales chart data…')
        call_command('seed_sales')

        self.stdout.write(self.style.SUCCESS('\nSeed complete. Run the server and log in.'))