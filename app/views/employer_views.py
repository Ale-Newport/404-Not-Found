from django.shortcuts import render, redirect, get_object_or_404
from app.models import Job, JobApplication
from app.forms.forms import JobForm
from django.contrib import messages
from app.decorators import user_type_required
from app.services.job_matcher import JobMatcher

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
