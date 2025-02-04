from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from app.views import views, employer_views


urlpatterns = [
    path('admin/', admin.site.urls),
    # Home page
    path('', views.home, name='home'),
    # Authentication Routes
    path('login/', views.user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    # Sign-up routes
    path('employee-signup/', views.employee_signup, name='employee_signup'),
    path('employer-signup/', views.employer_signup, name='employer_signup'),
    # Dashboard paths
    path('employee-dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('employer-dashboard/', employer_views.employer_dashboard, name='employer_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='employer_admin'),
    path('account/', employer_views.account_page, name='account_page'),
    path('add-job/', employer_views.add_job, name='add_job'),
    path('job/<int:job_id>/', employer_views.job_detail, name='job_detail'),
]
