# tests/test_employer_application_review.py
from django.test import TestCase, Client
from django.urls import reverse
from app.models import User, Employee, Employer, Job, JobApplication
from decimal import Decimal

class ApplicationReviewTest(TestCase):
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
        
        # Create application
        self.application = JobApplication.objects.create(
            job=self.job,
            applicant=self.employee.employee,
            cover_letter="Test cover letter",
            full_name="Test Employee",
            email="employee@test.com",
            skills="Python, Django, JavaScript",
            status="pending"
        )
        
        self.client = Client()
        
    def test_job_detail_shows_applications(self):
        """Test that employer can see applications in job detail"""
        self.client.login(username="@employer", password="testpass123")
        response = self.client.get(reverse('job_detail', args=[self.job.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Applications (1)")
        self.assertContains(response, "Test Employee")
        
    def test_update_application_status(self):
        """Test that employer can update application status"""
        self.client.login(username="@employer", password="testpass123")
        
        # Update status to 'reviewing'
        response = self.client.post(
            reverse('update_application_status', args=[self.application.id]),
            {'status': 'reviewing'}
        )
        
        # Should redirect back to job detail
        self.assertEqual(response.status_code, 302)
        
        # Check if status was updated
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'reviewing')
        
    def test_application_lifecycle(self):
        """Test the complete application lifecycle"""
        self.client.login(username="@employer", password="testpass123")
        
        # Update from pending to reviewing
        self.client.post(
            reverse('update_application_status', args=[self.application.id]),
            {'status': 'reviewing'}
        )
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'reviewing')
        
        # Update from reviewing to accepted
        self.client.post(
            reverse('update_application_status', args=[self.application.id]),
            {'status': 'accepted'}
        )
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'accepted')
        
    def test_unauthorized_access(self):
        """Test that other employers cannot update applications they don't own"""
        # Create another employer
        other_employer = User.objects.create_user(
            username="@employer2",
            email="employer2@test.com",
            password="testpass123",
            user_type="employer"
        )
        Employer.objects.create(
            user=other_employer,
            company_name="Other Company"
        )
        
        # Log in as the other employer
        self.client.login(username="@employer2", password="testpass123")
        
        # Try to update application
        response = self.client.post(
            reverse('update_application_status', args=[self.application.id]),
            {'status': 'reviewing'}
        )
        
        # Should receive an error/redirect
        self.assertEqual(response.status_code, 302)  # Redirect expected
        
        # Status should remain unchanged
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'pending')