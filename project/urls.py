from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from app.views.views import employee_signup, employer_signup, home, employee_dashboard, employer_dashboard, user_login
from app.views.employer_views import add_job, job_detail, employer_dashboard, account_page


urlpatterns = [
    path('admin/', admin.site.urls),
    # Home page
    path('', home, name='home'),
    # Authentication Routes
    path('login/', user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    # Sign-up routes
    path('employee-signup/', employee_signup, name='employee_signup'),
    path('employer-signup/', employer_signup, name='employer_signup'),
    # Dashboard paths
    path('employee-dashboard/', employee_dashboard, name='employee_dashboard'),
    path('employer-dashboard/', employer_dashboard, name='employer_dashboard'),
    path('account/', account_page, name='account_page'),
    path('add-job/', add_job, name='add_job'),
    path('job/<int:job_id>/', job_detail, name='job_detail'),
]
