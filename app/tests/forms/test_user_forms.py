from django.test import TestCase
from app.forms import EmployeeSignUpForm, EmployerSignUpForm
from app.models import User, Employee, Employer, Admin, Job
from unittest.mock import patch

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

    @patch('app.forms.forms.ReCaptchaField.clean', return_value=True)
    def test_employee_form_valid_data(self, mock_captcha):
        form = EmployeeSignUpForm(data=self.employee_data)
        self.assertTrue(form.is_valid())

    @patch('app.forms.forms.ReCaptchaField.clean', return_value=True)
    def test_employer_form_valid_data(self, mock_captcha):
        form = EmployerSignUpForm(data=self.employer_data)
        self.assertTrue(form.is_valid())

    @patch('app.forms.forms.ReCaptchaField.clean', return_value=True)
    def test_employee_form_no_data(self, mock_captcha):
        form = EmployeeSignUpForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 7)

    @patch('app.forms.forms.ReCaptchaField.clean', return_value=True)
    def test_employer_form_no_data(self, mock_captcha):
        form = EmployerSignUpForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 8)
