from django.core.management.base import BaseCommand
from store.models import Product  # Adjust this import if your model name or app is different

class Command(BaseCommand):
    help = 'Seeds the database with project evaluation product inventory data'

    def handle(self, *args, **options):
        products_data = [
            {"name": "Oraimo Power Bank 20000mAh", "category": "Technology", "price": 18500, "quantity": 14, "threshold": 3},
            {"name": "Logitech Wireless Mouse", "category": "Technology", "price": 7200, "quantity": 9, "threshold": 2},
            {"name": "Frozen Chicken Wings", "category": "Frozen Foods", "price": 9500, "quantity": 18, "threshold": 5},
            {"name": "Pringles Original", "category": "Snacks", "price": 2500, "quantity": 30, "threshold": 8},
            {"name": "Colgate Toothpaste", "category": "Personal Care", "price": 1200, "quantity": 45, "threshold": 10},
            {"name": "Harpic Toilet Cleaner", "category": "Household", "price": 1800, "quantity": 12, "threshold": 4},
            {"name": "Peak Milk Powder", "category": "Dairy", "price": 3800, "quantity": 22, "threshold": 6},
            {"name": "Coca-Cola 50cl", "category": "Beverages", "price": 500, "quantity": 120, "threshold": 20},
            {"name": "Plain White T-Shirt", "category": "Clothing", "price": 4500, "quantity": 16, "threshold": 5},
            {"name": "Chocolate Muffin", "category": "Bakery", "price": 900, "quantity": 7, "threshold": 3},
            {"name": "Disposable Plates", "category": "Other", "price": 1500, "quantity": 25, "threshold": 5},
            {"name": "Bluetooth Earbuds Pro", "category": "Technology", "price": 13500, "quantity": 5, "threshold": 2},
            {"name": "Ice Cream Vanilla Tub", "category": "Frozen Foods", "price": 4200, "quantity": 4, "threshold": 5},
            {"name": "Plantain Chips", "category": "Snacks", "price": 800, "quantity": 60, "threshold": 10},
            {"name": "Dove Bath Soap", "category": "Personal Care", "price": 1500, "quantity": 28, "threshold": 6},
            {"name": "Air Freshener Lavender", "category": "Household", "price": 2200, "quantity": 35, "threshold": 5},
        ]

        self.stdout.write("Seeding product inventory database records...")
        
        count = 0
        for item in products_data:
            # update_or_create prevents duplicate errors if you run it multiple times
            product, created = Product.objects.update_or_create(
                name=item["name"],
                defaults={
                    "category": item["category"],
                    "price": item["price"],
                    "stock": item["quantity"],          # Double check if your model uses 'stock' or 'quantity'
                    "low_stock_threshold": item["threshold"] # Double check your threshold field name
                }
            )
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {count} new products into inventory!"))