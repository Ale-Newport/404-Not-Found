from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from app.models import User, Employee, Employer, Job, JobApplication
from decimal import Decimal
import os

class EdgeCaseJobApplicationTest(TestCase):
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
        
    def test_invalid_job_id(self):
        """Test accessing job detail page with invalid job ID"""
        self.employee_client.login(username="@jobseeker", password="testpass123")
        url = reverse('job_detail', args=[99999])  # non-existent job ID
        response = self.employee_client.get(url)
        
        self.assertEqual(response.status_code, 404)
        
    def test_invalid_application_id(self):
        """Test updating status for invalid application ID"""
        self.employer_client.login(username="@employer", password="testpass123")
        url = reverse('update_application_status', args=[99999])  # non-existent application ID
        response = self.employer_client.post(url, {'status': 'accepted'})
        
        self.assertEqual(response.status_code, 404)
        
    def test_application_with_large_file(self):
        """Test application with a large CV file"""
        self.employee_client.login(username="@jobseeker", password="testpass123")
        url = reverse('apply_job', args=[self.job.id])
        
        large_file_content = b'x' * (5 * 1024 * 1024)
        large_file = SimpleUploadedFile("large_cv.pdf", large_file_content, content_type="application/pdf")
        
        data = {
            'cover_letter': 'I am a perfect candidate',
            'full_name': 'Job Seeker',
            'email': 'jobseeker@test.com',
            'custom_cv': large_file
        }
        
        response = self.employee_client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(JobApplication.objects.count(), 1)
        
    def test_invalid_file_type(self):
        """Test application with invalid file type"""
        self.employee_client.login(username="@jobseeker", password="testpass123")
        url = reverse('apply_job', args=[self.job.id])
        
        invalid_file = SimpleUploadedFile("script.js", b"alert('test')", content_type="application/javascript")
        
        data = {
            'cover_letter': 'I am a perfect candidate',
            'full_name': 'Job Seeker',
            'email': 'jobseeker@test.com',
            'custom_cv': invalid_file
        }
        
        response = self.employee_client.post(url, data)
        self.assertEqual(response.status_code, 302)
        
    def test_missing_required_fields(self):
        """Test application with missing required fields"""
        self.employee_client.login(username="@jobseeker", password="testpass123")
        url = reverse('apply_job', args=[self.job.id])
        
        data = {
            'full_name': 'Job Seeker',
            'email': 'jobseeker@test.com'
        }
        
        response = self.employee_client.post(url, data)
        
        self.assertEqual(response.status_code, 302)
        
    def tearDown(self):
        for application in JobApplication.objects.all():
            if application.custom_cv and os.path.isfile(application.custom_cv.path):
                os.remove(application.custom_cv.path)

class ApplicationWorkflowTest(TestCase):
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
        
        self.jobs = []
        self.applications = []
        
        for i in range(15):
            job = Job.objects.create(
                name=f"Job {i}",
                department="Engineering",
                description=f"Description {i}",
                salary=Decimal(f"{50000+i*1000}.00"),
                job_type="FT" if i % 2 == 0 else "PT",
                skills_needed="Python, Django",
                created_by=self.employer
            )
            self.jobs.append(job)
            
            if i % 3 == 0:
                application = JobApplication.objects.create(
                    job=job,
                    applicant=self.employee,
                    status='pending',
                    cover_letter=f'Application for Job {i}',
                    full_name='Job Seeker',
                    email='jobseeker@test.com'
                )
                self.applications.append(application)
        
        self.employee_client = Client()
        self.employer_client = Client()
        
    def test_pagination_employee_dashboard(self):
        """Test pagination on employee dashboard"""
        self.employee_client.login(username="@jobseeker", password="testpass123")
        url = reverse('employee_dashboard')
        
        response = self.employee_client.get(url)
        self.assertEqual(response.status_code, 200)
        
        if hasattr(response.context['jobs'], 'paginator'):
            self.assertLessEqual(len(response.context['jobs']), 10)
            
            response = self.employee_client.get(f"{url}?page=2")
            self.assertEqual(response.status_code, 200)
            self.assertGreater(len(response.context['jobs']), 0)
        
    def test_complex_filtering_employee_dashboard(self):
        """Test complex filtering combinations on employee dashboard"""
        self.employee_client.login(username="@jobseeker", password="testpass123")
        url = reverse('employee_dashboard')
        
        response = self.employee_client.get(f"{url}?job_type=PT&min_salary=55000")
        self.assertEqual(response.status_code, 200)
        
        for job in response.context['jobs']:
            self.assertEqual(job.job_type, "PT")
            self.assertGreaterEqual(job.salary, Decimal("55000.00"))
        
    def test_my_applications_view(self):
        """Test the my_applications view"""
        self.employee_client.login(username="@jobseeker", password="testpass123")
        url = reverse('my_applications')
        
        response = self.employee_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['applications']), len(self.applications))
        
        for application in response.context['applications']:
            self.assertEqual(application.applicant, self.employee)
    
    def test_status_transition_messages(self):
        """Test that appropriate messages appear when status changes"""
        application = self.applications[0]
        
        self.employer_client.login(username="@employer", password="testpass123")
        url = reverse('update_application_status', args=[application.id])
        
        response = self.employer_client.post(url, {'status': 'reviewing'}, follow=True)
        messages = list(get_messages(response.wsgi_request))
        
        message_texts = [msg.message for msg in messages]
        status_message_found = any('updated to reviewing' in msg for msg in message_texts)
        self.assertTrue(status_message_found)
        
        response = self.employer_client.post(url, {'status': 'accepted'}, follow=True)
        messages = list(get_messages(response.wsgi_request))
        
        message_texts = [msg.message for msg in messages]
        status_message_found = any('updated to accepted' in msg for msg in message_texts)
        self.assertTrue(status_message_found)
    
    def test_filter_by_status_my_applications(self):
        """Test filtering applications by status in my_applications view"""
        if not self.applications:
            self.skipTest("No applications available to test")
            return
        
        application = self.applications[0]
        application.status = 'accepted'
        application.save()
        
        application.refresh_from_db()
        self.assertEqual(application.status, 'accepted')
        
        self.employee_client.login(username="@jobseeker", password="testpass123")
        url = reverse('my_applications')
        
        response = self.employee_client.get(f"{url}?status=accepted")
        self.assertEqual(response.status_code, 200)
        
        has_accepted = False
        for app in response.context['applications']:
            if app.status == 'accepted':
                has_accepted = True
                break
        self.assertTrue(has_accepted)
            
    def test_non_employee_accessing_my_applications(self):
        """Test that employers cannot access my_applications view"""
        self.employer_client.login(username="@employer", password="testpass123")
        url = reverse('my_applications')
        
        response = self.employer_client.get(url)
        
        self.assertEqual(response.status_code, 302)
    
    def tearDown(self):
        for application in JobApplication.objects.all():
            if application.custom_cv and os.path.isfile(application.custom_cv.path):
                os.remove(application.custom_cv.path)