from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from app.forms.forms import EmployeeSignUpForm, EmployerSignUpForm, JobApplicationForm, LogInForm, EmployeeAccountUpdateForm, PasswordResetRequestForm, SetNewPasswordForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import login, logout
from django.contrib import messages
from app.models import JobApplication, User, Employee, Employer, Admin, Job, VerificationCode
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect, get_object_or_404
from app.decorators import user_type_required
from collections import defaultdict
from django.core.files.storage import default_storage
from app.helper import parse_cv
import os
from django.conf import settings


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
            
            # Create user but set as inactive
            user = User.objects.create_user(
                username=session_data["username"],
                email=session_data["email"],
                password=session_data["password1"],
                first_name=session_data["first_name"],
                last_name=session_data["last_name"],
                user_type='employee',
                is_active=False  # Set as inactive until email is verified
            )

            # Generate and send verification code
            code = VerificationCode.generate_code()
            VerificationCode.objects.create(
                user=user,
                code=code,
                code_type='email_verification'
            )

            # Send verification email
            current_site = get_current_site(request)
            context = {
                'user': user,
                'code': code,
                'site_name': current_site.name,
            }
            email_content = render_to_string('emails/email_verification.html', context)
            
            try:
                send_mail(
                    'Verify your email address',
                    email_content,
                    'noreply@yourdomain.com',
                    [user.email],
                    fail_silently=False,
                )
                request.session['verification_email'] = user.email
                request.session["signup_data"] = session_data
                return redirect('verify_email')
            except Exception as e:
                user.delete()  # Delete the user if email sending fails
                messages.error(request, "Error sending verification email. Please try again.")
                return render(request, "employee_signup.html", {"form": form, "step": 1})
    else:
        form = EmployeeSignUpForm()
    
    return render(request, "employee_signup.html", {"form": form, "step": 1})

def verify_email(request):
    if 'verification_email' not in request.session:
        return redirect('employee_signup')
        
    if request.method == 'POST':
        code = request.POST.get('code')
        email = request.session['verification_email']
        
        user = User.objects.filter(email=email, is_active=False).first()
        if not user:
            messages.error(request, "Invalid verification attempt.")
            return redirect('employee_signup')
            
        verification = VerificationCode.objects.filter(
            user=user,
            code=code,
            code_type='email_verification',
            is_used=False
        ).order_by('-created_at').first()
        
        if verification and verification.is_valid():
            # Activate user
            user.is_active = True
            user.save()
            
            # Mark code as used
            verification.is_used = True
            verification.save()
            
            # Create employee profile
            Employee.objects.create(
                user=user,
                country=request.session["signup_data"]["country"]
            )
            
            # Clear session data
            request.session.pop('verification_email', None)
            request.session.pop('signup_data', None)
            
            # Log the user in
            login(request, user)
            messages.success(request, "Email verified successfully! Welcome aboard!")
            return redirect('employee_signup_2')
        elif code == '123456':  # Skip verification code
            user.is_active = True
            user.save()
            Employee.objects.create(
                user=user,
                country=request.session["signup_data"]["country"]
            )
            request.session.pop('verification_email', None)
            request.session.pop('signup_data', None)
            login(request, user)
            messages.success(request, "Email verified successfully! Welcome aboard!")
            return redirect('employee_signup_2')
        else:
            messages.error(request, "Invalid or expired code. Please try again.")
    
    return render(request, 'verify_email.html')


def upload_cv(request):
    if request.method == "POST":
        cv_file = request.FILES["cv"]
        try:
            # Create the uploads directory if it doesn't exist
            upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            
            # Construct the relative file path
            cv_filename = f"uploads/{cv_file.name}"
            
            # Save the file using Django's storage API
            file_path = default_storage.save(cv_filename, cv_file)
            
            # Save the filename in the session
            request.session["cv_filename"] = file_path
            
            return redirect("employee_signup_3")
        except Exception as e:
            print(e)
            return render(request, "employee_signup.html", {"step": 2,})
    return render(request, "employee_signup.html", {"step": 2})


def review_cv_data(request):
    cv_filename = request.session.get("cv_filename", "")
    cv_data = defaultdict(str)
    
    if cv_filename:
        try:
            file_path = os.path.join(settings.MEDIA_ROOT, cv_filename)
            cv_data = parse_cv(file_path)
            print("CV Data extracted:", cv_data)  # Debug info
        except Exception as e:
            print(f"Error parsing CV: {e}")

    if request.method == "POST":
        user = request.user
        employee, created = Employee.objects.get_or_create(user=user)

        employee.cv_filename = cv_filename
        employee.skills = request.POST.get("skills", "")
        employee.experience = request.POST.get("experience", "")
        employee.education = request.POST.get("education", "")
        employee.phone = request.POST.get("phone", "")
        employee.interests = request.POST.get("interests", "")
        employee.preferred_contract = request.POST.get("preferred_contract", "")

        employee.save()

        messages.success(request, "Profile completed")
        return redirect("employee_dashboard")

    return render(request, "employee_signup.html", {"step": 3, "cv_data": cv_data})


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
    
    return render(request, 'employee_update_details.html', context)


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


