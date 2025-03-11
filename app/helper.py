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
    """
    Extract skills from CV text using a more comprehensive approach.
    This combines predefined skills with skills mentioned in dedicated skills sections.
    """
    # Common technical skills to look for
    common_skills = [
        # Programming Languages
        "Python", "Java", "C++", "C#", "JavaScript", "TypeScript", "Ruby", "PHP", "Go", "Rust", "Swift", 
        "Kotlin", "Scala", "R", "Perl", "Bash", "Shell", "COBOL", "Fortran", "Assembly", "HTML", "CSS",
        
        # Databases
        "SQL", "MySQL", "PostgreSQL", "SQLite", "MongoDB", "Oracle", "Redis", "Cassandra", "DynamoDB",
        "MariaDB", "Firebase", "Neo4j", "CouchDB", "Elasticsearch",
        
        # Frameworks & Libraries
        "React", "Angular", "Vue", "Django", "Flask", "Spring", "Node.js", "Express", "Rails", "Laravel",
        "ASP.NET", "jQuery", "Bootstrap", "Tailwind", "Pandas", "NumPy", "TensorFlow", "PyTorch", "Keras",
        "Scikit-learn", "Matplotlib", "Seaborn", 
        
        # Cloud & DevOps
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Jenkins", "Git", "GitHub", "GitLab", "BitBucket",
        "CI/CD", "Terraform", "Ansible", "Puppet", "Chef", "Prometheus", "Grafana", "ELK Stack",
        
        # Other Technical Areas
        "Machine Learning", "Deep Learning", "Data Science", "Artificial Intelligence", "NLP", "Computer Vision",
        "Big Data", "Data Mining", "Data Analysis", "Data Visualization", "ETL", "Business Intelligence",
        "Blockchain", "Cybersecurity", "Network Security", "Penetration Testing", "Cryptography",
        "Web Development", "Mobile Development", "Android", "iOS", "Responsive Design", "UX/UI",
        
        # Soft Skills (include some to be comprehensive)
        "Leadership", "Project Management", "Agile", "Scrum", "Kanban", "Communication", "Teamwork", 
        "Problem Solving", "Critical Thinking", "Time Management"
    ]
    
    # First pass: check if skills are mentioned anywhere in the text
    found_skills = set([skill for skill in common_skills if skill.lower() in text.lower()])
    
    # Second pass: look for dedicated skills sections and extract all items
    skills_keywords = ["Skills", "Technical Skills", "Core Competencies", "Competencies", "Expertise", "Proficiencies"]
    
    # Split the text into lines and look for skills sections
    lines = text.split('\n')
    in_skills_section = False
    for i, line in enumerate(lines):
        # Check if this line is a skills section header
        if any(keyword.lower() in line.lower() for keyword in skills_keywords):
            in_skills_section = True
            continue
        
        # If we're in a skills section, extract comma or bullet separated items
        if in_skills_section:
            # Check if we've moved to a new section
            if line.strip() and any(line.strip().endswith(c) for c in [':', '.']):
                if any(keyword.lower() in line.lower() for keyword in ["Education", "Experience", "Work", "Employment", "Projects"]):
                    in_skills_section = False
                    continue
            
            # Process skills in this line
            if line.strip():
                # Try to split by common separators
                for separator in [',', '•', '·', '○', '●', '■', '▪', '▫', '□', '➢', '►', '»', '|', ';']:
                    if separator in line:
                        skills_in_line = [s.strip() for s in line.split(separator) if s.strip()]
                        found_skills.update(skills_in_line)
                        break
                else:
                    # If no separator found, use the whole line
                    if len(line.strip().split()) <= 4:  # Likely a skill if 4 words or fewer
                        found_skills.add(line.strip())
    
    filtered_skills = {s for s in found_skills if len(s.split()) <= 4}
    
    return sorted(list(filtered_skills))

def extract_interests(text):
    """
    Extract interests and hobbies from CV text using a more comprehensive approach.
    Looks for dedicated interest sections and extracts items.
    """
    common_interests = [
        # Sports & Physical Activities
        "Soccer", "Football", "Basketball", "Tennis", "Golf", "Swimming", "Cycling", 
        "Running", "Hiking", "Climbing", "Yoga", "Fitness", "Gym", "Martial Arts",
        
        # Creative Activities
        "Photography", "Painting", "Drawing", "Writing", "Reading", "Poetry", "Music",
        "Singing", "Dancing", "Playing Guitar", "Piano", "Drums", "Composing", "Art",
        
        # Tech Related
        "Programming", "Coding", "Game Development", "Web Design", "App Development",
        "Robotics", "3D Printing", "Electronics", "DIY Projects", "Maker",
        
        # Travel & Exploration
        "Traveling", "Backpacking", "Camping", "Road Trips", "Sightseeing", "Exploring",
        
        # Social & Entertainment
        "Cooking", "Baking", "Gardening", "Chess", "Board Games", "Video Games", 
        "Movies", "Cinema", "Theater", "Concerts", "Volunteering", "Community Service",
        
        # Learning & Knowledge
        "Learning Languages", "History", "Science", "Astronomy", "Philosophy", "Psychology",
        "Politics", "Current Events", "Public Speaking", "Debating", "Teaching"
    ]
    
    found_interests = set()
    
    for interest in common_interests:
        if interest.lower() in text.lower():
            found_interests.add(interest)
    
    interest_section_keywords = [
        "Interests", "Hobbies", "Personal Interests", "Activities", 
        "Extracurricular Activities", "Leisure Activities", "Pastimes"
    ]
    
    lines = text.split('\n')
    in_interest_section = False
    for i, line in enumerate(lines):
        if any(keyword.lower() in line.lower() for keyword in interest_section_keywords):
            in_interest_section = True
            continue
        
        if in_interest_section:
            if line.strip() and any(line.strip().endswith(c) for c in [':', '.']):
                if any(keyword.lower() in line.lower() for keyword in ["Education", "Experience", "Work", "Skills", "References"]):
                    in_interest_section = False
                    continue
            
            if line.strip():
                for separator in [',', '•', '·', '○', '●', '■', '▪', '▫', '□', '➢', '►', '»', '|', ';']:
                    if separator in line:
                        interests_in_line = [s.strip() for s in line.split(separator) if s.strip()]
                        found_interests.update(interests_in_line)
                        break
                else:
                    if len(line.strip().split()) <= 5:  
                        found_interests.add(line.strip())
    
    filtered_interests = {interest for interest in found_interests if len(interest.split()) <= 5}
    
    return sorted(list(filtered_interests))

