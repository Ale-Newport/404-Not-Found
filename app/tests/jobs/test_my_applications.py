# tests/test_my_applications.py
from django.test import TestCase, Client
from django.urls import reverse
from app.models import User, Employee, Employer, Job, JobApplication
from decimal import Decimal

class MyApplicationsTest(TestCase):
    def setUp(self):
        # Create employer
        self.employer = User.objects.create_user(
            username="@employer",
            email="employer@test.com",
            password="testpass123",
            first_name="Test",
            last_name="Employer",
            user_type="employer"
        )
        Employer.objects.create(
            user=self.employer,
            company_name="Test Company",
            country="US"
        )
        
        # Create employee
        self.employee = User.objects.create_user(
            username="@employee",
            email="employee@test.com",
            password="testpass123",
            first_name="Test",
            last_name="Employee",
            user_type="employee"
        )
        Employee.objects.create(
            user=self.employee,
            country="US",
            skills="Python, Django"
        )
        
        # Create jobs
        self.job1 = Job.objects.create(
            name="Backend Developer",
            department="Engineering",
            description="Backend role",
            salary=Decimal("75000.00"),
            job_type="FT",
            skills_needed="Python, Django",
            created_by=self.employer.employer
        )
        
        self.job2 = Job.objects.create(
            name="Frontend Developer",
            department="Engineering",
            description="Frontend role",
            salary=Decimal("65000.00"),
            job_type="FT",
            skills_needed="JavaScript, React",
            created_by=self.employer.employer
        )
        
        # Create applications
        self.application1 = JobApplication.objects.create(
            job=self.job1,
            applicant=self.employee.employee,
            cover_letter="Backend application",
            full_name="Test Employee",
            email="employee@test.com",
            status="pending"
        )
        
        self.application2 = JobApplication.objects.create(
            job=self.job2,
            applicant=self.employee.employee,
            cover_letter="Frontend application",
            full_name="Test Employee",
            email="employee@test.com",
            status="reviewing"
        )
        
        self.client = Client()
        
    def test_my_applications_view(self):
        """Test that my applications view shows all applications"""
        self.client.login(username="@employee", password="testpass123")
        response = self.client.get(reverse('my_applications'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_applications.html')
        self.assertContains(response, "Backend Developer")
        self.assertContains(response, "Frontend Developer")
        
    def test_application_status_display(self):
        """Test that application statuses are correctly displayed"""
        self.client.login(username="@employee", password="testpass123")
        response = self.client.get(reverse('my_applications'))
        self.assertContains(response, "Pending")
        self.assertContains(response, "Reviewing")
        
    def test_status_updates_reflected(self):
        """Test that status updates are reflected in my applications view"""
        # Update application status
        self.client.login(username="@employer", password="testpass123")
        self.client.post(
            reverse('update_application_status', args=[self.application1.id]),
            {'status': 'accepted'}
        )
        
        # Check if status update is reflected
        self.client.login(username="@employee", password="testpass123")
        response = self.client.get(reverse('my_applications'))
        self.assertContains(response, "Accepted")
        
    def test_empty_applications(self):
        """Test view when no applications exist"""
        # Create new employee with no applications
        new_employee = User.objects.create_user(
            username="@newemployee",
            email="newemployee@test.com",
            password="testpass123",
            first_name="New",
            last_name="Employee",
            user_type="employee"
        )
        Employee.objects.create(
            user=new_employee,
            country="US"
        )
        
        # Log in as new employee
        self.client.login(username="@newemployee", password="testpass123")
        response = self.client.get(reverse('my_applications'))
        
        # Should show "No applications yet" message
        self.assertContains(response, "No applications yet")
        self.assertContains(response, "Browse Jobs")
        
    def test_unauthorized_access(self):
        """Test that employers cannot access my applications"""
        self.client.login(username="@employer", password="testpass123")
        response = self.client.get(reverse('my_applications'))
        
        # Should redirect with access denied message
        self.assertEqual(response.status_code, 302)