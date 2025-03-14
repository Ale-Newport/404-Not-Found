from django.test import TestCase, Client
from django.urls import reverse
from app.models import User, Admin, Employee, Employer, Job
from django.core.paginator import Paginator

class AdminViewsTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="@admintest",
            email="admin@test.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            user_type="admin",
            is_staff=True,
            is_superuser=True
        )
        Admin.objects.create(user=self.admin_user)
        
        self.employee_user = User.objects.create_user(
            username="@employeetest",
            email="employee@test.com",
            password="testpass123",
            first_name="Test",
            last_name="Employee",
            user_type="employee"
        )
        Employee.objects.create(user=self.employee_user, country="US")
        
        self.employer_user = User.objects.create_user(
            username="@employertest",
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
        
        for i in range(5):
            Job.objects.create(
                name=f"Test Job {i}",
                department="Engineering",
                description=f"Test description {i}",
                salary=50000 + i * 1000,
                job_type="FT" if i % 2 == 0 else "PT",
                skills_needed="Python, Django",
                created_by=self.employer
            )
        
        self.admin_client = Client()
        self.admin_client.login(username="@admintest", password="testpass123")
        self.employee_client = Client()
        self.employee_client.login(username="@employeetest", password="testpass123")
        
    def test_admin_dashboard_access(self):
        """Test that admin can access dashboard and non-admins cannot"""
        response = self.admin_client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/admin_dashboard.html')
        
        response = self.employee_client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        
    def test_admin_dashboard_content(self):
        """Test that admin dashboard shows correct statistics"""
        response = self.admin_client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(response.context['total_users'], 3)
        self.assertEqual(response.context['employee_users'], 1)
        self.assertEqual(response.context['employer_users'], 1)
        self.assertEqual(response.context['admin_users'], 1)
        self.assertEqual(response.context['total_jobs'], 5)
        
    def test_list_users_view(self):
        """Test the list_users view"""
        response = self.admin_client.get(reverse('list_users'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/list_users.html')
        
        self.assertEqual(len(response.context['users_page']), 3)
        
    def test_list_users_with_filters(self):
        """Test list_users view with filters"""
        response = self.admin_client.get(reverse('list_users') + '?type=employee')
        self.assertEqual(response.status_code, 200)
        
        response = self.admin_client.get(reverse('list_users') + '?search=admin')
        self.assertEqual(response.status_code, 200)
        
    def test_list_users_ordering(self):
        """Test list_users view with ordering"""
        response = self.admin_client.get(reverse('list_users') + '?order_by=email')
        self.assertEqual(response.status_code, 200)
        
        response = self.admin_client.get(reverse('list_users') + '?order_by=user_type')
        self.assertEqual(response.status_code, 200)
        
    def test_list_jobs_view(self):
        """Test the list_jobs view"""
        response = self.admin_client.get(reverse('list_jobs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/list_jobs.html')
        
        self.assertEqual(len(response.context['jobs']), 5)
        
    def test_list_jobs_with_filters(self):
        """Test list_jobs view with filters"""
        response = self.admin_client.get(reverse('list_jobs') + '?job_type=PT')
        self.assertEqual(response.status_code, 200)
        
        pt_jobs = [job for job in response.context['jobs'] if job.job_type == 'PT']
        self.assertEqual(len(pt_jobs), len(response.context['jobs']))

    def test_list_users_pagination(self):
        """Test pagination in list_users view"""
        self.admin_client.login(username="@admintest", password="testpass123")
        
        for i in range(30):
            User.objects.create_user(
                username=f"@testuser{i}",
                email=f"user{i}@example.com",
                password="testpass123",
                user_type="employee"
            )
        
        response = self.admin_client.get(reverse('list_users'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(hasattr(response.context['users_page'], 'paginator'))
        
        response = self.admin_client.get(reverse('list_users') + '?page=2')
        self.assertEqual(response.status_code, 200)

    def test_list_jobs_search_filter(self):
        """Test search filter in list_jobs view"""
        self.admin_client.login(username="@admintest", password="testpass123")
        Job.objects.all().delete()
        
        Job.objects.create(
            name="UNIQUE_Python_Developer",
            department="Engineering",
            description="Python development",
            salary=70000,
            job_type="FT",
            skills_needed="Python, Django",
            created_by=self.employer
        )
        
        Job.objects.create(
            name="UNIQUE_JavaScript_Developer",
            department="Frontend",
            description="JavaScript development",
            salary=65000,
            job_type="FT",
            skills_needed="JavaScript, React",
            skills_wanted="TypeScript",
            created_by=self.employer
        )
        
        response = self.admin_client.get(reverse('list_jobs') + '?search=UNIQUE_Python')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['jobs']), 1)
        self.assertEqual(response.context['jobs'][0].name, "UNIQUE_Python_Developer")