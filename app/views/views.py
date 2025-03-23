from django.shortcuts import render, redirect
from django.urls import reverse
from app.forms.forms import LogInForm, PasswordResetRequestForm, SetNewPasswordForm
from django.contrib.auth import login, logout
from django.contrib import messages
from app.models import User, Employee, Employer
from django.shortcuts import render, redirect
from app.helper import create_and_send_code_email, validate_verification_code


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
