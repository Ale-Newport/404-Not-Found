# app/tests/views/test_auth_views.py
from django.test import TestCase, Client
from django.urls import reverse
from app.models import User, Employee, Employer, Admin, VerificationCode
from django.contrib.auth import get_user_model
from django.core import mail

class PasswordResetTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='@testuser',
            email='test@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User',
            user_type='employee'
        )
        
        self.password_reset_url = reverse('password_reset')
        self.verify_code_url = reverse('verify_reset_code')
        self.set_password_url = reverse('set_new_password')
        
    def test_password_reset_request_page(self):
        """Test that the password reset request page loads"""
        response = self.client.get(self.password_reset_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password_reset.html')
        
   # app/tests/views/test_auth_views.py
    def test_password_reset_request_submission(self):
        """Test submitting a password reset request"""
        from unittest.mock import patch, Mock
        from app.forms.forms import PasswordResetRequestForm
        
        # Create a mock form that always passes validation
        mock_form = Mock(spec=PasswordResetRequestForm)
        mock_form.is_valid.return_value = True
        mock_form.cleaned_data = {'email': 'test@example.com'}
        
        # Replace the form with our mock in the view
        with patch('app.views.views.PasswordResetRequestForm', return_value=mock_form):
            response = self.client.post(self.password_reset_url, {
                'email': 'test@example.com',
                'captcha': 'PASSED'
            })
            
            # Now it should redirect
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, reverse('verify_reset_code'))
        
    def test_verify_reset_code_page(self):
        """Test that verify reset code page loads when session data exists"""
        session = self.client.session
        session['reset_email'] = 'test@example.com'
        session.save()
        
        response = self.client.get(self.verify_code_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'verify_reset_code.html')
        
    def test_verify_reset_code_without_session(self):
        """Test that verify reset code redirects when no session data"""
        response = self.client.get(self.verify_code_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('password_reset'))
        
    def test_verify_reset_code_submission(self):
        """Test submitting a valid reset code"""
        # Set up session
        session = self.client.session
        session['reset_email'] = 'test@example.com'
        session.save()
        
        # Create verification code
        code = '123456'
        verification = VerificationCode.objects.create(
            user=self.user,
            code=code,
            code_type='password_reset'
        )
        
        # Submit code
        response = self.client.post(self.verify_code_url, {'code': code})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('set_new_password'))
        
        # Check that code was marked as used
        verification.refresh_from_db()
        self.assertTrue(verification.is_used)
        
    def test_set_new_password_page(self):
        """Test that set new password page loads when session data exists"""
        session = self.client.session
        session['reset_email'] = 'test@example.com'
        session['reset_code_verified'] = True
        session.save()
        
        response = self.client.get(self.set_password_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'set_new_password.html')
        
    def test_set_new_password_submission(self):
        """Test setting a new password"""
        # Set up session
        session = self.client.session
        session['reset_email'] = 'test@example.com'
        session['reset_code_verified'] = True
        session.save()
        
        # Submit new password
        response = self.client.post(self.set_password_url, {
            'password1': 'NewPassword123',
            'password2': 'NewPassword123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        
        # Check that password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword123'))


class EmployeeSignupTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('employee_signup')
        self.verify_email_url = reverse('verify_email')
        self.upload_cv_url = reverse('employee_signup_2')
        self.review_cv_url = reverse('employee_signup_3')
        
    def test_signup_page_loads(self):
        """Test that the signup page loads correctly"""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employee_signup.html')
        self.assertEqual(response.context['step'], 1)
        
    def test_valid_signup_submission(self):
        """Test submitting valid signup data"""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': '@johndoe',
            'email': 'john@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'country': 'US',
        }
        
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('verify_email'))
        
        # Check user was created but inactive
        self.assertTrue(User.objects.filter(username='@johndoe').exists())
        user = User.objects.get(username='@johndoe')
        self.assertFalse(user.is_active)
        
        # Check verification code was created
        self.assertTrue(VerificationCode.objects.filter(
            user=user,
            code_type='email_verification'
        ).exists())
        
    def test_verify_email_page(self):
        """Test that verify email page loads when session data exists"""
        session = self.client.session
        session['verification_email'] = 'john@example.com'
        session['signup_data'] = {
            'username': '@johndoe',
            'email': 'john@example.com',
            'password1': 'TestPass123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'country': 'US'
        }
        session.save()
        
        response = self.client.get(self.verify_email_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'verify_email.html')
        
    def test_verify_email_without_session(self):
        """Test that verify email redirects when no session data"""
        response = self.client.get(self.verify_email_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('employee_signup'))