from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from app.models import User, Employee, Employer, Job, JobApplication
from decimal import Decimal
import os

class JobViewsTest(TestCase):
    def setUp(self):
        
        self.employee_user = User.objects.create_user(
            username="@jobseeker",
            email="jobseeker@test.com",
            password="testpass123",
            first_name="Job",
            last_name="Seeker",
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
            first_name="Em",
            last_name="Ployer",
            user_type="employer"
        )
        self.employer = Employer.objects.create(
            user=self.employer_user,
            country="US",
            company_name="Test Corp"
        )
        
        self.job = Job.objects.create(
            name="Test Job",
            department="Engineering",
            description="Test job description",
            salary=Decimal("75000.00"),
            job_type="FT",
            skills_needed="Python, Django",
            created_by=self.employer
        )
        
        self.employee_client = Client()
        self.employer_client = Client()
        self.anonymous_client = Client()
        
    def test_job_detail_view_as_employee(self):
        """Test job detail view when accessed by employee"""
        self.employee_client.login(username="@jobseeker", password="testpass123")
        url = reverse('job_detail', args=[self.job.id])
        response = self.employee_client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'job/job_detail.html')
        self.assertContains(response, "Test Job")
        self.assertContains(response, "Apply Now")
        self.assertTrue(response.context['is_employee'])
        self.assertFalse(response.context['has_applied'])
        
    def test_job_detail_view_as_employer(self):
        """Test job detail view when accessed by the employer who created it"""
        self.employer_client.login(username="@employer", password="testpass123")
        url = reverse('job_detail', args=[self.job.id])
        response = self.employer_client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'job/job_detail.html')
        self.assertContains(response, "Test Job")
        self.assertFalse(response.context['is_employee'])
        
    def test_job_detail_view_with_application(self):
        """Test job detail when employee has already applied"""
        application = JobApplication.objects.create(
            job=self.job,
            applicant=self.employee,
            status='pending',
            cover_letter='Test application',
            full_name='Job Seeker'
        )
        
        self.employee_client.login(username="@jobseeker", password="testpass123")
        url = reverse('job_detail', args=[self.job.id])
        response = self.employee_client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['has_applied'])
        self.assertContains(response, "Application Submitted")
        
    def test_job_detail_view_without_login(self):
        """Test that job detail requires login"""
        url = reverse('job_detail', args=[self.job.id])
        response = self.anonymous_client.get(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))
        
    def test_apply_to_job_success(self):
        """Test successful job application submission"""
        self.employee_client.login(username="@jobseeker", password="testpass123")
        url = reverse('apply_job', args=[self.job.id])
        
        cv_content = b"This is a test CV"
        cv_file = SimpleUploadedFile("test_cv.pdf", cv_content, content_type="application/pdf")
        
        data = {
            'cover_letter': 'I am a perfect candidate',
            'full_name': 'Job Seeker',
            'email': 'jobseeker@test.com',
            'phone': '555-1234',
            'country': 'US',
            'skills': 'Python, Django',
            'custom_cv': cv_file
        }
        
        response = self.employee_client.post(url, data)
        
        self.assertEqual(response.status_code, 302)
        
        application = JobApplication.objects.filter(job=self.job, applicant=self.employee).first()
        self.assertIsNotNone(application)
        self.assertEqual(application.cover_letter, 'I am a perfect candidate')
        self.assertEqual(application.status, 'pending')
        
    def test_apply_to_job_non_employee(self):
        """Test that only employees can apply to jobs"""
        self.employer_client.login(username="@employer", password="testpass123")
        url = reverse('apply_job', args=[self.job.id])
        
        data = {
            'cover_letter': 'I want this job',
            'full_name': 'Test User'
        }
        
        response = self.employer_client.post(url, data)
        
        self.assertEqual(response.status_code, 302)
        
        self.assertEqual(JobApplication.objects.count(), 0)
        
    def test_update_application_status_success(self):
        """Test employer successfully updating application status"""
        application = JobApplication.objects.create(
            job=self.job,
            applicant=self.employee,
            status='pending',
            cover_letter='Test application',
            full_name='Job Seeker'
        )
        
        self.employer_client.login(username="@employer", password="testpass123")
        url = reverse('update_application_status', args=[application.id])
        response = self.employer_client.post(url, {'status': 'reviewing'})
        self.assertEqual(response.status_code, 302)
        application.refresh_from_db()
        self.assertEqual(application.status, 'reviewing')
        response = self.employer_client.post(url, {'status': 'accepted'})
        self.assertEqual(response.status_code, 302)
        application.refresh_from_db()
        self.assertEqual(application.status, 'accepted')
        
    def test_update_application_status_wrong_employer(self):
        """Test that only the job creator can update application status"""

        other_employer_user = User.objects.create_user(
            username="@other",
            email="other@test.com",
            password="testpass123",
            user_type="employer"
        )
        other_employer = Employer.objects.create(
            user=other_employer_user,
            company_name="Other Company"
        )
        
        application = JobApplication.objects.create(
            job=self.job,
            applicant=self.employee,
            status='pending',
            cover_letter='Test application',
            full_name='Job Seeker'
        )
        
        other_client = Client()
        other_client.login(username="@other", password="testpass123")
        url = reverse('update_application_status', args=[application.id])
        response = other_client.post(url, {'status': 'accepted'})
        self.assertEqual(response.status_code, 302)
        application.refresh_from_db()
        self.assertEqual(application.status, 'pending')
        
    def test_employee_dashboard_job_filtering(self):
        """Test job filtering in employee dashboard"""
        
        Job.objects.create(
            name="Frontend Developer",
            department="Design",
            description="Frontend job",
            salary=Decimal("65000.00"),
            job_type="FT",
            skills_needed="JavaScript, React",
            created_by=self.employer
        )
        
        Job.objects.create(
            name="Part-time Developer",
            department="Engineering",
            description="Part-time role",
            salary=Decimal("40000.00"),
            job_type="PT",
            skills_needed="Python, Django",
            created_by=self.employer
        )
        
        self.employee_client.login(username="@jobseeker", password="testpass123")
        url = reverse('employee_dashboard')
        response = self.employee_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['jobs']), 3)
        response = self.employee_client.get(f"{url}?job_type=PT")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['jobs']), 1)
        self.assertEqual(response.context['jobs'][0].name, "Part-time Developer")
        response = self.employee_client.get(f"{url}?department=Design")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['jobs']), 1)
        self.assertEqual(response.context['jobs'][0].name, "Frontend Developer")
        response = self.employee_client.get(f"{url}?min_salary=70000")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['jobs']), 1)
        self.assertEqual(response.context['jobs'][0].name, "Test Job")
        response = self.employee_client.get(f"{url}?search=frontend")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['jobs']), 1)
        self.assertEqual(response.context['jobs'][0].name, "Frontend Developer")
        
    def tearDown(self):
        for application in JobApplication.objects.all():
            if application.custom_cv and os.path.isfile(application.custom_cv.path):
                os.remove(application.custom_cv.path)