from django.shortcuts import render, redirect
from django.urls import reverse
from app.forms.forms import EmployeeSignUpForm, EmployerSignUpForm, LogInForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import login, logout
from django.contrib import messages
from app.models import Employee, Employer, Admin

def home(request):
    return render(request, 'home.html')

def employee_signup(request):
    if request.method == 'POST':
        form = EmployeeSignUpForm(request.POST)
        if form.is_valid():
            form.save()  # Saves the new Employee user
            return redirect('login')  # or wherever you want
    else:
        form = EmployeeSignUpForm()
    return render(request, 'employee_signup.html', {'form': form})

def employer_signup(request):
    if request.method == 'POST':
        form = EmployerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            print(f"User created: {user.email}")  # Debug print
            return redirect('login')
        else:
            print(f"Form errors: {form.errors}")  # Debug print
    else:
        form = EmployerSignUpForm()
    return render(request, 'employer_signup.html', {'form': form})

def user_login(request):
    form = LogInForm(request.POST)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                login(request, user)
                return redirect(get_redirect(user))
            else:
                messages.error(request, "The credentials provided were invalid!")
        else:
            messages.error(request, 'There was an error with your submission. Please check the form for details.')

    return render(request, 'login.html', {'form': form})

def get_redirect(user):
    if isinstance(user, Employer):
        return reverse('employer_dashboard')
    elif isinstance(user, Employee):
        return reverse('employee_dashboard')
    elif isinstance(user, Admin):
        return reverse('admin_dashboard')
    else:
        return reverse('login')


@login_required
def employee_dashboard(request):
    return render(request, 'employee_dashboard.html')

@login_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')