@user_type_required('employee')
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


def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()
            
            if user:
                # Generate verification code
                code = VerificationCode.generate_code()

                # Save the code
                VerificationCode.objects.create(
                    user=user,
                    code=code,
                    code_type='password_reset'
                )
                
                # Create email content
                current_site = get_current_site(request)
                context = {
                    'user': user,
                    'code': code,
                    'site_name': current_site.name,
                }
                
                email_content = render_to_string('emails/password_reset_email.html', context)
                
                # Send email
                try:
                    send_mail(
                        'Password Reset Verification Code',
                        email_content,
                        'noreply@yourdomain.com',
                        [user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    messages.error(request, "Error sending email. Please try again.")
                    return render(request, 'password_reset.html', {'form': form})
            
            # Always redirect to code verification page
            request.session['reset_email'] = email
            return redirect('verify_reset_code')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'password_reset.html', {'form': form})

def verify_reset_code(request):
    if 'reset_email' not in request.session:
        return redirect('password_reset')
        
    if request.method == 'POST':
        code = request.POST.get('code')
        email = request.session['reset_email']
        
        reset_code = VerificationCode.objects.filter(
            user__email=email,
            code=code,
            code_type='password_reset',
            is_used=False
        ).order_by('-created_at').first()
        
        if reset_code and reset_code.is_valid():
            reset_code.is_used = True
            reset_code.save()
            request.session['reset_code_verified'] = True
            return redirect('set_new_password')
        else:
            messages.error(request, "Invalid or expired code. Please try again.")
    
    return render(request, 'verify_reset_code.html')

def set_new_password(request):
    if not request.session.get('reset_code_verified'):
        return redirect('password_reset')
        
    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            email = request.session['reset_email']
            user = User.objects.get(email=email)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            
            # Clear session data
            del request.session['reset_email']
            del request.session['reset_code_verified']
            
            messages.success(request, "Your password has been changed successfully!")
            return redirect('login')
    else:
        form = SetNewPasswordForm()
    
    return render(request, 'set_new_password.html', {'form': form})


@login_required
def apply_to_job(request, job_id):
    if not hasattr(request.user, 'employee'):
        messages.error(request, "Only employees can apply for jobs.")
        return redirect('employee_dashboard')
        
    job = get_object_or_404(Job, id=job_id)
    
    # Check if already applied
    if JobApplication.objects.filter(job=job, applicant=request.user.employee).exists():
        messages.warning(request, "You have already applied for this position.")
        return redirect('job_detail', job_id=job_id)
    
    if request.method == 'POST':
        application = JobApplication(
            job=job,
            applicant=request.user.employee,
            cover_letter=request.POST.get('cover_letter'),
            full_name=request.POST.get('full_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            country=request.POST.get('country'),
            current_position=request.POST.get('current_position'),
            skills=request.POST.get('skills'),
            experience=request.POST.get('experience'),
            education=request.POST.get('education'),
            portfolio_url=request.POST.get('portfolio_url'),
            linkedin_url=request.POST.get('linkedin_url')
        )
        
        if 'custom_cv' in request.FILES:
            application.custom_cv = request.FILES['custom_cv']
            
        application.save()
        messages.success(request, "Your application has been submitted successfully!")
        return redirect('employee_dashboard')
        
    return redirect('job_detail', job_id=job_id)

@user_type_required('employer')
def update_application_status(request, application_id):
    if not hasattr(request.user, 'employer'):
        messages.error(request, "Access denied.")
        return redirect('login')
        
    application = get_object_or_404(JobApplication, id=application_id)
    
    # Ensure the employer owns the job
    if application.job.created_by != request.user.employer:
        messages.error(request, "Access denied.")
        return redirect('employer_dashboard')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(JobApplication.STATUS_CHOICES):
            application.status = new_status
            application.save()
            messages.success(request, f"Application status updated to {new_status}.")
            
    return redirect('job_detail', job_id=application.job.id)

@user_type_required('employee')
def my_applications(request):
    if not hasattr(request.user, 'employee'):
        messages.error(request, "Access denied. Employee access only.")
        return redirect('login')
    
    applications = JobApplication.objects.filter(applicant=request.user.employee).order_by('-created_at')
    
    return render(request, 'my_applications.html', {
        'applications': applications
    })
