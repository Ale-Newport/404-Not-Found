# app/tests/forms/test_more_forms.py
from django.test import TestCase
from app.forms import EmployeeAccountUpdateForm
from app.models import User, Employee

class MoreFormsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="@testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            user_type="employee"
        )
        Employee.objects.create(user=self.user, country="US")
    
    # app/tests/forms/test_more_forms.py
    def test_employee_account_update_form_password_validation(self):
        """Test password validation in EmployeeAccountUpdateForm"""
        # Test when password2 exists but not password1
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'country': 'US',
            # No password1
            'password2': 'NewPass123'
        }
        form = EmployeeAccountUpdateForm(instance=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)  # Changed from password1 to password2
        
        # Test when passwords don't match
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'country': 'US',
            'password1': 'NewPass123',
            'password2': 'DifferentPass123'
        }
        form = EmployeeAccountUpdateForm(instance=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        
        # Test password validation failure
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'country': 'US',
            'password1': '123',  # Too short
            'password2': '123'
        }
        form = EmployeeAccountUpdateForm(instance=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)
