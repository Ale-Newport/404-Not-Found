from django.shortcuts import render, redirect
from app.models import Employee, Employer
from app.helper import validate_verification_code
from django.contrib.auth import login
from django.contrib import messages

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
