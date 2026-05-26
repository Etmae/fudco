import random
from datetime import datetime, time, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.utils import timezone

from store.models import Product, Sale, SaleItem

# Simulated week: Mon–Sat build up, today (day 7) lighter — first real day of use
DAILY_REVENUE = [42_000, 51_000, 47_500, 58_000, 63_500, 71_000, 28_500]


class Command(BaseCommand):
    help = (
        'Backfills the last 7 days of sales for the dashboard chart. '
        'By default only fills days with no revenue (keeps real sales on today).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all sales, then seed a full simulated week',
        )

    def handle(self, *args, **options):
        cashier = User.objects.filter(username='cashier1').first()
        if not cashier:
            cashier = User.objects.filter(is_superuser=True).first()
        if not cashier:
            self.stderr.write(
                self.style.ERROR('No cashier found. Run: python manage.py seed_manager')
            )
            return

        products = list(Product.objects.all()[:8])
        if not products:
            self.stderr.write(
                self.style.ERROR('No products found. Run: python manage.py seed_manager')
            )
            return

        if options['clear']:
            deleted, _ = Sale.objects.all().delete()
            self.stdout.write(f'Cleared {deleted} sale record(s).')

        today = timezone.localdate()
        created = 0
        filled_days = []

        for i, target in enumerate(DAILY_REVENUE):
            day = today - timedelta(days=len(DAILY_REVENUE) - 1 - i)
            existing = self._revenue_for_day(day)
            needed = Decimal(target) - existing

            if needed <= 0:
                self.stdout.write(
                    f'  {day:%d %b}: NGN {existing:,.0f} already recorded — skipped'
                )
                continue

            count = self._seed_day(cashier, products, day, needed)
            created += count
            filled_days.append(day)
            self.stdout.write(
                f'  {day:%d %b}: +NGN {needed:,.0f} ({count} sale(s)) '
                f'-> NGN {existing + needed:,.0f} total'
            )

        if created == 0:
            self.stdout.write(self.style.WARNING('All 7 days already have chart data.'))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nAdded {created} sale(s) across {len(filled_days)} day(s). '
                    f'Refresh the dashboard to see the revenue chart.'
                )
            )

    def _revenue_for_day(self, day):
        total = (
            Sale.objects.filter(created_at__date=day)
            .aggregate(t=Sum('total_amount'))['t']
        )
        return Decimal(total or 0)

    def _seed_day(self, cashier, products, day, target):
        """Create 2–4 sales on `day` that sum to `target`."""
        txn_count = random.randint(2, 4)
        amounts = self._split_amount(target, txn_count)
        created = 0

        for amount in amounts:
            product = random.choice(products)
            # Midday timestamps avoid timezone edge cases on date filters
            hour = random.randint(10, 18)
            minute = random.randint(0, 59)
            when = timezone.make_aware(
                datetime.combine(day, time(hour, minute)),
                timezone.get_current_timezone(),
            )

            sale = Sale.objects.create(
                cashier=cashier,
                total_amount=amount,
                receipt_number=self._demo_receipt_number(),
            )
            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=1,
                price=amount,
                subtotal=amount,
            )
            Sale.objects.filter(pk=sale.pk).update(created_at=when)
            created += 1

        return created

    def _demo_receipt_number(self):
        last = (
            Sale.objects.filter(receipt_number__startswith='DEMO-')
            .order_by('-id')
            .first()
        )
        n = 1
        if last and last.receipt_number.startswith('DEMO-'):
            try:
                n = int(last.receipt_number.split('-')[1]) + 1
            except ValueError:
                pass
        return f'DEMO-{n:05d}'

    def _split_amount(self, total, parts):
        """Split `total` into `parts` positive amounts that sum exactly."""
        total = float(total)
        if parts == 1:
            return [Decimal(str(round(total, 2)))]

        cuts = sorted(random.uniform(0.15, 0.85) for _ in range(parts - 1))
        shares = []
        prev = 0.0
        for cut in cuts:
            shares.append(round(total * (cut - prev), 2))
            prev = cut
        shares.append(round(total * (1.0 - prev), 2))

        drift = round(total - sum(shares), 2)
        shares[-1] = round(shares[-1] + drift, 2)

        return [Decimal(str(s)) for s in shares if s > 0]
