from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from app.models import Admin, Employee, Employer, Job
from django.db.models import Q
from itertools import chain
from django.apps import apps

# Admin dashboard
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


def list_users(request):
    admins = Admin.objects.all().select_related('user')
    employees = Employee.objects.all().select_related('user')
    employers = Employer.objects.all().select_related('user')
    
    type_filter = request.GET.get('type')
    if type_filter:
        if type_filter == 'Admin':
            employees = Employee.objects.none()
            employers = Employer.objects.none()
        elif type_filter == 'Employee':
            admins = Admin.objects.none()
            employers = Employer.objects.none()
        elif type_filter == 'Employer':
            admins = Admin.objects.none()
            employees = Employee.objects.none()
    
    search_query = request.GET.get('search')
    if search_query:
        admins = admins.filter(
            Q(user__username__icontains=search_query) | 
            Q(user__email__icontains=search_query) | 
            Q(user__first_name__icontains=search_query) | 
            Q(user__last_name__icontains=search_query)
        )
        employees = employees.filter(
            Q(user__username__icontains=search_query) | 
            Q(user__email__icontains=search_query) | 
            Q(user__first_name__icontains=search_query) | 
            Q(user__last_name__icontains=search_query)
        )
        employers = employers.filter(
            Q(user__username__icontains=search_query) | 
            Q(user__email__icontains=search_query) | 
            Q(user__first_name__icontains=search_query) | 
            Q(user__last_name__icontains=search_query)
        )
    
    order_by = request.GET.get('order_by', 'user__username')
    
    field_mapping = {
        'username': 'user__username',
        '-username': '-user__username',
        'email': 'user__email',
        '-email': '-user__email',
        'first_name': 'user__first_name',
        '-first_name': '-user__first_name', 
        'last_name': 'user__last_name',
        '-last_name': '-user__last_name',
        'type': 'user__user_type',
        '-type': '-user__user_type'
    }
    
    django_order_by = field_mapping.get(order_by, 'user__username')
    
    admins = admins.order_by(django_order_by)
    employees = employees.order_by(django_order_by)
    employers = employers.order_by(django_order_by)
    
    context = {
        'admins': admins,
        'employees': employees,
        'employers': employers,
        'order_by': order_by
    }
    
    return render(request, 'admin/list_users.html', context)


# Jobs views
def list_jobs(request):
    jobs = Job.objects.all()

    # Filtering
    department_filter = request.GET.get('department')
    job_type_filter = request.GET.get('job_type')
    created_by_filter = request.GET.get('created_by')

    if department_filter: jobs = jobs.filter(department=department_filter)
    if job_type_filter: jobs = jobs.filter(job_type=job_type_filter)
    if job_type_filter: jobs = jobs.filter(created_by__id=created_by_filter)

    # Searching
    search_query = request.GET.get('search')
    if search_query: jobs = jobs.filter(Q(name__icontains=search_query) | Q(created_by__username__icontains=search_query) | Q(department__icontains=search_query) | Q(description__icontains=search_query) | Q(skills_needed__icontains=search_query) | Q(skills_wanted__icontains=search_query))

    # Ordering
    order_by = request.GET.get('order_by', 'created_at')
    jobs = jobs.order_by(order_by)

    # Get values for dropdowns
    employers_with_jobs = Employer.objects.filter(id__in=Job.objects.all().values_list('created_by', flat=True).distinct()).order_by('username')
    job_types = Job.objects.all().values_list('job_type', flat=True).distinct()
    departments = Job.objects.all().values_list('department', flat=True).distinct()
    
    context = {'jobs': jobs, 'order_by': order_by, 'employers_with_jobs': employers_with_jobs, 'job_types': job_types, 'departments': departments}

    return render(request, 'admin/list_jobs.html', context)
