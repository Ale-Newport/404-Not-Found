import unittest
from unittest.mock import patch, Mock, MagicMock
from app.helper import is_valid_pdf, extract_text_from_pdf, extract_email, extract_phone_number, extract_name, extract_education, extract_experience, extract_skills, extract_interests, extract_languages, parse_cv

class TestHelperMethods(unittest.TestCase):
    def setUp(self):
        self.sample_text = """
        John Smith
        Software Engineer
        
        john.smith@example.com
        (123) 456-7890
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of Technology - 2015-2019
        
        WORK EXPERIENCE
        Software Engineer at Tech Company
        2019 - Present
        
        SKILLS
        Python, Java, JavaScript, Machine Learning, Project Management
        
        LANGUAGES
        English (Fluent), Spanish (Intermediate), French (Basic)
        
        INTERESTS
        Hiking, Photography, Reading
        """

    @patch('app.helper.fitz.open')
    def test_is_valid_pdf_true(self, mock_fitz_open):
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 5
        mock_fitz_open.return_value = mock_doc
        
        result = is_valid_pdf("valid.pdf")
        self.assertTrue(result)
        mock_fitz_open.assert_called_once_with("valid.pdf")

    @patch('app.helper.fitz.open')
    def test_is_valid_pdf_false_empty(self, mock_fitz_open):
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 0
        mock_fitz_open.return_value = mock_doc
        
        result = is_valid_pdf("empty.pdf")
        self.assertFalse(result)

    @patch('app.helper.fitz.open')
    def test_is_valid_pdf_exception(self, mock_fitz_open):
        mock_fitz_open.side_effect = Exception("Invalid PDF")
        
        result = is_valid_pdf("invalid.pdf")
        self.assertFalse(result)

    @patch('app.helper.pdfplumber.open')
    def test_extract_text_from_pdf(self, mock_plumber_open):
        mock_pdf = MagicMock()
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 content"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Page 2 content"
        mock_pdf.pages = [mock_page1, mock_page2]
        mock_plumber_open.return_value.__enter__.return_value = mock_pdf
        
        result = extract_text_from_pdf("test.pdf")
        self.assertEqual(result, "Page 1 content\nPage 2 content")

    @patch('app.helper.pdfplumber.open')
    def test_extract_text_from_pdf_empty_page(self, mock_plumber_open):
        mock_pdf = MagicMock()
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 content"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = None
        mock_pdf.pages = [mock_page1, mock_page2]
        mock_plumber_open.return_value.__enter__.return_value = mock_pdf
        
        result = extract_text_from_pdf("test.pdf")
        self.assertEqual(result, "Page 1 content")

    @patch('app.helper.pdfplumber.open')
    def test_extract_text_from_pdf_exception(self, mock_plumber_open):
        mock_plumber_open.side_effect = Exception("Error opening PDF")
        
        result = extract_text_from_pdf("invalid.pdf")
        self.assertEqual(result, "")

    def test_extract_email(self):
        text = "Contact me at john.doe@example.com for more information."
        self.assertEqual(extract_email(text), "john.doe@example.com")

        text = "There is no email address here."
        self.assertIsNone(extract_email(text))

    def test_extract_phone_number(self):
        text1 = "Call me at (123) 456-7890"
        self.assertEqual(extract_phone_number(text1), "(123) 456-7890")
        
        text2 = "My number is +1-234-567-8901"
        self.assertEqual(extract_phone_number(text2), "+1-234-567")
        
        text3 = "Contact me at 123.456.7890"
        self.assertEqual(extract_phone_number(text3), "123.456.7890")
        
        text4 = "There is no phone number here."
        self.assertIsNone(extract_phone_number(text4))

    @patch('app.helper.nlp')
    def test_extract_name(self, mock_nlp):
        mock_doc = Mock()
        mock_ent = Mock()
        mock_ent.label_ = "PERSON"
        mock_ent.text = "John Smith"
        mock_doc.ents = [mock_ent]
        mock_nlp.return_value = mock_doc
        
        result = extract_name("John Smith is a software engineer.")
        self.assertEqual(result, "John Smith")
        
        mock_doc.ents = []
        result = extract_name("No person here.")
        self.assertIsNone(result)

    def test_extract_education(self):
        text = """
        EDUCATION
        Bachelor of Science in Computer Science
        University of Technology - 2015-2019
        
        Master of Business Administration
        Business School - 2020-2022
        """
        
        result = extract_education(text)
        self.assertEqual(len(result), 3)
        self.assertIn("Bachelor of Science in Computer Science", result)
        self.assertIn("University of Technology - 2015-2019", result)
        
        result = extract_education("No education information here.")
        self.assertEqual(result, [])

    def test_extract_experience(self):
        text = """
        EXPERIENCE
        Software Engineer at Tech Company
        2019 - Present
        
        Internship at Startup
        Summer 2018
        """
        
        result = extract_experience(text)
        self.assertEqual(len(result), 3)
        self.assertIn("Software Engineer at Tech Company", result)

        result = extract_experience("No experience information here.")
        self.assertEqual(result, ["No experience information here."])

    def test_extract_skills_edge_cases(self):
        text = """
        SKILLS
        Python including various frameworks, etc.
        Java such as Spring, Hibernate
        JavaScript like React, Angular
        """
        
        result = extract_skills(text)
        self.assertIn("Python", result)
        self.assertIn("Java", result)
        self.assertIn("JavaScript", result)
        
        text2 = """
        SKILLS
        and Python
        the Java
        with JavaScript
        """
        result2 = extract_skills(text2)
        self.assertIn("Python", result2)
        self.assertIn("Java", result2)
        self.assertIn("JavaScript", result2)
        
        text3 = """
        SKILLS
        JAVA - 2020
        reference skills
        hobby skills
        """
        result3 = extract_skills(text3)
        self.assertNotIn("JAVA - 2020", result3)
        self.assertNotIn("reference skills", result3)
        self.assertNotIn("hobby skills", result3)

    def test_extract_interests_edge_cases(self):
        text = """
        INTERESTS
        and Reading
        the Photography
        with Traveling
        """
        
        result = extract_interests(text)
        self.assertIn("Reading", result)
        self.assertIn("Photography", result)
        self.assertIn("Traveling", result)
        
        text2 = """
        INTERESTS
        I enjoy reading books about science fiction and fantasy
        """
        
        result2 = extract_interests(text2)
        self.assertIn("Reading", result2)
        
        text3 = "I am interested in hiking and outdoor activities."
        result3 = extract_interests(text3)
        self.assertIn("Hiking", result3)

        text4 = "I enjoy playing Guitar and am interested in the UK Space Industry and Renewable Energy."
        result4 = extract_interests(text4)
        self.assertIn("Guitar", result4)
        self.assertIn("UK Space Industry", result4)
        self.assertIn("Renewable Energy", result4)

    def test_extract_languages_edge_cases(self):
        text = """
        Languages:
        I am fluent in English and have professional working proficiency in Spanish.
        I have limited working proficiency in French and proficiency in German.
        """
        
        result = extract_languages(text)
        self.assertIn("English", result)
        self.assertIn("French", result)
        
        text2 = """
        LANGUAGES
        English (C2), Spanish (B2), German (A1)
        """
        
        result2 = extract_languages(text2)
        self.assertTrue(any("English" in lang for lang in result2))
        self.assertTrue(any("Spanish" in lang for lang in result2))
        self.assertTrue(any("German" in lang for lang in result2))
        
        text3 = "This resume is written in English."
        result3 = extract_languages(text3)
        self.assertIn("English", result3)

    def test_extract_skills_sections(self):
        text = """
        Core Competencies:
        Leadership, Project Management, Communication
        
        Technical Proficiencies
        Python, SQL, Data Analysis
        """
        result = extract_skills(text)
        self.assertIn("Leadership", result)
        self.assertIn("Python", result)
        self.assertIn("SQL", result)
        
        text_separators = """
        SKILLS:
        Python • Java | SQL; Excel
        Machine Learning ○ Data Science
        """
        result_separators = extract_skills(text_separators)
        self.assertIn("Python", result_separators)
        self.assertIn("Java", result_separators)
        self.assertIn("SQL", result_separators)
        self.assertIn("Excel", result_separators)
        self.assertIn("Machine Learning", result_separators)
        self.assertIn("Data Science", result_separators)
        
        text_specific = """
        Experience with Warehouse Management and Inventory Control
        Customer Support and Technical Support
        """
        result_specific = extract_skills(text_specific)
        self.assertIn("Warehouse Management", result_specific)

    def test_extract_interests_patterns(self):
        text = "I am interested in artificial intelligence and machine learning."
        result = extract_interests(text)
        self.assertTrue(any("artificial intelligence" in interest.lower() for interest in result))
        
        text_sections = """
        Personal Interests:
        Reading, Photography
        
        Activities & Hobbies
        Hiking • Cycling • Swimming
        """
        result_sections = extract_interests(text_sections)
        self.assertIn("Reading", result_sections)
        self.assertIn("Photography", result_sections)
        self.assertIn("Hiking", result_sections)
        self.assertIn("Cycling", result_sections)
        self.assertIn("Swimming", result_sections)
        
        text_long = """
        INTERESTS
        I have a very long description of my interest in modern art and contemporary painting styles
        """
        result_long = extract_interests(text_long)
        self.assertFalse(any(len(interest.split()) > 5 for interest in result_long))
        
        text_filter = """
        INTERESTS
        References available upon request
        """
        result_filter = extract_interests(text_filter)
        self.assertNotIn("References available upon request", result_filter)

    def test_extract_languages_proficiency_patterns(self):
        text_cefr = "Languages: English (C2), Spanish (B1), German (A2)"
        result_cefr = extract_languages(text_cefr)
        self.assertIn("English", result_cefr)
        
        text_mentions = "I wrote this CV in English and I can also communicate in Japanese."
        result_mentions = extract_languages(text_mentions)
        self.assertIn("English", result_mentions)
        
        text_filter = """
        LANGUAGES
        References available upon request
        """
        result_filter = extract_languages(text_filter)
        self.assertNotIn("References available upon request", result_filter)

    @patch('app.helper.extract_text_from_pdf')
    @patch('app.helper.extract_name')
    @patch('app.helper.extract_email')
    @patch('app.helper.extract_phone_number')
    @patch('app.helper.extract_education')
    @patch('app.helper.extract_experience')
    @patch('app.helper.extract_skills')
    @patch('app.helper.extract_languages')
    @patch('app.helper.extract_interests')
    def test_parse_cv_all_missing(self, mock_interests, mock_languages, mock_skills, 
                                mock_experience, mock_education, mock_phone, 
                                mock_email, mock_name, mock_extract_text):
        mock_extract_text.return_value = "Sample CV text"
        mock_name.return_value = None
        mock_email.return_value = None
        mock_phone.return_value = None
        mock_education.return_value = []
        mock_experience.return_value = []
        mock_skills.return_value = []
        mock_languages.return_value = []
        mock_interests.return_value = []
        
        result = parse_cv("test.pdf")
        
        self.assertIsNone(result["Name"])
        self.assertIsNone(result["E-mail"])
        self.assertIsNone(result["Phone"])
        self.assertEqual(result["Education"], [])
        self.assertEqual(result["Experience"], [])
        self.assertEqual(result["Skills"], [])
        self.assertEqual(result["Languages"], [])
        self.assertEqual(result["Interests"], [])

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
                     mock_experience, mock_education, mock_phone, 
                     mock_email, mock_name, mock_extract_text):
        mock_extract_text.return_value = "Sample CV text"
        mock_name.return_value = "John Smith"
        mock_email.return_value = "john.smith@example.com"
        mock_phone.return_value = "(123) 456-7890"
        mock_education.return_value = ["BSc Computer Science"]
        mock_experience.return_value = ["Software Engineer at XYZ"]
        mock_skills.return_value = ["Python", "Java"]
        mock_languages.return_value = ["English", "Spanish"]
        mock_interests.return_value = ["Hiking", "Reading"]
        
        result = parse_cv("test.pdf")
        
        self.assertEqual(result["Name"], "John Smith")
        self.assertEqual(result["E-mail"], "john.smith@example.com")
        self.assertEqual(result["Phone"], "(123) 456-7890")
        self.assertEqual(result["Education"], ["BSc Computer Science"])
        self.assertEqual(result["Experience"], ["Software Engineer at XYZ"])
        self.assertEqual(result["Skills"], ["Python", "Java"])
        self.assertEqual(result["Languages"], ["English", "Spanish"])
        self.assertEqual(result["Interests"], ["Hiking", "Reading"])
        
        mock_extract_text.assert_called_once_with("test.pdf")
        mock_name.assert_called_once_with("Sample CV text")
        mock_email.assert_called_once_with("Sample CV text")
        mock_phone.assert_called_once_with("Sample CV text")
        mock_education.assert_called_once_with("Sample CV text")
        mock_experience.assert_called_once_with("Sample CV text")
        mock_skills.assert_called_once_with("Sample CV text")
        mock_languages.assert_called_once_with("Sample CV text")
        mock_interests.assert_called_once_with("Sample CV text")

    def test_empty_input_extractions(self):
        empty_text = ""
        self.assertIsNone(extract_email(empty_text))
        self.assertIsNone(extract_phone_number(empty_text))
        self.assertEqual(extract_education(empty_text), [])
        self.assertEqual(extract_experience(empty_text), [])
        self.assertEqual(extract_skills(empty_text), [])
        self.assertEqual(extract_interests(empty_text), [])
        self.assertEqual(extract_languages(empty_text), [])

    def test_malformed_input_extractions(self):
        text_bad_email = "Contact me at john.smith[at]example.com"
        self.assertIsNone(extract_email(text_bad_email))
        
        text_bad_phone = "My number is 12345"
        self.assertIsNone(extract_phone_number(text_bad_phone))

    def test_extreme_cv_section_cases(self):
        long_edu_text = "EDUCATION\n" + "\n".join([f"Course {i} at University {i}" for i in range(30)])
        edu_result = extract_education(long_edu_text)
        self.assertTrue(len(edu_result) > 0)
        
        unusual_edu = """
        *** EDUCATION HISTORY ***
        BSc, Computer Science
        University of Example (2018-2022)
        """
        unusual_edu_result = extract_education(unusual_edu)
        self.assertTrue(len(unusual_edu_result) > 0)
        
        unusual_skills = """
        === SKILLS AND COMPETENCIES ===
        * Programming: Python, Java
        * Tools: Git, Docker
        """
        unusual_skills_result = extract_skills(unusual_skills)
        self.assertIn("Python", unusual_skills_result)
        self.assertIn("Java", unusual_skills_result)
        self.assertIn("Git", unusual_skills_result)
        self.assertIn("Docker", unusual_skills_result)
        
        fragment_skills = """
        SKILLS
        Python including various libraries
        Java such as Spring
        JavaScript like React
        Excel etc.
        Tools wherever needed
        """
        fragment_result = extract_skills(fragment_skills)
        self.assertIn("Python", fragment_result)
        self.assertIn("Java", fragment_result)
        self.assertIn("JavaScript", fragment_result)
        self.assertIn("Excel", fragment_result)
        
        no_separator_skills = """
        SKILLS
        Python
        Java
        JavaScript
        """
        no_sep_result = extract_skills(no_separator_skills)
        self.assertIn("Python", no_sep_result)
        self.assertIn("Java", no_sep_result)
        self.assertIn("JavaScript", no_sep_result)

    def test_specific_skill_detection(self):
        text_eng = "Proficient in CAD, SolidWorks, and MATLAB."
        result_eng = extract_skills(text_eng)
        self.assertIn("CAD", result_eng)
        self.assertIn("SolidWorks", result_eng)
        self.assertIn("MATLAB", result_eng)
        
        text_soft = "Strong leadership and communication abilities."
        result_soft = extract_skills(text_soft)
        self.assertIn("Leadership", result_soft)
        self.assertIn("Communication", result_soft)
    
    def test_extract_interests_specific_patterns(self):
        text_context = "My hobbies include playing chess and swimming."
        result_context = extract_interests(text_context)
        self.assertTrue(len(result_context) > 0)
        
        text_phrase = "I am interested in artificial intelligence with focus on neural networks."
        result_phrase = extract_interests(text_phrase)
        self.assertTrue(any("artificial intelligence" in interest.lower() for interest in result_phrase) or
                        any("neural networks" in interest.lower() for interest in result_phrase))
        
        text_multi = "I enjoy playing board games in my free time."
        result_multi = extract_interests(text_multi)
        self.assertTrue(any("board games" in interest.lower() for interest in result_multi) or 
                       "Gaming" in result_multi)
        
        text_no_marker = "I like hiking, photography, and traveling. No interests section here."
        result_no_marker = extract_interests(text_no_marker)
        self.assertTrue(any(interest in ["Hiking", "Photography", "Traveling"] for interest in result_no_marker))
    
    def test_language_extraction_patterns(self):
        text_colon = """
        LANGUAGES:
        English: Native
        Spanish: Intermediate
        """
        result_colon = extract_languages(text_colon)
        self.assertTrue(any("English" in lang for lang in result_colon))
        self.assertTrue(any("Spanish" in lang for lang in result_colon))
        
        text_dash = """
        LANGUAGES
        English - Native
        Spanish - Intermediate
        """
        result_dash = extract_languages(text_dash)
        self.assertTrue(any("English" in lang for lang in result_dash))
        self.assertTrue(any("Spanish" in lang for lang in result_dash))
        
        text_mentions = "I am bilingual in English and Spanish with elementary French."
        result_mentions = extract_languages(text_mentions)
        self.assertIn("English", result_mentions)
    
    def test_language_pattern_detection(self):
        text_fluency = "I am fluent in English and have professional working proficiency in Spanish."
        result_fluency = extract_languages(text_fluency)
        self.assertIn("English", result_fluency)
        
        text_multi_lang = "I am proficient in both English and German."
        result_multi = extract_languages(text_multi_lang)
        self.assertIn("English", result_multi)
        
        text_filter = """
        LANGUAGES
        English (C2) REFERENCES
        Spanish with reference information
        """
        result_filter = extract_languages(text_filter)
        self.assertIn("English", result_filter)
        self.assertNotIn("REFERENCES", result_filter)

        text_implied = "This document is in English but doesn't explicitly list languages."
        result_implied = extract_languages(text_implied)
        self.assertIn("English", result_implied)