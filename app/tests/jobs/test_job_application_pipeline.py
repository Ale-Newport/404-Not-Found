from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from app.models import User, Employee, Employer, Job, JobApplication
from decimal import Decimal
import os

class FullJobApplicationPipelineTest(TestCase):
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
            skills="Python, Django, Testing"
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
            name="Test Developer",
            department="Engineering",
            description="Test job description",
            salary=Decimal("80000.00"),
            job_type="FT",
            skills_needed="Testing, Python",
            created_by=self.employer
        )
        
        self.employee_client = Client()
        self.employer_client = Client()
        
        self.job_detail_url = reverse('job_detail', args=[self.job.id])
        self.apply_job_url = reverse('apply_job', args=[self.job.id])
        
    def test_full_application_pipeline(self):
        """Test the complete job application pipeline from application to decision"""
        
        self.employee_client.login(username="@jobseeker", password="testpass123")
        
        response = self.employee_client.get(self.job_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Developer")
        self.assertContains(response, "Apply Now")
        
        cv_content = b"This is a test CV file content"
        cv_file = SimpleUploadedFile("test_cv.pdf", cv_content, content_type="application/pdf")
        
        application_data = {
            'cover_letter': 'I would like to apply for this position',
            'full_name': 'Job Seeker',
            'email': 'jobseeker@test.com',
            'phone': '555-1234',
            'country': 'US',
            'current_position': 'Junior Developer',
            'skills': 'Python, Django, Testing',
            'experience': '2 years as software developer',
            'education': 'BS Computer Science',
            'portfolio_url': 'https://portfolio.jobseeker.com',
            'linkedin_url': 'https://linkedin.com/in/jobseeker',
            'custom_cv': cv_file
        }
        
        response = self.employee_client.post(self.apply_job_url, application_data)
        self.assertEqual(response.status_code, 302)
        
        self.assertEqual(JobApplication.objects.count(), 1)
        application = JobApplication.objects.first()
        self.assertEqual(application.job, self.job)
        self.assertEqual(application.applicant, self.employee)
        self.assertEqual(application.status, 'pending')
        self.assertEqual(application.full_name, 'Job Seeker')
        self.assertTrue(application.custom_cv)
        
        my_applications_url = reverse('my_applications')
        response = self.employee_client.get(my_applications_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Developer")
        self.assertContains(response, "pending")
        
        self.employee_client.logout()
        self.employer_client.login(username="@employer", password="testpass123")
        
        response = self.employer_client.get(self.job_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Job Seeker")
        self.assertContains(response, "pending")
        
        update_url = reverse('update_application_status', args=[application.id])
        response = self.employer_client.post(update_url, {'status': 'reviewing'})
        self.assertEqual(response.status_code, 302)
        
        application.refresh_from_db()
        self.assertEqual(application.status, 'reviewing')
        
        response = self.employer_client.post(update_url, {'status': 'accepted'})
        self.assertEqual(response.status_code, 302)
        
        application.refresh_from_db()
        self.assertEqual(application.status, 'accepted')
        
        self.employer_client.logout()
        self.employee_client.login(username="@jobseeker", password="testpass123")
        
        response = self.employee_client.get(my_applications_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "accepted")
        
    def test_employer_rejects_application(self):
        """Test employer rejecting an application"""
        application = JobApplication.objects.create(
            job=self.job,
            applicant=self.employee,
            status='pending',
            cover_letter='Application letter',
            full_name='Job Seeker',
            email='jobseeker@test.com'
        )
        
        self.employer_client.login(username="@employer", password="testpass123")
        
        update_url = reverse('update_application_status', args=[application.id])
        response = self.employer_client.post(update_url, {'status': 'rejected'})
        self.assertEqual(response.status_code, 302)
        
        application.refresh_from_db()
        self.assertEqual(application.status, 'rejected')
        
    def test_unauthorized_application_status_updates(self):
        """Test that only the job's creator can update applications"""
        other_employer_user = User.objects.create_user(
            username="@otheremployer",
            password="testpass123",
            email="other@test.com",
            user_type="employer"
        )
        other_employer = Employer.objects.create(user=other_employer_user, company_name="Other Corp")
        
        application = JobApplication.objects.create(
            job=self.job,
            applicant=self.employee,
            status='pending',
            cover_letter='Application letter',
            full_name='Job Seeker',
            email='jobseeker@test.com'
        )
        
        other_client = Client()
        other_client.login(username="@otheremployer", password="testpass123")
        
        update_url = reverse('update_application_status', args=[application.id])
        response = other_client.post(update_url, {'status': 'accepted'})
        
        self.assertEqual(response.status_code, 302)
        application.refresh_from_db()
        self.assertEqual(application.status, 'pending')
        
    def test_employee_cannot_apply_twice(self):
        """Test that an employee cannot apply twice for the same job"""
        JobApplication.objects.create(
            job=self.job,
            applicant=self.employee,
            status='pending',
            cover_letter='First application',
            full_name='Job Seeker',
            email='jobseeker@test.com'
        )
        
        self.employee_client.login(username="@jobseeker", password="testpass123")
        
        application_data = {
            'cover_letter': 'Second application attempt',
            'full_name': 'Job Seeker',
            'email': 'jobseeker@test.com'
        }
        
        response = self.employee_client.post(self.apply_job_url, application_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(JobApplication.objects.count(), 1)
        
    def tearDown(self):
        for application in JobApplication.objects.all():
            if application.custom_cv:
                if os.path.isfile(application.custom_cv.path):
                    os.remove(application.custom_cv.path)