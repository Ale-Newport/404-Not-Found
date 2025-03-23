# app/tests/forms/test_account_form.py
from django.test import TestCase
from app.forms import EmployeeAccountUpdateForm
from app.models import User, Employee

class EmployeeAccountUpdateFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="@testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            user_type="employee"
        )
        self.employee = Employee.objects.create(
            user=self.user,
            country="US"
        )
        
    def test_form_valid_data(self):
        """Test form with valid data"""
        form_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
            'country': 'UK'
        }
        form = EmployeeAccountUpdateForm(instance=self.user, data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_form_duplicate_email(self):
        """Test form with duplicate email"""
        # Create another user with different email
        other_user = User.objects.create_user(
            username="@otheruser",
            email="other@example.com",
            password="testpass123",
            user_type="employee"
        )
        
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'other@example.com',  # Already used by other user
            'country': 'US'
        }
        form = EmployeeAccountUpdateForm(instance=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        
    def test_form_password_change(self):
        """Test form with password change"""
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'country': 'US',
            'password1': 'NewPass123!',
            'password2': 'NewPass123!'
        }
        form = EmployeeAccountUpdateForm(instance=self.user, data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_form_password_mismatch(self):
        """Test form with mismatched passwords"""
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'country': 'US',
            'password1': 'NewPass123!',
            'password2': 'DifferentPass123!'
        }
        form = EmployeeAccountUpdateForm(instance=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        
    def test_form_save(self):
        """Test form save method"""
        form_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
            'country': 'UK',
            'password1': 'NewPass123!',
            'password2': 'NewPass123!'
        }
        form = EmployeeAccountUpdateForm(instance=self.user, data=form_data)
        self.assertTrue(form.is_valid())
        
        # Save form
        user = form.save()
        
        # Check that user was updated
        self.assertEqual(user.first_name, 'Updated')
        self.assertEqual(user.last_name, 'Name')
        self.assertEqual(user.email, 'updated@example.com')
        
        # Check that password was changed
        self.assertTrue(user.check_password('NewPass123!'))
