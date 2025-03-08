# app/tests/views/test_additional_views.py
# app/tests/views/test_more_views.py
from django.test import TestCase, Client
from django.urls import reverse
from app.models import User, Employee, Employer, Admin, Job, JobApplication, VerificationCode  # Added VerificationCode
from django.contrib.auth import authenticate, login

class RedirectTests(TestCase):
    def setUp(self):
        # Create users of different types
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
        
        # Create inactive user
        self.user = User.objects.create_user(
            username="@inactive",
            email="inactive@test.com",
            password="testpass123",
            first_name="Inactive",
            last_name="User",
            user_type="employee",
            is_active=False
        )
        
        # Create verification code
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
        # Set session data
        session = self.client.session
        session['verification_email'] = "inactive@test.com"
        session.save()
        
        # Submit invalid code
        response = self.client.post(reverse('verify_email'), {'code': 'invalid'})
        self.assertEqual(response.status_code, 200)
        
        # User should still be inactive
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        
    def test_verify_email_valid_code(self):
        """Test verify_email with valid code"""
        # Set session data
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
        
        # Submit valid code
        response = self.client.post(reverse('verify_email'), {'code': self.code})
        self.assertEqual(response.status_code, 302)
        
        # User should be active now
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        
        # Verification code should be used
        self.verification.refresh_from_db()
        self.assertTrue(self.verification.is_used)