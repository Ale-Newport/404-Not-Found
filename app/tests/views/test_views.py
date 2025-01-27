# app/tests/views/test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from app.models import Employee, Employer

class SignUpViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.employee_signup_url = reverse('employee_signup')
        self.employer_signup_url = reverse('employer_signup')
        
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
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Employee.objects.filter(email='john@example.com').exists())

    def test_employer_signup_POST_valid(self):
        response = self.client.post(self.employer_signup_url, self.valid_employer_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Employer.objects.filter(email='jane@company.com').exists())

    def test_employee_signup_POST_invalid(self):
        invalid_data = self.valid_employee_data.copy()
        invalid_data['email'] = 'invalid-email'
        response = self.client.post(self.employee_signup_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Employee.objects.filter(email='invalid-email').exists())
        self.assertTrue('form' in response.context)

    def test_employer_signup_POST_invalid(self):
        invalid_data = self.valid_employer_data.copy()
        invalid_data['email'] = 'invalid-email'
        response = self.client.post(self.employer_signup_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Employer.objects.filter(email='invalid-email').exists())
        self.assertTrue('form' in response.context)