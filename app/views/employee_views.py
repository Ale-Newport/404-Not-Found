from app.forms import EmployeeSignUpForm, EmployeeAccountUpdateForm
from app.models import User, Employee, Job, JobApplication
from app.helper import create_and_send_code_email, parse_cv
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import Q
from collections import defaultdict
from django.contrib.auth import update_session_auth_hash
from app.decorators import user_type_required
from django.core.paginator import Paginator
from project.constants import COUNTRIES


def employee_signup(request):
    if request.method == "POST":
        form = EmployeeSignUpForm(request.POST)
        if form.is_valid():
            
            session_data = {
                'username': form.cleaned_data['username'],
                'email': form.cleaned_data['email'],
                'password1': form.cleaned_data['password1'],
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'country': form.cleaned_data['country'],
            }
            
            user = User.objects.create_user(
                username=session_data["username"],
                email=session_data["email"],
                password=session_data["password1"],
                first_name=session_data["first_name"],
                last_name=session_data["last_name"],
                user_type='employee',
                is_active=False
            )
            if create_and_send_code_email(
                user, 
                request, 
                'email_verification', 
                'account/email_verification.html', 
                'Verify your email address'
            ):
                request.session["signup_data"] = session_data
                return redirect('verify_email')
            else:
                user.delete()
                messages.error(request, "Error sending verification email. Please try again.")
                return render(request, "employee/employee_signup.html", {"form": form, "step": 1})
    else:
        form = EmployeeSignUpForm()
    
    return render(request, "employee/employee_signup.html", {"form": form, "step": 1})

def upload_cv(request):
    if request.method == "POST":
        cv_file = request.FILES["cv"]
        try:
            upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            cv_filename = f"uploads/{cv_file.name}"
            file_path = default_storage.save(cv_filename, cv_file)
            request.session["cv_filename"] = file_path
            
            return redirect("employee_signup_3")
        except Exception as e:
            return render(request, "employee/employee_signup.html", {"step": 2,})
    return render(request, "employee/employee_signup.html", {"step": 2})

def review_cv_data(request):
    
    cv_filename = request.session.get("cv_filename", "")
    if cv_filename:
        try:
            file_path = os.path.join(settings.MEDIA_ROOT, cv_filename)
            cv_data = parse_cv(file_path)
        except Exception as e:
            print(f"Error parsing CV: {e}")
            cv_data = defaultdict(str)
    else:
        cv_data = defaultdict(str)

    if request.method == "POST":
        
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to complete this action.")
            return redirect("login")
            
        user = request.user
        employee, created = Employee.objects.get_or_create(user=user)

        employee.cv_filename = cv_filename
        employee.skills = request.POST.get("skills", "")
        employee.experience = request.POST.get("experience", "")
        employee.education = request.POST.get("education", "")
        employee.languages = request.POST.get("languages", "")
        employee.phone = request.POST.get("phone", "")
        employee.interests = request.POST.get("interests", "")
        employee.preferred_contract = request.POST.get("preferred_contract", "")

        employee.save()

        messages.success(request, "Profile completed")
        return redirect("employee_dashboard")

    return render(request, "employee/employee_signup.html", {"step": 3, "cv_data": cv_data})

