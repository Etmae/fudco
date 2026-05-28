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
            {"name": "Yoghurt Strawberry 500g", "category": "dairy", "price": 3000, "quantity": 10, "threshold": 4},
            {"name": "Orange Juice 1L", "category": "beverages", "price": 2500, "quantity": 50, "threshold": 10},
            {"name": "Denim Jeans", "category": "clothing", "price": 8500, "quantity": 8, "threshold": 3},
            {"name": "Banana Bread Loaf", "category": "bakery", "price": 1200, "quantity": 5, "threshold": 2},
            {"name": "Paper Towels Pack", "category": "other", "price": 2000, "quantity": 40, "threshold": 8},
            {"name": "Smartphone 128GB", "category": "technology", "price": 75000, "quantity": 3, "threshold": 1},
            {"name": "Frozen Fish Fillets", "category": "frozen", "price": 6000, "quantity": 6, "threshold": 4},
            {"name": "Salted Peanuts", "category": "snacks", "price": 700, "quantity": 80, "threshold": 15},
            {"name": "Nivea Body Lotion", "category": "personal", "price": 2500, "quantity": 20, "threshold": 5},
            {"name": "Laundry Detergent", "category": "household", "price": 3500, "quantity": 18, "threshold": 4},
            {"name": "Cheddar Cheese Block", "category": "dairy", "price": 4500, "quantity": 12, "threshold": 3},
            {"name": "Mineral Water 1.5L", "category": "beverages", "price": 300, "quantity": 100, "threshold": 20},
            {"name": "Graphic T-Shirt", "category": "clothing", "price": 5000, "quantity": 10, "threshold": 4},
            {"name": "Croissant Butter", "category": "bakery", "price": 800, "quantity": 15, "threshold": 5},
            {"name": "Aluminum Foil Roll", "category": "other", "price": 1200, "quantity": 30, "threshold": 6},
            {"name": "Gaming Laptop", "category": "technology", "price": 150000, "quantity": 2, "threshold": 1},
            {"name": "Frozen Mixed Vegetables", "category": "frozen", "price": 3500, "quantity": 8, "threshold": 5},
            {"name": "Chocolate Bar", "category": "snacks", "price": 500, "quantity": 150, "threshold": 20},
            {"name": "Rexona Deodorant", "category": "personal", "price": 1800, "quantity": 25, "threshold": 5},
            {"name": "Dishwashing Liquid", "category": "household", "price": 2200, "quantity": 22, "threshold": 4},
            {"name": "Butter Milk 1L", "category": "dairy", "price": 2800, "quantity": 14, "threshold": 4},
            {"name": "Energy Drink 250ml", "category": "beverages", "price": 1200, "quantity": 40, "threshold": 10},
            {"name": "Leather Jacket", "category": "clothing", "price": 20000, "quantity": 3, "threshold": 1},
            {"name": "Sourdough Bread Loaf", "category": "bakery", "price": 1500, "quantity": 10, "threshold": 3},
            {"name": "Garbage Bags Pack", "category": "other", "price": 1800, "quantity": 35, "threshold": 7},
            {"name": "4K Ultra HD TV", "category": "technology", "price": 250000, "quantity": 1, "threshold": 1},
            {"name": "Frozen Pizza", "category": "frozen", "price": 5000, "quantity": 10, "threshold": 5},
            {"name": "Potato Chips", "category": "snacks", "price": 600, "quantity": 90, "threshold": 15},
            {"name": "Head & Shoulders Shampoo", "category": "personal", "price": 2000, "quantity": 30, "threshold": 5},
            {"name": "Multi-Surface Cleaner", "category": "household", "price": 2500, "quantity": 20, "threshold": 4},
            {"name": "Greek Yogurt 500g", "category": "dairy", "price": 3500, "quantity": 18, "threshold": 5},
            {"name": "Iced Tea Lemon Flavor", "category": "beverages", "price": 1500, "quantity": 60, "threshold": 10},
            {"name": "Summer Dress", "category": "clothing", "price": 7000, "quantity": 7, "threshold": 3},
            {"name": "Blueberry Muffin", "category": "bakery", "price": 1000, "quantity": 8, "threshold": 3},
            {"name": "Plastic Cups Pack", "category": "other", "price": 800, "quantity": 50, "threshold": 10},
            {"name": "Wireless Bluetooth Speaker", "category": "technology", "price": 12000, "quantity": 6, "threshold": 2},
            {"name": "Frozen Beef Patties", "category": "frozen", "price": 7000, "quantity": 5, "threshold": 4},
            {"name": "Granola Bars", "category": "snacks", "price": 900, "quantity": 70, "threshold": 10},
            {"name": "Vaseline Petroleum Jelly", "category": "personal", "price": 1500, "quantity": 40, "threshold": 5},
            {"name": "Floor Cleaner", "category": "household", "price": 3000, "quantity": 15, "threshold": 4},
            {"name": "Mozzarella Cheese Block", "category": "dairy", "price": 4000, "quantity": 10, "threshold": 3},
            {"name": "Sparkling Water 500ml", "category": "beverages", "price": 800, "quantity": 80, "threshold": 15},
            {"name": "Winter Coat", "category": "clothing", "price": 25000, "quantity": 2, "threshold": 1},
            {"name": "Banana Bread Muffin", "category": "bakery", "price": 1200, "quantity": 12, "threshold": 4},
            {"name": "Paper Plates Pack", "category": "other", "price": 1000, "quantity": 45, "threshold": 8},
            {"name": "Noise-Canceling Headphones", "category": "technology", "price": 18000, "quantity": 4, "threshold": 2},
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