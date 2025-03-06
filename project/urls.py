from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from app.views import views, employer_views, admin_views
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    # Home page
    path('', views.home, name='home'),
    # Authentication routes
    path('login/', views.user_login, name='login'),
    path('logout/', views.log_out, name='logout'),

    # Password reset routes
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/verify/', views.verify_reset_code, name='verify_reset_code'),
    path('password-reset/set-password/', views.set_new_password, name='set_new_password'),

    # Sign-up routes
    path('employer/signup/', views.employer_signup, name='employer_signup'),
    path('employee/signup/', views.employee_signup, name='employee_signup'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path("employee-signup/CV/", views.upload_cv, name="employee_signup_2"),
    path("employee-signup/CV/parse/", views.review_cv_data, name="employee_signup_3"),
    
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

    path('job/<int:job_id>/apply/', views.apply_to_job, name='apply_job'),
    path('application/<int:application_id>/update/', views.update_application_status, name='update_application_status'),
    path('employee/applications/', views.my_applications, name='my_applications'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
