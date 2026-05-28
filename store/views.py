from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, F, Q, Count
from store.decorators import login_required_custom, manager_required
from store.models import Product, Sale, SaleItem, Cart, CartItem, CATEGORY_CHOICES, PAYMENT_METHOD_CHOICES
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction as db_transaction
from datetime import timedelta
from django.contrib.auth.models import User
from decimal import Decimal, InvalidOperation

def get_recent_revenue_chart_data(today):
    start_window = today - timedelta(days=6)
    first_sale = (
        Sale.objects
        .filter(created_at__date__gte=start_window, created_at__date__lte=today)
        .order_by('created_at')
        .values_list('created_at', flat=True)
        .first()
    )
    start_day = timezone.localtime(first_sale).date() if first_sale else start_window

    chart_labels = []
    chart_data = []
    current_day = start_day
    while current_day <= today:
        rev = Sale.objects.filter(
            created_at__date=current_day
        ).aggregate(t=Sum('total_amount'))['t'] or 0
        chart_labels.append(current_day.strftime('%d %b'))
        chart_data.append(float(rev))
        current_day += timedelta(days=1)

    return chart_labels, chart_data


def login_view(request):
    if request.user.is_authenticated:
        return redirect('store:dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('store:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'store/login.html')


def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('store:login')


@login_required_custom
def dashboard(request):
    from datetime import timedelta
    today = timezone.localdate()

    total_products     = Product.objects.count()
    low_stock_count    = Product.objects.filter(Q(quantity__lte=F('restock_threshold'))).count()
    transactions_today = Sale.objects.filter(created_at__date=today).count()
    revenue_today      = Sale.objects.filter(
                             created_at__date=today
                         ).aggregate(total=Sum('total_amount'))['total'] or 0

    recent_sales       = Sale.objects.select_related('cashier').all()[:8]
    low_stock_products = Product.objects.filter(
                             Q(quantity__lte=F('restock_threshold'))
                         ).order_by('quantity')[:10]

    chart_labels, chart_data = get_recent_revenue_chart_data(today)

    context = {
        'total_products':     total_products,
        'low_stock_count':    low_stock_count,
        'transactions_today': transactions_today,
        'revenue_today':      revenue_today,
        'recent_sales':       recent_sales,
        'low_stock_products': low_stock_products,
        'chart_labels':       json.dumps(chart_labels),
        'chart_data':         json.dumps(chart_data),
    }
    return render(request, 'store/dashboard.html', context)

# ── Inventory ─────────────────────────────────────────────────────────────────

@login_required_custom
def inventory(request):
    query    = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    status   = request.GET.get('status', '').strip()

    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    if category:
        products = products.filter(category=category)

    if status == 'in_stock':
        products = products.filter(quantity__gt=F('restock_threshold'))
    elif status == 'low_stock':
        products = products.filter(quantity__lte=F('restock_threshold'), quantity__gt=0)
    elif status == 'out_of_stock':
        products = products.filter(quantity=0)

    context = {
        'products':         products,
        'categories':       CATEGORY_CHOICES,
        'query':            query,
        'selected_category': category,
        'selected_status':  status,
        'low_stock_count':  Product.objects.filter(Q(quantity__lte=F('restock_threshold'))).count(),
    }
    return render(request, 'store/inventory.html', context)


