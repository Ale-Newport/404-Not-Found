from django.shortcuts import render
from app.models import Admin, Employee, Employer, Job, User
from django.core.paginator import Paginator
from django.db.models import Q
from itertools import chain
from django.apps import apps
from app.decorators import user_type_required

@user_type_required('admin')
def dashboard(request):
    """Display the admin dashboard"""
    total_users = Admin.objects.count() + Employee.objects.count() + Employer.objects.count()
    employee_users = Employee.objects.count()
    employer_users = Employer.objects.count()
    admin_users = Admin.objects.count()
    total_jobs = Job.objects.count()

    context = {
        'total_users': total_users,
        'employee_users': employee_users,
        'employer_users': employer_users,
        'admin_users': admin_users,
        'total_jobs': total_jobs,
    }
    return render(request, 'admin/admin_dashboard.html', context)

@user_type_required('admin')
def list_users(request):
    users = User.objects.all()
    
    type_filter = request.GET.get('type')
    if type_filter:
        users = users.filter(user_type = type_filter.lower())
    
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) | 
            Q(email__icontains=search_query) | 
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query)
        )
    
    order_by = request.GET.get('order_by', 'username')
    
    paginator = Paginator(users, 25)
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)
    
    context = {
        'users_page' : users_page,
        'order_by': order_by,
        'current_type': type_filter or '',
        'current_search': search_query or '',
    }
    
    return render(request, 'admin/list_users.html', context)

@user_type_required('admin')
# In app/views/admin_views.py
def list_jobs(request):
    jobs = Job.objects.all()

    department_filter = request.GET.get('department')
    job_type_filter = request.GET.get('job_type')
    created_by_filter = request.GET.get('created_by')

    if department_filter: jobs = jobs.filter(department=department_filter)
    if job_type_filter: jobs = jobs.filter(job_type=job_type_filter)
    if created_by_filter: jobs = jobs.filter(created_by__id=created_by_filter)

    search_query = request.GET.get('search')
    if search_query: 
        # Remove the problematic created_by__username__icontains part
        jobs = jobs.filter(
            Q(name__icontains=search_query) | 
            Q(department__icontains=search_query) | 
            Q(description__icontains=search_query) | 
            Q(skills_needed__icontains=search_query) | 
            Q(skills_wanted__icontains=search_query)
        )

    order_by = request.GET.get('order_by', 'created_at')
    jobs = jobs.order_by(order_by)

    employers_with_jobs = Employer.objects.filter(user_id__in=Job.objects.all().values_list('created_by', flat=True).distinct()).order_by('company_name')
    job_types = Job.objects.all().values_list('job_type', flat=True).distinct()
    departments = Job.objects.all().values_list('department', flat=True).distinct()
    
    context = {'jobs': jobs, 'order_by': order_by, 'employers_with_jobs': employers_with_jobs, 'job_types': job_types, 'departments': departments}

    return render(request, 'admin/list_jobs.html', context)