# Helper methods for the application

# CV reader:
import pdfplumber
import spacy
import re


nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    return text.strip()

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else None

def extract_phone_number(text):
    match = re.search(r'\(?\+?[0-9]{1,4}\)?[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}', text)
    return match.group(0) if match else None

def extract_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None

def extract_education(text):
    education_keywords = ["Bachelor", "Master", "PhD", "Degree", "University", "College", "BSc", "MSc", "MBA"]
    education_info = []
    for line in text.split("\n"):
        if any(keyword.lower() in line.lower() for keyword in education_keywords):
            education_info.append(line.strip())
    return education_info

def extract_experience(text):
    """Busca menciones de experiencia laboral en el CV."""
    experience_keywords = ["Experience", "Internship", "Worked at", "Company", "Job", "Position"]
    experience_info = []
    for line in text.split("\n"):
        if any(keyword.lower() in line.lower() for keyword in experience_keywords):
            experience_info.append(line.strip())
    return experience_info

def extract_skills(text):
    common_skills = ["Python", "Java", "C++", "SQL", "Machine Learning", "Data Science", "Cloud Computing", "Cybersecurity", "Docker", "AWS"]
    found_skills = [skill for skill in common_skills if skill.lower() in text.lower()]
    return found_skills

def extract_interests(text):
    """Extract interests or hobbies from the CV text."""
    interest_keywords = ["Interest", "Hobby", "Hobbies", "Passion", "Activities", "Enjoy"]
    interest_info = []
    for line in text.split("\n"):
        if any(keyword.lower() in line.lower() for keyword in interest_keywords):
            interest_info.append(line.strip())
    return interest_info

def parse_cv(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    extracted_data = {
        "Name": extract_name(text),
        "E-mail": extract_email(text),
        "Phone": extract_phone_number(text),
        "Education": extract_education(text),
        "Experience": extract_experience(text),
        "Skills": extract_skills(text),
        "Interests": extract_interests(text)
    }
    return extracted_data
