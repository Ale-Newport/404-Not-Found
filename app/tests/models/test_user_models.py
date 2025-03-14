from django.test import TestCase
from app.models import User, Admin, Employee, Employer
from django.core.exceptions import ValidationError

class UserCreationTest(TestCase):
    def setUp(self):
        admin_user = User.objects.create_user(
            username="@admin",
            email="admin@example.com",
            password="testpassword123",
            first_name="Admin",
            last_name="User",
            user_type="admin",
            is_staff=True,
            is_superuser=True
        )
        self.admin = Admin.objects.create(user=admin_user)
        
        employee_user = User.objects.create_user(
            username="@employee",
            email="employee1@example.com",
            password="testpassword123",
            first_name="Test",  
            last_name="Employee",
            user_type="employee"
        )
        self.employee = Employee.objects.create(
            user=employee_user,
            country="US"
        )
        
        employer_user = User.objects.create_user(
            username="@employer",
            email="employer1@example.com",
            password="testpassword123",
            first_name="Test", 
            last_name="Employer",
            user_type="employer"
        )
        self.employer = Employer.objects.create(
            user=employer_user,
            company_name="Company1",
            country="UK"
        )

    def test_user_str_representation(self):
        expected_employee_str = f"{self.employee.user.username} (Employee)"
        expected_employer_str = f"{self.employer.user.username} (Employer) - {self.employer.company_name}"
        self.assertEqual(str(self.employee), expected_employee_str)
        self.assertEqual(str(self.employer), expected_employer_str)

    def test_admin_creation(self):
        self.assertEqual(self.admin.user.email, "admin@example.com")
        self.assertTrue(self.admin.user.is_staff)
        self.assertTrue(self.admin.user.is_superuser)

    def test_employer_creation(self):
        self.assertEqual(self.employer.user.email, "employer1@example.com")
        self.assertEqual(self.employer.company_name, "Company1")
        self.assertTrue(self.employer.user.is_active)

    def test_employee_creation(self):
        self.assertEqual(self.employee.user.email, "employee1@example.com")
        self.assertEqual(self.employee.user.first_name, "Test")
        self.assertEqual(self.employee.user.last_name, "Employee")
        self.assertTrue(self.employee.user.is_active)

    def test_superuser_creation(self):
        superuser = User.objects.create_superuser(
            username="@superadmin",
            email="superadmin@example.com", 
            password="adminpassword"
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_superuser_invalid_is_staff(self):
        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(
                username="@superadmin2",
                email="superadmin2@example.com", 
                password="adminpassword", 
                is_staff=False
            )
        self.assertEqual(str(context.exception), "Superuser must have is_staff=True.")

    def test_superuser_invalid_is_superuser(self):
        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(
                username="@superadmin3",
                email="superadmin3@example.com", 
                password="adminpassword", 
                is_superuser=False
            )
        self.assertEqual(str(context.exception), "Superuser must have is_superuser=True.")

    def test_user_creation_with_extra_fields(self):
        """Test creating a user with extra fields"""
        extra_fields = {
            'first_name': 'Test',
            'last_name': 'User',
            'is_staff': True
        }
        user = User.objects.create_user(
            username='@testuser',
            email='extrafields@test.com',
            password='testpass123',
            **extra_fields
        )
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.is_staff)
    
    def test_create_user_normalizes_email(self):
        """Test email is normalized when creating user"""
        email = 'test@EXAMPLE.com'
        user = User.objects.create_user(username='@test', email=email, password='test123')
        self.assertEqual(user.email, email.lower())

    def test_admin_user_str(self):
        """Test the string representation of admin user"""
        self.assertEqual(str(self.admin), f"{self.admin.user.username} (Admin)")