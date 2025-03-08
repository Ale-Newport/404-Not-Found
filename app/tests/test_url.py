# app/tests/test_urls.py
import os
from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse, resolve
from app.views import views, employer_views, admin_views

class UrlsTest(TestCase):
    def test_home_url(self):
        """Test home URL pattern"""
        url = reverse('home')
        self.assertEqual(url, '/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, views.home)
        
    def test_login_url(self):
        """Test login URL pattern"""
        url = reverse('login')
        self.assertEqual(url, '/login/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, views.user_login)
        
    def test_logout_url(self):
        """Test logout URL pattern"""
        url = reverse('logout')
        self.assertEqual(url, '/logout/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, views.log_out)
        
    def test_employee_signup_url(self):
        """Test employee signup URL pattern"""
        url = reverse('employee_signup')
        self.assertEqual(url, '/employee/signup/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, views.employee_signup)
        
    def test_employer_signup_url(self):
        """Test employer signup URL pattern"""
        url = reverse('employer_signup')
        self.assertEqual(url, '/employer/signup/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, views.employer_signup)
        
    def test_employee_dashboard_url(self):
        """Test employee dashboard URL pattern"""
        url = reverse('employee_dashboard')
        self.assertEqual(url, '/employee/dashboard/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, views.employee_dashboard)
        
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
        self.assertEqual(resolver.func, admin_views.dashboard)
        
    def test_job_detail_url(self):
        """Test job detail URL pattern"""
        url = reverse('job_detail', args=[1])
        self.assertEqual(url, '/job/1/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, employer_views.job_detail)
        
    def test_apply_job_url(self):
        """Test apply job URL pattern"""
        url = reverse('apply_job', args=[1])
        self.assertEqual(url, '/job/1/apply/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, views.apply_to_job)
        
    def test_my_applications_url(self):
        """Test my applications URL pattern"""
        url = reverse('my_applications')
        self.assertEqual(url, '/employee/applications/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, views.my_applications)

    # app/tests/test_url.py
    def test_update_application_status_url(self):
        """Test update application status URL pattern"""
        url = reverse('update_application_status', args=[1])
        self.assertEqual(url, '/application/1/update/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, views.update_application_status)
    
    # app/tests/test_url.py
    def test_static_urls_in_debug_mode(self):
        """Test static URLs when DEBUG is True"""
        from django.conf import settings
        from django.conf.urls.static import static
        
        # Save original debug value
        original_debug = settings.DEBUG
        
        try:
            # Set DEBUG to True
            settings.DEBUG = True
            
            # Get static URLs
            static_urls = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
            
            # Verify static URLs are generated
            self.assertTrue(len(static_urls) > 0)
        finally:
            # Restore original DEBUG value
            settings.DEBUG = original_debug

    # app/tests/test_url.py - add this test
    from django.test import override_settings
    import os

    # app/tests/test_url.py
    from unittest.mock import patch

    def test_debug_static_urls(self):
        """Test static URLs configuration with DEBUG=True"""
        from django.conf import settings
        from project.urls import urlpatterns
        
        # Store original urlpatterns and DEBUG setting
        original_urlpatterns = urlpatterns.copy()
        original_debug = settings.DEBUG
        
        # Patch static function to return a known list
        with patch('django.conf.urls.static.static') as mock_static:
            mock_static.return_value = ['mock_static_url']
            
            # Set DEBUG to True
            settings.DEBUG = True
            
            # Import the module again to trigger urlpatterns evaluation
            import importlib
            import project.urls
            importlib.reload(project.urls)
            
            # Check if the mock was called
            mock_static.assert_called_once()
            
            # Reset DEBUG
            settings.DEBUG = original_debug