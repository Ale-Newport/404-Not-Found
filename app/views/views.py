from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from app.forms.forms import EmployeeSignUpForm, EmployerSignUpForm, JobApplicationForm, LogInForm, EmployeeAccountUpdateForm, PasswordResetRequestForm, SetNewPasswordForm
from django.contrib.auth import update_session_auth_hash, login, logout
from django.contrib import messages
from app.models import JobApplication, User, Employee, Employer, Admin, Job, VerificationCode
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from app.decorators import user_type_required
from collections import defaultdict
from django.core.files.storage import default_storage
from app.helper import parse_cv, create_and_send_code_email, validate_verification_code
import os
from django.conf import settings
from project.constants import COUNTRIES


def home(request):
    return render(request, 'account/home.html')


def verify_email(request):
    if 'verification_email' not in request.session:
        return redirect('login')
        
    if request.method == 'POST':
        code = request.POST.get('code')
        email = request.session['verification_email']
        
        is_valid, user, verification = validate_verification_code(
            code, 
            email, 
            'email_verification'
        )
        
        if is_valid:
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
    
    return render(request, 'account/verify_email.html')

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
                return render(request, "employer/employer_signup.html", {"form": form})

    else:
        form = EmployerSignUpForm()
    return render(request, 'employer/employer_signup.html', {'form': form})

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
    return render(request, 'account/login.html', {'form': form})

def get_redirect(user):
    if user.user_type == 'employer':
        return reverse('employer_dashboard')
    elif user.user_type == 'employee':
        return reverse('employee_dashboard')
    elif user.user_type == 'admin':
        return reverse('admin_dashboard')
    return reverse('login')

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
                if create_and_send_code_email(
                    user, 
                    request, 
                    'password_reset', 
                    'account/password_reset_email.html', 
                    'Password Reset Verification Code'
                ):
                    return redirect('verify_reset_code')
                else:
                    messages.error(request, "Error sending email. Please try again.")
                    return render(request, 'account/password_reset.html', {'form': form})

            return redirect('verify_reset_code')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'account/password_reset.html', {'form': form})

def verify_reset_code(request):
    if 'reset_email' not in request.session:
        return redirect('password_reset')
        
    if request.method == 'POST':
        code = request.POST.get('code')
        email = request.session['reset_email']
        
        is_valid, user, verification = validate_verification_code(
            code, 
            email, 
            'password_reset'
        )
        
        if is_valid:
            verification.is_used = True
            verification.save()
            request.session['reset_code_verified'] = True
            return redirect('set_new_password')
        else:
            messages.error(request, "Invalid or expired code. Please try again.")
    
    return render(request, 'account/verify_reset_code.html')

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
    
    return render(request, 'account/set_new_password.html', {'form': form})

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