@manager_required
def product_add(request):
    if request.method == 'POST':
        name              = request.POST.get('name', '').strip()
        category          = request.POST.get('category', '')
        price             = request.POST.get('price', '')
        quantity          = request.POST.get('quantity', '')
        restock_threshold = request.POST.get('restock_threshold', '')

        errors = []
        if not name:
            errors.append('Product name is required.')
        if Product.objects.filter(name__iexact=name).exists():
            errors.append('A product with this name already exists.')
        try:
            price = float(price)
            if price <= 0:
                raise ValueError
        except (ValueError, TypeError):
            errors.append('Price must be a positive number.')
        try:
            quantity = int(quantity)
            if quantity < 0:
                raise ValueError
        except (ValueError, TypeError):
            errors.append('Quantity must be a non-negative whole number.')
        try:
            restock_threshold = int(restock_threshold)
            if restock_threshold < 0:
                raise ValueError
        except (ValueError, TypeError):
            errors.append('Restock threshold must be a non-negative whole number.')

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            product = Product.objects.create(
                name=name,
                category=category,
                price=price,
                quantity=quantity,
                restock_threshold=restock_threshold,
            )
            if request.FILES.get('image'):
                product.image = request.FILES['image']
                product.save(update_fields=['image'])
            messages.success(request, f'"{name}" has been added to inventory.')
            return redirect('store:inventory')

    context = {
        'categories':      CATEGORY_CHOICES,
        'low_stock_count': Product.objects.filter(Q(quantity__lte=F('restock_threshold'))).count(),
    }
    return render(request, 'store/product_form.html', context)


@manager_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        name              = request.POST.get('name', '').strip()
        category          = request.POST.get('category', '')
        price             = request.POST.get('price', '')
        quantity          = request.POST.get('quantity', '')
        restock_threshold = request.POST.get('restock_threshold', '')

        errors = []
        if not name:
            errors.append('Product name is required.')
        if Product.objects.filter(name__iexact=name).exclude(pk=pk).exists():
            errors.append('Another product with this name already exists.')
        try:
            price = float(price)
            if price <= 0:
                raise ValueError
        except (ValueError, TypeError):
            errors.append('Price must be a positive number.')
        try:
            quantity = int(quantity)
            if quantity < 0:
                raise ValueError
        except (ValueError, TypeError):
            errors.append('Quantity must be a non-negative whole number.')
        try:
            restock_threshold = int(restock_threshold)
            if restock_threshold < 0:
                raise ValueError
        except (ValueError, TypeError):
            errors.append('Restock threshold must be a non-negative whole number.')

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            product.name              = name
            product.category          = category
            product.price             = price
            product.quantity          = quantity
            product.restock_threshold = restock_threshold
            if request.FILES.get('image'):
                product.image = request.FILES['image']
            product.save()
            messages.success(request, f'"{name}" updated successfully.')
            return redirect('store:inventory')

    context = {
        'product':         product,
        'categories':      CATEGORY_CHOICES,
        'low_stock_count': Product.objects.filter(Q(quantity__lte=F('restock_threshold'))).count(),
    }
    return render(request, 'store/product_form.html', context)


@manager_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'"{name}" has been deleted.')
    return redirect('store:inventory')



# ── Cart helpers ──────────────────────────────────────────────────────────────

def get_active_cart(request):
    cart_id = request.session.get('active_cart_id')
    cart = None

    if cart_id:
        cart = (
            Cart.objects
            .filter(pk=cart_id, cashier=request.user, status__in=['open', 'checkout_pending'])
            .first()
        )

    if cart is None:
        cart = (
            Cart.objects
            .filter(cashier=request.user, status='open')
            .order_by('-updated_at')
            .first()
        )

    if cart is None:
        cart = Cart.objects.create(cashier=request.user)

    request.session['active_cart_id'] = cart.pk
    request.session.modified = True
    return cart


def release_active_cart(request, cart=None):
    if cart and request.session.get('active_cart_id') == cart.pk:
        request.session.pop('active_cart_id', None)
        request.session.modified = True


# ── POS page ──────────────────────────────────────────────────────────────────

@login_required_custom
def pos(request):
    query    = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    products = Product.objects.filter(quantity__gt=0)
    if query:
        products = products.filter(name__icontains=query)
    if category:
        products = products.filter(category=category)

    cart     = get_active_cart(request)
    cart_items, cart_total = _build_cart_display(cart)

    context = {
        'products':          products,
        'categories':        CATEGORY_CHOICES,
        'query':             query,
        'selected_category': category,
        'cart_items':        cart_items,
        'cart_total':        cart_total,
        'cart_count':        sum(item['quantity'] for item in cart_items),
        'low_stock_count':   Product.objects.filter(
                                 Q(quantity__lte=F('restock_threshold'))
                             ).count(),
    }
    return render(request, 'store/pos.html', context)


