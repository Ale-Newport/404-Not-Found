from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from app.models import Job
from app.forms.forms import JobForm


@login_required
def add_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.created_by = request.user
            job.save()
            return redirect('employer_dashboard')
    else:
        form = JobForm()
    return render(request, 'add_job.html', {'form': form})

@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id, created_by=request.user)
    return render(request, 'job_detail.html', {
        'job': job,
        'applicants': []  # We'll implement this later
    })

@login_required
def employer_dashboard(request):
    jobs = Job.objects.filter(created_by=request.user)
    return render(request, 'employer_dashboard.html', {
        'jobs': jobs,
        'username': request.user.email
    })

@login_required
def account_page(request):
    return render(request, 'account_page.html', {
        'user': request.user
    })