from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from app.views import views, employer_views, admin_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Home page
    path('', views.home, name='home'),
    # Authentication routes
    path('login/', views.user_login, name='login'),
    path('logout/', views.log_out, name='logout'),
    # Sign-up routes
    path('employee/signup/', views.employee_signup, name='employee_signup'),
    path("employee-signup/step2/", views.employee_signup_2, name="employee_signup_2"),
    path("employee-signup/step3/", views.employee_signup_3, name="employee_signup_3"),
    path('employer/signup/', views.employer_signup, name='employer_signup'),
    # Employee routes
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
     path('employee/update/', views.employee_update, name='employee_update'),
    # Employer routes
    path('employer/dashboard/', employer_views.employer_dashboard, name='employer_dashboard'),
    path('account/', employer_views.account_page, name='account_page'),
    path('add-job/', employer_views.add_job, name='add_job'),
    path('job/<int:job_id>/', employer_views.job_detail, name='job_detail'),
    # Admin routes
    path('administrator/dashboard/', admin_views.dashboard, name='admin_dashboard'),
    path('administrator/list-users/', admin_views.list_users, name='list_users'),
    path('administrator/list-jobs/', admin_views.list_jobs, name='list_jobs'),

]
