# app/tests/test_decorators.py
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.http import HttpResponse
from app.decorators import user_type_required
from app.models import User, Admin, Employee, Employer
from django.urls import reverse

class UserTypeRequiredDecoratorTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        
        # Create users
        self.admin_user = User.objects.create_user(
            username="@admintest",
            email="admin@test.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            user_type="admin"
        )
        Admin.objects.create(user=self.admin_user)
        
        self.employee_user = User.objects.create_user(
            username="@employeetest",
            email="employee@test.com",
            password="testpass123",
            first_name="Test",
            last_name="Employee",
            user_type="employee"
        )
        Employee.objects.create(user=self.employee_user)
        
        self.employer_user = User.objects.create_user(
            username="@employertest",
            email="employer@test.com",
            password="testpass123",
            first_name="Test",
            last_name="Employer",
            user_type="employer"
        )
        Employer.objects.create(user=self.employer_user)
        
        # Test view function
        @user_type_required('admin')
        def admin_view(request):
            return HttpResponse("Admin view")
            
        @user_type_required(['employer', 'admin'])
        def multi_view(request):
            return HttpResponse("Multi view")
        
        self.admin_view = admin_view
        self.multi_view = multi_view
        
    def add_middleware(self, request):
        """Add session and message middleware to request"""
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        
        middleware = MessageMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        
        return request
        
    def test_admin_only_view_with_admin(self):
        """Test admin-only view with admin user"""
        request = self.factory.get('/admin-view/')
        request.user = self.admin_user
        request = self.add_middleware(request)
        
        response = self.admin_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Admin view")
        
    def test_admin_only_view_with_employee(self):
        """Test admin-only view with employee user (should redirect)"""
        request = self.factory.get('/admin-view/')
        request.user = self.employee_user
        request = self.add_middleware(request)
        
        response = self.admin_view(request)
        self.assertEqual(response.status_code, 302)  # Should redirect
        
    def test_multi_type_view_with_admin(self):
        """Test multi-type view with admin user"""
        request = self.factory.get('/multi-view/')
        request.user = self.admin_user
        request = self.add_middleware(request)
        
        response = self.multi_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Multi view")
        
    def test_multi_type_view_with_employer(self):
        """Test multi-type view with employer user"""
        request = self.factory.get('/multi-view/')
        request.user = self.employer_user
        request = self.add_middleware(request)
        
        response = self.multi_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Multi view")
        
    def test_multi_type_view_with_employee(self):
        """Test multi-type view with employee user (should redirect)"""
        request = self.factory.get('/multi-view/')
        request.user = self.employee_user
        request = self.add_middleware(request)
        
        response = self.multi_view(request)
        self.assertEqual(response.status_code, 302)  # Should redirect
        
    def test_decorator_without_login(self):
        """Test decorator with anonymous user (should redirect to login)"""
        request = self.factory.get('/admin-view/')
        request.user = AnonymousUser()
        request = self.add_middleware(request)
        
        response = self.admin_view(request)
        self.assertEqual(response.status_code, 302)  # Should redirect to login

    # app/tests/views/test_more_decorators.py
    def test_invalid_user_access(self):
        """Test handling users with invalid user_type"""
        # Create user with invalid type
        invalid_user = User.objects.create_user(
            username="@invalidtype",
            email="invalid@example.com",
            password="testpass123",
            user_type="invalid_type"  # Not a standard type
        )
        
        # Create view that requires specific user type
        @user_type_required('admin')
        def admin_view(request):
            return HttpResponse("Admin view")
        
        # Try to access with invalid user type
        request = self.factory.get('/admin-view/')
        request.user = invalid_user
        request = self.add_middleware(request)
        
        response = admin_view(request)
        
        # Should redirect with access denied
        self.assertEqual(response.status_code, 302)