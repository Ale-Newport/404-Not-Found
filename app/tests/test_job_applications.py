# tests/test_job_application.py
from django.test import TestCase, Client
from django.urls import reverse
from app.models import User, Employee, Employer, Job, JobApplication
from decimal import Decimal
from django.core.files.uploadedfile import SimpleUploadedFile

class JobApplicationTest(TestCase):
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
        
        # Create job
        self.job = Job.objects.create(
            name="Test Job",
            department="Engineering",
            description="Test description",
            salary=Decimal("75000.00"),
            job_type="FT",
            skills_needed="Python, Django",
            created_by=self.employer.employer
        )
        
        self.client = Client()
        
    def test_job_detail_view(self):
        """Test that job detail view loads correctly for employee"""
        self.client.login(username="@employee", password="testpass123")
        response = self.client.get(reverse('job_detail', args=[self.job.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'job_detail.html')
        self.assertContains(response, "Apply Now")
        
    def test_apply_to_job(self):
        """Test submitting a job application"""
        self.client.login(username="@employee", password="testpass123")
        
        application_data = {
            'cover_letter': 'I am applying for this position.',
            'full_name': 'Test Employee',
            'email': 'employee@test.com',
            'country': 'US',
            'skills': 'Python, Django, JavaScript',
            'experience': 'Worked at tech companies for 5 years',
            'education': 'BS in Computer Science'
        }
        
        response = self.client.post(
            reverse('apply_job', args=[self.job.id]),
            application_data
        )
        
        # Should redirect to employee dashboard
        self.assertEqual(response.status_code, 302)
        
        # Check if application was created
        self.assertTrue(JobApplication.objects.filter(
            job=self.job,
            applicant=self.employee.employee
        ).exists())
        
    def test_apply_to_job_with_file(self):
        """Test submitting a job application with CV upload"""
        self.client.login(username="@employee", password="testpass123")
        
        # Create a simple uploaded file
        cv_file = SimpleUploadedFile(
            "test_cv.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        application_data = {
            'cover_letter': 'I am applying for this position.',
            'full_name': 'Test Employee',
            'email': 'employee@test.com',
            'country': 'US',
            'skills': 'Python, Django, JavaScript',
            'experience': 'Worked at tech companies for 5 years',
            'education': 'BS in Computer Science',
            'custom_cv': cv_file
        }
        
        response = self.client.post(
            reverse('apply_job', args=[self.job.id]),
            application_data
        )
        
        # Should redirect to employee dashboard
        self.assertEqual(response.status_code, 302)
        
        # Check if application was created with CV
        application = JobApplication.objects.get(
            job=self.job,
            applicant=self.employee.employee
        )
        self.assertTrue(application.custom_cv)
        
    def test_cannot_apply_twice(self):
        """Test that employee cannot apply to the same job twice"""
        self.client.login(username="@employee", password="testpass123")
        
        # Create initial application
        JobApplication.objects.create(
            job=self.job,
            applicant=self.employee.employee,
            cover_letter="Initial application"
        )
        
        # Try to apply again
        application_data = {
            'cover_letter': 'Second application attempt',
            'full_name': 'Test Employee',
            'email': 'employee@test.com',
            'country': 'US',
            'skills': 'Python, Django, JavaScript'
        }
        
        response = self.client.post(
            reverse('apply_job', args=[self.job.id]),
            application_data
        )
        
        # Should redirect but with warning message
        self.assertEqual(response.status_code, 302)
        
        # Check that only one application exists
        self.assertEqual(
            JobApplication.objects.filter(
                job=self.job,
                applicant=self.employee.employee
            ).count(),
            1
        )