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
        
        @user_type_required('admin')
        def admin_view(request):
            return HttpResponse("Admin view")
            
        @user_type_required(['employer', 'admin'])
        def multi_view(request):
            return HttpResponse("Multi view")
        
        @user_type_required(['admin', 'employee'])
        def multi_type_view(request):
            return HttpResponse("Multi-type view")
            
        self.multi_type_view = multi_type_view
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
        self.assertEqual(response.status_code, 302)
        
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
        self.assertEqual(response.status_code, 302)
        
    def test_decorator_without_login(self):
        """Test decorator with anonymous user (should redirect to login)"""
        request = self.factory.get('/admin-view/')
        request.user = AnonymousUser()
        request = self.add_middleware(request)
        
        response = self.admin_view(request)
        self.assertEqual(response.status_code, 302)
    
    def test_invalid_user_access(self):
        """Test handling users with invalid user_type"""
        invalid_user = User.objects.create_user(
            username="@invalidtype",
            email="invalid@example.com",
            password="testpass123",
            user_type="invalid_type"
        )
        
        @user_type_required('admin')
        def admin_view(request):
            return HttpResponse("Admin view")
        
        request = self.factory.get('/admin-view/')
        request.user = invalid_user
        request = self.add_middleware(request)
        
        response = admin_view(request)
        
        self.assertEqual(response.status_code, 302)
    
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
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/login/' in response.url)

    def test_decorator_with_wrong_user_type(self):
        """Test decorator with user having the wrong type"""

        @user_type_required('employer')
        def employer_only_view(request):
            return HttpResponse("Employer only")
        
        request = self.factory.get('/employer-view/')
        request.user = self.employee_user
        request = self.add_middleware(request)
        response = employer_only_view(request)
        
        self.assertEqual(response.status_code, 302)

    def test_decorator_with_string_allowed_types(self):
        """Test decorator with string allowed_types when user doesn't match"""
        
        @user_type_required('admin')
        def admin_only_view(request):
            return HttpResponse("Admin only view")
        
        request = self.factory.get('/admin-view/')
        request.user = self.employee_user
        request = self.add_middleware(request)
        
        response = admin_only_view(request)
        
        self.assertEqual(response.status_code, 302)
        
        @user_type_required('custom_type')
        def custom_type_view(request):
            return HttpResponse("Custom type view")
        
        response = custom_type_view(request)
        self.assertEqual(response.status_code, 302)

    def test_invalid_user_type(self):
        """Test with a user having an invalid/unknown user_type"""

        invalid_user = User.objects.create_user(
            username="@invaliduser",
            email="invalid@test.com",
            password="testpass123",
            user_type="unknown_type"
        )
        
        @user_type_required('admin')
        def admin_only_view(request):
            return HttpResponse("Admin only view")
        
        request = self.factory.get('/admin-view/')
        request.user = invalid_user
        request = self.add_middleware(request)
        
        response = admin_only_view(request)
        
        self.assertEqual(response.status_code, 302)

    def test_allowed_types_string_matching(self):
        """Test when allowed_types is a string and it matches the user's type"""

        @user_type_required('employee')
        def employee_view(request):
            return HttpResponse("Employee view")
        
        request = self.factory.get('/employee-view/')
        request.user = self.employee_user
        request = self.add_middleware(request)
        
        response = employee_view(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Employee view")

    def test_invalid_user_access(self):
        """Test handling users with invalid user_type"""
        invalid_user = User.objects.create_user(
            username="@invalidtype",
            email="invalid@example.com",
            password="testpass123",
            user_type="invalid_type"
        )
        
        @user_type_required('admin')
        def admin_view(request):
            return HttpResponse("Admin view")
        
        request = self.factory.get('/admin-view/')
        request.user = invalid_user
        request = self.add_middleware(request)
        
        response = admin_view(request)
        
        self.assertEqual(response.status_code, 302)
