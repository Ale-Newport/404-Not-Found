from django.test import TestCase
from app.models import User, Employee, Employer, Job, JobApplication
from django.db import IntegrityError
from decimal import Decimal

class MoreModelTests(TestCase):
    def setUp(self):
        self.employee_user = User.objects.create_user(
            username="@employee",
            email="employee@test.com",
            password="testpass123",
            first_name="Test",
            last_name="Employee",
            user_type="employee"
        )
        self.employee = Employee.objects.create(
            user=self.employee_user,
            country="US",
            skills="Python, Django"
        )
        
        self.employer_user = User.objects.create_user(
            username="@employer",
            email="employer@test.com",
            password="testpass123",
            first_name="Test",
            last_name="Employer",
            user_type="employer"
        )
        self.employer = Employer.objects.create(
            user=self.employer_user,
            company_name="Test Company",
            country="US"
        )
        
        self.job = Job.objects.create(
            name="Test Job",
            department="Engineering",
            description="Test description",
            salary=Decimal("75000.00"),
            job_type="FT",
            skills_needed="Python, Django",
            created_by=self.employer
        )
        
    def test_job_application_unique_constraint(self):
        """Test that an employee can only apply once to a job"""
        application = JobApplication.objects.create(
            job=self.job,
            applicant=self.employee,
            status="pending",
            cover_letter="First application"
        )
        
        with self.assertRaises(IntegrityError):
            JobApplication.objects.create(
                job=self.job,
                applicant=self.employee,
                status="pending",
                cover_letter="Second application"
            )
            
    def test_job_application_status_choices(self):
        """Test JobApplication status choices"""
        application = JobApplication.objects.create(
            job=self.job,
            applicant=self.employee,
            status="pending",
            cover_letter="Test application"
        )
        
        self.assertEqual(application.status, "pending")
        
        for status in ["reviewing", "accepted", "rejected"]:
            application.status = status
            application.save()
            application.refresh_from_db()
            self.assertEqual(application.status, status)
            
    def test_employee_manager_create_user(self):
        """Test EmployeeManager create_user method"""
        employee = Employee.objects.create_user(
            username="@newemployee",
            email="new@example.com",
            password="testpass123",
            first_name="New",
            last_name="Employee",
            country="UK",
            skills="JavaScript, React",
            interests="Coding, Reading",
            preferred_contract="PT"
        )
        
        self.assertEqual(employee.user.username, "@newemployee")
        self.assertEqual(employee.user.email, "new@example.com")
        self.assertEqual(employee.user.user_type, "employee")
        self.assertEqual(employee.country, "UK")
        self.assertEqual(employee.skills, "JavaScript, React")
        self.assertEqual(employee.interests, "Coding, Reading")
        self.assertEqual(employee.preferred_contract, "PT")

    def test_employee_manager_methods(self):
        """Test EmployeeManager methods"""
        new_employee = Employee.objects.create_user(
            username="@newuser",
            email="new2@example.com",
            password="testpass123",
            first_name="New",
            last_name="User",
            country="UK",
            skills="JavaScript, React",
            interests="Coding",
            preferred_contract="FT"
        )
        
        self.assertTrue(User.objects.filter(username="@newuser").exists())
        self.assertTrue(Employee.objects.filter(user__username="@newuser").exists())
        
        self.assertEqual(new_employee.country, "UK")
        self.assertEqual(new_employee.skills, "JavaScript, React")
        self.assertEqual(new_employee.interests, "Coding")
        self.assertEqual(new_employee.preferred_contract, "FT")

    def test_employer_manager_methods(self):
        """Test EmployerManager methods"""
        new_employer = Employer.objects.create_user(
            username="@newemployer",
            email="employer@example.com",
            password="testpass123",
            first_name="New",
            last_name="Employer",
            company_name="New Company",
            country="US"
        )
        
        self.assertTrue(User.objects.filter(username="@newemployer").exists())
        self.assertTrue(Employer.objects.filter(user__username="@newemployer").exists())
        
        self.assertEqual(new_employer.company_name, "New Company")
        self.assertEqual(new_employer.country, "US")

    def test_user_manager_create_methods(self):
        """Test additional CustomUserManager methods"""
        user = User.objects.create_user(
            username="@customtype",
            email="custom@example.com",
            password="testpass123",
            user_type="custom_type"
        )
        self.assertEqual(user.user_type, "custom_type")
        
        user = User.objects.create_user(
            username="@default",
            email="default@example.com",
            password="testpass123"
        )
        self.assertEqual(user.user_type, "")

    def test_job_application_str_method(self):
        """Test JobApplication.__str__ method"""
        application = JobApplication.objects.create(
            job=self.job,
            applicant=self.employee,
            status="pending",
            cover_letter="Test application",
            # no full_name
        )
        
        expected_str = f"{self.employee.user.get_full_name()} - {self.job.name}"
        self.assertEqual(str(application), expected_str)
        application.full_name = "Custom Name"
        application.save()
        expected_str = f"Custom Name - {self.job.name}"
        self.assertEqual(str(application), expected_str)