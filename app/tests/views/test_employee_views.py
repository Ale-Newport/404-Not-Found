from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from app.models import User, Employee, Job, Employer
import os
from django.conf import settings
from app.forms import EmployeeSignUpForm
from unittest.mock import patch
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.test.client import RequestFactory


class EmployeeViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('employee_signup')
        
        self.employee_user = User.objects.create_user(
            username="@employeetest",
            email="employee@test.com",
            password="testpass123",
            first_name="Test",
            last_name="Employee",
            user_type="employee"
        )
        self.employee = Employee.objects.create(
            user=self.employee_user,
            country="US",
            skills="Python, Django"
        )
        
        self.update_url = reverse('employee_update')
        self.upload_cv_url = reverse('employee_signup_2')
        self.review_cv_url = reverse('employee_signup_3')
        
    def test_employee_update_get(self):
        """Test getting the employee update form"""
        self.client.login(username="@employeetest", password="testpass123")
        response = self.client.get(self.update_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employee/employee_update_details.html')
        self.assertTrue('form' in response.context)
        
    def test_employee_update_post(self):
        """Test updating employee account details"""
        self.client.login(username="@employeetest", password="testpass123")
        
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@test.com',
            'country': 'UK'
        }
        
        response = self.client.post(self.update_url, data)
        self.assertEqual(response.status_code, 302)
        
        self.employee_user.refresh_from_db()
        self.employee.refresh_from_db()
        
        self.assertEqual(self.employee_user.first_name, 'Updated')
        self.assertEqual(self.employee_user.last_name, 'Name')
        self.assertEqual(self.employee_user.email, 'updated@test.com')
        self.assertEqual(self.employee.country, 'UK')
        
    def test_employee_update_password(self):
        """Test updating employee password"""
        self.client.login(username="@employeetest", password="testpass123")
        
        data = {
            'first_name': 'Test',
            'last_name': 'Employee',
            'email': 'employee@test.com',
            'country': 'US',
            'password1': 'NewPass123!',
            'password2': 'NewPass123!'
        }
        
        response = self.client.post(self.update_url, data)
        
        self.assertEqual(response.status_code, 302)
        
        self.employee_user.refresh_from_db()
        self.assertTrue(self.employee_user.check_password('NewPass123!'))
        
    def test_upload_cv_get(self):
        """Test getting the upload CV page"""
        self.client.login(username="@employeetest", password="testpass123")
        
        session = self.client.session
        session['signup_data'] = {
            'username': '@employeetest',
            'email': 'employee@test.com',
            'password1': 'testpass123',
            'first_name': 'Test',
            'last_name': 'Employee',
            'country': 'US'
        }
        session.save()
        
        response = self.client.get(self.upload_cv_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employee/employee_signup.html')
        self.assertEqual(response.context['step'], 2)
        
    def test_upload_cv_post(self):
        """Test uploading a CV file"""
        self.client.login(username="@employeetest", password="testpass123")
        
        cv_content = b"This is a test CV file"
        cv_file = SimpleUploadedFile("test_cv.pdf", cv_content, content_type="application/pdf")
        
        uploads_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        
        response = self.client.post(self.upload_cv_url, {'cv': cv_file})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('employee_signup_3'))
        
        self.assertTrue('cv_filename' in self.client.session)
        
    def test_review_cv_data_get(self):
        """Test getting the review CV data page"""
        self.client.login(username="@employeetest", password="testpass123")
        
        session = self.client.session
        session['cv_filename'] = "uploads/test_cv.pdf"
        session.save()
        
        response = self.client.get(self.review_cv_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employee/employee_signup.html')
        self.assertEqual(response.context['step'], 3)
        
    def test_review_cv_data_post(self):
        """Test submitting review CV data"""
        self.client.login(username="@employeetest", password="testpass123")
        
        session = self.client.session
        session['cv_filename'] = "uploads/test_cv.pdf"
        session.save()
        
        data = {
            'skills': 'Python, Django, JavaScript',
            'experience': 'Developer for 5 years',
            'education': 'BS Computer Science',
            'phone': '555-1234',
            'interests': 'Coding, Reading',
            'preferred_contract': 'FT'
        }
        
        response = self.client.post(self.review_cv_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('employee_dashboard'))
        
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.skills, 'Python, Django, JavaScript')
        self.assertEqual(self.employee.experience, 'Developer for 5 years')
        self.assertEqual(self.employee.education, 'BS Computer Science')
        self.assertEqual(self.employee.phone, '555-1234')
        self.assertEqual(self.employee.interests, 'Coding, Reading')
        self.assertEqual(self.employee.preferred_contract, 'FT')


    def test_signup_get_request(self):
        """Test that the signup page loads correctly with GET request"""
        response = self.client.get(self.signup_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employee/employee_signup.html')
        self.assertIsInstance(response.context['form'], EmployeeSignUpForm)
        self.assertEqual(response.context['step'], 1)
    
    @patch('app.views.employee_views.create_and_send_code_email')
    @patch('app.forms.user_forms.ReCaptchaField.clean', return_value=True)
    def test_signup_post_success(self, mock_send_email, mock_recaptcha):
        """Test successful employee signup submission"""
        mock_send_email.return_value = True
        
        initial_user_count = User.objects.count()
        form_data = {
            'username': '@newemployee',
            'email': 'newemployee@test.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'Employee',
            'country': 'US'
        }
        
        response = self.client.post(self.signup_url, form_data)
        
        # Check redirection to verify_email
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('verify_email'))
        
        # Check that a new user was created
        self.assertEqual(User.objects.count(), initial_user_count + 1)
        
        # Check that the created user has correct data
        new_user = User.objects.get(username='@newemployee')
        self.assertEqual(new_user.email, 'newemployee@test.com')
        self.assertEqual(new_user.first_name, 'New')
        self.assertEqual(new_user.last_name, 'Employee')
        self.assertEqual(new_user.user_type, 'employee')
        self.assertFalse(new_user.is_active)  # User should be inactive until email verification
        
        # Check that the session contains the signup data
        self.assertTrue('signup_data' in self.client.session)
        self.assertEqual(self.client.session['signup_data']['username'], '@newemployee')
    
    @patch('app.helper.create_and_send_code_email', return_value=False)
    def test_signup_post_email_failure(self, mock_send_email):
        """Test employee signup when email sending fails"""
        
        initial_user_count = User.objects.count()
        form_data = {
            'username': '@newemployee',
            'email': 'newemployee@testcom',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'Employee',
            'country': 'US',
        }
        
        response = self.client.post(self.signup_url, form_data)
        
        # Should stay on the same page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employee/employee_signup.html')
        
        # Check that no new user remains (should be created then deleted)
        self.assertEqual(User.objects.count(), initial_user_count)
    
    def test_signup_post_invalid_form(self):
        """Test employee signup with invalid form data"""
        # Count users before the test
        initial_user_count = User.objects.count()
        
        # Invalid signup form data (missing required fields)
        form_data = {
            'username': '@newemployee',
            'email': 'newemployee@test.com',
            # Missing password fields
            'first_name': 'New',
            # Missing last_name
            'country': 'US',
        }
        
        response = self.client.post(self.signup_url, form_data)
        
        # Should stay on the same page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employee/employee_signup.html')
        
        # Check that form has errors
        self.assertTrue(response.context['form'].errors)
        
        # Check that no new user was created
        self.assertEqual(User.objects.count(), initial_user_count)
    
    def test_signup_post_password_mismatch(self):
        """Test employee signup with mismatched passwords"""
        # Count users before the test
        initial_user_count = User.objects.count()
        
        # Signup form data with mismatched passwords
        form_data = {
            'username': '@newemployee',
            'email': 'newemployee@test.com',
            'password1': 'SecurePass123!',
            'password2': 'DifferentPass123!',  # Different from password1
            'first_name': 'New',
            'last_name': 'Employee',
            'country': 'US',
        }
        
        response = self.client.post(self.signup_url, form_data)
        
        # Should stay on the same page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employee/employee_signup.html')
        
        # Check that form has password error
        self.assertTrue('password2' in response.context['form'].errors)
        
        # Check that no new user was created
        self.assertEqual(User.objects.count(), initial_user_count)
    
    def test_signup_post_existing_username(self):
        """Test employee signup with an existing username"""
        # Create a user first
        User.objects.create_user(
            username='@existinguser',
            email='existing@test.com',
            password='testpass123',
            first_name='Existing',
            last_name='User',
            user_type='employee'
        )
        
        # Count users before the test
        initial_user_count = User.objects.count()
        
        # Signup form data with existing username
        form_data = {
            'username': '@existinguser',  # Already exists
            'email': 'newemployee@test.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'Employee',
            'country': 'US',
        }
        
        response = self.client.post(self.signup_url, form_data)
        
        # Should stay on the same page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employee/employee_signup.html')
        
        # Check that form has username error
        self.assertTrue('username' in response.context['form'].errors)
        
        # Check that no new user was created
        self.assertEqual(User.objects.count(), initial_user_count)
    
    def test_signup_post_existing_email(self):
        """Test employee signup with an existing email"""
        # Create a user first
        User.objects.create_user(
            username='@existinguser',
            email='existing@test.com',
            password='testpass123',
            first_name='Existing',
            last_name='User',
            user_type='employee'
        )
        
        # Count users before the test
        initial_user_count = User.objects.count()
        
        # Signup form data with existing email
        form_data = {
            'username': '@newemployee',
            'email': 'existing@test.com',  # Already exists
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'Employee',
            'country': 'US',
        }
        
        response = self.client.post(self.signup_url, form_data)
        
        # Should stay on the same page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employee/employee_signup.html')
        
        # Check that form has email error
        self.assertTrue('email' in response.context['form'].errors)
        
        # Check that no new user was created
        self.assertEqual(User.objects.count(), initial_user_count)

class EmployeeViewsEdgeCasesTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        
        # Create employee user
        self.employee_user = User.objects.create_user(
            username="@employeetest",
            email="employee@test.com",
            password="testpass123",
            first_name="Test",
            last_name="Employee",
            user_type="employee"
        )
        self.employee = Employee.objects.create(
            user=self.employee_user,
            country="US",
            skills="Python, Django"
        )
        
        # Create some jobs for testing
        self.employer_user = User.objects.create_user(
            username="@employertest",
            email="employer@test.com",
            password="testpass123",
            first_name="Test",
            last_name="Employer",
            user_type="employer"
        )
        self.employer = Employer.objects.create(
            user=self.employer_user,
            country="US",
            company_name="Test Company"
        )
        
        # Create test upload directory if it doesn't exist
        self.upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
        os.makedirs(self.upload_dir, exist_ok=True)
        
        # URLs
        self.upload_cv_url = reverse('employee_signup_2')
        self.review_cv_url = reverse('employee_signup_3')
        self.dashboard_url = reverse('employee_dashboard')
        
    def add_session_to_request(self, request):
        """Helper method to add session to request"""
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        
    def add_message_middleware(self, request):
        """Helper method to add message middleware to request"""
        middleware = MessageMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        
    def test_upload_cv_exception_handling(self):
        """Test exception handling in upload_cv view (lines 50-52)"""
        # Create a request with a file that will cause an exception
        with patch('django.core.files.storage.default_storage.save') as mock_save:
            # Simulate an exception during file saving
            mock_save.side_effect = Exception("Test storage exception")
            
            # Create a file upload
            cv_file = SimpleUploadedFile(
                "test_cv.pdf", 
                b"file content", 
                content_type="application/pdf"
            )
            
            response = self.client.post(
                self.upload_cv_url,
                {'cv': cv_file}
            )
            
            # Should render the template with step 2
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'employee/employee_signup.html')
            self.assertEqual(response.context['step'], 2)
            
    def test_upload_cv_get_request(self):
        """Test GET request to upload_cv view (lines 69-70)"""
        response = self.client.get(self.upload_cv_url)
        
        # Should render the template with step 2
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employee/employee_signup.html')
        self.assertEqual(response.context['step'], 2)
        
    def test_review_cv_data_unauthenticated(self):
        """Test review_cv_data with unauthenticated user (lines 80-82)"""
        # Set up session data
        session = self.client.session
        session['cv_filename'] = 'uploads/test_cv.pdf'
        session.save()
        
        # Submit form without being logged in
        form_data = {
            'skills': 'Python, Django',
            'experience': '5 years',
            'education': 'BS in Computer Science',
            'phone': '555-1234',
            'preferred_contract': 'FT'
        }
        
        response = self.client.post(self.review_cv_url, form_data)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        
    def test_employee_dashboard_unauthorized_user(self):
        """Test employee_dashboard with unauthorized user (line 132)"""
        # Create a non-employee user
        other_user = User.objects.create_user(
            username="@otheruser",
            email="other@test.com",
            password="testpass123",
            first_name="Other",
            last_name="User",
            user_type="employer"  # Not an employee
        )
        
        # Log in as the non-employee user
        self.client.login(username="@otheruser", password="testpass123")
        
        # Try to access employee dashboard
        response = self.client.get(self.dashboard_url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        
    @patch('app.services.job_matcher.JobMatcher.match_employee_to_jobs')
    def test_employee_dashboard_suitable_tab(self, mock_match):
        """Test employee_dashboard with suitable tab (lines 150-151)"""
        # Mock the job matcher
        mock_match.return_value = []
        
        # Log in as employee
        self.client.login(username="@employeetest", password="testpass123")
        
        # Create test job
        job = Job.objects.create(
            name="Test Job",
            department="IT",
            description="Test job description",
            salary=50000,
            job_type="FT",
            skills_needed="Python, Django",
            country="US",
            created_by=self.employer
        )
        
        # Access dashboard with suitable tab
        response = self.client.get(self.dashboard_url + '?tab=suitable')
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employee/employee_dashboard.html')
        self.assertEqual(response.context['active_tab'], 'suitable')
        self.assertIsNotNone(response.context['job_matches'])
        
    def test_employee_dashboard_with_filters(self):
        """Test employee_dashboard with various filters"""
        # Log in as employee
        self.client.login(username="@employeetest", password="testpass123")
        
        # Create test jobs
        Job.objects.create(
            name="Full Time Python Developer",
            department="IT",
            description="Python development",
            salary=60000,
            job_type="FT",
            skills_needed="Python, Django",
            country="US",
            created_by=self.employer
        )
        
        Job.objects.create(
            name="Part Time Web Developer",
            department="Web",
            description="Web development",
            salary=40000,
            job_type="PT",
            skills_needed="JavaScript, HTML",
            country="UK",
            created_by=self.employer
        )
        
        # Test job_type filter (line 189)
        response = self.client.get(self.dashboard_url + '?job_type=FT')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['jobs']), 1)
        self.assertEqual(response.context['jobs'][0].name, "Full Time Python Developer")
        
        # Test department filter (line 190-191)
        response = self.client.get(self.dashboard_url + '?department=Web')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['jobs']), 1)
        self.assertEqual(response.context['jobs'][0].name, "Part Time Web Developer")
        
        # Test country filter (line 194)
        response = self.client.get(self.dashboard_url + '?country=UK')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['jobs']), 1)
        self.assertEqual(response.context['jobs'][0].name, "Part Time Web Developer")
        
        # Test min_salary filter (line 185-186)
        response = self.client.get(self.dashboard_url + '?min_salary=50000')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['jobs']), 1)
        self.assertEqual(response.context['jobs'][0].name, "Full Time Python Developer")
        
        # Test invalid min_salary filter (line 185-186)
        response = self.client.get(self.dashboard_url + '?min_salary=invalid')
        self.assertEqual(response.status_code, 200)
        # Should ignore the invalid filter and return all jobs
        self.assertEqual(len(response.context['jobs']), 2)