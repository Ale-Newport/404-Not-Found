from django.test import TestCase
from app.models import Admin, Employer, Employee

class UserCreationTest(TestCase):
    """Unit tests for the Users models."""

    fixtures = ['app/tests/fixtures/users.json']

    def setUp(self):
        self.admin = Admin.objects.get(pk=1)
        self.employer = Employer.objects.get(pk=1)
        self.employee = Employee.objects.get(pk=1)

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
        self.assertEqual(self.employee.first_name, "John")
        self.assertEqual(self.employee.last_name, "Doe")
        self.assertTrue(self.employee.is_active)

    def test_invalid_user_creation(self):
        with self.assertRaises(ValueError):
            Admin.objects.create_user(email=None, password="password123")

    def test_superuser_creation(self):
        superuser = Admin.objects.create_superuser(email="superadmin@example.com", password="adminpassword")
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_superuser_invalid_is_staff(self):
        with self.assertRaises(ValueError) as context:
            Admin.objects.create_superuser(email="superadmin2@example.com", password="adminpassword", is_staff=False)
        self.assertEqual(str(context.exception), "Superuser must have is_staff=True.")

    def test_superuser_invalid_is_superuser(self):
        with self.assertRaises(ValueError) as context:
            Admin.objects.create_superuser(email="superadmin3@example.com", password="adminpassword", is_superuser=False)
        self.assertEqual(str(context.exception), "Superuser must have is_superuser=True.")

    def test_user_str_representation(self):
        self.assertEqual(str(self.admin), self.admin.email)
        self.assertEqual(str(self.employer), self.employer.email)
        self.assertEqual(str(self.employee), self.employee.email)
