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


