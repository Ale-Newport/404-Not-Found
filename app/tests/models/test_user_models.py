from django.test import TestCase
from app.models import Admin, Employer, Employee, AbstractUser

class UserCreationTest(TestCase):
    def setUp(self):
        # Create admin user
        self.admin = Admin.objects.create(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            is_staff=True,
            is_superuser=False
        )

        # Create employee user
        self.employee = Employee.objects.create(
            email="employee1@example.com",
            first_name="Test",  # Match this with what you're testing
            last_name="Employee",
            country="US"
        )
        
        # Create employer user
        self.employer = Employer.objects.create(
            email="employer1@example.com",
            first_name="Test",
            last_name="Employer",
            country="UK",
            company_name="Company1"
        )

    def test_user_str_representation(self):
        expected_employee_str = f"{self.employee.email} (Employee)"
        expected_employer_str = f"{self.employer.email} (Employer) - {self.employer.company_name}"
        self.assertEqual(str(self.employee), expected_employee_str)
        self.assertEqual(str(self.employer), expected_employer_str)

    def test_admin_creation(self):
        self.assertEqual(self.admin.email, "admin@example.com")
        self.assertTrue(self.admin.is_staff)
        self.assertFalse(self.admin.is_superuser)

    def test_employer_creation(self):
        self.assertEqual(self.employer.email, "employer1@example.com")
        self.assertEqual(self.employer.company_name, "Company1")
        self.assertTrue(self.employer.is_active)

    def test_employee_creation(self):
        self.assertEqual(self.employee.email, "employee1@example.com")
        self.assertEqual(self.employee.first_name, "Test")  # Changed from "John" to "Test"
        self.assertEqual(self.employee.last_name, "Employee")
        self.assertTrue(self.employee.is_active)

    def test_invalid_user_creation(self):
        with self.assertRaises(ValueError):
            Admin.objects.create_user(email=None, password="password123")

    def test_superuser_creation(self):
        superuser = Admin.objects.create_superuser(
            email="superadmin@example.com", 
            password="adminpassword"
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_superuser_invalid_is_staff(self):
        with self.assertRaises(ValueError) as context:
            Admin.objects.create_superuser(
                email="superadmin2@example.com", 
                password="adminpassword", 
                is_staff=False
            )
        self.assertEqual(str(context.exception), "Superuser must have is_staff=True.")

    def test_superuser_invalid_is_superuser(self):
        with self.assertRaises(ValueError) as context:
            Admin.objects.create_superuser(
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
        user = Admin.objects.create_user(
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
        user = Admin.objects.create_user(email=email, password='test123')
        self.assertEqual(user.email, email.lower())

    def test_create_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            Admin.objects.create_user(email='', password='test123')

    def test_admin_user_str(self):
        """Test the string representation of abstract user"""
        user = Admin.objects.create_user(
            email='test@example.com',
            password='test123'
        )
        self.assertEqual(str(user), user.email +" (Admin)")