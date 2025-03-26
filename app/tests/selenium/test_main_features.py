from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from app.models import User, Admin, Employee, Employer, VerificationCode
from unittest.mock import patch
import os
from django.conf import settings
import time

class SeleniumTests(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(10)
        self.wait = WebDriverWait(self.browser, 10)

        admin_user = User.objects.create_user(
            username="@admin",
            email="admin@example.com",
            password="testpassword123",
            first_name="Admin",
            last_name="User",
            user_type="admin",
            is_staff=True,
            is_superuser=True
        )
        self.admin = Admin.objects.create(user=admin_user)
        
        employee_user = User.objects.create_user(
            username="@employee",
            email="employee1@example.com",
            password="testpassword123",
            first_name="Test",  
            last_name="Employee",
            user_type="employee"
        )
        self.employee = Employee.objects.create(
            user=employee_user,
            country="US"
        )
        
        employer_user = User.objects.create_user(
            username="@employer",
            email="employer1@example.com",
            password="testpassword123",
            first_name="Test", 
            last_name="Employer",
            user_type="employer"
        )
        self.employer = Employer.objects.create(
            user=employer_user,
            company_name="Company1",
            country="UK"
        )

    def tearDown(self):
        self.browser.quit()

    def login(self, user):
        self.browser.get(f'{self.live_server_url}{reverse("login")}')

        username_field = self.browser.find_element(By.NAME, 'username')
        username_field.send_keys(user.user.username)
        password_field = self.browser.find_element(By.NAME, 'password')
        password_field.send_keys('testpassword123')
        password_field.submit()

        try:
            self.wait.until(lambda driver: driver.current_url != f'{self.live_server_url}{reverse("login")}')
        except TimeoutException:
            self.fail("login timeout - redirect did not occur")

    def wait_for_element(self, by, value, timeout=10):
        try:
            element = WebDriverWait(self.browser, timeout).until(EC.presence_of_element_located((by, value)))
            return element
        except TimeoutException:
            self.fail(f"element {value} not found within {timeout} seconds")

    def wait_for_text(self, text, timeout=10):
        try:
            WebDriverWait(self.browser, timeout).until(EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{text}')]")))
        except TimeoutException:
            self.fail(f"text '{text}' not found within {timeout} seconds")

    def wait_for_url(self, url, timeout=10):
        try:
            WebDriverWait(self.browser, timeout).until(EC.url_contains(url))
        except TimeoutException:
            self.fail(f"url '{url}' not found within {timeout} seconds")

    def find_submit_button(self):
        try:
            return self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        except:
            try:
                return self.browser.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
            except:
                self.fail("submit button not found")


class LoginFunctionalTest(SeleniumTests):

    @patch('app.forms.user_forms.ReCaptchaField.clean', return_value=True)
    @patch('app.helper.create_and_send_code_email', return_value=True)
    def test_successful_employee_singup(self, mock_email_sender, mock_recaptcha):
        employees = Employee.objects.count()
        self.browser.get(f'{self.live_server_url}{reverse("employee_signup")}')
        
        first_name_field = self.browser.find_element(By.NAME, 'first_name')
        last_name_field = self.browser.find_element(By.NAME, 'last_name')
        email_field = self.browser.find_element(By.NAME, 'email')
        username_field = self.browser.find_element(By.NAME, 'username')
        password1_field = self.browser.find_element(By.NAME, 'password1')
        password2_field = self.browser.find_element(By.NAME, 'password2')
        country_field = self.browser.find_element(By.NAME, 'country')
        
        first_name_field.send_keys("Test")
        last_name_field.send_keys("Employee")
        email_field.send_keys("test@employee.com")
        username_field.send_keys("@testemployee")
        password1_field.send_keys("testpassword123")
        password2_field.send_keys("testpassword123")
        country_field.send_keys("UK")
        password2_field.submit()
        
        self.wait_for_url(reverse("verify_email"))
        verify_email_url = f'{self.live_server_url}{reverse("verify_email")}'
        self.assertEqual(self.browser.current_url, verify_email_url)
        
        user = User.objects.get(username='@testemployee')
        verification = VerificationCode.objects.create(
            user=user,
            code='123456',
            code_type='email_verification'
        )
        
        session = self.client.session
        session['verification_email'] = user.email
        session['signup_data'] = {
            'username': '@testemployee',
            'email': 'test@employee.com',
            'password1': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'Employee',
            'country': 'UK'
        }
        session.save()
        
        code_field = self.browser.find_element(By.NAME, 'code')
        code_field.send_keys('123456')
        code_field.submit()
        
        self.wait_for_url(reverse("employee_signup_2"))
        self.assertEqual(self.browser.current_url, f'{self.live_server_url}{reverse("employee_signup_2")}')
        
        cv_content = b"""
            Test CV file:
            LANGUAGES
            - Spanish
            SKILLS
            - Python
            - Django
            - Testing
            EXPERIENCE
            - 5 years of software development
            EDUCATION
            - Bachelor's in Computer Science
            PHONE
            - +44123456789
            INTERESTS
            - Web development
            """
        test_cv_path = os.path.join(settings.MEDIA_ROOT, "uploads", "selenium_test_cv.pdf")
        os.makedirs(os.path.dirname(test_cv_path), exist_ok=True)
        with open(test_cv_path, "wb") as f:
            f.write(cv_content)
        
        cv_file_input = self.browser.find_element(By.NAME, 'cv')
        cv_file_input.send_keys(test_cv_path)
        
        upload_button = self.find_submit_button()
        self.browser.execute_script("arguments[0].scrollIntoView(true);", upload_button)
        self.browser.execute_script("arguments[0].click();", upload_button)
        
        self.wait_for_url(reverse("employee_signup_3"))
        self.assertEqual(self.browser.current_url, f'{self.live_server_url}{reverse("employee_signup_3")}')
        
        form_data = {
            'skills': "Python, Django, Testing",
            'experience': "5 years of software development",
            'education': "Bachelor in Computer Science", 
            'languages': "English, Spanish",
            'phone': "+44123456789",
            'interests': "Web development, AI",
            'preferred_contract': "FT"
        }
        
        for field_name, value in form_data.items():
            self.browser.execute_script(f"document.getElementsByName('{field_name}')[0].value = '{value}';")
        
        self.browser.execute_script("document.querySelector('form').submit();")
        
        self.wait_for_url(reverse("employee_dashboard"))
        self.assertEqual(self.browser.current_url, f'{self.live_server_url}{reverse("employee_dashboard")}')
        
        user = User.objects.get(username='@testemployee')
        self.assertTrue(user.is_active)
        self.assertEqual(user.user_type, 'employee')
        self.assertEqual(Employee.objects.count(), employees + 1)
        
        if os.path.exists(test_cv_path):
            os.remove(test_cv_path)
        
        uploads_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
        if os.path.exists(uploads_dir):
            for filename in os.listdir(uploads_dir):
                if filename.startswith("selenium_test"):
                    os.remove(os.path.join(uploads_dir, filename))

    @patch('app.forms.user_forms.ReCaptchaField.clean', return_value=True)
    def test_successful_employer_singup(self, mock_recaptcha):
        employers = Employer.objects.count()
        self.browser.get(f'{self.live_server_url}{reverse("employer_signup")}')
        
        first_name_field = self.browser.find_element(By.NAME, 'first_name')
        last_name_field = self.browser.find_element(By.NAME, 'last_name')
        email_field = self.browser.find_element(By.NAME, 'email')
        username_field = self.browser.find_element(By.NAME, 'username')
        password1_field = self.browser.find_element(By.NAME, 'password1')
        password2_field = self.browser.find_element(By.NAME, 'password2')
        company_name_field = self.browser.find_element(By.NAME, 'company_name')
        country_field = self.browser.find_element(By.NAME, 'country')
        first_name_field.send_keys("Test")
        last_name_field.send_keys("Employer")
        email_field.send_keys("test@employer.com")
        username_field.send_keys("@testemployer")
        password1_field.send_keys("testpassword123")
        password2_field.send_keys("testpassword123")
        company_name_field.send_keys("Company1")
        country_field.send_keys("UK")
        password2_field.submit()

        self.wait_for_url(reverse("verify_email"))

        
        user = User.objects.get(username='@testemployer')
        verification = VerificationCode.objects.create(
            user=user,
            code='123456',
            code_type='email_verification'
        )
        
        session = self.client.session
        session['verification_email'] = user.email
        session['signup_data'] = {
            'username': '@testemployer',
            'email': 'test@employer.com',
            'password1': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'Employer',
            'country': 'UK'
        }
        session.save()
        
        code_field = self.browser.find_element(By.NAME, 'code')
        code_field.send_keys('123456')
        code_field.submit()

        self.wait_for_url(reverse("employer_dashboard"))
        self.assertEqual(self.browser.current_url, f'{self.live_server_url}{reverse("employer_dashboard")}')

    def test_redirect_to_appropriate_dashboard(self):
        # test admin redirect
        self.login(self.admin)
        admin_dashboard_url = f'{self.live_server_url}{reverse("admin_dashboard")}'
        self.assertEqual(self.browser.current_url, admin_dashboard_url)
        self.browser.get(f'{self.live_server_url}{reverse("logout")}')

        # test employee redirect
        self.login(self.employee)
        tutor_dashboard_url = f'{self.live_server_url}{reverse("employee_dashboard")}'
        self.assertEqual(self.browser.current_url, tutor_dashboard_url)
        self.browser.get(f'{self.live_server_url}{reverse("logout")}')

        # test employer redirect
        self.login(self.employer)
        student_dashboard_url = f'{self.live_server_url}{reverse("employer_dashboard")}'
        self.assertEqual(self.browser.current_url, student_dashboard_url)
        self.browser.get(f'{self.live_server_url}{reverse("logout")}')


