from django.test import TestCase
from app.helper import (
    extract_text_from_pdf, extract_email, extract_phone_number,
    extract_name, extract_education, extract_experience,
    extract_skills, extract_interests, parse_cv
)
import spacy

class HelperFunctionsTest(TestCase):
    def setUp(self):
        self.sample_text = """
        John Smith
        123 Main St, Anytown, CA 12345
        john.smith@example.com
        (555) 123-4567
        
        Education
        Bachelor of Science in Computer Science, University of Example, 2015-2019
        
        Experience
        Software Developer, Tech Company, 2019-2022
        - Developed web applications using Python and Django
        - Implemented RESTful APIs
        
        Skills
        Python, Django, JavaScript, React, Git, SQL
        
        Interests
        Reading, Hiking, Photography
        """
        
        self.original_extract_text = extract_text_from_pdf
        
        
    def test_extract_email(self):
        email = extract_email(self.sample_text)
        self.assertEqual(email, "john.smith@example.com")
        
        text_with_multiple = "Contact me at john@example.com or support@example.com"
        email = extract_email(text_with_multiple)
        self.assertEqual(email, "john@example.com")
        
        text_without_email = "There is no email here"
        email = extract_email(text_without_email)
        self.assertIsNone(email)
        
    def test_extract_phone_number(self):
        phone = extract_phone_number(self.sample_text)
        self.assertEqual(phone, "(555) 123-4567")
        
        text_with_diff_formats = "Call me at +1 555-123-4567 or 555.123.4567"
        phone = extract_phone_number(text_with_diff_formats)
        self.assertEqual(phone, "+1 555-123")
            
    def test_extract_skills(self):
        skills = extract_skills(self.sample_text)
        actual_skills = sorted(skills)
        self.assertIn('Python', actual_skills)
        self.assertIn('Django', actual_skills)
        
            
    def test_extract_interests(self):
        interests = extract_interests(self.sample_text)
        actual_interests = sorted(interests)
        self.assertIn('Reading', actual_interests)
        self.assertIn('Hiking', actual_interests)
        self.assertIn('Photography', actual_interests)
        
    def test_extract_education(self):
        education = extract_education(self.sample_text)
        self.assertEqual(len(education), 1)
        self.assertIn("Bachelor of Science in Computer Science, University of Example, 2015-2019", education)
        
    def test_extract_experience(self):
        experience = extract_experience(self.sample_text)
        self.assertTrue(any("Software Developer" in exp for exp in experience))
        self.assertTrue(any("Tech Company" in exp for exp in experience))
        
    def test_parse_cv_integration(self):
        def mock_extract_text(*args, **kwargs):
            return self.sample_text
        
        import app.helper
        app.helper.extract_text_from_pdf = mock_extract_text
        
        result = parse_cv("dummy_path.pdf")

        self.assertIn("john.smith@example.com", result["E-mail"])
        self.assertIn("(555) 123-4567", result["Phone"])
        self.assertTrue(any("Python" in skill for skill in result["Skills"]))
        self.assertTrue(any("Reading" in interest for interest in result["Interests"]))
        
        app.helper.extract_text_from_pdf = self.original_extract_text