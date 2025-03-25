from django.test import TestCase
from django.urls import reverse, resolve
from app.views import base_views, auth_views, employee_views, employer_views, admin_views
from django.test import override_settings
from unittest.mock import patch

class UrlsTest(TestCase):
    def test_home_url(self):
        """Test home URL pattern"""
        url = reverse('home')
        self.assertEqual(url, '/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, base_views.home)
        
    def test_login_url(self):
        """Test login URL pattern"""
        url = reverse('login')
        self.assertEqual(url, '/login/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, auth_views.user_login)
        
    def test_logout_url(self):
        """Test logout URL pattern"""
        url = reverse('logout')
        self.assertEqual(url, '/logout/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, auth_views.log_out)
        
    def test_employee_signup_url(self):
        """Test employee signup URL pattern"""
        url = reverse('employee_signup')
        self.assertEqual(url, '/employee/signup/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, employee_views.employee_signup)
        
    def test_employer_signup_url(self):
        """Test employer signup URL pattern"""
        url = reverse('employer_signup')
        self.assertEqual(url, '/employer/signup/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, employer_views.employer_signup)
        
    def test_employee_dashboard_url(self):
        """Test employee dashboard URL pattern"""
        url = reverse('employee_dashboard')
        self.assertEqual(url, '/employee/dashboard/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, employee_views.employee_dashboard)
        
    def test_employer_dashboard_url(self):
        """Test employer dashboard URL pattern"""
        url = reverse('employer_dashboard')
        self.assertEqual(url, '/employer/dashboard/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, employer_views.employer_dashboard)
        
    def test_admin_dashboard_url(self):
        """Test admin dashboard URL pattern"""
        url = reverse('admin_dashboard')
        self.assertEqual(url, '/administrator/dashboard/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, admin_views.admin_dashboard)
        
    def test_job_detail_url(self):
        """Test job detail URL pattern"""
        url = reverse('job_detail', args=[1])
        self.assertEqual(url, '/employer/job/1/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, employer_views.job_detail)
        
    def test_apply_job_url(self):
        """Test apply job URL pattern"""
        url = reverse('apply_job', args=[1])
        self.assertEqual(url, '/employee/job/1/apply/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, employee_views.apply_to_job)
        
    def test_my_applications_url(self):
        """Test my applications URL pattern"""
        url = reverse('my_applications')
        self.assertEqual(url, '/employee/applications/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, employee_views.my_applications)

    def test_update_application_status_url(self):
        """Test update application status URL pattern"""
        url = reverse('update_application_status', args=[1])
        self.assertEqual(url, '/employer/update-application/1/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, employer_views.update_application_status)
    
    def test_static_urls_in_debug_mode(self):
        """Test static URLs when DEBUG is True"""
        from django.conf import settings
        from django.conf.urls.static import static
        
        original_debug = settings.DEBUG
        
        try:
            settings.DEBUG = True
            static_urls = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
            
            self.assertTrue(len(static_urls) > 0)
        finally:
            settings.DEBUG = original_debug

    def test_debug_static_urls(self):
        """Test static URLs configuration with DEBUG=True"""
        from django.conf import settings
        from project.urls import urlpatterns
        
        original_urlpatterns = urlpatterns.copy()
        original_debug = settings.DEBUG
        
        with patch('django.conf.urls.static.static') as mock_static:
            mock_static.return_value = ['mock_static_url']
            
            settings.DEBUG = True
            
            import importlib
            import project.urls
            importlib.reload(project.urls)
            
            mock_static.assert_called_once()
            
            settings.DEBUG = original_debug