from django.shortcuts import redirect
from functools import wraps


def manager_required(view_func):
    """Only managers can access this view. Redirects others to dashboard."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('store:login')
        if request.user.profile.role != 'manager':
            return redirect('store:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def login_required_custom(view_func):
    """Any authenticated user (manager or cashier) can access this view."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('store:login')
        return view_func(request, *args, **kwargs)
    return wrapper