def extract_languages(text):
    """
    Extract languages from CV text using a comprehensive approach.
    Looks for dedicated language sections and common language mentions.
    """
    common_languages = [
        "English", "Spanish", "French", "German", "Portuguese", "Italian", "Dutch", "Russian",
        "Arabic", "Chinese", "Mandarin", "Cantonese", "Japanese", "Korean", "Hindi", "Bengali",
        "Urdu", "Turkish", "Vietnamese", "Thai", "Indonesian", "Malay", "Filipino", "Tagalog",
        
        "Swedish", "Norwegian", "Danish", "Finnish", "Polish", "Czech", "Slovak", "Hungarian",
        "Romanian", "Bulgarian", "Greek", "Albanian", "Serbian", "Croatian", "Slovenian",
        "Ukrainian", "Belarusian", "Lithuanian", "Latvian", "Estonian", "Icelandic", "Irish",
        "Welsh", "Gaelic", "Catalan", "Basque", "Galician", "Luxembourgish", "Maltese",
        
        "Punjabi", "Telugu", "Tamil", "Marathi", "Gujarati", "Kannada", "Malayalam", 
        "Nepali", "Sinhalese", "Burmese", "Khmer", "Lao", "Mongolian", "Kazakh", "Uzbek",
        
        "Hebrew", "Persian", "Farsi", "Kurdish", "Armenian", "Georgian", "Azerbaijani",
        
        "Swahili", "Amharic", "Somali", "Yoruba", "Igbo", "Hausa", "Zulu", "Xhosa", 
        "Afrikaans", "Malagasy", "Oromo",
        
        "Bengali", "Javanese", "Wu", "Telugu", "Marathi", "Tamil", "Punjabi"
    ]
    
    found_languages = set()
    
    language_fluency_patterns = [
        "fluent in", "proficient in", "native speaker of", "mother tongue", "bilingual",
        "basic knowledge of", "working knowledge of", "elementary proficiency in",
        "limited working proficiency in", "professional working proficiency in",
        "full professional proficiency in", "native or bilingual proficiency in",
        "A1", "A2", "B1", "B2", "C1", "C2", "CEFR"  # CEFR language levels
    ]
    
    for line in text.split('\n'):
        line_lower = line.lower()
        if any(pattern in line_lower for pattern in language_fluency_patterns):
            for language in common_languages:
                if language.lower() in line_lower:
                    # Try to extract language with proficiency level
                    if ':' in line:
                        parts = line.split(':')
                        if language.lower() in parts[0].lower():
                            found_languages.add(line.strip())
                    elif '-' in line:
                        parts = line.split('-')
                        if language.lower() in parts[0].lower():
                            found_languages.add(line.strip())
                    else:
                        found_languages.add(language)
    
    language_section_keywords = [
        "Languages", "Language Skills", "Language Proficiency", "Foreign Languages",
        "Spoken Languages", "Language Competencies"
    ]
    
    lines = text.split('\n')
    in_language_section = False
    for i, line in enumerate(lines):
        if any(keyword.lower() in line.lower() for keyword in language_section_keywords):
            in_language_section = True
            continue
        
        if in_language_section:
            if line.strip() and any(line.strip().endswith(c) for c in [':', '.']):
                if any(keyword.lower() in line.lower() for keyword in ["Education", "Experience", "Work", "Skills", "References", "Interests"]):
                    in_language_section = False
                    continue
            
            if line.strip():
                for separator in [',', '•', '·', '○', '●', '■', '▪', '▫', '□', '➢', '►', '»', '|', ';']:
                    if separator in line:
                        languages_in_line = [s.strip() for s in line.split(separator) if s.strip()]
                        for item in languages_in_line:
                            if any(language.lower() in item.lower() for language in common_languages):
                                found_languages.add(item)
                        break
                else:
                    if any(language.lower() in line.lower() for language in common_languages):
                        found_languages.add(line.strip())
    
    for language in common_languages:
        pattern = f"{language} language"
        if pattern.lower() in text.lower():
            found_languages.add(language)
    
    filtered_languages = {lang for lang in found_languages if len(lang.split()) <= 7}
    
    return sorted(list(filtered_languages))

def parse_cv(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    extracted_data = {
        "Name": extract_name(text),
        "E-mail": extract_email(text),
        "Phone": extract_phone_number(text),
        "Education": extract_education(text),
        "Experience": extract_experience(text),
        "Skills": extract_skills(text),
        "Languages": extract_languages(text),
        "Interests": extract_interests(text)
    }
    return extracted_data