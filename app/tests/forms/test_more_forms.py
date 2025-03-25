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
    
    def test_employee_account_update_form_password_validation(self):
        """Test password validation in EmployeeAccountUpdateForm"""
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'country': 'US',
            # no password1
            'password2': 'NewPass123'
        }
        form = EmployeeAccountUpdateForm(instance=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        
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
        
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'country': 'US',
            'password1': '123', # too short
            'password2': '123'
        }
        form = EmployeeAccountUpdateForm(instance=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)
