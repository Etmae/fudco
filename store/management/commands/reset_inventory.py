# store/management/commands/reset_inventory.py
from django.core.management.base import BaseCommand
from django.core.management import call_command
from store.models import Product

class Command(BaseCommand):
    help = "Wipes out existing stale database records and triggers seed_inventory cleanly."

    def handle(self, *args, **options):
        self.stdout.write("Deleting existing products with broken image references...")
        count, _ = Product.objects.all().delete()
        self.stdout.write(f"Successfully deleted {count} old records.")

        self.stdout.write("Running seed_inventory to push fresh images to Cloudinary...")
        call_command('seed_inventory')
        self.stdout.write("Database inventory reset completely successful!")