from django.test import TestCase, Client
from django.urls import reverse
from app.models import Employer, Job
from decimal import Decimal

class EmployerViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.employer = Employer.objects.create_user(
            username="employer",
            email="employer@test.com",
            password="testpass123",
            first_name="Test",
            last_name="Employer",
            company_name="Test Company"
        )
        self.job = Job.objects.create(
            name="Software Developer",
            department="Engineering",
            description="Test job description",
            salary=Decimal("75000.00"),
            job_type="FT",
            skills_needed="Python, Django",
            created_by=self.employer
        )
        
        # URLs
        self.login_url = reverse('login')
        self.dashboard_url = reverse('employer_dashboard')
        self.add_job_url = reverse('add_job')
        self.job_detail_url = reverse('job_detail', args=[self.job.id])
        self.account_url = reverse('account_page')

    def test_employer_login_required(self):
        """Test that views require login"""
        urls = [self.dashboard_url, self.add_job_url, 
               self.job_detail_url, self.account_url]
        
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith('/login/'))

    def test_employer_dashboard_with_login(self):
        """Test employer dashboard when logged in"""
        self.client.login(username='employer', password="testpass123")
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employer_dashboard.html')
        self.assertContains(response, "Software Developer")

    def test_add_job_get(self):
        """Test getting the add job form"""
        self.client.login(username='employer',  password="testpass123")
        response = self.client.get(self.add_job_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_job.html')

    def test_add_job_post(self):
        """Test creating a new job"""
        self.client.login(username='employer', password="testpass123")
        job_data = {
            'name': 'Frontend Developer',
            'department': 'Engineering',
            'description': 'Frontend role',
            'salary': '65000.00',
            'job_type': 'FT',
            'skills_needed': 'JavaScript, React'
        }
        response = self.client.post(self.add_job_url, job_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Job.objects.filter(name='Frontend Developer').exists())

    def test_job_detail_view(self):
        """Test viewing job details"""
        self.client.login(username='employer', password="testpass123")
        response = self.client.get(self.job_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'job_detail.html')
        self.assertContains(response, "Software Developer")
        self.assertContains(response, "Engineering")

    def test_account_page(self):
        """Test viewing account details"""
        self.client.login(username='employer', password="testpass123")
        response = self.client.get(self.account_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account_page.html')
        self.assertContains(response, "Test Company")

    def test_unauthorized_job_detail_access(self):
        """Test that employers can't view other employers' job details"""
        other_employer = Employer.objects.create_user(
            username="other",
            email="other@test.com",
            password="testpass123",
            company_name="Other Company"
        )
        other_job = Job.objects.create(
            name="Other Job",
            department="Other Dept",
            description="Other description",
            salary=Decimal("50000.00"),
            job_type="PT",
            skills_needed="Other skills",
            created_by=other_employer
        )
        
        self.client.login(username='employer', password="testpass123")
        response = self.client.get(
            reverse('job_detail', args=[other_job.id])
        )
        self.assertEqual(response.status_code, 404)