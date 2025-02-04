from django.shortcuts import render, redirect
from app.forms.forms import EmployeeSignUpForm, EmployerSignUpForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from app.models import Employee, Employer
from django.views.decorators.csrf import csrf_protect
from django.core.files.storage import FileSystemStorage

def employee_signup(request):
    if request.method == "POST":
        form = EmployeeSignUpForm(request.POST)
        if form.is_valid():
            request.session["signup_data"] = request.POST  # Store in session
            return redirect("employee_signup_2")  # Move to Step 2
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
    """Step 3: Select Interests & Finalize Signup."""
    if request.method == "POST":
        interests = request.POST.getlist("interests")  # Capture selected interests
        request.session["interests"] = interests  # Store in session

        # Retrieve stored session data to create the Employee
        signup_data = request.session.get("signup_data", {})
        email = signup_data.get("email")
        password = signup_data.get("password")

        # Create Employee object (use create_user for hashed passwords)
        employee = Employee.objects.create_user(
            email=email,
            password=password,
            first_name=signup_data.get("first_name"),
            last_name=signup_data.get("last_name"),
            country=signup_data.get("country"),
        )

        # Store CV filename and interests
        employee.cv_filename = request.session.get("cv_filename")  # Associate CV
        employee.interests = ", ".join(interests)  # Store interests as string
        employee.save()

        # Log the user in and redirect
        login(request, employee)
        return redirect("employee_dashboard")

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