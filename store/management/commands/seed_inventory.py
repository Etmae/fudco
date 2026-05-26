from django.core.management.base import BaseCommand
from store.models import Product

class Command(BaseCommand):
    help = 'Seeds the database with project evaluation product inventory data'

    def handle(self, *args, **options):
        # We use your exact model choices lowercase slug keys here
        products_data = [
            {"name": "Oraimo Power Bank 20000mAh", "category": "technology", "price": 18500, "quantity": 14, "threshold": 3},
            {"name": "Logitech Wireless Mouse", "category": "technology", "price": 7200, "quantity": 9, "threshold": 2},
            {"name": "Frozen Chicken Wings", "category": "frozen", "price": 9500, "quantity": 18, "threshold": 5},
            {"name": "Pringles Original", "category": "snacks", "price": 2500, "quantity": 30, "threshold": 8},
            {"name": "Colgate Toothpaste", "category": "personal", "price": 1200, "quantity": 45, "threshold": 10},
            {"name": "Harpic Toilet Cleaner", "category": "household", "price": 1800, "quantity": 12, "threshold": 4},
            {"name": "Peak Milk Powder", "category": "dairy", "price": 3800, "quantity": 22, "threshold": 6},
            {"name": "Coca-Cola 50cl", "category": "beverages", "price": 500, "quantity": 120, "threshold": 20},
            {"name": "Plain White T-Shirt", "category": "clothing", "price": 4500, "quantity": 16, "threshold": 5},
            {"name": "Chocolate Muffin", "category": "bakery", "price": 900, "quantity": 7, "threshold": 3},
            {"name": "Disposable Plates", "category": "other", "price": 1500, "quantity": 25, "threshold": 5},
            {"name": "Bluetooth Earbuds Pro", "category": "technology", "price": 13500, "quantity": 5, "threshold": 2},
            {"name": "Ice Cream Vanilla Tub", "category": "frozen", "price": 4200, "quantity": 4, "threshold": 5},
            {"name": "Plantain Chips", "category": "snacks", "price": 800, "quantity": 60, "threshold": 10},
            {"name": "Dove Bath Soap", "category": "personal", "price": 1500, "quantity": 28, "threshold": 6},
            {"name": "Air Freshener Lavender", "category": "household", "price": 2200, "quantity": 35, "threshold": 5},
        ]

        self.stdout.write("Seeding product inventory database records...")
        
        count = 0
        for item in products_data:
            product, created = Product.objects.update_or_create(
                name=item["name"],
                defaults={
                    "category": item["category"],
                    "price": item["price"],
                    "quantity": item["quantity"],          # Matches your model field perfectly
                    "restock_threshold": item["threshold"] # Matches your model field perfectly
                }
            )
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {count} new products into inventory!"))