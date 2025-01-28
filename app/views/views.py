from django.shortcuts import render, redirect
from app.forms.forms import EmployeeSignUpForm, EmployerSignUpForm

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
