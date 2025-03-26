import unittest
from unittest.mock import patch, MagicMock, mock_open
from django.test import TestCase
from django.contrib.auth import get_user_model
from app.models import User, VerificationCode
from app.helper import (
    is_valid_pdf, extract_text_from_pdf, extract_email, extract_phone_number,
    extract_name, extract_education, extract_experience, extract_skills,
    extract_interests, extract_languages, parse_cv, 
    create_and_send_code_email, validate_verification_code
)
import tempfile
import os
import datetime

User = get_user_model()

class PDFHelperTests(TestCase):
    def setUp(self):
        # Create a temporary PDF file for testing
        self.temp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        self.temp_pdf.close()
        
        # Sample CV text
        self.sample_cv_text = """
        John Smith
        john.smith@example.com
        +44 123 456 7890
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of Example, 2015-2019
        
        EXPERIENCE
        Software Developer at Tech Company
        Worked on various projects using Python
        
        SKILLS
        Python, Django, JavaScript
        
        LANGUAGES
        English (Native), Spanish (Intermediate)
        
        INTERESTS
        Reading, Hiking, Photography
        """
    
    def tearDown(self):
        # Clean up the temporary file
        if os.path.exists(self.temp_pdf.name):
            os.unlink(self.temp_pdf.name)
    
    @patch('app.helper.fitz.open')
    def test_is_valid_pdf_success(self, mock_fitz_open):
        # Test the success case for is_valid_pdf (line 42->41)
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 1
        mock_fitz_open.return_value = mock_doc
        
        self.assertTrue(is_valid_pdf(self.temp_pdf.name))
        mock_fitz_open.assert_called_once_with(self.temp_pdf.name)
    
    @patch('app.helper.fitz.open')
    def test_is_valid_pdf_failure(self, mock_fitz_open):
        # Test the failure case for is_valid_pdf when an exception occurs
        mock_fitz_open.side_effect = Exception("PDF error")
        
        self.assertFalse(is_valid_pdf(self.temp_pdf.name))
        mock_fitz_open.assert_called_once_with(self.temp_pdf.name)
    
    @patch('app.helper.pdfplumber.open')
    def test_extract_text_from_pdf_success(self, mock_pdf_open):
        # Test the success path of extract_text_from_pdf (line 53)
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample text"
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page, mock_page]  # Two pages
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf_open.return_value = mock_pdf
        
        result = extract_text_from_pdf(self.temp_pdf.name)
        self.assertEqual(result, "Sample text\nSample text")
        mock_pdf_open.assert_called_once_with(self.temp_pdf.name)
    
    @patch('app.helper.pdfplumber.open')
    def test_extract_text_from_pdf_failure(self, mock_pdf_open):
        # Test the failure path of extract_text_from_pdf when an exception occurs (line 53)
        mock_pdf_open.side_effect = Exception("PDF error")
        
        result = extract_text_from_pdf(self.temp_pdf.name)
        self.assertEqual(result, "")
        mock_pdf_open.assert_called_once_with(self.temp_pdf.name)
    
    @patch('app.helper.extract_text_from_pdf')
    @patch('app.helper.extract_name')
    @patch('app.helper.extract_email')
    @patch('app.helper.extract_phone_number')
    @patch('app.helper.extract_education')
    @patch('app.helper.extract_experience')
    @patch('app.helper.extract_skills')
    @patch('app.helper.extract_languages')
    @patch('app.helper.extract_interests')
    def test_parse_cv(self, mock_interests, mock_languages, mock_skills, 
                    mock_experience, mock_education, mock_phone, mock_email, 
                    mock_name, mock_extract_text):
        # Test parse_cv functionality (line 530->533, 534-535)
        mock_extract_text.return_value = self.sample_cv_text
        mock_name.return_value = "John Smith"
        mock_email.return_value = "john.smith@example.com"
        mock_phone.return_value = "+44 123 456 7890"
        mock_education.return_value = ["Bachelor of Science in Computer Science"]
        mock_experience.return_value = ["Software Developer at Tech Company"]
        mock_skills.return_value = ["Python", "Django", "JavaScript"]
        mock_languages.return_value = ["English (Native)", "Spanish (Intermediate)"]
        mock_interests.return_value = ["Reading", "Hiking", "Photography"]
        
        result = parse_cv(self.temp_pdf.name)
        
        self.assertEqual(result["Name"], "John Smith")
        self.assertEqual(result["E-mail"], "john.smith@example.com")
        self.assertEqual(result["Phone"], "+44 123 456 7890")
        self.assertEqual(result["Education"], ["Bachelor of Science in Computer Science"])
        self.assertEqual(result["Experience"], ["Software Developer at Tech Company"])
        self.assertEqual(result["Skills"], ["Python", "Django", "JavaScript"])
        self.assertEqual(result["Languages"], ["English (Native)", "Spanish (Intermediate)"])
        self.assertEqual(result["Interests"], ["Reading", "Hiking", "Photography"])
        
        mock_extract_text.assert_called_once_with(self.temp_pdf.name)
    
    def test_extract_email(self):
        # Test extract_email function (line 55)
        self.assertEqual(extract_email("Contact me at john.smith@example.com"), "john.smith@example.com")
        self.assertIsNone(extract_email("No email here"))
    
    def test_extract_phone_number(self):
        # Test extract_phone_number function (line 58)
        self.assertEqual(extract_phone_number("Call me at +44 123 456 7890"), "+44 123 456")
        self.assertIsNone(extract_phone_number("No phone number here"))
    
    @patch('app.helper.nlp')
    def test_extract_name(self, mock_nlp):
        # Test extract_name function (line 61->64)
        mock_ent = MagicMock()
        mock_ent.label_ = "PERSON"
        mock_ent.text = "John Smith"
        
        mock_doc = MagicMock()
        mock_doc.ents = [mock_ent]
        mock_nlp.return_value = mock_doc
        
        self.assertEqual(extract_name("John Smith is a software developer"), "John Smith")
        mock_nlp.assert_called_once_with("John Smith is a software developer")
    
    @patch('app.helper.nlp')
    def test_extract_name_not_found(self, mock_nlp):
        # Test extract_name when no name is found (line 63)
        mock_doc = MagicMock()
        mock_doc.ents = []
        mock_nlp.return_value = mock_doc
        
        self.assertIsNone(extract_name("No name here"))
        mock_nlp.assert_called_once_with("No name here")
    
    def test_extract_education(self):
        # Test extract_education function (line 65->70)
        text = """
        EDUCATION
        Bachelor of Science in Computer Science
        University of Example, 2015-2019
        
        OTHER SECTION
        """
        result = extract_education(text)
        self.assertIn("Bachelor of Science in Computer Science", result)
        self.assertIn("University of Example, 2015-2019", result)
    
    def test_extract_experience(self):
        # Test extract_experience function (line 71->77)
        text = """
        EXPERIENCE
        Software Developer at Tech Company
        Worked on various projects using Python
        
        OTHER SECTION
        """
        result = extract_experience(text)
        self.assertIn("Software Developer at Tech Company", result)
    
    def test_extract_skills_finds_common_skills(self):
        # Test extract_skills function (line 144, 153, 174)
        text = """
        SKILLS
        • Python
        • Django
        • JavaScript
        
        OTHER SECTION
        """
        result = extract_skills(text)
        self.assertIn("Python", result)
        self.assertIn("Django", result)
        self.assertIn("JavaScript", result)
    
    def test_extract_interests_finds_common_interests(self):
        # Test extract_interests function (line 258, 261, 264)
        text = """
        INTERESTS
        • Reading
        • Hiking
        • Photography
        
        OTHER SECTION
        """
        result = extract_interests(text)
        self.assertIn("Reading", result)
        self.assertIn("Hiking", result)
        self.assertIn("Photography", result)
    
    def test_extract_languages_finds_common_languages(self):
        # Test extract_languages function (line 411, 414, 417->438)
        text = """
        LANGUAGES
        • English (Native)
        • Spanish (Intermediate)
        
        OTHER SECTION
        """
        result = extract_languages(text)
        self.assertIn("English (Native)", result)
        self.assertIn("Spanish (Intermediate)", result)
    
    def test_extract_skills_with_fragment_indicators(self):
        # Test extract_skills function with fragment indicators (line 276->274)
        text = """
        SKILLS
        • Python including frameworks like Django
        • JavaScript etc.
        
        OTHER SECTION
        """
        result = extract_skills(text)
        self.assertIn("Python", result)
        self.assertIn("JavaScript", result)
    
    def test_extract_skills_with_context_skills(self):
        # Test extract_skills with context skills (line 290->286)
        text = """
        SKILLS
        • Vehicle Maintenance
        • Customer Service
        
        OTHER SECTION
        """
        result = extract_skills(text)
        self.assertIn("Vehicle Maintenance", result)
        self.assertIn("Customer Service", result)
    
    def test_extract_interests_with_genuine_interests(self):
        # Test extract_interests with genuine interests (line 312, 330, 332, 334)
        text = """
        ABOUT ME
        I'm interested in photography and travel.
        
        OTHER SECTION
        """
        result = extract_interests(text)
        self.assertTrue(any("Photography" in interest for interest in result) or 
                        any("photography" in interest.lower() for interest in result))
    
    def test_extract_languages_with_fluency_patterns(self):
        # Test extract_languages with fluency patterns (line 423->417, 428->417)
        text = """
        LANGUAGES
        I am fluent in English and have basic knowledge of Spanish.
        
        OTHER SECTION
        """
        result = extract_languages(text)
        self.assertTrue(any("English" in lang for lang in result))
        self.assertTrue(any("Spanish" in lang for lang in result))
    
    def test_extract_languages_without_section(self):
        # Test extract_languages fallback to English (line 447->444)
        text = """
        This CV is written in English but doesn't have a languages section.
        """
        result = extract_languages(text)
        self.assertIn("English", result)


class EmailHelperTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='@testuser',
            email='test@example.com',
            password='testpassword',
            is_active=False
        )
        self.request = MagicMock()
        self.request.session = {}
    
    @patch('app.helper.SendGridAPIClient')
    @patch('app.helper.render_to_string')
    @patch('app.helper.Mail')
    def test_create_and_send_code_email_success(self, mock_mail, mock_render, mock_sendgrid):
        # Test create_and_send_code_email success path (line 462, 467, 469, 471)
        mock_render.return_value = '<html>Email content</html>'
        mock_mail_instance = MagicMock()
        mock_mail.return_value = mock_mail_instance
        mock_sg = MagicMock()
        mock_sendgrid.return_value = mock_sg
        
        result = create_and_send_code_email(
            self.user, 
            self.request, 
            'email_verification', 
            'template.html', 
            'Verify Email'
        )
        
        self.assertTrue(result)
        self.assertEqual(self.request.session.get('verification_email'), 'test@example.com')
        mock_render.assert_called_once()
        mock_mail.assert_called_once()
        mock_sg.send.assert_called_once_with(mock_mail_instance)
        
        # Verify code was created
        self.assertEqual(VerificationCode.objects.count(), 1)
        code = VerificationCode.objects.first()
        self.assertEqual(code.user, self.user)
        self.assertEqual(code.code_type, 'email_verification')
    
    @patch('app.helper.SendGridAPIClient')
    @patch('app.helper.render_to_string')
    def test_create_and_send_code_email_password_reset(self, mock_render, mock_sendgrid):
        # Test create_and_send_code_email for password reset (line 469)
        mock_render.return_value = '<html>Email content</html>'
        mock_sg = MagicMock()
        mock_sendgrid.return_value = mock_sg
        mock_sg.send.return_value = True
        
        result = create_and_send_code_email(
            self.user, 
            self.request, 
            'password_reset', 
            'template.html', 
            'Reset Password'
        )
        
        self.assertTrue(result)
        self.assertEqual(self.request.session.get('reset_email'), 'test@example.com')
    
    @patch('app.helper.SendGridAPIClient')
    @patch('app.helper.render_to_string')
    def test_create_and_send_code_email_failure(self, mock_render, mock_sendgrid):
        # Test create_and_send_code_email failure path (line 471)
        mock_render.side_effect = Exception("Email error")
        
        result = create_and_send_code_email(
            self.user, 
            self.request, 
            'email_verification', 
            'template.html', 
            'Verify Email'
        )
        
        self.assertFalse(result)
    
    def test_validate_verification_code_valid(self):
        # Test validate_verification_code with valid code (line 486)
        # Create a verification code
        code = "123456"
        VerificationCode.objects.create(
            user=self.user,
            code=code,
            code_type='email_verification',
            is_used=False
        )
        
        # Test the validation
        is_valid, user, verification = validate_verification_code(
            code, 
            self.user.email, 
            'email_verification'
        )
        
        self.assertTrue(is_valid)
        self.assertEqual(user, self.user)
        self.assertIsNotNone(verification)
    
    def test_validate_verification_code_inactive_user(self):
        # Test validation with inactive user (line 476)
        code = "123456"
        VerificationCode.objects.create(
            user=self.user,
            code=code,
            code_type='email_verification',
            is_used=False
        )
        
        # The user is already inactive from setUp
        is_valid, user, verification = validate_verification_code(
            code, 
            self.user.email, 
            'email_verification'
        )
        
        self.assertTrue(is_valid)
        self.assertEqual(user, self.user)
    
    def test_validate_verification_code_no_user(self):
        # Test validation when user not found (line 479)
        is_valid, user, verification = validate_verification_code(
            "123456", 
            "nonexistent@example.com", 
            'email_verification'
        )
        
        self.assertFalse(is_valid)
        self.assertIsNone(user)
        self.assertIsNone(verification)
    
    def test_validate_verification_code_used_code(self):
        # Test validation with used code (line 488)
        code = "123456"
        VerificationCode.objects.create(
            user=self.user,
            code=code,
            code_type='email_verification',
            is_used=True  # Code already used
        )
        
        is_valid, user, verification = validate_verification_code(
            code, 
            self.user.email, 
            'email_verification'
        )
        
        self.assertFalse(is_valid)
        self.assertEqual(user, self.user)
        self.assertIsNone(verification)
    
    def test_validate_verification_code_invalid_code(self):
        # Test validation with incorrect code (line 488)
        VerificationCode.objects.create(
            user=self.user,
            code="123456",
            code_type='email_verification',
            is_used=False
        )
        
        is_valid, user, verification = validate_verification_code(
            "wrong_code", 
            self.user.email, 
            'email_verification'
        )
        
        self.assertFalse(is_valid)
        self.assertEqual(user, self.user)
        self.assertIsNone(verification)
    
    @patch('app.models.VerificationCode.is_valid')
    def test_validate_verification_code_expired(self, mock_is_valid):
        # Test validation with expired code (line 488)
        mock_is_valid.return_value = False
        
        code = "123456"
        verification = VerificationCode.objects.create(
            user=self.user,
            code=code,
            code_type='email_verification',
            is_used=False
        )
        
        is_valid, user, returned_verification = validate_verification_code(
            code, 
            self.user.email, 
            'email_verification'
        )
        
        self.assertFalse(is_valid)
        self.assertEqual(user, self.user)
        self.assertIsNone(returned_verification)
        mock_is_valid.assert_called_once()


