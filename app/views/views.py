from django.shortcuts import render, redirect
from app.forms.forms import EmployeeSignUpForm, EmployerSignUpForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from app.models import Employee, Employer
from django.views.decorators.csrf import csrf_protect


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

def home(request):
    return render(request, 'home.html')

@csrf_protect
def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            # Check if the user is an instance of our custom user models
            if isinstance(user, (Employee, Employer)):
                if isinstance(user, Employer):
                    return redirect('employer_dashboard')
                else:
                    return redirect('employee_dashboard')
            return render(request, 'login.html', {'error': 'Invalid user type'})
        return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

@login_required
def employer_dashboard(request):
    return render(request, 'employer_dashboard.html')

@login_required
def employee_dashboard(request):
    return render(request, 'employee_dashboard.html')