from django.shortcuts import render, redirect
from django.urls import reverse
from app.forms.forms import EmployeeSignUpForm, EmployerSignUpForm, LogInForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import login, logout
from django.contrib import messages
from app.models import User, Employee, Employer, Admin, Job
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator

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
            #create user first
            user = User.objects.create_user(
                username=signup_data["username"],
                email=signup_data["email"],
                password=signup_data["password1"],
                first_name=signup_data["first_name"],
                last_name=signup_data["last_name"],
                user_type='employee',
            )
            
            #then link to employee
            employee = Employee.objects.create(
                user=user,
                country=signup_data["country"],
                cv_filename=request.session.get("cv_filename"),
                skills=request.POST.get("skills", ""),
                interests=request.POST.get("interests", ""),
                preferred_contract=request.POST.get("preferred_contract")
            )
            
            request.session.pop("signup_data", None)
            request.session.pop("cv_filename", None)
            
            login(request, user)
            return redirect("employee_dashboard")
            
        except KeyError:
            return redirect("employee_signup")

    return render(request, "employee_signup.html", {"step": 3})


def employer_signup(request):
    if request.method == 'POST':
        form = EmployerSignUpForm(request.POST)
        if form.is_valid():
            #create user
            user = form.save(commit=False)
            user.user_type = 'employer'
            user.save()

            #link to employer
            Employer.objects.create(
                user=user,
                country=form.cleaned_data.get('country', ''),
                company_name=form.cleaned_data.get('company_name', '')
            )

            return redirect('login')
    else:
        form = EmployerSignUpForm()
    return render(request, 'employer_signup.html', {'form': form})

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
            messages.error(request, 'There was an error with your submission. Please check the form for details.')
    else:
        form = LogInForm()
    return render(request, 'login.html', {'form': form})

def get_redirect(user):
    if user.user_type == 'employer':
        return reverse('employer_dashboard')
    elif user.user_type == 'employee':
        return reverse('employee_dashboard')
    elif user.user_type == 'admin':
        return reverse('admin_dashboard')
    return reverse('login')


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from app.models import Job, Employee

@login_required
def employee_dashboard(request):
    if request.user.user_type != 'employee':
        messages.error(request, "Access denied. Employee access only.")
        return redirect('login')
        
    # Get the employee profile
    employee = Employee.objects.get(user=request.user)
    
    # Determine active tab
    active_tab = request.GET.get('tab', 'all')
    
    # Only query jobs if we're on the 'all' tab
    jobs = []
    if active_tab == 'all':
        # Build the job query
        jobs = Job.objects.all().order_by('-created_at')
        
        # Apply filters
        if 'search' in request.GET:
            search_query = request.GET.get('search')
            if search_query:
                jobs = jobs.filter(
                    Q(name__icontains=search_query) |
                    Q(description__icontains=search_query) |
                    Q(department__icontains=search_query) |
                    Q(skills_needed__icontains=search_query)
                )
                
        if 'job_type' in request.GET:
            job_type = request.GET.get('job_type')
            if job_type in ['FT', 'PT']:
                jobs = jobs.filter(job_type=job_type)
                
        if 'department' in request.GET:
            department = request.GET.get('department')
            if department:
                jobs = jobs.filter(department__icontains=department)
                
        if 'min_salary' in request.GET:
            min_salary = request.GET.get('min_salary')
            if min_salary:
                try:
                    jobs = jobs.filter(salary__gte=float(min_salary))
                except ValueError:
                    pass
                    
        if 'country' in request.GET:
            country = request.GET.get('country')
            if country:
                jobs = jobs.filter(created_by__employer__country__icontains=country)
        
        # Pagination
        paginator = Paginator(jobs, 10)  # 10 jobs per page
        page_number = request.GET.get('page')
        jobs = paginator.get_page(page_number)
    
    context = {
        'employee': employee,
        'jobs': jobs,
        'active_tab': active_tab,
        # Preserve filter values for form
        'filters': {
            'search': request.GET.get('search', ''),
            'job_type': request.GET.get('job_type', ''),
            'department': request.GET.get('department', ''),
            'country': request.GET.get('country', ''),
            'min_salary': request.GET.get('min_salary', ''),
            'tab': active_tab,  # Include tab in filters to preserve it during pagination
        }
    }
    
    return render(request, 'employee_dashboard.html', context)
@login_required
def admin_dashboard(request):
    if request.user.user_type != 'admin':
        messages.error(request, "Access denied. Admin access only.")
        return redirect('login')
    return render(request, 'admin_dashboard.html')

def log_out(request):
    """Log out the current user"""
    logout(request)
    return redirect('home')
