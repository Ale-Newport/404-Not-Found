from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from app.views.views import employee_signup, employer_signup
from app.views import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Home page
    path('', views.home, name='home'),
    # Built-in login/logout (optional)
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Sign-up routes
    path('employee_signup/', employee_signup, name='employee_signup'),
    path('employer_signup/', employer_signup, name='employer_signup'),
]
