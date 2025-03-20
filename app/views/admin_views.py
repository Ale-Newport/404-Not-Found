from django.shortcuts import render, redirect, get_object_or_404
from app.models import Admin, Employee, Employer, Job, User
from django.core.paginator import Paginator
from django.db.models import Q
from app.decorators import user_type_required
from django.contrib import messages
from app.forms.forms import UserForm

@user_type_required('admin')
def admin_dashboard(request):
    """Display the admin dashboard"""
    employee_users = Employee.objects.count()
    employer_users = Employer.objects.count()
    admin_users = Admin.objects.count()
    total_users = employee_users + employer_users + admin_users
    ft_jobs = Job.objects.filter(job_type='FT').count()
    pt_jobs = Job.objects.filter(job_type='PT').count()
    total_jobs = Job.objects.count()

    context = {
        'total_users': total_users,
        'employee_users': employee_users,
        'employer_users': employer_users,
        'admin_users': admin_users,
        'ft_jobs': ft_jobs,
        'pt_jobs': pt_jobs,
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
    users = users.order_by(order_by)
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
def list_jobs(request):
    jobs = Job.objects.all()

    job_type_filter = request.GET.get('job_type')
    created_by_filter = request.GET.get('created_by')

    if job_type_filter: jobs = jobs.filter(job_type=job_type_filter)
    if created_by_filter: jobs = jobs.filter(created_by__id=created_by_filter)

    search_query = request.GET.get('search')
    if search_query: 
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
    
    context = {'jobs': jobs, 'order_by': order_by, 'employers_with_jobs': employers_with_jobs, 'job_types': job_types}

    return render(request, 'admin/list_jobs.html', context)


@user_type_required('admin')
def create_user(request):
    """
    View for administrators to create new users of any type
    (Admin, Employee, or Employer).
    """
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_type = form.cleaned_data.get('user_type')
            user_type_display = dict(form.fields['user_type'].choices)[user_type]
            
            messages.success(
                request, 
                f'Successfully created {user_type_display} account for {user.get_full_name()} ({user.username})'
            )
            return redirect('list_users')
    else:
        form = UserForm()
    
    return render(request, 'admin/create_user.html', {
        'form': form,
        'title': 'Create New User'
    })

@user_type_required('admin')
def delete_user(request, user_id):
    """
    View for administrators to delete users.
    """
    user = get_object_or_404(User, id=user_id)
    
    # Prevent self-deletion
    if request.user.id == user_id:
        messages.error(
            request,
            'You cannot delete your own account.'
        )
        return redirect('list_users')
    
    if request.method == 'POST':
        # Confirm the user wants to delete
        username = user.username
        full_name = user.get_full_name()
        user_type_display = dict(User.USER_TYPES)[user.user_type]

        user.delete()
        
        messages.success(
            request, 
            f'Successfully deleted {user_type_display} account for {full_name} ({username})'
        )
        return redirect('list_users')
    
    return render(request, 'admin/delete_user.html', {'user': user_id})
