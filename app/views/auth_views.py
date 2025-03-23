from app.forms.forms import LogInForm
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse

def user_login(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                login(request, user)
                return redirect(get_redirect(user))
            else:
                messages.error(request, "The credentials provided were invalid!")
        else:
            messages.error(request, 'There was an error with your submission. Please check the form for details.') # pragma: no cover
    else:
        form = LogInForm()
    return render(request, 'account/login.html', {'form': form})

def get_redirect(user):
    if user.user_type == 'employer':
        return reverse('employer_dashboard')
    elif user.user_type == 'employee':
        return reverse('employee_dashboard')
    elif user.user_type == 'admin':
        return reverse('admin_dashboard')
    return reverse('login')

def log_out(request):
    """Log out the current user"""
    logout(request)
    return redirect('home')
