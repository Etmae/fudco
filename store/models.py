from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


# ── Choices ───────────────────────────────────────────────────────────────────

ROLE_CHOICES = [
    ('manager', 'Manager'),
    ('cashier', 'Cashier'),
]

CATEGORY_CHOICES = [
    ('groceries',   'Groceries'),
    ('technology',  'Technology'),
    ('clothing',    'Clothing'),
    ('beverages',   'Beverages'),
    ('dairy',       'Dairy'),
    ('bakery',      'Bakery'),
    ('frozen',      'Frozen Foods'),
    ('snacks',      'Snacks'),
    ('household',   'Household'),
    ('personal',    'Personal Care'),
    ('other',       'Other'),
]

CART_STATUS_CHOICES = [
    ('open', 'Open'),
    ('checkout_pending', 'Checkout Pending'),
    ('cancelled', 'Cancelled'),
    ('completed', 'Completed'),
]

PAYMENT_METHOD_CHOICES = [
    ('cash', 'Cash'),
    ('card', 'Card'),
    ('transfer', 'Transfer'),
    ('mobile_money', 'Mobile Money'),
]

PAYMENT_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('paid', 'Paid'),
    ('failed', 'Failed'),
    ('cancelled', 'Cancelled'),
]


# ── UserProfile ───────────────────────────────────────────────────────────────

class UserProfile(models.Model):
    """
    Extends Django's built-in User with a role field.
    Created automatically whenever a new User is saved (via signal below).
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='cashier',
    )

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    def is_manager(self):
        return self.role == 'manager'

    def is_cashier(self):
        return self.role == 'cashier'


# Auto-create a UserProfile every time a User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


# ── Product ───────────────────────────────────────────────────────────────────

class Product(models.Model):
    name               = models.CharField(max_length=200)
    category           = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    price              = models.DecimalField(max_digits=10, decimal_places=2)
    quantity           = models.PositiveIntegerField(default=0)
    restock_threshold  = models.PositiveIntegerField(default=5)
    image              = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def is_low_stock(self):
        return self.quantity <= self.restock_threshold and self.quantity > 0

    def is_out_of_stock(self):
        return self.quantity == 0

    def stock_status(self):
        if self.is_out_of_stock():
            return 'out_of_stock'
        if self.is_low_stock():
            return 'low_stock'
        return 'in_stock'


class Cart(models.Model):
    cashier = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='carts',
    )
    status = models.CharField(
        max_length=20,
        choices=CART_STATUS_CHOICES,
        default='open',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        cart_id = f"CART-{self.pk:05d}" if self.pk else "CART-new"
        return f"{cart_id} ({self.status})"

    @property
    def total_amount(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)


# ── Sale ──────────────────────────────────────────────────────────────────────

def generate_receipt_number():
    """Generates a unique receipt number like RCPT-00021."""
    last = Sale.objects.order_by('-id').first()
    next_id = (last.id + 1) if last else 1
    return f"RCPT-{next_id:05d}"


class Sale(models.Model):
    cart           = models.OneToOneField(
        Cart,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sale',
    )
    cashier        = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sales',
    )
    total_amount   = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cash',
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='paid',
    )
    amount_received = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    change_given    = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_confirmed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='confirmed_payments',
    )
    receipt_number = models.CharField(max_length=20, unique=True, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.receipt_number} — ₦{self.total_amount}"

    def save(self, *args, **kwargs):
        # Auto-generate receipt number on first save
        if not self.receipt_number:
            self.receipt_number = generate_receipt_number()
        super().save(*args, **kwargs)


# ── SaleItem ──────────────────────────────────────────────────────────────────

class SaleItem(models.Model):
    sale     = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product  = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='sale_items')
    quantity = models.PositiveIntegerField()
    price    = models.DecimalField(max_digits=10, decimal_places=2)   # price at time of sale
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    def save(self, *args, **kwargs):
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)
