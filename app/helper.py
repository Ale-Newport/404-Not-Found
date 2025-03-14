import pdfplumber
import spacy
import re
import fitz

nlp = spacy.load("en_core_web_sm")

def is_valid_pdf(pdf_path):
    """Check if a file is a valid PDF before attempting to parse it."""
    try:
        doc = fitz.open(pdf_path)
        return len(doc) > 0
    except Exception:
        return False

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF, ensuring it is valid."""
    if not is_valid_pdf(pdf_path):
        return ""

    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n"
        return text.strip()
    except Exception as e:
        return ""


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
    Extract skills from CV text using a more reliable approach that filters out non-skills.
    """
    common_skills = [
        # Technical Skills
        "Python", "Java", "C++", "C#", "JavaScript", "TypeScript", "Ruby", "PHP", "Go", "Swift", 
        "SQL", "MySQL", "PostgreSQL", "MongoDB", "AWS", "Azure", "GCP", "Docker", "Kubernetes",
        "Git", "GitHub", "Jenkins", "CI/CD", "React", "Angular", "Vue", "Django", "Flask", 
        "TensorFlow", "PyTorch", "Machine Learning", "Data Science", "AI", "Data Analysis",
        "Web Development", "Mobile Development", "Android", "iOS", "Excel", "PowerPoint", "Word",
        
        # Engineering Skills
        "CAD", "AutoCAD", "SolidWorks", "MATLAB", "Simulink", "Circuit Design", "PCB Design",
        "Mechanical Engineering", "Civil Engineering", "Electrical Engineering", "Aerospace Engineering",
        "Structural Analysis", "Fluid Dynamics", "Thermodynamics", "Control Systems",
        
        # Transferable Skills
        "Project Management", "Teamwork", "Leadership", "Communication", "Problem Solving",
        "Critical Thinking", "Time Management", "Customer Service", "Sales", "Negotiation",
        "Conflict Resolution", "Presentation", "Public Speaking", "Report Writing", "Research",
        
        # Industry-Specific
        "Vehicle Maintenance", "Repair", "Servicing", "Diagnostics", "Parts Management",
        "Warehouse Management", "Inventory Control", "Stock Management", "Customer Support",
        "Technical Support", "Quality Assurance", "Quality Control"
    ]
    
    exclude_sections = [
        "REFERENCES", "EDUCATION", "WORK EXPERIENCE", "INTERESTS", "HOBBIES", 
        "CONTACT", "PROFILE", "SUMMARY", "OBJECTIVE", "NAME"
    ]
    
    non_skill_indicators = [
        "and", "the", "to", "in", "for", "of", "with", "from", "by", "as", "on", "at", "also",
        "i", "my", "we", "this", "that", "these", "those", "then", "than", "when"
    ]
    
    fragment_indicators = [
        "including", "included", "includes", "such as", "like", "etc", "etc.", "wherever",
        "wherever needed", "wherever required"
    ]
    
    found_skills = set()
    
    for skill in common_skills:
        if skill.lower() in text.lower():
            words = re.findall(r'\b\w+\b', text.lower())
            if skill.lower() in words:
                found_skills.add(skill)
    
    skills_keywords = ["Skills", "Technical Skills", "Core Competencies", "Competencies", 
                       "Key Skills", "Professional Skills", "Technical Proficiencies"]
    
    lines = text.split('\n')
    in_skills_section = False
    skills_section_content = []
    
    for i, line in enumerate(lines):
        if any(keyword.lower() in line.lower() for keyword in skills_keywords) and not in_skills_section:
            in_skills_section = True
            continue
        
        if in_skills_section and line.strip() and any(keyword.lower() in line.lower() for keyword in exclude_sections):
            in_skills_section = False
        
        if in_skills_section and line.strip():
            skills_section_content.append(line.strip())
    
    if skills_section_content:
        for line in skills_section_content:
            skills_in_line = []
            for separator in [',', '•', '·', '○', '●', '■', '▪', '▫', '□', '➢', '►', '»', '|', ';']:
                if separator in line:
                    skills_in_line = [s.strip() for s in line.split(separator) if s.strip()]
                    break
            else:
                skills_in_line = [line.strip()]
            
            for skill in skills_in_line:
                if len(skill.split()) > 4:
                    continue
                
                if any(skill.lower().startswith(indicator + " ") for indicator in non_skill_indicators):
                    continue
                
                if any(indicator in skill.lower() for indicator in fragment_indicators):
                    continue
                
                if any(exclude.lower() in skill.lower() for exclude in exclude_sections):
                    continue
                
                if re.search(r'[A-Z]+ - \d+', skill):
                    continue
                
                found_skills.add(skill)
    
    context_skills = [
        "Vehicle Maintenance", "Vehicle Repair", "Parts Management", "Warehouse Management",
        "Stock Control", "Customer Service", "Food Preparation", "Kitchen Operations",
        "Industrial Dishwasher Operation", "Cleaning", "Money Handling", "Retail Operations",
        "Technical Apprenticeship", "Vehicle Servicing", "Workshop Operations"
    ]
    
    for skill in context_skills:
        if skill.lower() in text.lower():
            found_skills.add(skill)
    
    filtered_skills = set()
    for skill in found_skills:
        if re.search(r'[A-Z]+ - \d+', skill):
            continue
        if any(word in skill.lower() for word in ["reference", "interest", "hobby"]):
            continue
        filtered_skills.add(skill)
    
    return sorted(list(filtered_skills))

