from django.shortcuts import render, redirect
from django.urls import reverse
from app.forms.forms import EmployeeSignUpForm, EmployerSignUpForm, LogInForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import login, logout
from django.contrib import messages
from app.models import Employee, Employer, Admin
from django.views.decorators.csrf import csrf_protect
from django.core.files.storage import FileSystemStorage

def home(request):
    return render(request, 'home.html')

def employee_signup(request):
    if request.method == "POST":
        form = EmployeeSignUpForm(request.POST)
        if form.is_valid():
            # Store all form data in session
            session_data = {
                'username': form.cleaned_data['username'],
                'email': form.cleaned_data['email'],
                'password1': form.cleaned_data['password1'],
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'country': form.cleaned_data['country'],
            }
            request.session["signup_data"] = session_data
            return redirect("employee_signup_2")
    else:
        form = EmployeeSignUpForm()
    
    return render(request, "employee_signup.html", {"form": form, "step": 1})


def employee_signup_2(request):
    if request.method == "POST" and request.FILES.get("cv"):
        cv_file = request.FILES["cv"]
        fs = FileSystemStorage()
        filename = fs.save(cv_file.name, cv_file)  # Save file to storage
        request.session["cv_filename"] = filename  # Store file reference
        return redirect("employee_signup_3")  # Move to step 3

    return render(request, "employee_signup.html", {"step": 2})


def employee_signup_3(request):
    if request.method == "POST":
        signup_data = request.session.get("signup_data")
        
        if not signup_data:
            return redirect("employee_signup")
            
        if request.POST.get("preferred_contract") not in ['FT', 'PT']:
            return render(request, "employee_signup.html", {
                "step": 3,
                "error": "Invalid contract type"
            })
            
        try:
            employee = Employee.objects.create_user(
                username=signup_data["username"],
                email=signup_data["email"],
                password=signup_data["password1"],
                first_name=signup_data["first_name"],
                last_name=signup_data["last_name"],
                country=signup_data["country"],
            )
            
            employee.cv_filename = request.session.get("cv_filename")
            employee.skills = request.POST.get("skills", "")
            employee.interests = request.POST.get("interests", "")
            employee.preferred_contract = request.POST.get("preferred_contract")
            employee.save()
            
            request.session.pop("signup_data", None)
            request.session.pop("cv_filename", None)
            
            login(request, employee)
            return redirect("employee_dashboard")
            
        except KeyError:
            return redirect("employee_signup")

    return render(request, "employee_signup.html", {"step": 3})


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