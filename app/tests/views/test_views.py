from django.test import TestCase, Client
from django.urls import reverse
from app.models import Admin, Employee, Employer, Job, VerificationCode
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

User = get_user_model()

class SignUpViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.employee_signup_url = reverse('employee_signup')
        self.employer_signup_url = reverse('employer_signup')
        
        self.valid_employee_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': '@john',
            'email': 'john@example.com',
            'country': 'US',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }
        
        self.valid_employer_data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'username': '@jane',
            'email': 'jane@company.com',
            'country': 'UK',
            'company_name': 'Test Company',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }

    def test_employee_signup_GET(self):
        response = self.client.get(self.employee_signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employee_signup.html')
        self.assertTrue('form' in response.context)

    def test_employer_signup_GET(self):
        response = self.client.get(self.employer_signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employer_signup.html')
        self.assertTrue('form' in response.context)

    def test_employee_signup_POST_valid(self):
        response = self.client.post(self.employee_signup_url, self.valid_employee_data)
        self.assertTrue(response.status_code in [200, 302])

    def test_employer_signup_POST_valid(self):
        response = self.client.post(self.employer_signup_url, self.valid_employer_data)
        self.assertTrue(response.status_code in [200, 302])

    def test_employee_signup_POST_invalid(self):
        invalid_data = self.valid_employee_data.copy()
        invalid_data['email'] = 'invalid-email'
        response = self.client.post(self.employee_signup_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='invalid-email').exists())
        self.assertTrue('form' in response.context)

    def test_employer_signup_POST_invalid(self):
        invalid_data = self.valid_employer_data.copy()
        invalid_data['email'] = 'invalid-email'
        response = self.client.post(self.employer_signup_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='invalid-email').exists())
        self.assertTrue('form' in response.context)