@user_type_required('employee')
def employee_update(request):
    if request.method == 'POST':
        form = EmployeeAccountUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)

            password = form.cleaned_data.get('password1')
            if password:
                user.set_password(password)
                update_session_auth_hash(request, user)

            user.save()

            if hasattr(user, 'employee'):
                user.employee.country = form.cleaned_data['country']
                user.employee.save()
            
            messages.success(request, 'Your account details have been updated successfully.')
            return redirect('employee_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        initial_data = {}
        if hasattr(request.user, 'employee'):
            initial_data['country'] = request.user.employee.country
        
        form = EmployeeAccountUpdateForm(instance=request.user, initial=initial_data)

    context = {
        'form': form,
        'username': request.user.username
    }
    
    return render(request, 'employee/employee_update_details.html', context)

user_type_required('employee')
def employee_dashboard(request):
    if request.user.user_type != 'employee':
        messages.error(request, "Access denied. Employee access only.")
        return redirect('login')
    
    employee = Employee.objects.get(user=request.user)
    active_tab = request.GET.get('tab', 'all')
    filters = {
        'search': request.GET.get('search', ''),
        'job_type': request.GET.get('job_type', ''),
        'department': request.GET.get('department', ''),
        'country': request.GET.get('country', ''),
        'min_salary': request.GET.get('min_salary', ''),
        'tab': active_tab,
    }
    
    job_matches = None
    jobs = []
    base_jobs_query = Job.objects.all().order_by('-created_at')
    
    if filters['search']:
        base_jobs_query = base_jobs_query.filter(
            Q(name__icontains=filters['search']) |
            Q(description__icontains=filters['search']) |
            Q(department__icontains=filters['search']) |
            Q(skills_needed__icontains=filters['search'])
        )
    
    if filters['job_type'] in ['FT', 'PT']:
        base_jobs_query = base_jobs_query.filter(job_type=filters['job_type'])
    
    if filters['department']:
        base_jobs_query = base_jobs_query.filter(department__icontains=filters['department'])
    
    if filters['min_salary']:
        try:
            base_jobs_query = base_jobs_query.filter(salary__gte=float(filters['min_salary']))
        except ValueError:
            pass
    
    if filters['country']:
        country_code = filters['country'].strip()
        if country_code:
            base_jobs_query = base_jobs_query.filter(country=country_code)
    
    if active_tab == 'suitable':
        filtered_jobs = base_jobs_query
        
        from app.services.job_matcher import JobMatcher
        job_matches_list = JobMatcher.match_employee_to_jobs(employee, filtered_jobs)
        
        paginator = Paginator(job_matches_list, 10)
        page_number = request.GET.get('page')
        job_matches = paginator.get_page(page_number)
    else:
        jobs = base_jobs_query
        paginator = Paginator(jobs, 10)
        page_number = request.GET.get('page')
        jobs = paginator.get_page(page_number)
    
    context = {
        'employee': employee,
        'jobs': jobs,
        'job_matches': job_matches,
        'active_tab': active_tab,
        'filters': filters,
        'countries': COUNTRIES
    }
    
    return render(request, 'employee/employee_dashboard.html', context)

@user_type_required('employee')
def apply_to_job(request, job_id):
    if not hasattr(request.user, 'employee'):
        messages.error(request, "Only employees can apply for jobs.")
        return redirect('employee_dashboard')
        
    job = get_object_or_404(Job, id=job_id)
    
    if JobApplication.objects.filter(job=job, applicant=request.user.employee).exists():
        messages.warning(request, "You have already applied for this position.")
        return redirect('job_detail', job_id=job_id)
    
    if request.method == 'POST':
        application = JobApplication(
            job=job,
            applicant=request.user.employee,
            cover_letter=request.POST.get('cover_letter', ''),
            full_name=request.POST.get('full_name', f"{request.user.first_name} {request.user.last_name}"),
            email=request.POST.get('email', request.user.email),
            phone=request.POST.get('phone', ''),
            country=request.POST.get('country', request.user.employee.country),
            current_position=request.POST.get('current_position', ''),
            skills=request.POST.get('skills', request.user.employee.skills or ''),
            experience=request.POST.get('experience', ''),
            education=request.POST.get('education', ''),
            portfolio_url=request.POST.get('portfolio_url', ''),
            linkedin_url=request.POST.get('linkedin_url', '')
        )
        
        if 'custom_cv' in request.FILES:
            application.custom_cv = request.FILES['custom_cv']
            
        application.save()
        messages.success(request, "Your application has been submitted successfully!")
        return redirect('employee_dashboard')
        
    return redirect('job_detail', job_id=job_id)

@user_type_required('employee')
def my_applications(request):
    if not hasattr(request.user, 'employee'):
        messages.error(request, "Access denied. Employee access only.")
        return redirect('login')
    
    applications = JobApplication.objects.filter(applicant=request.user.employee).order_by('-created_at')
    
    return render(request, 'job/my_applications.html', {
        'applications': applications
    })


