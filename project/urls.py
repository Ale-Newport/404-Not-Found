from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from app.views import (
    base_views,
    auth_views,
    password_views,
    employee_views,
    employer_views,
    admin_views,
    verification_views,
)

urlpatterns = [
    # Django Admin routes
    path('admin/', admin.site.urls),
    # Home page
    path('', base_views.home, name='home'),
    # Authentication routes
    path('login/', auth_views.user_login, name='login'),
    path('logout/', auth_views.log_out, name='logout'),
    # Password reset routes
    path('password-reset/', password_views.password_reset_request, name='password_reset'),
    path('password-reset/verify/', password_views.verify_reset_code, name='verify_reset_code'),
    path('password-reset/set-password/', password_views.set_new_password, name='set_new_password'),
    # Sign-up routes
    path('employer/signup/', employer_views.employer_signup, name='employer_signup'),
    path('employee/signup/', employee_views.employee_signup, name='employee_signup'),
    path('verify-email/', verification_views.verify_email, name='verify_email'),
    path("employee-signup/CV/", employee_views.upload_cv, name="employee_signup_2"),
    path("employee-signup/CV/parse/", employee_views.review_cv_data, name="employee_signup_3"),
    # Employee routes
    path('employee/dashboard/', employee_views.employee_dashboard, name='employee_dashboard'),
    path('employee/update/', employee_views.employee_update, name='employee_update'),
    path('employee/job/<int:job_id>/apply/', employee_views.apply_to_job, name='apply_job'),
    path('employee/applications/', employee_views.my_applications, name='my_applications'),
    # Employer routes
    path('employer/dashboard/', employer_views.employer_dashboard, name='employer_dashboard'),
    path('employer/account/', employer_views.account_page, name='account_page'),
    path('employer/add-job/', employer_views.add_job, name='add_job'),
    path('employer/job/<int:job_id>/', employer_views.job_detail, name='job_detail'),
    path('employer/update-application/<int:application_id>/', employer_views.update_application_status, name='update_application_status'),
    # Admin routes
    path('administrator/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('administrator/list-users/', admin_views.list_users, name='list_users'),
    path('administrator/list-jobs/', admin_views.list_jobs, name='list_jobs'),
    path('administrator/create-user/', admin_views.create_user, name='create_user'),
    path('administrator/delete-user/<int:user_id>/', admin_views.delete_user, name='delete_user'),
    path('administrator/create-job/', admin_views.create_job, name='create_job'),
    path('administrator/delete-job/<int:job_id>/', admin_views.delete_job, name='delete_job'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
