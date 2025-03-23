from .admin_views import admin_dashboard, list_users, list_jobs, create_user, delete_job, delete_user, create_job
from .auth_views import user_login, get_redirect, log_out
from .base_views import home
from .employee_views import employee_signup, upload_cv, review_cv_data, employee_update, employee_dashboard, apply_to_job, my_applications
from .employer_views import add_job, job_detail, employer_dashboard, account_page, update_application_status, employer_signup
from .password_views import password_reset_request, verify_reset_code, set_new_password
from .verification_views import verify_email
