from django.test import TestCase
from app.forms import JobApplicationForm
from app.models import User, Employee, Employer, Job
from django.core.files.uploadedfile import SimpleUploadedFile

class JobApplicationFormTest(TestCase):
    def setUp(self):
        employee_user = User.objects.create_user(
            username="@employee",
            email="employee@test.com",
            password="testpass123",
            first_name="Test",
            last_name="Employee",
            user_type="employee"
        )
        self.employee = Employee.objects.create(
            user=employee_user,
            country="US",
            skills="Python, Django"
        )
        
        employer_user = User.objects.create_user(
            username="@employer",
            email="employer@test.com",
            password="testpass123",
            first_name="Test",
            last_name="Employer",
            user_type="employer"
        )
        self.employer = Employer.objects.create(
            user=employer_user,
            company_name="Test Company",
            country="US"
        )
        
        self.job = Job.objects.create(
            name="Test Developer",
            department="Engineering",
            description="Test job description",
            salary=75000,
            job_type="FT",
            skills_needed="Python, Django",
            created_by=self.employer
        )
        
        self.valid_data = {
            'cover_letter': 'I am applying for this position',
            'full_name': 'Test Employee',
            'email': 'employee@test.com',
            'phone': '555-1234',
            'country': 'US',
            'current_position': 'Junior Developer',
            'skills': 'Python, Django, JavaScript',
            'experience': '2 years of experience',
            'education': 'BS Computer Science',
            'portfolio_url': 'https://portfolio.example.com',
            'linkedin_url': 'https://linkedin.com/in/test-employee'
        }
        
    def test_job_application_form_valid(self):
        """Test job application form with valid data"""
        form = JobApplicationForm(data=self.valid_data, employee=self.employee)
        self.assertTrue(form.is_valid())
        
    def test_job_application_form_with_file(self):
        """Test job application form with CV file"""
        data = self.valid_data.copy()
        cv_content = b"This is a test CV file"
        cv_file = SimpleUploadedFile("test_cv.pdf", cv_content, content_type="application/pdf")
        
        form = JobApplicationForm(data=data, files={'custom_cv': cv_file}, employee=self.employee)
        self.assertTrue(form.is_valid())
        
    def test_job_application_form_prefill(self):
        """Test that form is pre-filled with employee data"""
        self.employee.phone = '555-1234'
        self.employee.save()
        
        form = JobApplicationForm(employee=self.employee)
        
        self.assertEqual(form.fields['full_name'].initial, 'Test Employee')
        self.assertEqual(form.fields['email'].initial, 'employee@test.com')
        self.assertEqual(form.fields['country'].initial, 'US')
        self.assertEqual(form.fields['skills'].initial, 'Python, Django')