# Additional tests for specific statements in extract_skills, extract_interests, extract_languages

class ExtractSkillsEdgeCasesTests(TestCase):
    def test_extract_skills_filters_out_non_skills(self):
        # Test filtering out non-skills (line 293)
        text = """
        SKILLS
        • The way I approach problems
        • And how I solve them
        • Python
        """
        result = extract_skills(text)
        self.assertIn("Python", result)
        self.assertNotIn("The way I approach problems", result)
        self.assertNotIn("And how I solve them", result)
    
    def test_extract_skills_handles_section_identifiers(self):
        # Test handling section identifiers (line 310-312)
        text = """
        SKILLS SECTION:
        • Python
        • Django
        
        EDUCATION:
        • Bachelor's degree
        """
        result = extract_skills(text)
        self.assertIn("Python", result)
        self.assertIn("Django", result)
        self.assertNotIn("Bachelor's degree", result)


class ExtractInterestsEdgeCasesTests(TestCase):
    def test_extract_interests_excludes_non_interests(self):
        # Test excluding non-interests (line 439)
        text = """
        INTERESTS
        • Reading
        • This is not a valid interest because it's too long and doesn't match any patterns
        """
        result = extract_interests(text)
        self.assertIn("Reading", result)
        self.assertNotIn("This is not a valid interest because it's too long", result)


class ExtractLanguagesEdgeCasesTests(TestCase):
    def test_extract_languages_with_direct_mentions(self):
        # Test extracting languages directly mentioned (line 462)
        text = """
        I am fluent in English and Spanish.
        """
        result = extract_languages(text)
        self.assertTrue(any("English" in lang for lang in result))