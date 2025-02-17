from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from app.models import Job, JobApplication
from app.forms.forms import JobForm
from django.contrib import messages


@login_required
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
    return render(request, 'add_job.html', {'form': form})

# In employer_views.py
@login_required
def job_detail(request, job_id):
    if not hasattr(request.user, 'employer'):
        # If user is an employee, show the job application view
        job = get_object_or_404(Job, id=job_id)
        has_applied = False
        if hasattr(request.user, 'employee'):
            has_applied = JobApplication.objects.filter(
                job=job, 
                applicant=request.user.employee
            ).exists()
        return render(request, 'job_detail.html', {
            'job': job,
            'has_applied': has_applied,
            'is_employee': True,
            'employee': request.user.employee if hasattr(request.user, 'employee') else None
        })
    
    # Employer view
    job = get_object_or_404(Job, id=job_id, created_by=request.user.employer)
    applications = JobApplication.objects.filter(job=job)  # Ensure applications are queried
    
    return render(request, 'job_detail.html', {
        'job': job,
        'applications': applications,
        'is_employee': False
    })

@login_required
def employer_dashboard(request):
    if request.user.user_type != 'employer':
        messages.error(request, "Access denied. Employer access only.")
        return redirect('login')
    jobs = Job.objects.filter(created_by=request.user.employer)
    return render(request, 'employer_dashboard.html', {
        'jobs': jobs,
        'username': request.user.email
    })

@login_required
def account_page(request):
    return render(request, 'account_page.html', {
        'user': request.user
    })

@login_required
def job_detail(request, job_id):
    if not hasattr(request.user, 'employer'):
        # If user is an employee, show the job application view
        job = get_object_or_404(Job, id=job_id)
        has_applied = False
        if hasattr(request.user, 'employee'):
            has_applied = JobApplication.objects.filter(
                job=job, 
                applicant=request.user.employee
            ).exists()
        return render(request, 'job_detail.html', {
            'job': job,
            'has_applied': has_applied,
            'is_employee': True
        })
    
    # Employer view
    job = get_object_or_404(Job, id=job_id, created_by=request.user.employer)
    applications = job.applications.all()
    
    return render(request, 'job_detail.html', {
        'job': job,
        'applications': applications,
        'is_employee': False
    })