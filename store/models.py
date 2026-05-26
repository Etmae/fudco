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
    ('beverages',   'Beverages'),
    ('dairy',       'Dairy'),
    ('bakery',      'Bakery'),
    ('frozen',      'Frozen Foods'),
    ('snacks',      'Snacks'),
    ('household',   'Household'),
    ('personal',    'Personal Care'),
    ('other',       'Other'),
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


# ── Sale ──────────────────────────────────────────────────────────────────────

def generate_receipt_number():
    """Generates a unique receipt number like RCPT-00021."""
    last = Sale.objects.order_by('-id').first()
    next_id = (last.id + 1) if last else 1
    return f"RCPT-{next_id:05d}"


class Sale(models.Model):
    cashier        = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sales',
    )
    total_amount   = models.DecimalField(max_digits=12, decimal_places=2, default=0)
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