# app/tests/views/test_employee_views.py
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from app.models import User, Employee, VerificationCode
import os
from django.conf import settings

class EmployeeViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create an employee user
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
        
        # URLs
        self.signup_url = reverse('employee_signup')
        self.dashboard_url = reverse('employee_dashboard')
        self.update_url = reverse('employee_update')
        self.upload_cv_url = reverse('employee_signup_2')
        self.review_cv_url = reverse('employee_signup_3')
        
    def test_employee_update_get(self):
        """Test getting the employee update form"""
        self.client.login(username="@employeetest", password="testpass123")
        response = self.client.get(self.update_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employee_update_details.html')
        self.assertTrue('form' in response.context)
        
    def test_employee_update_post(self):
        """Test updating employee account details"""
        self.client.login(username="@employeetest", password="testpass123")
        
        # Data with updated fields
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@test.com',
            'country': 'UK'
        }
        
        response = self.client.post(self.update_url, data)
        
        # Should show success message
        self.assertEqual(response.status_code, 200)
        
        # Reload user from database
        self.employee_user.refresh_from_db()
        self.employee.refresh_from_db()
        
        # Check that fields were updated
        self.assertEqual(self.employee_user.first_name, 'Updated')
        self.assertEqual(self.employee_user.last_name, 'Name')
        self.assertEqual(self.employee_user.email, 'updated@test.com')
        self.assertEqual(self.employee.country, 'UK')
        
    def test_employee_update_password(self):
        """Test updating employee password"""
        self.client.login(username="@employeetest", password="testpass123")
        
        # Data with new password
        data = {
            'first_name': 'Test',
            'last_name': 'Employee',
            'email': 'employee@test.com',
            'country': 'US',
            'password1': 'NewPass123!',
            'password2': 'NewPass123!'
        }
        
        response = self.client.post(self.update_url, data)
        
        # Should show success message
        self.assertEqual(response.status_code, 200)
        
        # Check that password was updated
        self.employee_user.refresh_from_db()
        self.assertTrue(self.employee_user.check_password('NewPass123!'))
        
    def test_upload_cv_get(self):
        """Test getting the upload CV page"""
        # Log in first
        self.client.login(username="@employeetest", password="testpass123")
        
        # Set up session data
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
        self.assertTemplateUsed(response, 'employee_signup.html')
        self.assertEqual(response.context['step'], 2)
        
    def test_upload_cv_post(self):
        """Test uploading a CV file"""
        # Log in first
        self.client.login(username="@employeetest", password="testpass123")
        
        # Create a test CV file
        cv_content = b"This is a test CV file"
        cv_file = SimpleUploadedFile("test_cv.pdf", cv_content, content_type="application/pdf")
        
        # Make sure uploads directory exists
        uploads_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        
        response = self.client.post(self.upload_cv_url, {'cv': cv_file})
        
        # Should redirect to the next step
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('employee_signup_3'))
        
        # Check that the file was saved in session
        self.assertTrue('cv_filename' in self.client.session)
        
    def test_review_cv_data_get(self):
        """Test getting the review CV data page"""
        # Log in first
        self.client.login(username="@employeetest", password="testpass123")
        
        # Set up session data with CV filename
        session = self.client.session
        session['cv_filename'] = "uploads/test_cv.pdf"
        session.save()
        
        response = self.client.get(self.review_cv_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employee_signup.html')
        self.assertEqual(response.context['step'], 3)
        
    def test_review_cv_data_post(self):
        """Test submitting review CV data"""
        # Log in first
        self.client.login(username="@employeetest", password="testpass123")
        
        # Set up session data with CV filename
        session = self.client.session
        session['cv_filename'] = "uploads/test_cv.pdf"
        session.save()
        
        # Submit profile data
        data = {
            'skills': 'Python, Django, JavaScript',
            'experience': 'Developer for 5 years',
            'education': 'BS Computer Science',
            'phone': '555-1234',
            'interests': 'Coding, Reading',
            'preferred_contract': 'FT'
        }
        
        response = self.client.post(self.review_cv_url, data)
        
        # Should redirect to dashboard
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('employee_dashboard'))
        
        # Check that the employee profile was updated
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.skills, 'Python, Django, JavaScript')
        self.assertEqual(self.employee.experience, 'Developer for 5 years')
        self.assertEqual(self.employee.education, 'BS Computer Science')
        self.assertEqual(self.employee.phone, '555-1234')
        self.assertEqual(self.employee.interests, 'Coding, Reading')
        self.assertEqual(self.employee.preferred_contract, 'FT')