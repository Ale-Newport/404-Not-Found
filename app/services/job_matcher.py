from django.db.models import Q
from app.models import Job, Employee

class JobMatcher:
    """
    Service for matching employees to jobs based on skills and interests
    """

    @staticmethod
    def _parse_skills(skills_text):
        if not skills_text:
            return []
        
        separator = ','
        if ';' in skills_text and skills_text.count(';') > skills_text.count(','):
            separator = ';'
        elif '\n' in skills_text and skills_text.count('\n') > max(skills_text.count(','), skills_text.count(';')):
            separator = '\n'
    
    # Split, clean, and filter skills
    skills = [skill.strip().lower() for skill in skills_text.split(separator)]
    return [skill for skill in skills if skill]
    
    @staticmethod
    def _skill_matches(job_skill, employee_skills):
        if job_skill in employee_skills:
            return True
        
        job_skill_lower = job_skill.lower()
        
        skill_variations = {
            'javascript': ['js'],
            'typescript': ['ts'],
            'react': ['reactjs', 'react.js'],
            'react native': ['rn'],
            'node.js': ['nodejs', 'node'],
            'python': ['py'],
            'ruby on rails': ['rails', 'ror'],
            'amazon web services': ['aws'],
            'google cloud platform': ['gcp'],
            'microsoft azure': ['azure'],
            'ci/cd': ['cicd', 'continuous integration', 'continuous deployment'],
            'machine learning': ['ml'],
            'artificial intelligence': ['ai'],
            'user experience': ['ux'],
            'user interface': ['ui'],
            'docker': ['containerization'],
            'kubernetes': ['k8s'],
            'database': ['db'],
            'postgresql': ['postgres'],
            'mongodb': ['mongo']
        }
        
        if job_skill_lower in skill_variations:
            variations = skill_variations[job_skill_lower]
            for variation in variations:
                if variation in employee_skills:
                    return True
        
        for key, variations in skill_variations.items():
            if job_skill_lower in variations and key in employee_skills:
                return True
        
        for employee_skill in employee_skills:
            if (len(employee_skill) > 3 and employee_skill in job_skill_lower) or \
               (len(job_skill_lower) > 3 and job_skill_lower in employee_skill):
                return True
        
        return False

    @staticmethod
    def calculate_match_score(employee_skills, job_required_skills, 
            job_preferred_skills = None, employee_preferred_contract = None, job_type = None):
        """
        Returns a match score from 0-100, list of skills that matched, list of required skills candidate is missing
        """
        
        employee_skills_list = JobMatcher._parse_skills(employee_skills)
        job_required_list = JobMatcher._parse_skills(job_required_skills)
        job_preferred_list = JobMatcher._parse_skills(job_preferred_skills)

        if not employee_skills_list:
            return 15.0, [], job_required_list #base score of 15 for employees with no skills
        
        if not job_required_list and not job_preferred_skills:
            return 50.0, employee_skills_list, [] #if job has no skills, average score of 50
        
        required_matches = [skill for skill in job_required_list if JobMatcher._skill_matches(skill, employee_skills_list)]
        preferred_matches = [skill for skill in job_preferred_list if JobMatcher._skill_matches(skill, employee_skills_list)]
        missing_required = [skill for skill in job_required_list if not JobMatcher._skill_matches(skill, employee_skills_list)]

        required_match_pct = len(required_matches) / len(job_required_list) if job_required_list else 1.0
        preferred_match_pct = len(preferred_matches) / len(job_preferred_list) if job_preferred_list else 1.0

               
        if job_required_list and job_preferred_list:
            required_weight = 0.7  #70% of score from required skills
            preferred_weight = 0.3  #30% of score from preferred skills
        #if either missing, 100% score from present skills
        elif job_required_list:
            required_weight = 1.0
            preferred_weight = 0.0
        else:
            required_weight = 0.0
            preferred_weight = 1.0
        
        skill_score = (required_match_pct * required_weight + preferred_match_pct * preferred_weight) * 90
        
        #add contract type bonus if matching 
        contract_bonus = 0
        if employee_preferred_contract and job_type and employee_preferred_contract == job_type:
            contract_bonus = 10
        
        #calculate final score (cap at 100)
        final_score = min(100, skill_score + contract_bonus)
        
        #combine matching skills lists
        all_matches = required_matches + [s for s in preferred_matches if s not in required_matches]
        
        return round(final_score, 1), all_matches, missing_required
    
    @staticmethod
    def match_employee_to_jobs(employee, jobs = None):
        #if no specific jobs provided, use all
        if jobs is None:
            jobs = Job.objects.all()

        matches = []
        for job in jobs:
            score, matching_skills, missing_skills = JobMatcher.calculate_match_score(
                employee.skills, 
                job.skills_needed, 
                job.skills_wanted,
                employee.preferred_contract,
                job.job_type
            )
            
            matches.append({
                'job': job,
                'score': score,
                'matching_skills': matching_skills,
                'missing_skills': missing_skills,
                'contract_match': employee.preferred_contract == job.job_type
            })

        return sorted(matches, key=lambda x: x['score'], reverse=True)
    

    @staticmethod
    def match_job_to_employees(job, employees=None):
        #if no specific employees provided, use all
        if employees is None:
            employees = Employee.objects.all()
        
        matches = []
        for employee in employees:
            score, matching_skills, missing_skills = JobMatcher.calculate_match_score(
                employee.skills, 
                job.skills_needed, 
                job.skills_wanted,
                employee.preferred_contract,
                job.job_type
            )
            
            matches.append({
                'employee': employee,
                'score': score,
                'matching_skills': matching_skills,
                'missing_skills': missing_skills,
                'contract_match': employee.preferred_contract == job.job_type
            })
        
        return sorted(matches, key=lambda x: x['score'], reverse=True)
