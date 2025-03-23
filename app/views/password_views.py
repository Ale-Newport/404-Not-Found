from app.forms import PasswordResetRequestForm, SetNewPasswordForm
from app.models import User
from app.helper import create_and_send_code_email, validate_verification_code
from django.shortcuts import render, redirect
from django.contrib import messages

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

