from django.test import TestCase
from app.forms.forms import EmployerSignUpForm, JobForm
from app.models import User, Employer, Job
from decimal import Decimal
from unittest.mock import patch

class EmployerFormsTest(TestCase):
    def setUp(self):
        self.employer_user = User.objects.create_user(
            username="@employer",
            email="employer@test.com",
            password="testpass123",
            first_name="Test",
            last_name="Employer",
            user_type="employer"
        )
        self.employer = Employer.objects.create(
            user=self.employer_user,
            company_name="Test Company",
            country="US"
        )
        
        self.valid_employer_data = {
            'first_name': 'John',
            'last_name': 'Smith',
            'username': '@johnsmith',
            'email': 'john@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'country': 'US',
            'company_name': 'Smith Industries'
        }
        
        self.valid_job_data = {
            'name': 'Software Developer',
            'department': 'Engineering',
            'description': 'Developing software applications',
            'salary': '75000',
            'job_type': 'FT',
            'skills_needed': 'Python, Django',
            'skills_wanted': 'JavaScript, React'
        }
    
    @patch('app.forms.forms.ReCaptchaField.clean', return_value=True)
    def test_employer_signup_form_valid(self, mock_recaptcha):
        """Test that the employer signup form is valid with correct data"""
        form = EmployerSignUpForm(data=self.valid_employer_data)
        self.assertTrue(form.is_valid())
    
    @patch('app.forms.forms.ReCaptchaField.clean', return_value=True)
    def test_employer_signup_form_password_mismatch(self, mock_recaptcha):
        """Test that passwords must match"""
        data = self.valid_employer_data.copy()
        data['password2'] = 'DifferentPass123!'
        form = EmployerSignUpForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    @patch('app.forms.forms.ReCaptchaField.clean', return_value=True)
    def test_employer_signup_form_username_validation(self, mock_recaptcha):
        """Test that username must start with @"""
        data = self.valid_employer_data.copy()
        data['username'] = 'johnsmith'
        form = EmployerSignUpForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
    
    @patch('app.forms.forms.ReCaptchaField.clean', return_value=True)
    def test_employer_signup_form_email_unique(self, mock_recaptcha):
        """Test that email must be unique"""
        data = self.valid_employer_data.copy()
        data['email'] = 'employer@test.com' # Already exists
        form = EmployerSignUpForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    @patch('app.forms.forms.ReCaptchaField.clean', return_value=True)
    def test_employer_signup_form_username_unique(self, mock_recaptcha):
        """Test that username must be unique"""
        data = self.valid_employer_data.copy()
        data['username'] = '@employer' # Already exists
        form = EmployerSignUpForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_job_form_valid(self):
        """Test that the job form is valid with correct data"""
        form = JobForm(data=self.valid_job_data)
        self.assertTrue(form.is_valid())
    
    def test_job_form_invalid_salary(self):
        """Test that salary must be a number"""
        data = self.valid_job_data.copy()
        data['salary'] = 'not-a-number'
        form = JobForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('salary', form.errors)
    
    def test_job_form_missing_required_field(self):
        """Test that required fields are enforced"""
        data = self.valid_job_data.copy()
        data.pop('name')
        form = JobForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_job_form_save(self):
        """Test that form save creates a job"""
        form = JobForm(data=self.valid_job_data)
        self.assertTrue(form.is_valid())
        job = form.save(commit=False)
        job.created_by = self.employer
        job.save()
        self.assertEqual(Job.objects.count(), 1)
        saved_job = Job.objects.first()
        self.assertEqual(saved_job.name, 'Software Developer')
        self.assertEqual(saved_job.department, 'Engineering')
        self.assertEqual(saved_job.salary, Decimal('75000'))
        self.assertEqual(saved_job.created_by, self.employer)