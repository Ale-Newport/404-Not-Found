# app/tests/test_more_helpers.py
from django.test import TestCase
from app.helper import extract_text_from_pdf, extract_name, extract_education, extract_experience, extract_skills, extract_interests, parse_cv
from unittest.mock import patch, MagicMock

class MoreHelperTests(TestCase):
    def setUp(self):
        self.sample_text = """
        John Smith
        123 Main St, Anytown, CA 12345
        john.smith@example.com
        (555) 123-4567
        
        Skills
        Python, Django, JavaScript, React
        
        Education
        Bachelor of Science in Computer Science, University of Example, 2015-2019
        
        Experience
        Software Developer, Tech Company, 2019-2022
        - Developed web applications using Python and Django
        - Implemented RESTful APIs
        
        Interests
        Reading, Hiking, Photography
        """
    
    @patch('app.helper.pdfplumber.open')
    def test_extract_text_from_pdf(self, mock_open):
        """Test PDF text extraction"""
        # Mock the PDF object and its pages
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample text from PDF"
        mock_pdf.pages = [mock_page]
        mock_open.return_value.__enter__.return_value = mock_pdf
        
        result = extract_text_from_pdf("dummy.pdf")
        self.assertEqual(result, "Sample text from PDF")
        
        # Test with multiple pages
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "More text"
        mock_pdf.pages = [mock_page, mock_page2]
        
        result = extract_text_from_pdf("dummy.pdf")
        self.assertEqual(result, "Sample text from PDF\nMore text")
        
        # Test with a page returning None (no text)
        mock_page3 = MagicMock()
        mock_page3.extract_text.return_value = None
        mock_pdf.pages = [mock_page, mock_page3, mock_page2]
        
        result = extract_text_from_pdf("dummy.pdf")
        self.assertEqual(result, "Sample text from PDF\nMore text")
    
    @patch('app.helper.nlp')
    def test_extract_name_with_entity(self, mock_nlp):
        """Test name extraction when PERSON entity is found"""
        # Create mock entities
        mock_ent = MagicMock()
        mock_ent.label_ = "PERSON"
        mock_ent.text = "John Smith"
        
        # Set up mock doc with entities
        mock_doc = MagicMock()
        mock_doc.ents = [mock_ent]
        mock_nlp.return_value = mock_doc
        
        name = extract_name("Sample text")
        self.assertEqual(name, "John Smith")
    
    def test_extract_skills_with_section(self):
        """Test extracting skills from a dedicated skills section"""
        text = """
        Summary
        Experienced software developer
        
        Skills:
        • Python
        • JavaScript
        • React
        
        Education
        Bachelor's degree
        """
        
        skills = extract_skills(text)
        self.assertIn("Python", skills)
        self.assertIn("JavaScript", skills)
        self.assertIn("React", skills)
    
    def test_extract_interests_with_section(self):
        """Test extracting interests from a dedicated interests section"""
        text = """
        Experience
        Various jobs
        
        Interests:
        • Reading
        • Travel
        • Photography
        
        References
        Available upon request
        """
        
        interests = extract_interests(text)
        self.assertIn("Reading", interests)
        self.assertIn("Travel", interests)
        self.assertIn("Photography", interests)
    
    @patch('app.helper.extract_text_from_pdf')
    @patch('app.helper.extract_name')
    @patch('app.helper.extract_email')
    @patch('app.helper.extract_phone_number')
    @patch('app.helper.extract_education')
    @patch('app.helper.extract_experience')
    @patch('app.helper.extract_skills')
    @patch('app.helper.extract_interests')
    def test_parse_cv_full(self, mock_interests, mock_skills, mock_experience, 
                         mock_education, mock_phone, mock_email, mock_name, mock_extract):
        """Test full CV parsing with all extractors"""
        # Configure mocks
        mock_extract.return_value = "Sample CV text"
        mock_name.return_value = "John Smith"
        mock_email.return_value = "john@example.com"
        mock_phone.return_value = "555-1234"
        mock_education.return_value = ["BS in Computer Science"]
        mock_experience.return_value = ["Software Developer at Company"]
        mock_skills.return_value = ["Python", "JavaScript"]
        mock_interests.return_value = ["Reading", "Hiking"]
        
        # Parse CV
        result = parse_cv("dummy.pdf")
        
        # Check results
        self.assertEqual(result["Name"], "John Smith")
        self.assertEqual(result["E-mail"], "john@example.com")
        self.assertEqual(result["Phone"], "555-1234")
        self.assertEqual(result["Education"], ["BS in Computer Science"])
        self.assertEqual(result["Experience"], ["Software Developer at Company"])
        self.assertEqual(result["Skills"], ["Python", "JavaScript"])
        self.assertEqual(result["Interests"], ["Reading", "Hiking"])