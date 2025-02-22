from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.urls import reverse

def user_type_required(allowed_types):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            def get_dashboard_url(user_type):
                if user_type == 'employee':
                    return reverse('employee_dashboard')
                elif user_type == 'employer':
                    return reverse('employer_dashboard')
                elif user_type == 'admin':
                    return reverse('admin_dashboard')
                return reverse('home')

            if isinstance(allowed_types, (list, tuple)):
                if request.user.user_type not in allowed_types:
                    messages.error(request, f"Access denied. You do not have permission to access this page.")
                    return redirect(get_dashboard_url(request.user.user_type))
            else:
                if request.user.user_type != allowed_types:
                    if allowed_types == 'admin':
                        error_msg = "Access denied. This page is restricted to administrators only."
                    elif allowed_types == 'employer':
                        error_msg = "Access denied. This page is restricted to employers only."
                    elif allowed_types == 'employee':
                        error_msg = "Access denied. This page is restricted to employees only."
                    else:
                        error_msg = "Access denied. You do not have permission to access this page."
                    
                    messages.error(request, error_msg)
                    return redirect(get_dashboard_url(request.user.user_type))
                    
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator