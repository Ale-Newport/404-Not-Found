# app/tests/views/test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from app.models import Employee, Employer
from django.contrib.auth import authenticate

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

class WelcomePageTest(TestCase):
    def test_welcome_page_status_code(self):
        response = self.client.get(reverse('home'))  
        self.assertEqual(response.status_code, 200)

    def test_welcome_page_template_used(self):
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home.html')  

    def test_welcome_page_content(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, "Welcome to the Job Hiring Website") 
        self.assertContains(response, "Sign Up as Job Seeker") 
        self.assertContains(response, "Sign Up as Employer") 
        self.assertContains(response, "Log in here")  

    def test_welcome_page_links(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, reverse('employee_signup')) 
        self.assertContains(response, reverse('employer_signup'))  
        self.assertContains(response, reverse('login')) 

class ViewsTestCase(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create_user(
            email="employee@test.com",
            password="testpass",
            first_name="John",
            last_name="Doe",
            country="USA"
        )

        self.employer = Employer.objects.create_user(
            email="employer@test.com",
            password="testpass",
            first_name="Jane",
            last_name="Smith",
            country="UK",
            company_name="Tech Corp"
        )

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    """
    def test_employee_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'employee@test.com',
            'password': 'testpass',
        })
        self.assertRedirects(response, reverse('employee_dashboard'))

    def test_employer_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'employer@test.com',
            'password': 'testpass',
        })
        self.assertRedirects(response, reverse('employer_dashboard'))
    """

    def test_invalid_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'nonexistent@test.com',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password")