class EmployeeSignupStep3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('employee_signup_3')
        
        self.test_user = User.objects.create_user(
            username='@testuser',
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User',
            user_type='employee'
        )
        
        self.client.login(username='@testuser', password='TestPass123!')
        
        session = self.client.session
        session['signup_data'] = {
            'username': '@testuser',
            'email': 'test@example.com',
            'password1': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'country': 'US'
        }
        session['cv_filename'] = 'test_cv.pdf'
        session.save()

    def test_step3_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employee_signup.html')
        self.assertEqual(response.context['step'], 3)

    def test_step3_successful_signup(self):
        data = {
            'skills': 'Python, Django, JavaScript',
            'interests': 'Web Development, AI',
            'preferred_contract': 'FT'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('employee_dashboard'))

    def test_step3_missing_session(self):
        session = self.client.session
        session.flush()
        session.save()
        
        data = {
            'skills': 'Python, Django',
            'interests': 'Web Development',
            'preferred_contract': 'FT'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/')

    def test_step3_invalid_contract(self):
        data = {
            'skills': 'Python, Django',
            'interests': 'Web Development',
            'preferred_contract': 'INVALID'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)

class WelcomePageTest(TestCase):
    def test_welcome_page_status_code(self):
        response = self.client.get(reverse('home'))  
        self.assertEqual(response.status_code, 200)

    def test_welcome_page_template_used(self):
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home.html')  

    def test_welcome_page_links(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, reverse('employee_signup')) 
        self.assertContains(response, reverse('employer_signup'))  
        self.assertContains(response, reverse('login')) 

class ViewsTestCase(TestCase):
    def setUp(self):

        employee_user = User.objects.create_user(
            username="@employee",
            email="employee@test.com",
            password="testpass",
            first_name="John",
            last_name="Doe",
            user_type="employee"
        )
        self.employee = Employee.objects.create(
            user=employee_user,
            country="USA"
        )

        employer_user = User.objects.create_user(
            username="@employer",
            email="employer@test.com",
            password="testpass",
            first_name="Jane",
            last_name="Smith",
            user_type="employer"
        )
        self.employer = Employer.objects.create(
            user=employer_user,
            company_name="Tech Corp",
            country="UK"
        )

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_invalid_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'nonexistent@test.com',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "credentials provided were invalid")

    def test_employee_signup_get(self):
        """Test GET request to employee signup page"""
        response = self.client.get(reverse('employee_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employee_signup.html')

    def test_employee_signup_post_invalid(self):
        """Test POST request to employee signup with invalid data"""
        response = self.client.post(reverse('employee_signup'), {})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employee_signup.html')
        self.assertIn('form', response.context)

    def test_employer_signup_invalid_form(self):
        """Test employer signup with invalid form data"""
        response = self.client.post(reverse('employer_signup'), {
            'username': 'employer',
            'email': 'invalid-email',
            'password1': 'pass1',
            'password2': 'pass2',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employer_signup.html')

    def test_login_get_request(self):
        """Test GET request to login page"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_with_invalid_credentials(self):
        """Test login attempt with invalid credentials"""
        response = self.client.post(reverse('login'), {
            'username': 'nonexistent@test.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'credentials provided were invalid')

    def test_login_invalid_user_type(self):
        """Test login with a user that doesn't match known types"""
        
        admin_user = User.objects.create_user(
            username='@generic',
            email='generic@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            user_type='admin'
        )
        Admin.objects.create(user=admin_user)
        
        response = self.client.post(reverse('login'), {
            'username': '@generic',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)


class ViewsEdgeTests(TestCase):
    def setUp(self):

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
            country="US"
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
            company_name="Test Company"
        )
        
    def test_home_view(self):
        """Test the home view"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        
    def test_logout_view(self):
        """Test the logout view"""

        self.client.login(username="@employee", password="testpass123")
        response = self.client.get(reverse('logout'))
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))
        
    def test_admin_dashboard_not_admin(self):
        """Test accessing admin dashboard as non-admin"""

        self.client.login(username="@employee", password="testpass123")
        
        response = self.client.get(reverse('admin_dashboard'))
        
        self.assertEqual(response.status_code, 302)
    
    def test_verify_email_invalid_user(self):
        """Test verify_email with invalid user"""

        session = self.client.session
        session['verification_email'] = "nonexistent@test.com"
        session.save()
        
        response = self.client.post(reverse('verify_email'), {'code': '123456'})
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('employee_signup'))
        
    def test_set_new_password_without_verification(self):
        """Test set_new_password without going through verification"""
        response = self.client.get(reverse('set_new_password'))
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('password_reset'))
    
    def test_employee_dashboard_filtering(self):
        """Test the dashboard with various filters"""
        self.client.login(username="@employee", password="testpass123")
        
        job = Job.objects.create(
            name="Test Job",
            department="Engineering",
            description="Test description",
            salary=75000,
            job_type="FT",
            skills_needed="Python, Django",
            created_by=self.employer
        )
        
        filter_combinations = [
            {'search': 'Python'},
            {'job_type': 'FT'},
            {'department': 'Engineering'},
            {'min_salary': '50000'},
            {'search': 'Python', 'job_type': 'FT', 'department': 'Engineering'},
        ]
        
        for filters in filter_combinations:
            query_string = '&'.join([f"{k}={v}" for k, v in filters.items()])
            response = self.client.get(f"{reverse('employee_dashboard')}?{query_string}")
            self.assertEqual(response.status_code, 200)

class RedirectTests(TestCase):
    def setUp(self):
        
        self.admin_user = User.objects.create_user(
            username="@admin",
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
            username="@employee",
            email="employee@test.com",
            password="testpass123",
            first_name="Employee",
            last_name="User",
            user_type="employee"
        )
        Employee.objects.create(user=self.employee_user, country="US")
        
        self.employer_user = User.objects.create_user(
            username="@employer",
            email="employer@test.com",
            password="testpass123",
            first_name="Employer",
            last_name="User",
            user_type="employer"
        )
        Employer.objects.create(user=self.employer_user, company_name="Test Company")
        
    def test_get_redirect_admin(self):
        """Test get_redirect for admin users"""
        user = authenticate(username="@admin", password="testpass123")
        self.assertIsNotNone(user)
        
        response = self.client.post(reverse('login'), {
            'username': '@admin',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('admin_dashboard'))
        
    def test_get_redirect_employee(self):
        """Test get_redirect for employee users"""
        user = authenticate(username="@employee", password="testpass123")
        self.assertIsNotNone(user)
        
        response = self.client.post(reverse('login'), {
            'username': '@employee',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('employee_dashboard'))
        
    def test_get_redirect_employer(self):
        """Test get_redirect for employer users"""
        user = authenticate(username="@employer", password="testpass123")
        self.assertIsNotNone(user)
        
        response = self.client.post(reverse('login'), {
            'username': '@employer',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('employer_dashboard'))

class VerifyEmailTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        self.user = User.objects.create_user(
            username="@inactive",
            email="inactive@test.com",
            password="testpass123",
            first_name="Inactive",
            last_name="User",
            user_type="employee",
            is_active=False
        )
        
        self.code = "123456"
        self.verification = VerificationCode.objects.create(
            user=self.user,
            code=self.code,
            code_type="email_verification"
        )
        
    def test_verify_email_without_session(self):
        """Test verify_email without session data"""
        response = self.client.get(reverse('verify_email'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('employee_signup'))
        
    def test_verify_email_invalid_code(self):
        """Test verify_email with invalid code"""

        session = self.client.session
        session['verification_email'] = "inactive@test.com"
        session.save()
        
        response = self.client.post(reverse('verify_email'), {'code': 'invalid'})
        self.assertEqual(response.status_code, 200)
        
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        
    def test_verify_email_valid_code(self):
        """Test verify_email with valid code"""
        
        session = self.client.session
        session['verification_email'] = "inactive@test.com"
        session['signup_data'] = {
            'username': '@inactive',
            'email': 'inactive@test.com',
            'password1': 'testpass123',
            'first_name': 'Inactive',
            'last_name': 'User',
            'country': 'US'
        }
        session.save()
        
        response = self.client.post(reverse('verify_email'), {'code': self.code})
        self.assertEqual(response.status_code, 302)
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        
        self.verification.refresh_from_db()
        self.assertTrue(self.verification.is_used)