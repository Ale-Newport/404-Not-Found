from django.test import TestCase
from django.contrib.auth import get_user_model
from app.forms import EmployeeSignUpForm, EmployerSignUpForm, UserForm, EmployeeAccountUpdateForm
from app.models import User, Employee, Employer, Admin
from unittest.mock import patch, MagicMock
from django import forms

class SignUpFormsTest(TestCase):
    def setUp(self):
        self.employee_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': '@john',
            'email': 'john@example.com',
            'password1': 'testPassword',
            'password2': 'testPassword',
            'country': 'UK'
        }
        self.employer_data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'username': '@jane',
            'email': 'jane@example.com',
            'password1': 'testPassword',
            'password2': 'testPassword',
            'country': 'UK',
            'company_name': 'Smith & Co'
        }
        self.admin_data = {
            'user_type': 'admin',
            'first_name': 'Admin',
            'last_name': 'User',
            'username': '@admin',
            'email': 'admin@example.com',
            'password1': 'testPassword',
            'password2': 'testPassword',
        }
        self.inactive_user = User.objects.create_user(
            username='@inactive',
            email='inactive@example.com',
            password='testPassword',
            is_active=False
        )

    @patch('app.forms.user_forms.ReCaptchaField.clean', return_value=True)
    def test_employee_form_valid_data(self, mock_captcha):
        form = EmployeeSignUpForm(data=self.employee_data)
        self.assertTrue(form.is_valid())

    @patch('app.forms.user_forms.ReCaptchaField.clean', return_value=True)
    def test_employer_form_valid_data(self, mock_captcha):
        form = EmployerSignUpForm(data=self.employer_data)
        self.assertTrue(form.is_valid())

    @patch('app.forms.user_forms.ReCaptchaField.clean', return_value=True)
    def test_employee_form_no_data(self, mock_captcha):
        form = EmployeeSignUpForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 7)

    @patch('app.forms.user_forms.ReCaptchaField.clean', return_value=True)
    def test_employer_form_no_data(self, mock_captcha):
        form = EmployerSignUpForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 8)

    # Tests for UserForm save method with different user types
    def test_user_form_save_admin_commit_true(self):
        form = UserForm(data=self.admin_data)
        self.assertTrue(form.is_valid())
        user = form.save(commit=True)
        
        # Check main user was saved
        self.assertEqual(user.user_type, 'admin')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        
        # Check related Admin model was created
        self.assertTrue(Admin.objects.filter(user=user).exists())
        
    def test_user_form_save_employee_commit_true(self):
        data = {
            'user_type': 'employee',
            'first_name': 'Test',
            'last_name': 'Employee',
            'username': '@testemployee',
            'email': 'employee@example.com', 
            'password1': 'testPassword',
            'password2': 'testPassword',
            'country': 'US',
            'skills': 'Python, Django',
            'experience': '5 years',
            'education': 'Bachelor',
            'languages': 'English, Spanish',
            'phone': '123456789', 
            'interests': 'Coding',
            'preferred_contract': 'FT'
        }
        
        form = UserForm(data=data)
        self.assertTrue(form.is_valid())
        user = form.save(commit=True)
        
        # Check that Employee model was created with all fields
        employee = Employee.objects.get(user=user)
        self.assertEqual(employee.country, 'US')
        self.assertEqual(employee.skills, 'Python, Django')
        self.assertEqual(employee.experience, '5 years')
        self.assertEqual(employee.education, 'Bachelor')
        self.assertEqual(employee.languages, 'English, Spanish')
        self.assertEqual(employee.phone, '123456789')
        self.assertEqual(employee.interests, 'Coding')
        self.assertEqual(employee.preferred_contract, 'FT')
        
    def test_user_form_save_employer_commit_true(self):
        data = {
            'user_type': 'employer',
            'first_name': 'Test',
            'last_name': 'Employer',
            'username': '@testemployer',
            'email': 'employer@example.com',
            'password1': 'testPassword',
            'password2': 'testPassword',
            'company_name': 'Test Company',
            'country': 'CA'
        }
        
        form = UserForm(data=data)
        self.assertTrue(form.is_valid())
        user = form.save(commit=True)
        
        # Check that Employer model was created with correct fields
        employer = Employer.objects.get(user=user)
        self.assertEqual(employer.company_name, 'Test Company')
        self.assertEqual(employer.country, 'CA')
    
    # Tests for clean_username in different forms
    @patch('app.forms.user_forms.ReCaptchaField.clean', return_value=True)
    def test_employee_clean_username_already_exists(self, mock_captcha):
        # Create a user with the same username
        User.objects.create_user(
            username='@john',
            email='different@example.com',
            password='testPassword'
        )
        
        form = EmployeeSignUpForm(data=self.employee_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertEqual(form.errors['username'][0], 'A user with this username already exists.')
    
    @patch('app.forms.user_forms.ReCaptchaField.clean', return_value=True)
    def test_employee_clean_username_inactive_user(self, mock_captcha):
        # Create an inactive user with the same username
        data = self.employee_data.copy()
        data['username'] = '@inactive'
        
        form = EmployeeSignUpForm(data=data)
        self.assertTrue(form.is_valid())
        
        # Verify the inactive user was deleted
        self.assertFalse(User.objects.filter(username='@inactive').exists())
    
    @patch('app.forms.user_forms.ReCaptchaField.clean', return_value=True)
    def test_employer_clean_username_already_exists(self, mock_captcha):
        # Create a user with the same username
        User.objects.create_user(
            username='@jane',
            email='different@example.com',
            password='testPassword'
        )
        
        form = EmployerSignUpForm(data=self.employer_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertEqual(form.errors['username'][0], 'A user with this username already exists.')
    
    # Tests for clean_email in different forms
    @patch('app.forms.user_forms.ReCaptchaField.clean', return_value=True)
    def test_employee_clean_email_already_exists(self, mock_captcha):
        # Create a user with the same email
        User.objects.create_user(
            username='@different',
            email='john@example.com',
            password='testPassword'
        )
        
        form = EmployeeSignUpForm(data=self.employee_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertEqual(form.errors['email'][0], 'A user with this email already exists.')
    
    @patch('app.forms.user_forms.ReCaptchaField.clean', return_value=True)
    def test_employee_clean_email_inactive_user(self, mock_captcha):
        # Create an inactive user with the same email
        data = self.employee_data.copy()
        data['email'] = 'inactive@example.com'
        
        form = EmployeeSignUpForm(data=data)
        self.assertTrue(form.is_valid())
        
        # Verify the inactive user was deleted
        self.assertFalse(User.objects.filter(email='inactive@example.com').exists())
    
    @patch('app.forms.user_forms.ReCaptchaField.clean', return_value=True)
    def test_employer_clean_email_already_exists(self, mock_captcha):
        # Create a user with the same email
        User.objects.create_user(
            username='@different',
            email='jane@example.com',
            password='testPassword'
        )
        
        form = EmployerSignUpForm(data=self.employer_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertEqual(form.errors['email'][0], 'A user with this email already exists.')
    
    # Tests for password validation in EmployeeAccountUpdateForm
    def test_employee_account_update_form_password_validation(self):
        user = User.objects.create_user(
            username='@update',
            email='update@example.com',
            password='testPassword'
        )
        
        # Test missing password2
        data = {
            'first_name': 'Update',
            'last_name': 'User',
            'email': 'update@example.com',
            'country': 'UK',
            'password1': 'newPassword',  # Only password1, missing password2
        }
        
        form = EmployeeAccountUpdateForm(data=data, instance=user)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        self.assertEqual(form.errors['password2'][0], 'Please confirm your new password')
    
    # Test for EmployerSignUpForm save method
    @patch('app.forms.user_forms.ReCaptchaField.clean', return_value=True)
    def test_employer_signup_form_save_method(self, mock_captcha):
        form = EmployerSignUpForm(data=self.employer_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        
        # Verify user was created correctly
        self.assertEqual(user.user_type, 'employer')
        self.assertEqual(user.username, '@jane')
        
        # Verify employer profile was created
        employer = Employer.objects.get(user=user)
        self.assertEqual(employer.company_name, 'Smith & Co')
        self.assertEqual(employer.country, 'UK')

    def test_user_form_employer_without_company_name(self):
        data = {
            'user_type': 'employer',
            'first_name': 'Test',
            'last_name': 'User',
            'username': '@testuser',
            'email': 'test@example.com',
            'password1': 'testPassword',
            'password2': 'testPassword',
            # Missing company_name
        }
        form = UserForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('company_name', form.errors)
        self.assertEqual(form.errors['company_name'][0], 'Company name is required for Employer accounts')

    def test_user_form_clean_admin_flags(self):
        form = UserForm(data=self.admin_data)
        self.assertTrue(form.is_valid())
        # Check that clean method set is_staff and is_superuser to True
        cleaned_data = form.cleaned_data
        self.assertTrue(cleaned_data['is_staff'])
        self.assertTrue(cleaned_data['is_superuser'])

    def test_user_form_save_with_commit_false(self):
        # Test for admin
        form = UserForm(data=self.admin_data)
        self.assertTrue(form.is_valid())
        user = form.save(commit=False)
        
        # Verify properties were set but user wasn't saved
        self.assertEqual(user.user_type, 'admin')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(User.objects.filter(username='@admin').count(), 0)
        self.assertEqual(Admin.objects.count(), 0)
        
        # Test for employee
        employee_data = {
            'user_type': 'employee',
            'first_name': 'Test',
            'last_name': 'Employee',
            'username': '@employee',
            'email': 'test@employee.com',
            'password1': 'testPassword',
            'password2': 'testPassword'
        }
        form = UserForm(data=employee_data)
        self.assertTrue(form.is_valid())
        user = form.save(commit=False)
        
        # Verify user_type was set but user and employee weren't saved
        self.assertEqual(user.user_type, 'employee')
        self.assertEqual(User.objects.filter(username='@employee').count(), 0)
        self.assertEqual(Employee.objects.count(), 0)
        
        # Test for employer
        employer_data = {
            'user_type': 'employer',
            'first_name': 'Test',
            'last_name': 'Employer',
            'username': '@employer',
            'email': 'test@employer.com',
            'password1': 'testPassword',
            'password2': 'testPassword',
            'company_name': 'Test Company'
        }
        form = UserForm(data=employer_data)
        self.assertTrue(form.is_valid())
        user = form.save(commit=False)
        
        # Verify user_type was set but user and employer weren't saved
        self.assertEqual(user.user_type, 'employer')
        self.assertEqual(User.objects.filter(username='@employer').count(), 0)
        self.assertEqual(Employer.objects.count(), 0)

    @patch('app.forms.user_forms.ReCaptchaField.clean', return_value=True)
    def test_employee_signup_form_clean_username(self, mock_captcha):
        # First test: username doesn't exist
        form = EmployeeSignUpForm(data=self.employee_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['username'], '@john')
        
        # Second test: direct call to clean_username to verify it's working
        User.objects.create_user(
            username='@testuser',
            email='test@example.com',
            password='testPassword'
        )
        form = EmployeeSignUpForm()
        form.cleaned_data = {'username': '@testuser'}
        
        with self.assertRaises(forms.ValidationError) as context:
            form.clean_username()
        
        self.assertEqual(str(context.exception.messages[0]), 'A user with this username already exists.')

    # Test for EmployeeSignUpForm.clean_email
    @patch('app.forms.user_forms.ReCaptchaField.clean', return_value=True)
    def test_employee_signup_form_clean_email_logic(self, mock_captcha):
        # Direct call to clean_email to verify its logic
        form = EmployeeSignUpForm()
        form.cleaned_data = {'email': 'new@example.com'}
        
        # Should return email when no matching user exists
        self.assertEqual(form.clean_email(), 'new@example.com')
        
        # Create an active user
        User.objects.create_user(
            username='@active',
            email='active@example.com',
            password='testPassword',
            is_active=True
        )
        
        form.cleaned_data = {'email': 'active@example.com'}
        with self.assertRaises(forms.ValidationError) as context:
            form.clean_email()
        self.assertEqual(str(context.exception.messages[0]), 'A user with this email already exists.')

    # Test for EmployeeAccountUpdateForm password validation
    def test_employee_account_update_form_missing_password1(self):
        user = User.objects.create_user(
            username='@update',
            email='update@example.com',
            password='testPassword'
        )
        
        # Test missing password1 but providing password2
        data = {
            'first_name': 'Update',
            'last_name': 'User',
            'email': 'update@example.com',
            'country': 'UK',
            'password2': 'newPassword',  # Only providing password2
        }
        
        form = EmployeeAccountUpdateForm(data=data, instance=user)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)
        self.assertEqual(form.errors['password1'][0], 'Please enter your new password')

    @patch('app.forms.user_forms.ReCaptchaField.clean', return_value=True)
    def test_employer_signup_form_init_method(self, mock_captcha):
        form = EmployerSignUpForm()
        
        # Check that widget attributes were set correctly
        for field_name, field in form.fields.items():
            if field_name != 'captcha':
                self.assertIn('class', field.widget.attrs)
                self.assertEqual(field.widget.attrs['class'], 'form-control')
                self.assertIn('placeholder', field.widget.attrs)
                self.assertTrue(field.widget.attrs['placeholder'].startswith('Enter'))

    @patch('app.forms.user_forms.ReCaptchaField.clean', return_value=True)
    def test_employer_signup_form_clean_method(self, mock_captcha):
        form = EmployerSignUpForm(data=self.employer_data)
        self.assertTrue(form.is_valid())
        
        # Directly call the clean method to verify it works
        cleaned_data = form.clean()
        # Verify clean returns the cleaned data
        self.assertEqual(cleaned_data['first_name'], 'Jane')
        self.assertEqual(cleaned_data['company_name'], 'Smith & Co')