def extract_interests(text):
    """
    Extract genuine interests and hobbies from CV text using a more reliable approach
    that filters out non-interest content.
    """
    # Common interest and hobby keywords to look for
    common_interests = [
        # Sports & Physical Activities
        "Soccer", "Football", "Basketball", "Tennis", "Golf", "Swimming", "Cycling", 
        "Running", "Hiking", "Climbing", "Yoga", "Fitness", "Gym", "Martial Arts",
        "Badminton", "Kayaking", "Sports", "Athletics", "Boxing", "Skiing", "Snowboarding",
        
        # Creative Activities
        "Photography", "Painting", "Drawing", "Writing", "Reading", "Poetry", "Music",
        "Singing", "Dancing", "Guitar", "Piano", "Drums", "Art", "Crafts", "Design",
        "Cooking", "Baking", "Knitting", "Sewing", "Theatre", "Acting",
        
        # Tech & Intellectual Interests
        "Programming", "Coding", "Technology", "Computers", "Robotics", "Electronics",
        "Science", "Physics", "Astronomy", "Space", "History", "Philosophy", "Politics",
        "Psychology", "Literature", "Languages", "Learning", "Research", "Chess",
        
        # Travel & Exploration
        "Traveling", "Travel", "Backpacking", "Camping", "Hiking", "Sightseeing",
        "Exploring", "Adventure", "Outdoors", "Nature", "Wildlife", "Environment",
        
        # Social & Entertainment
        "Volunteering", "Community Service", "Charity", "Mentoring", "Teaching",
        "Movies", "Cinema", "Theatre", "Gaming", "Video Games", "Board Games",
        "Socializing", "Networking", "Events", "Festivals", "Concerts"
    ]
    
    exclude_sections = [
        "REFERENCES", "EDUCATION", "WORK EXPERIENCE", "SKILLS", "CONTACT", 
        "PROFILE", "SUMMARY", "OBJECTIVE", "NAME"
    ]
    
    non_interest_indicators = [
        "and", "the", "to", "in", "for", "of", "with", "from", "by", "as", "on", "at",
        "i", "my", "we", "this", "that", "these", "those", "then", "than", "when"
    ]
    
    found_interests = set()
    genuine_interests = set()
    
    interest_section_keywords = [
        "Interests", "Hobbies", "Personal Interests", "Activities", 
        "Extracurricular Activities", "Leisure Activities", "Pastimes"
    ]
    
    lines = text.split('\n')
    in_interest_section = False
    interest_section_content = []
    
    for i, line in enumerate(lines):
        if any(keyword.lower() in line.lower() for keyword in interest_section_keywords) and not in_interest_section:
            in_interest_section = True
            continue
        
        if in_interest_section and line.strip() and any(keyword.lower() in line.lower() for keyword in exclude_sections):
            in_interest_section = False
        
        if in_interest_section and line.strip():
            interest_section_content.append(line.strip())
    
    if interest_section_content:
        for line in interest_section_content:
            interests_in_line = []
            for separator in [',', '•', '·', '○', '●', '■', '▪', '▫', '□', '➢', '►', '»', '|', ';']:
                if separator in line:
                    interests_in_line = [s.strip() for s in line.split(separator) if s.strip()]
                    break
            else:
                interests_in_line = [line.strip()]
            
            for interest in interests_in_line:
                if any(exclude.lower() in interest.lower() for exclude in exclude_sections):
                    continue
                    
                if re.search(r'[A-Z]+ - \d+', interest):
                    continue
                    
                if "reference" in interest.lower():
                    continue
                    
                found_interests.add(interest)
    
    for interest in common_interests:
        pattern = r'\b' + re.escape(interest.lower()) + r'\b'
        if re.search(pattern, text.lower()):
            genuine_interests.add(interest)
    
    interest_phrases = re.findall(r'interested in\s+(.+?)(?:\.|\,|\;|\n)', text.lower())
    for phrase in interest_phrases:
        clean_phrase = phrase.strip()
        if clean_phrase and len(clean_phrase.split()) <= 7: 
            for interest in common_interests:
                if interest.lower() in clean_phrase:
                    match_pos = clean_phrase.find(interest.lower())
                    start_pos = max(0, match_pos - 20)
                    end_pos = min(len(clean_phrase), match_pos + len(interest) + 20)
                    context = clean_phrase[start_pos:end_pos]
                    
                    context_words = context.split()
                    if len(context_words) > 1:
                        for i in range(len(context_words)):
                            if interest.lower() in context_words[i].lower():
                                end_idx = min(i + 4, len(context_words))
                                phrase = " ".join(context_words[i:end_idx])
                                if phrase and not any(exclude.lower() in phrase.lower() for exclude in exclude_sections):
                                    genuine_interests.add(phrase.capitalize())
                    else:
                        genuine_interests.add(interest)
    
    for item in found_interests:
        if len(item.split()) > 5:
            continue
            
        if any(item.lower().startswith(indicator + " ") for indicator in non_interest_indicators):
            continue
            
        contains_interest = False
        for interest in common_interests:
            if interest.lower() in item.lower():
                contains_interest = True
                interest_parts = item.split()
                if len(interest_parts) <= 2:  
                    genuine_interests.add(item)
                else:
                    for part in interest_parts:
                        if any(interest.lower() in part.lower() for interest in common_interests):
                            genuine_interests.add(part)
                break
        
        if not contains_interest and 1 <= len(item.split()) <= 3:
            genuine_interests.add(item)
    
    specific_interests = [
        "Guitar", "Martial Arts", "Kayaking", "Badminton",
        "UK Space Industry", "Renewable Energy", "Bio-technology"
    ]
    
    for interest in specific_interests:
        if interest.lower() in text.lower():
            genuine_interests.add(interest)
    
    final_interests = set()
    for interest in genuine_interests:
        if re.search(r'[A-Z]+ - \d+', interest):
            continue
        if any(word in interest.lower() for word in ["reference", "skill", "experience", "education", "two references here"]):
            continue
        if len(interest.strip()) < 3:
            continue
        final_interests.add(interest)
    
    return sorted(list(final_interests))

