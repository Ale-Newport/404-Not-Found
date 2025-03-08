# app/tests/models/test_model_methods.py
from django.test import TestCase
from app.models import User, Admin, Employee, Employer, VerificationCode, Job, JobApplication
from datetime import timedelta
from django.utils import timezone

class VerificationCodeModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="@testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            user_type="employee"
        )
        
    def test_generate_code(self):
        """Test the generate_code method"""
        code = VerificationCode.generate_code()
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())
        
    def test_is_valid_fresh_code(self):
        """Test is_valid method with fresh code"""
        code = VerificationCode.objects.create(
            user=self.user,
            code="123456",
            code_type="password_reset"
        )
        self.assertTrue(code.is_valid())
        
    def test_is_valid_used_code(self):
        """Test is_valid method with used code"""
        code = VerificationCode.objects.create(
            user=self.user,
            code="123456",
            code_type="password_reset",
            is_used=True
        )
        self.assertFalse(code.is_valid())
        
    def test_is_valid_expired_code(self):
        """Test is_valid method with expired code"""
        # Instead of creating a code with backdated created_at directly,
        # we can monkey patch timezone.now to return a different time
        from django.utils import timezone
        import datetime
        
        original_now = timezone.now
        
        try:
            # Create a code normally
            code = VerificationCode.objects.create(
                user=self.user,
                code="123456",
                code_type="password_reset"
            )
            
            # Now make timezone.now return a time that's 30 minutes ahead
            timezone.now = lambda: original_now() + datetime.timedelta(minutes=30)
            
            # Now the code should be expired (assuming 15 minute expiration)
            self.assertFalse(code.is_valid())
        finally:
            # Restore original function
            timezone.now = original_now

class UserManagerTests(TestCase):
    def test_create_user_without_email(self):
        """Test creating a user without email raises error"""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                username="@testuser",
                email="",  # Empty email
                password="testpass123"
            )
            
    def test_create_user_with_extra_fields(self):
        """Test creating a user with extra fields"""
        user = User.objects.create_user(
            username="@testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            is_staff=True,
            is_active=True
        )
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        
    def test_create_superuser_with_staff_false(self):
        """Test creating a superuser with is_staff=False raises error"""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                username="@superuser",
                email="super@example.com",
                password="testpass123",
                is_staff=False
            )
            
    def test_create_superuser_with_superuser_false(self):
        """Test creating a superuser with is_superuser=False raises error"""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                username="@superuser",
                email="super@example.com",
                password="testpass123",
                is_superuser=False
            )

class AdminModelTests(TestCase):
    def test_admin_clean_method(self):
        """Test that Admin.clean() sets is_staff and is_superuser"""
        user = User.objects.create_user(
            username="@adminuser",
            email="admin@example.com",
            password="testpass123",
            user_type="admin",
            is_staff=False,
            is_superuser=False
        )
        admin = Admin.objects.create(user=user)
        
        # Call clean method
        admin.clean()
        
        # Check that user was updated
        user.refresh_from_db()
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        
    def test_create_user_class_method(self):
        """Test Admin.create_user class method"""
        admin = Admin.create_user(
            username="@newadmin",
            email="newadmin@example.com",
            password="testpass123",
            first_name="New",
            last_name="Admin"
        )
        
        # Check that admin was created
        self.assertIsInstance(admin, Admin)
        self.assertEqual(admin.user.username, "@newadmin")
        self.assertEqual(admin.user.email, "newadmin@example.com")
        self.assertEqual(admin.user.user_type, "admin")
        self.assertTrue(admin.user.is_staff)
        self.assertTrue(admin.user.is_superuser)

class EmployeeModelTests(TestCase):
    def test_create_user_class_method(self):
        """Test Employee.create_user class method"""
        employee = Employee.create_user(
            username="@newemployee",
            email="newemployee@example.com",
            password="testpass123",
            first_name="New",
            last_name="Employee",
            country="US"
        )
        
        # Check that employee was created
        self.assertIsInstance(employee, Employee)
        self.assertEqual(employee.user.username, "@newemployee")
        self.assertEqual(employee.user.email, "newemployee@example.com")
        self.assertEqual(employee.user.user_type, "employee")
        self.assertEqual(employee.country, "US")

class EmployerModelTests(TestCase):
    def test_create_user_class_method(self):
        """Test Employer.create_user class method"""
        employer = Employer.create_user(
            username="@newemployer",
            email="newemployer@example.com",
            password="testpass123",
            first_name="New",
            last_name="Employer",
            company_name="New Company",
            country="US"
        )
        
        # Check that employer was created
        self.assertIsInstance(employer, Employer)
        self.assertEqual(employer.user.username, "@newemployer")
        self.assertEqual(employer.user.email, "newemployer@example.com")
        self.assertEqual(employer.user.user_type, "employer")
        self.assertEqual(employer.company_name, "New Company")
        self.assertEqual(employer.country, "US")