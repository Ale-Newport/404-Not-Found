from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from app.views.views import employee_signup, employer_signup, home, employee_dashboard, employer_dashboard, user_login

urlpatterns = [
    path('admin/', admin.site.urls),
    # Home page
    path('', home, name='home'),
    # Authentication Routes
    path('login/', user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Sign-up routes
    path('employee-signup/', employee_signup, name='employee_signup'),
    path('employer-signup/', employer_signup, name='employer_signup'),
    # Dashboard paths
    path('employee-dashboard/', employee_dashboard, name='employee_dashboard'),
    path('employer-dashboard/', employer_dashboard, name='employer_dashboard'),

]
