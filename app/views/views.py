from django.shortcuts import render, redirect
from app.forms.forms import EmployeeSignUpForm, EmployerCompanyInfoForm, EmployerSignUpForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from app.models import Employee, Employer

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
            form.save()  # Saves the new Employer user
            return redirect('login')
    else:
        form = EmployerSignUpForm()
    return render(request, 'employer_signup.html', {'form': form})

def home(request):
    return render(request, 'home.html')


def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            if isinstance(user, Employer):
                return redirect('employer_dashboard')
            elif isinstance(user, Employee):
                return redirect('employee_dashboard')
            else:
                return HttpResponse("User type is invalid")
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    else:
        return render(request, 'login.html')

@login_required
def employer_company_info(request):
    
    if not isinstance(request.user, Employer):
        return HttpResponse("Unauthorized", status=401)
    
    if request.method == 'POST':
        
        form = EmployerCompanyInfoForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('employer_dashboard')
    else:
        form = EmployerCompanyInfoForm(instance=request.user)
    return render(request, 'employer_company_info.html', {'form': form})

@login_required
def employer_dashboard(request):
    return render(request, 'employer_dashboard.html')

@login_required
def employee_dashboard(request):
    return render(request, 'employee_dashboard.html')
