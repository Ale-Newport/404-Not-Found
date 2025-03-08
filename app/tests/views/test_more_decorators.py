# app/tests/test_more_decorators.py
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from app.decorators import user_type_required
from app.models import User, Admin, Employee, Employer
from django.http import HttpResponse

class MoreDecoratorTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        
        # Create different user types
        self.admin_user = User.objects.create_user(
            username="@adminuser",
            email="admin@test.com",
            password="testpass123",
            user_type="admin"
        )
        Admin.objects.create(user=self.admin_user)
        
        self.employee_user = User.objects.create_user(
            username="@employeeuser", 
            email="employee@test.com",
            password="testpass123",
            user_type="employee"
        )
        Employee.objects.create(user=self.employee_user)
        
        # Create test views
        @user_type_required(['admin', 'employee'])
        def multi_type_view(request):
            return HttpResponse("Multi-type view")
            
        self.multi_type_view = multi_type_view
        
    def add_middleware(self, request):
        """Add session and message middleware to request"""
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        
        middleware = MessageMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        
        return request
        
    def test_decorator_with_anonymous_user(self):
        """Test decorator with an anonymous user"""
        request = self.factory.get('/test-view/')
        request.user = AnonymousUser()
        request = self.add_middleware(request)
        
        response = self.multi_type_view(request)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/login/' in response.url)

    # app/tests/views/test_more_decorators.py
    def test_decorator_with_wrong_user_type(self):
        """Test decorator with user having the wrong type"""
        # Create a view that only accepts employers
        @user_type_required('employer')
        def employer_only_view(request):
            return HttpResponse("Employer only")
        
        # Try to access with an employee
        request = self.factory.get('/employer-view/')
        request.user = self.employee_user
        request = self.add_middleware(request)
        
        response = employer_only_view(request)
        
        # Should redirect with access denied
        self.assertEqual(response.status_code, 302)

    # app/tests/views/test_more_decorators.py
    def test_decorator_with_string_allowed_types(self):
        """Test decorator with string allowed_types when user doesn't match"""
        # Create a view that requires admin user type
        @user_type_required('admin')
        def admin_only_view(request):
            return HttpResponse("Admin only view")
        
        # Try to access with employee
        request = self.factory.get('/admin-view/')
        request.user = self.employee_user
        request = self.add_middleware(request)
        
        response = admin_only_view(request)
        
        # Should redirect with access denied
        self.assertEqual(response.status_code, 302)
        
        # Test with non-standard user type
        @user_type_required('custom_type')
        def custom_type_view(request):
            return HttpResponse("Custom type view")
        
        response = custom_type_view(request)
        self.assertEqual(response.status_code, 302)

    # app/tests/views/test_more_decorators.py
    def test_invalid_user_type(self):
        """Test with a user having an invalid/unknown user_type"""
        # Create a user with invalid type
        invalid_user = User.objects.create_user(
            username="@invaliduser",
            email="invalid@test.com",
            password="testpass123",
            user_type="unknown_type"  # This type doesn't match any defined types
        )
        
        # Create a view that requires specific user type
        @user_type_required('admin')
        def admin_only_view(request):
            return HttpResponse("Admin only view")
        
        # Try to access with invalid user type
        request = self.factory.get('/admin-view/')
        request.user = invalid_user
        request = self.add_middleware(request)
        
        response = admin_only_view(request)
        
        # Should redirect with generic access denied
        self.assertEqual(response.status_code, 302)

    # app/tests/views/test_more_decorators.py
    def test_allowed_types_string_matching(self):
        """Test when allowed_types is a string and it matches the user's type"""
        # Create a view that requires employee type
        @user_type_required('employee')
        def employee_view(request):
            return HttpResponse("Employee view")
        
        # Access with employee user
        request = self.factory.get('/employee-view/')
        request.user = self.employee_user
        request = self.add_middleware(request)
        
        response = employee_view(request)
        
        # Should allow access (no redirect)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Employee view")