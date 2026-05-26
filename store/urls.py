from django.urls import path
from store import views

app_name = 'store'

urlpatterns = [
    path('',                            views.home,           name='home'),
    path('login/',                      views.login_view,     name='login'),
    path('logout/',                     views.logout_view,    name='logout'),
    path('dashboard/',                  views.dashboard,      name='dashboard'),

    # Inventory
    path('inventory/',                  views.inventory,      name='inventory'),
    path('inventory/add/',              views.product_add,    name='product_add'),
    path('inventory/<int:pk>/edit/',    views.product_edit,   name='product_edit'),
    path('inventory/<int:pk>/delete/',  views.product_delete, name='product_delete'),

    # POS & cart
    path('pos/',                        views.pos,            name='pos'),
    path('cart/add/',                   views.cart_add,       name='cart_add'),
    path('cart/update/',                views.cart_update,    name='cart_update'),
    path('cart/remove/',                views.cart_remove,    name='cart_remove'),
    path('cart/clear/',                 views.cart_clear,     name='cart_clear'),
    path('checkout/',                   views.checkout,       name='checkout'),
    path('receipt/<int:pk>/',           views.receipt,        name='receipt'),

    # Reports & alerts
    path('reports/',                    views.reports,        name='reports'),
    path('restock-alerts/',             views.restock_alerts, name='restock_alerts'),
    path('cashiers/',                   views.cashiers,       name='cashiers'),
]