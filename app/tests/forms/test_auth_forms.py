from django.test import TestCase
from app.forms import LogInForm, PasswordResetRequestForm, SetNewPasswordForm
from app.models import User, Employee
from unittest.mock import patch

class AuthFormsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="@testuser",
            email="test@example.com",
            password="TestPass123!",
            first_name="Test",
            last_name="User",
            user_type="employee"
        )
        Employee.objects.create(
            user=self.user,
            country="US"
        )
        
    def test_login_form_valid(self):
        """Test login form with valid credentials"""
        form_data = {
            'username': '@testuser',
            'password': 'TestPass123!'
        }
        form = LogInForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        user = form.get_user()
        self.assertEqual(user, self.user)
        
    def test_login_form_invalid(self):
        """Test login form with invalid credentials"""
        form_data = {
            'username': '@testuser',
            'password': 'WrongPassword'
        }
        form = LogInForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        user = form.get_user()
        self.assertIsNone(user)
        
    def test_login_form_missing_fields(self):
        """Test login form with missing fields"""
        form_data = {
            'username': '@testuser'
            # Missing password
        }
        form = LogInForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
    
    @patch('app.forms.auth_forms.ReCaptchaField.clean', return_value=True)
    def test_password_reset_request_form_valid(self, mock_recaptcha):
        """Test password reset request form with valid email"""
        form_data = {
            'email': 'test@example.com'
        }
        form = PasswordResetRequestForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_set_new_password_form_valid(self):
        """Test set new password form with valid passwords"""
        form_data = {
            'password1': 'NewPass123!',
            'password2': 'NewPass123!'
        }
        form = SetNewPasswordForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_set_new_password_form_mismatch(self):
        """Test set new password form with mismatched passwords"""
        form_data = {
            'password1': 'NewPass123!',
            'password2': 'DifferentPass123!'
        }
        form = SetNewPasswordForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
