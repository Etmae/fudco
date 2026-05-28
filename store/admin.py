from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from store.models import UserProfile, Product, Cart, CartItem, Sale, SaleItem


# ── Inline UserProfile inside User admin ──────────────────────────────────────

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# ── Product ───────────────────────────────────────────────────────────────────

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ('name', 'category', 'price', 'quantity', 'restock_threshold', 'stock_status')
    list_filter   = ('category',)
    search_fields = ('name',)

    def stock_status(self, obj):
        return obj.stock_status()
    stock_status.short_description = 'Status'


# ── Sale ──────────────────────────────────────────────────────────────────────

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'cashier', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'cashier')
    inlines = (CartItemInline,)


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display  = ('receipt_number', 'cashier', 'total_amount', 'payment_method', 'payment_status', 'created_at')
    list_filter   = ('cashier', 'payment_method', 'payment_status')
    inlines       = (SaleItemInline,)
    readonly_fields = ('receipt_number',)
