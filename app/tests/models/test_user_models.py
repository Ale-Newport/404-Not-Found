from django.test import TestCase
from app.models import User, Admin, Employee, Employer

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


class UserDelegationMixinTest(TestCase):
    """Test the UserDelegationMixin functionality for all user profile types."""
    
    def setUp(self):
        """Set up test data with one instance of each user type."""
        self.admin = Admin.objects.create_user(
            username="@admintest",
            email="admintest@example.com",
            password="password123",
            first_name="Admin",
            last_name="Tester"
        )
        
        self.employee = Employee.objects.create_user(
            username="@employeetest",
            email="employeetest@example.com",
            password="password123",
            first_name="Employee",
            last_name="Tester",
            country="US"
        )
        
        self.employer = Employer.objects.create_user(
            username="@employertest",
            email="employertest@example.com",
            password="password123",
            first_name="Employer",
            last_name="Tester",
            company_name="Test Company",
            country="UK"
        )
    
    def test_email_property(self):
        """Test that the email property correctly gets and sets the user's email."""
        self.assertEqual(self.admin.email, "admintest@example.com")
        self.assertEqual(self.employee.email, "employeetest@example.com")
        self.assertEqual(self.employer.email, "employertest@example.com")
        
        self.admin.email = "newadmin@example.com"
        self.employee.email = "newemployee@example.com"
        self.employer.email = "newemployer@example.com"
        
        self.admin.user.refresh_from_db()
        self.employee.user.refresh_from_db()
        self.employer.user.refresh_from_db()
        
        self.assertEqual(self.admin.user.email, "newadmin@example.com")
        self.assertEqual(self.employee.user.email, "newemployee@example.com")
        self.assertEqual(self.employer.user.email, "newemployer@example.com")
        
        self.assertEqual(self.admin.email, "newadmin@example.com")
        self.assertEqual(self.employee.email, "newemployee@example.com")
        self.assertEqual(self.employer.email, "newemployer@example.com")
    
    def test_first_name_property(self):
        """Test that the first_name property correctly gets and sets the user's first name."""
        self.assertEqual(self.admin.first_name, "Admin")
        self.assertEqual(self.employee.first_name, "Employee")
        self.assertEqual(self.employer.first_name, "Employer")
        
        self.admin.first_name = "NewAdmin"
        self.employee.first_name = "NewEmployee"
        self.employer.first_name = "NewEmployer"
        
        self.admin.user.refresh_from_db()
        self.employee.user.refresh_from_db()
        self.employer.user.refresh_from_db()
        
        self.assertEqual(self.admin.user.first_name, "NewAdmin")
        self.assertEqual(self.employee.user.first_name, "NewEmployee")
        self.assertEqual(self.employer.user.first_name, "NewEmployer")
        
        self.assertEqual(self.admin.first_name, "NewAdmin")
        self.assertEqual(self.employee.first_name, "NewEmployee")
        self.assertEqual(self.employer.first_name, "NewEmployer")
    
    def test_last_name_property(self):
        """Test that the last_name property correctly gets and sets the user's last name."""
        self.assertEqual(self.admin.last_name, "Tester")
        self.assertEqual(self.employee.last_name, "Tester")
        self.assertEqual(self.employer.last_name, "Tester")
        
        self.admin.last_name = "AdminLast"
        self.employee.last_name = "EmployeeLast"
        self.employer.last_name = "EmployerLast"
        
        self.admin.user.refresh_from_db()
        self.employee.user.refresh_from_db()
        self.employer.user.refresh_from_db()
        
        self.assertEqual(self.admin.user.last_name, "AdminLast")
        self.assertEqual(self.employee.user.last_name, "EmployeeLast")
        self.assertEqual(self.employer.user.last_name, "EmployerLast")
        
        self.assertEqual(self.admin.last_name, "AdminLast")
        self.assertEqual(self.employee.last_name, "EmployeeLast")
        self.assertEqual(self.employer.last_name, "EmployerLast")
    
    def test_is_staff_property(self):
        """Test that the is_staff property correctly gets and sets the user's staff status."""
        self.assertTrue(self.admin.is_staff)
        self.assertFalse(self.employee.is_staff)
        self.assertFalse(self.employer.is_staff)

        self.employee.is_staff = True
        self.employer.is_staff = True
        self.admin.is_staff = False
        
        self.admin.user.refresh_from_db()
        self.employee.user.refresh_from_db()
        self.employer.user.refresh_from_db()
        
        self.assertFalse(self.admin.user.is_staff)
        self.assertTrue(self.employee.user.is_staff)
        self.assertTrue(self.employer.user.is_staff)
        
        self.assertFalse(self.admin.is_staff)
        self.assertTrue(self.employee.is_staff)
        self.assertTrue(self.employer.is_staff)
    
    def test_is_superuser_property(self):
        """Test that the is_superuser property correctly gets and sets the user's superuser status."""
        self.assertTrue(self.admin.is_superuser)
        self.assertFalse(self.employee.is_superuser)
        self.assertFalse(self.employer.is_superuser)
        
        self.employee.is_superuser = True
        self.employer.is_superuser = True
        self.admin.is_superuser = False
        
        self.admin.user.refresh_from_db()
        self.employee.user.refresh_from_db()
        self.employer.user.refresh_from_db()
        
        self.assertFalse(self.admin.user.is_superuser)
        self.assertTrue(self.employee.user.is_superuser)
        self.assertTrue(self.employer.user.is_superuser)
        
        self.assertFalse(self.admin.is_superuser)
        self.assertTrue(self.employee.is_superuser)
        self.assertTrue(self.employer.is_superuser)
    
    def test_is_active_property(self):
        """Test that the is_active property correctly gets and sets the user's active status."""
        self.assertTrue(self.admin.is_active)
        self.assertTrue(self.employee.is_active)
        self.assertTrue(self.employer.is_active)
        
        self.admin.is_active = False
        self.employee.is_active = False
        self.employer.is_active = False
        
        self.admin.user.refresh_from_db()
        self.employee.user.refresh_from_db()
        self.employer.user.refresh_from_db()
        
        self.assertFalse(self.admin.user.is_active)
        self.assertFalse(self.employee.user.is_active)
        self.assertFalse(self.employer.user.is_active)
        
        self.assertFalse(self.admin.is_active)
        self.assertFalse(self.employee.is_active)
        self.assertFalse(self.employer.is_active)
        
        self.admin.is_active = True
        self.employee.is_active = True
        self.employer.is_active = True
        
        self.admin.user.refresh_from_db()
        self.employee.user.refresh_from_db()
        self.employer.user.refresh_from_db()
        
        self.assertTrue(self.admin.user.is_active)
        self.assertTrue(self.employee.user.is_active)
        self.assertTrue(self.employer.user.is_active)