def extract_languages(text):
    """
    Extract languages from CV text using a comprehensive and refined approach.
    Looks for dedicated language sections and common language mentions while
    filtering out non-language content.
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
        "Afrikaans", "Malagasy", "Oromo"
    ]
    
    exclude_sections = [
        "REFERENCES", "EDUCATION", "WORK EXPERIENCE", "SKILLS", "INTERESTS", "HOBBIES",
        "CONTACT", "PROFILE", "SUMMARY", "OBJECTIVE", "NAME"
    ]
    
    found_languages = set()
    
    language_fluency_patterns = [
        "fluent in", "proficient in", "native speaker of", "mother tongue", "bilingual",
        "basic knowledge of", "working knowledge of", "elementary proficiency in",
        "limited working proficiency in", "professional working proficiency in",
        "full professional proficiency in", "native or bilingual proficiency in",
        "A1", "A2", "B1", "B2", "C1", "C2", "CEFR" 
    ]
    
    language_section_keywords = [
        "Languages", "Language Skills", "Language Proficiency", "Foreign Languages",
        "Spoken Languages", "Language Competencies"
    ]
    
    lines = text.split('\n')
    in_language_section = False
    language_section_content = []
    
    for i, line in enumerate(lines):
        if any(keyword.lower() in line.lower() for keyword in language_section_keywords) and not in_language_section:
            in_language_section = True
            continue
        
        if in_language_section and line.strip() and any(keyword.lower() in line.lower() for keyword in exclude_sections):
            in_language_section = False
        
        if in_language_section and line.strip():
            language_section_content.append(line.strip())
    
    if language_section_content:
        for line in language_section_content:
            languages_in_line = []
            for separator in [',', '•', '·', '○', '●', '■', '▪', '▫', '□', '➢', '►', '»', '|', ';']:
                if separator in line:
                    languages_in_line = [s.strip() for s in line.split(separator) if s.strip()]
                    break
            else:
                languages_in_line = [line.strip()]
            
            for language_entry in languages_in_line:
                if any(exclude.lower() in language_entry.lower() for exclude in exclude_sections):
                    continue
                    
                if re.search(r'[A-Z]+ - \d+', language_entry):
                    continue
                    
                contains_language = False
                for language in common_languages:
                    if language.lower() in language_entry.lower():
                        contains_language = True
                        
                        if ':' in language_entry:
                            parts = language_entry.split(':')
                            if language.lower() in parts[0].lower():
                                found_languages.add(language_entry.strip())
                                break
                        elif '-' in language_entry:
                            parts = language_entry.split('-')
                            if language.lower() in parts[0].lower():
                                found_languages.add(language_entry.strip())
                                break
                        elif '(' in language_entry and ')' in language_entry:
                            found_languages.add(language_entry.strip())
                            break
                        else:
                            found_languages.add(language)
                            break
                
                if not contains_language and len(language_entry.split()) <= 3:
                    found_languages.add(language_entry)
    
    for line in lines:
        line_lower = line.lower()
        if any(pattern in line_lower for pattern in language_fluency_patterns):
            for language in common_languages:
                if language.lower() in line_lower:
                    lang_pos = line_lower.find(language.lower())
                    if lang_pos >= 0:
                        for pattern in language_fluency_patterns:
                            pattern_pos = line_lower.find(pattern)
                            if pattern_pos >= 0:
                                start_pos = min(lang_pos, pattern_pos)
                                end_pos = max(lang_pos + len(language), pattern_pos + len(pattern))
                                
                                start_pos = max(0, start_pos - 5)
                                end_pos = min(len(line), end_pos + 15)
                                
                                language_info = line[start_pos:end_pos].strip()
                                
                                language_info = language_info.strip('.,;:()[]{}')
                                
                                if language_info and len(language_info.split()) <= 5:
                                    found_languages.add(language_info)
    
    filtered_languages = set()
    for entry in found_languages:
        if re.search(r'[A-Z]+ - \d+', entry):
            continue
        if any(word in entry.lower() for word in ["reference", "skill", "experience", "education", "two references here"]):
            continue
        if len(entry.strip()) < 3:
            continue
        filtered_languages.add(entry)
    
    if not filtered_languages and "English" in text:
        filtered_languages.add("English")
    
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