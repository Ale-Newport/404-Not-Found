# app/tests/models/test_more_models.py
from django.test import TestCase
from app.models import User, Admin, Employee, Employer, Job, JobApplication
from django.db import IntegrityError
from decimal import Decimal

class MoreModelTests(TestCase):
    def setUp(self):
        # Create users
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
        
        # Create a job
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
        # Create first application
        application = JobApplication.objects.create(
            job=self.job,
            applicant=self.employee,
            status="pending",
            cover_letter="First application"
        )
        
        # Attempt to create a second application for the same job/applicant
        with self.assertRaises(IntegrityError):
            JobApplication.objects.create(
                job=self.job,
                applicant=self.employee,
                status="pending",
                cover_letter="Second application"
            )
            
    def test_job_application_status_choices(self):
        """Test JobApplication status choices"""
        # Create an application
        application = JobApplication.objects.create(
            job=self.job,
            applicant=self.employee,
            status="pending",
            cover_letter="Test application"
        )
        
        # Check default status
        self.assertEqual(application.status, "pending")
        
        # Update to different valid statuses
        for status in ["reviewing", "accepted", "rejected"]:
            application.status = status
            application.save()
            application.refresh_from_db()
            self.assertEqual(application.status, status)
            
    def test_employee_manager_create_user(self):
        """Test EmployeeManager create_user method"""
        # Create a new employee via manager
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
        
        # Check that user and employee were created correctly
        self.assertEqual(employee.user.username, "@newemployee")
        self.assertEqual(employee.user.email, "new@example.com")
        self.assertEqual(employee.user.user_type, "employee")
        self.assertEqual(employee.country, "UK")
        self.assertEqual(employee.skills, "JavaScript, React")
        self.assertEqual(employee.interests, "Coding, Reading")
        self.assertEqual(employee.preferred_contract, "PT")

    # app/tests/models/test_edge_models.py
    def test_employee_manager_methods(self):
        """Test EmployeeManager methods"""
        # Create using create_user method
        new_employee = Employee.objects.create_user(
            username="@newuser",
            email="new@example.com",
            password="testpass123",
            first_name="New",
            last_name="User",
            user_type="employee",
            country="UK",
            skills="JavaScript, React",
            interests="Coding",
            preferred_contract="FT"
        )
        
        # Check that user and employee were created
        self.assertTrue(User.objects.filter(username="@newuser").exists())
        self.assertTrue(Employee.objects.filter(user__username="@newuser").exists())
        
        # Check profile fields
        self.assertEqual(new_employee.country, "UK")
        self.assertEqual(new_employee.skills, "JavaScript, React")
        self.assertEqual(new_employee.interests, "Coding")
        self.assertEqual(new_employee.preferred_contract, "FT")

    def test_employer_manager_methods(self):
        """Test EmployerManager methods"""
        # Create using create_user method
        new_employer = Employer.objects.create_user(
            username="@newemployer",
            email="employer@example.com",
            password="testpass123",
            first_name="New",
            last_name="Employer",
            user_type="employer",
            company_name="New Company",
            country="US"
        )
        
        # Check that user and employer were created
        self.assertTrue(User.objects.filter(username="@newemployer").exists())
        self.assertTrue(Employer.objects.filter(user__username="@newemployer").exists())
        
        # Check profile fields
        self.assertEqual(new_employer.company_name, "New Company")
        self.assertEqual(new_employer.country, "US")

    # app/tests/models/test_more_models.py
    def test_user_manager_create_methods(self):
        """Test additional CustomUserManager methods"""
        # Test create_user with different user_type
        user = User.objects.create_user(
            username="@customtype",
            email="custom@example.com",
            password="testpass123",
            user_type="custom_type"  # Non-standard type
        )
        self.assertEqual(user.user_type, "custom_type")
        
        # Test create_user without specifying user_type (should default to employee)
        user = User.objects.create_user(
            username="@default",
            email="default@example.com",
            password="testpass123"
        )
        self.assertEqual(user.user_type, "employee")  # Default type

    def test_job_application_str_method(self):
        """Test JobApplication.__str__ method"""
        # Create application without full_name (should use get_full_name)
        application = JobApplication.objects.create(
            job=self.job,
            applicant=self.employee,
            status="pending",
            cover_letter="Test application",
            # No full_name
        )
        
        expected_str = f"{self.employee.user.get_full_name()} - {self.job.name}"
        self.assertEqual(str(application), expected_str)
        
        # Update with full_name
        application.full_name = "Custom Name"
        application.save()
        
        expected_str = f"Custom Name - {self.job.name}"
        self.assertEqual(str(application), expected_str)