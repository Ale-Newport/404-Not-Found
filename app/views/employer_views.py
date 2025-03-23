from django.shortcuts import render, redirect, get_object_or_404
from app.models import Job, JobApplication, User
from app.forms.forms import JobForm, EmployerSignUpForm
from django.contrib import messages
from app.decorators import user_type_required
from app.services.job_matcher import JobMatcher
from helper import create_and_send_code_email

@user_type_required('employer')
def add_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.created_by = request.user.employer
            job.save()
            return redirect('employer_dashboard')
    else:
        form = JobForm()
    return render(request, 'job/add_job.html', {'form': form})

@user_type_required(['employer', 'employee', 'admin'])
def job_detail(request, job_id):
    if not hasattr(request.user, 'employer'):
        job = get_object_or_404(Job, id=job_id)
        has_applied = False
        if hasattr(request.user, 'employee'):
            has_applied = JobApplication.objects.filter(
                job=job, 
                applicant=request.user.employee
            ).exists()
        return render(request, 'job/job_detail.html', {
            'job': job,
            'has_applied': has_applied,
            'is_employee': True,
            'employee': request.user.employee if hasattr(request.user, 'employee') else None
        })
    
    job = get_object_or_404(Job, id=job_id, created_by=request.user.employer)
    applications = JobApplication.objects.filter(job=job)

    applications_with_scores = []
    for app in applications:
        score, matching_skills, missing_skills = JobMatcher.calculate_match_score(
            app.skills,
            job.skills_needed,
            job.skills_wanted,
            app.applicant.preferred_contract if hasattr(app, 'applicant') and app.applicant else None,
            job.job_type
        )
        
        app_data = {
            'application': app,
            'score': score,
            'matching_skills': matching_skills,
            'missing_skills': missing_skills
        }
        applications_with_scores.append(app_data)
    
    applications_with_scores.sort(key=lambda x: x['score'], reverse=True)
    
    return render(request, 'job/job_detail.html', {
        'job': job,
        'applications_with_scores': applications_with_scores,
        'is_employee': False
    })

@user_type_required('employer')
def employer_dashboard(request):
    jobs = Job.objects.filter(created_by=request.user.employer)
    return render(request, 'employer/employer_dashboard.html', {
        'jobs': jobs,
        'username': request.user.email
    })

@user_type_required('employer')
def account_page(request):
    return render(request, 'account/account_page.html', {
        'user': request.user
    })

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