def _build_cart_display(cart):
    """Converts the active cart into a list for template rendering and AJAX."""
    items = []
    total = Decimal('0')
    cart_items = cart.items.select_related('product').order_by('id')
    for item in cart_items:
        if not item.product:
            continue
        subtotal = item.subtotal
        total += subtotal
        items.append({
            'id':       item.product_id,
            'name':     item.product.name,
            'price':    item.unit_price,
            'quantity': item.quantity,
            'subtotal': subtotal,
        })
    return items, total


# ── Cart AJAX endpoints ───────────────────────────────────────────────────────

@require_POST
@login_required_custom
def cart_add(request):
    try:
        data       = json.loads(request.body)
        product_id = str(data.get('product_id'))
        product    = get_object_or_404(Product, pk=product_id)

        if product.quantity == 0:
            return JsonResponse({'error': 'This product is out of stock.'}, status=400)

        cart = get_active_cart(request)
        if cart.status != 'open':
            cart.status = 'open'
            cart.save(update_fields=['status', 'updated_at'])

        cart_item = CartItem.objects.filter(cart=cart, product=product).first()

        if cart_item:
            new_qty = cart_item.quantity + 1
            if new_qty > product.quantity:
                return JsonResponse(
                    {'error': f'Only {product.quantity} unit(s) available.'}, status=400
                )
            cart_item.quantity = new_qty
            cart_item.unit_price = product.price
            cart_item.save()
        else:
            CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=1,
                unit_price=product.price,
                subtotal=product.price,
            )

        cart_items, cart_total = _build_cart_display(cart)
        return JsonResponse({
            'success':    True,
            'cart_count': sum(item['quantity'] for item in cart_items),
            'cart_total': cart_total,
            'cart_items': cart_items,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_POST
@login_required_custom
def cart_update(request):
    try:
        data       = json.loads(request.body)
        product_id = str(data.get('product_id'))
        quantity   = int(data.get('quantity', 0))
        cart       = get_active_cart(request)
        if cart.status != 'open':
            cart.status = 'open'
            cart.save(update_fields=['status', 'updated_at'])
        product = get_object_or_404(Product, pk=product_id)
        cart_item = CartItem.objects.filter(cart=cart, product=product).first()

        if quantity <= 0:
            if cart_item:
                cart_item.delete()
        else:
            if quantity > product.quantity:
                return JsonResponse(
                    {'error': f'Only {product.quantity} unit(s) in stock.'}, status=400
                )
            if cart_item:
                cart_item.quantity = quantity
                cart_item.unit_price = product.price
                cart_item.save()
            else:
                CartItem.objects.create(
                    cart=cart,
                    product=product,
                    quantity=quantity,
                    unit_price=product.price,
                    subtotal=product.price * quantity,
                )

        cart_items, cart_total = _build_cart_display(cart)
        return JsonResponse({
            'success':    True,
            'cart_count': sum(item['quantity'] for item in cart_items),
            'cart_total': cart_total,
            'cart_items': cart_items,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_POST
@login_required_custom
def cart_remove(request):
    try:
        data       = json.loads(request.body)
        product_id = str(data.get('product_id'))
        cart       = get_active_cart(request)
        if cart.status != 'open':
            cart.status = 'open'
            cart.save(update_fields=['status', 'updated_at'])
        CartItem.objects.filter(cart=cart, product_id=product_id).delete()
        cart_items, cart_total = _build_cart_display(cart)
        return JsonResponse({
            'success':    True,
            'cart_count': sum(item['quantity'] for item in cart_items),
            'cart_total': cart_total,
            'cart_items': cart_items,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_POST
@login_required_custom
def cart_clear(request):
    cart = get_active_cart(request)
    cart.items.all().delete()
    cart.status = 'open'
    cart.save(update_fields=['status', 'updated_at'])
    return JsonResponse({'success': True})


# ── Checkout ──────────────────────────────────────────────────────────────────

@login_required_custom
def checkout(request):
    cart = get_active_cart(request)
    cart_items, cart_total = _build_cart_display(cart)

    if not cart_items:
        messages.error(request, 'Your cart is empty.')
        return redirect('store:pos')

    if request.method == 'GET':
        cart.status = 'checkout_pending'
        cart.save(update_fields=['status', 'updated_at'])
        return render(request, 'store/payment.html', {
            'cart': cart,
            'cart_items': cart_items,
            'cart_total': cart_total,
            'payment_methods': PAYMENT_METHOD_CHOICES,
            'low_stock_count': Product.objects.filter(
                Q(quantity__lte=F('restock_threshold'))
            ).count(),
        })

    action = request.POST.get('action', 'confirm')
    if action == 'cancel':
        cart.status = 'cancelled'
        cart.save(update_fields=['status', 'updated_at'])
        release_active_cart(request, cart)
        messages.info(request, 'Checkout cancelled. No inventory was deducted.')
        return redirect('store:pos')

    payment_method = request.POST.get('payment_method', 'cash')
    valid_methods = {method for method, _label in PAYMENT_METHOD_CHOICES}
    if payment_method not in valid_methods:
        messages.error(request, 'Select a valid payment method.')
        return redirect('store:checkout')

    try:
        amount_received = Decimal(request.POST.get('amount_received') or '0')
    except (InvalidOperation, TypeError):
        messages.error(request, 'Enter a valid amount received.')
        return redirect('store:checkout')

    if amount_received < cart_total:
        messages.error(request, 'Amount received cannot be less than the cart total.')
        return redirect('store:checkout')

    try:
        with db_transaction.atomic():
            locked_cart = (
                Cart.objects
                .select_for_update()
                .prefetch_related('items__product')
                .get(pk=cart.pk, cashier=request.user, status='checkout_pending')
            )
            locked_items = list(locked_cart.items.select_related('product'))

            if not locked_items:
                raise ValueError('Your cart is empty.')

            total = Decimal('0')
            sale_items = []
            for item in locked_items:
                product = Product.objects.select_for_update().get(pk=item.product_id)
                if product.quantity < item.quantity:
                    raise ValueError(
                        f'Insufficient stock for "{product.name}". '
                        f'Available: {product.quantity}, requested: {item.quantity}.'
                    )

                subtotal = product.price * item.quantity
                total += subtotal
                sale_items.append({
                    'product': product,
                    'quantity': item.quantity,
                    'price': item.unit_price,
                    'subtotal': subtotal,
                })

            if amount_received < total:
                raise ValueError('Amount received cannot be less than the cart total.')

            sale = Sale.objects.create(
                cart=locked_cart,
                cashier=request.user,
                total_amount=total,
                payment_method=payment_method,
                payment_status='paid',
                amount_received=amount_received,
                change_given=amount_received - total,
                payment_confirmed_by=request.user,
            )

            for item in sale_items:
                SaleItem.objects.create(sale=sale, **item)

                product = item['product']
                product.quantity -= item['quantity']
                product.save()

            locked_cart.status = 'completed'
            locked_cart.save(update_fields=['status', 'updated_at'])

        release_active_cart(request, cart)
        return redirect('store:receipt', pk=sale.pk)

    except ValueError as e:
        messages.error(request, str(e))
        return redirect('store:pos')
    except Exception as e:
        messages.error(request, f'Checkout failed: {str(e)}')
        return redirect('store:pos')


# ── Receipt ───────────────────────────────────────────────────────────────────

@login_required_custom
def receipt(request, pk):
    sale = get_object_or_404(
        Sale.objects.select_related('cashier').prefetch_related('items__product'),
        pk=pk,
    )
    context = {
        'sale':            sale,
        'low_stock_count': Product.objects.filter(
                               Q(quantity__lte=F('restock_threshold'))
                           ).count(),
    }
    return render(request, 'store/receipt.html', context)


# ── Sales Reports ─────────────────────────────────────────────────────────────

@manager_required
def reports(request):
    from django.db.models import Count

    today      = timezone.localdate()
    start_date = request.GET.get('start_date', '')
    end_date   = request.GET.get('end_date', '')

    sales = Sale.objects.select_related('cashier').prefetch_related('items__product')

    # Date filtering
    if start_date:
        try:
            sales = sales.filter(created_at__date__gte=start_date)
        except Exception:
            pass
    if end_date:
        try:
            sales = sales.filter(created_at__date__lte=end_date)
        except Exception:
            pass

    # Summary stats
    today_sales        = Sale.objects.filter(created_at__date=today)
    revenue_today      = today_sales.aggregate(t=Sum('total_amount'))['t'] or 0
    transactions_today = today_sales.count()

    total_revenue      = sales.aggregate(t=Sum('total_amount'))['t'] or 0
    total_transactions = sales.count()

    # Cashier activity
    cashier_stats = (
        sales.values('cashier__username', 'cashier__first_name', 'cashier__last_name')
        .annotate(
            txn_count=Count('id'),
            total=Sum('total_amount'),
        )
        .order_by('-total')
    )

    chart_labels, chart_data = get_recent_revenue_chart_data(today)

    context = {
        'sales':               sales.order_by('-created_at')[:50],
        'revenue_today':       revenue_today,
        'transactions_today':  transactions_today,
        'total_revenue':       total_revenue,
        'total_transactions':  total_transactions,
        'cashier_stats':       cashier_stats,
        'chart_labels':        json.dumps(chart_labels),
        'chart_data':          json.dumps(chart_data),
        'start_date':          start_date,
        'end_date':            end_date,
        'low_stock_count':     Product.objects.filter(
                                   Q(quantity__lte=F('restock_threshold'))
                               ).count(),
    }
    return render(request, 'store/reports.html', context)


# ── Restock Alerts ────────────────────────────────────────────────────────────

@login_required_custom
def restock_alerts(request):
    out_of_stock = Product.objects.filter(quantity=0).order_by('name')
    low_stock    = Product.objects.filter(
                       quantity__gt=0,
                       quantity__lte=F('restock_threshold'),
                   ).order_by('quantity')
    healthy      = Product.objects.filter(
                       quantity__gt=F('restock_threshold')
                   ).count()

    context = {
        'out_of_stock':    out_of_stock,
        'low_stock':       low_stock,
        'healthy_count':   healthy,
        'low_stock_count': out_of_stock.count() + low_stock.count(),
    }
    return render(request, 'store/restock_alerts.html', context)


# ── Cashier Management ────────────────────────────────────────────────────────

@manager_required
def cashiers(request):
    if request.method == 'POST':
        action   = request.POST.get('action')
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        first    = request.POST.get('first_name', '').strip()
        last     = request.POST.get('last_name', '').strip()

        if action == 'add':
            if not username or not password:
                messages.error(request, 'Username and password are required.')
            elif User.objects.filter(username=username).exists():
                messages.error(request, f'Username "{username}" is already taken.')
            elif len(password) < 6:
                messages.error(request, 'Password must be at least 6 characters.')
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=first,
                    last_name=last,
                )
                # profile auto-created as cashier by signal
                messages.success(request, f'Cashier "{username}" created successfully.')

        elif action == 'toggle':
            user_id = request.POST.get('user_id')
            user    = get_object_or_404(User, pk=user_id)
            if user == request.user:
                messages.error(request, 'You cannot deactivate your own account.')
            else:
                user.is_active = not user.is_active
                user.save()
                state = 'activated' if user.is_active else 'deactivated'
                messages.success(request, f'"{user.username}" has been {state}.')

        return redirect('store:cashiers')

    cashier_list = (
        User.objects
        .filter(profile__role='cashier')
        .select_related('profile')
        .annotate(txn_count=Count('sales'))
        .order_by('username')
    )

    context = {
        'cashier_list':    cashier_list,
        'low_stock_count': Product.objects.filter(
                               Q(quantity__lte=F('restock_threshold'))
                           ).count(),
    }
    return render(request, 'store/cashiers.html', context)


def home(request):
    return redirect('store:dashboard')
