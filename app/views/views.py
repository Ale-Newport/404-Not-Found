from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from app.forms.forms import EmployeeSignUpForm, EmployerSignUpForm, JobApplicationForm, LogInForm, EmployeeAccountUpdateForm, PasswordResetRequestForm, SetNewPasswordForm
from django.contrib.auth import update_session_auth_hash, login, logout
from django.contrib import messages
from app.models import JobApplication, User, Employee, Employer, Admin, Job, VerificationCode
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect, get_object_or_404
from app.decorators import user_type_required
from collections import defaultdict
from django.core.files.storage import default_storage
from app.helper import parse_cv
import os
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def home(request):
    return render(request, 'home.html')

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

            code = VerificationCode.generate_code()
            print(f"Generated verification code: {code}")  # Debugging statement
            VerificationCode.objects.create(
                user=user,
                code=code,
                code_type='email_verification'
            )

            current_site = get_current_site(request)
            context = {
                'user': user,
                'code': code,
                'site_name': current_site.name,
            }
            email_content = render_to_string('emails/email_verification.html', context)
            
            try:
                message = Mail(
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to_emails=user.email,
                    subject='Verify your email address',
                    html_content=email_content
                )
                message.reply_to = settings.DEFAULT_FROM_EMAIL
                
                sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
                response = sg.send(message)
                
                request.session['verification_email'] = user.email
                request.session["signup_data"] = session_data
                return redirect('verify_email')
            except Exception as e:
                user.delete()
                messages.error(request, "Error sending verification email. Please try again.")
                return render(request, "employee_signup.html", {"form": form, "step": 1})
    else:
        form = EmployeeSignUpForm()
    
    return render(request, "employee_signup.html", {"form": form, "step": 1})

def verify_email(request):
    if 'verification_email' not in request.session:
        return redirect('login')
        
    if request.method == 'POST':
        code = request.POST.get('code')
        email = request.session['verification_email']
        
        user = User.objects.filter(email=email, is_active=False).first()
        if not user:
            messages.error(request, "Invalid verification attempt.")
            return redirect('login')
            
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

            signup_data = request.session.get("signup_data", {})

            if user.user_type == 'employee':
                Employee.objects.create(
                    user=user,
                    country = signup_data.get("country", "")
                )
                redirect_url = 'employee_signup_2'
            elif user.user_type == 'employer':
                Employer.objects.create(
                    user=user,
                    country=signup_data.get("country", ""),
                    company_name=signup_data.get("company_name", "")
                )
                redirect_url = 'employer_dashboard'
            else:
                #fallback in case usertype unrecognised for some reason
                redirect_url = 'home'

            request.session.pop('verification_email', None)
            request.session.pop('signup_data', None)

            login(request, user)
            messages.success(request, "Email verified successfully! Welcome abord!")
            return redirect(redirect_url)
        else:
            messages.error(request, "Invalid or expired code. Please try again.")
    
    return render(request, 'verify_email.html')


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
            print(e)
            return render(request, "employee_signup.html", {"step": 2,})
    return render(request, "employee_signup.html", {"step": 2})


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
            #store form data in session
            session_data = {
                'username': form.cleaned_data['username'],
                'email': form.cleaned_data['email'],
                'password1': form.cleaned_data['password1'],
                'company_name': form.cleaned_data.get('company_name', ''),
                'country': form.cleaned_data.get('country', ''),
            }

            #create user but set as inactive
            user = User.objects.create_user(
                username=session_data["username"],
                email=session_data["email"],
                password=session_data["password1"],
                user_type='employer',
                is_active=False  
            )

            code = VerificationCode.generate_code()
            VerificationCode.objects.create(
                user=user,
                code=code,
                code_type='email_verification'
            )

            current_site = get_current_site(request)
            context = {
                'user': user,
                'code': code,
                'site_name': current_site.name,
            }
            email_content = render_to_string('emails/email_verification.html', context)

            try:
                message = Mail(
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to_emails=user.email,
                    subject='Verify your email address',
                    html_content=email_content
                )
                message.reply_to = settings.DEFAULT_FROM_EMAIL
                
                sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
                response = sg.send(message)
                
                request.session['verification_email'] = user.email
                request.session["signup_data"] = session_data
                return redirect('verify_email')
            except Exception as e:
                user.delete()  #delete the user if email sending fails
                messages.error(request, "Error sending verification email. Please try again.")
                return render(request, "employer_signup.html", {"form": form,})

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
            messages.error(request, 'There was an error with your submission. Please check the form for details.') # pragma: no cover
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
        base_jobs_query = base_jobs_query.filter(created_by__employer__country__icontains=filters['country'])
    
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
        'filters': filters
    }
    
    return render(request, 'employee_dashboard.html', context)


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
                code = VerificationCode.generate_code()

                VerificationCode.objects.create(
                    user=user,
                    code=code,
                    code_type='password_reset'
                )
                
                current_site = get_current_site(request)
                context = {
                    'user': user,
                    'code': code,
                    'site_name': current_site.name,
                }
                
                email_content = render_to_string('emails/password_reset_email.html', context)
                
                try:
                    message = Mail(
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to_emails=user.email,
                        subject='Password Reset Verification Code',
                        html_content=email_content
                    )
                    message.reply_to = settings.DEFAULT_FROM_EMAIL
                    
                    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
                    response = sg.send(message)
                except Exception as e:
                    messages.error(request, "Error sending email. Please try again.")
                    return render(request, 'password_reset.html', {'form': form})
            
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
            
            del request.session['reset_email']
            del request.session['reset_code_verified']
            
            messages.success(request, "Your password has been changed successfully!")
            return redirect('login')
    else:
        form = SetNewPasswordForm()
    
    return render(request, 'set_new_password.html', {'form': form})


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

@user_type_required('employer')
def update_application_status(request, application_id):
    if not hasattr(request.user, 'employer'):
        messages.error(request, "Access denied.")
        return redirect('login')
        
    application = get_object_or_404(JobApplication, id=application_id)
    
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
