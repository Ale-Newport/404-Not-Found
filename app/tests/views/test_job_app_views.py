# app/tests/views/test_job_application_views.py
from django.test import TestCase, Client
from django.urls import reverse
from app.models import User, Employee, Employer, Job, JobApplication
from django.core.files.uploadedfile import SimpleUploadedFile
import os

class JobApplicationViewsTest(TestCase):
    def setUp(self):
        # Create employee
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
        
        # Create employer
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
        
        # Create job
        self.job = Job.objects.create(
            name="Test Job",
            department="Engineering",
            description="Test description",
            salary=75000,
            job_type="FT",
            skills_needed="Python, Django",
            created_by=self.employer
        )
        
        # Set up clients
        self.employee_client = Client()
        self.employer_client = Client()
        self.anonymous_client = Client()
        
        # URLs
        self.my_applications_url = reverse('my_applications')
        self.apply_job_url = reverse('apply_job', args=[self.job.id])
        
    def test_my_applications_view_no_applications(self):
        """Test my_applications view when no applications exist"""
        self