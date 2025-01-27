from django.test import TestCase
from app.forms.forms import EmployeeSignUpForm, EmployerSignUpForm

class SignUpFormsTest(TestCase):
    def setUp(self):
        self.valid_employee_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'country': 'US',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }
        
        self.valid_employer_data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@company.com',
            'country': 'UK',
            'company_name': 'Test Company',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }

    def test_employee_form_valid_data(self):
        form = EmployeeSignUpForm(data=self.valid_employee_data)
        self.assertTrue(form.is_valid())

    def test_employer_form_valid_data(self):
        form = EmployerSignUpForm(data=self.valid_employer_data)
        self.assertTrue(form.is_valid())

    def test_employee_form_no_data(self):
        form = EmployeeSignUpForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 5)  # email, password1, password2, first_name, last_name
        # Optionally verify specific fields
        required_fields = ['email', 'password1', 'password2', 'first_name', 'last_name']
        for field in required_fields:
            self.assertIn(field, form.errors)

    def test_employer_form_no_data(self):
        form = EmployerSignUpForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 5)  # email, password1, password2, first_name, last_name
        # Optionally verify specific fields
        required_fields = ['email', 'password1', 'password2', 'first_name', 'last_name']
        for field in required_fields:
            self.assertIn(field, form.errors)

    def test_employer_form_bootstrap_classes(self):
        form = EmployerSignUpForm()
        for field in form.fields.values():
            self.assertIn('class', field.widget.attrs)
            self.assertEqual(field.widget.attrs['class'], 'form-control')