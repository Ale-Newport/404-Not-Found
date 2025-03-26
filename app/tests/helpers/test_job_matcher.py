from django.test import TestCase
from app.services.job_matcher import JobMatcher
from app.models import User, Employee, Job, Employer
from django.utils import timezone

class JobMatcherTests(TestCase):
    def setUp(self):
        # Create employer
        employer_user = User.objects.create_user(
            username='@employer',
            email='employer@example.com',
            password='testpassword',
            user_type='employer'
        )
        self.employer = Employer.objects.create(user=employer_user, company_name='Test Company')
        
        # Create employees
        employee1_user = User.objects.create_user(
            username='@employee1',
            email='employee1@example.com',
            password='testpassword',
            user_type='employee'
        )
        self.employee1 = Employee.objects.create(
            user=employee1_user,
            skills='Python, Django, JavaScript, React, AWS',
            preferred_contract='FT'
        )
        
        employee2_user = User.objects.create_user(
            username='@employee2',
            email='employee2@example.com',
            password='testpassword',
            user_type='employee'
        )
        self.employee2 = Employee.objects.create(
            user=employee2_user,
            skills='Java, Spring, Docker, Kubernetes',
            preferred_contract='PT'
        )
        
        # Create jobs
        self.job1 = Job.objects.create(
            name='Python Developer',
            department='Engineering',
            description='We need a Python developer',
            salary=50000,
            bonus=5000,
            country='UK',
            created_by=self.employer,
            skills_needed='Python, Django',
            skills_wanted='React, AWS',
            job_type='FT'
        )
        
        self.job2 = Job.objects.create(
            name='DevOps Engineer',
            department='Engineering',
            description='We need a DevOps engineer',
            salary=60000,
            bonus=6000,
            country='UK',
            created_by=self.employer,
            created_at=timezone.now(),
            skills_needed='Docker, Kubernetes, AWS',
            skills_wanted='Python, CI/CD',
            job_type='PT'
        )
    
    def test_parse_skills(self):
        # Test parsing comma-separated skills
        skills = "Python, Django, JavaScript"
        parsed = JobMatcher._parse_skills(skills)
        self.assertEqual(parsed, ['python', 'django', 'javascript'])
        
        # Test parsing semicolon-separated skills
        skills = "Python; Django; JavaScript"
        parsed = JobMatcher._parse_skills(skills)
        self.assertEqual(parsed, ['python', 'django', 'javascript'])
        
        # Test parsing newline-separated skills
        skills = "Python\nDjango\nJavaScript"
        parsed = JobMatcher._parse_skills(skills)
        self.assertEqual(parsed, ['python', 'django', 'javascript'])
        
        # Test parsing empty string
        parsed = JobMatcher._parse_skills("")
        self.assertEqual(parsed, [])
        
        # Test parsing None
        parsed = JobMatcher._parse_skills(None)
        self.assertEqual(parsed, [])
    
    def test_skill_matches(self):
        employee_skills = ['python', 'django', 'js', 'react.js', 'aws']
        
        # Test exact match
        self.assertTrue(JobMatcher._skill_matches('python', employee_skills))
        
        # Test mismatch
        self.assertFalse(JobMatcher._skill_matches('java', employee_skills))
        
        # Test variation match
        self.assertTrue(JobMatcher._skill_matches('JavaScript', employee_skills))
        self.assertTrue(JobMatcher._skill_matches('Amazon Web Services', employee_skills))
        
        # Test substring match
        self.assertTrue(JobMatcher._skill_matches('python programming', employee_skills))
    
    def test_calculate_match_score(self):
        # Test perfect match with contract bonus
        score, matching, missing = JobMatcher.calculate_match_score(
            "Python, Django, React, AWS",
            "Python, Django",
            "React, AWS",
            "FT",
            "FT"
        )
        self.assertEqual(score, 100.0)
        self.assertEqual(set(matching), {'python', 'django', 'react', 'aws'})
        self.assertEqual(missing, [])
        
        # Test partial match
        score, matching, missing = JobMatcher.calculate_match_score(
            "Python, Django",
            "Python, Django, JavaScript",
            "React, AWS"
        )
        self.assertLess(score, 90.0)  # Less than perfect score
        self.assertEqual(set(matching), {'python', 'django'})
        self.assertEqual(missing, ['javascript'])
        
        # Test no skills provided by employee
        score, matching, missing = JobMatcher.calculate_match_score(
            "",
            "Python, Django",
            "React, AWS"
        )
        self.assertEqual(score, 15.0)  # Base score for no skills
        self.assertEqual(matching, [])
        self.assertEqual(set(missing), {'python', 'django'})
        
        # Test no required skills in job
        score, matching, missing = JobMatcher.calculate_match_score(
            "Python, Django",
            "",
            "React, AWS"
        )
        self.assertEqual(missing, [])
        
        # Test with variation matches
        score, matching, missing = JobMatcher.calculate_match_score(
            "js, reactjs, aws",
            "JavaScript, React, Amazon Web Services",
            ""
        )
        self.assertEqual(score, 90.0)  # Perfect match with variations
        self.assertEqual(len(matching), 3)
        self.assertEqual(missing, [])
    
    def test_match_employee_to_jobs(self):
        # Test matching employee1 to all jobs
        matches = JobMatcher.match_employee_to_jobs(self.employee1)
        
        # Should match both jobs, but job1 should be higher match
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0]['job'], self.job1)  # First match should be job1
        self.assertTrue(matches[0]['score'] > matches[1]['score'])
        
        # Check contract match
        self.assertTrue(matches[0]['contract_match'])
        self.assertFalse(matches[1]['contract_match'])
        
        # Test matching against filtered job list
        matches = JobMatcher.match_employee_to_jobs(self.employee1, [self.job2])
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['job'], self.job2)
    
    def test_match_job_to_employees(self):
        # Test matching job1 to all employees
        matches = JobMatcher.match_job_to_employees(self.job1)
        
        # Should match both employees, but employee1 should be higher match
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0]['employee'], self.employee1)  # First match should be employee1
        self.assertTrue(matches[0]['score'] > matches[1]['score'])
        
        # Check contract match
        self.assertTrue(matches[0]['contract_match'])
        self.assertFalse(matches[1]['contract_match'])
        
        # Test matching against filtered employee list
        matches = JobMatcher.match_job_to_employees(self.job1, [self.employee2])
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['employee'], self.employee2)
    
    def test_edge_cases(self):
        # Test with empty skills fields
        empty_skills_employee = Employee.objects.create(
            user=User.objects.create_user(
                username='@emptyskills',
                email='empty@example.com',
                password='testpassword',
                user_type='employee'
            ),
            skills='',
            preferred_contract='FT'
        )
        
        matches = JobMatcher.match_employee_to_jobs(empty_skills_employee)
        # Should still return matches but with low scores
        self.assertEqual(len(matches), 2)
        self.assertLess(matches[0]['score'], 25.0)  # Low score expected
        
        # Test with job having no required skills
        no_skills_job = Job.objects.create(
            name='No Skills Job',
            department='None',
            description='A job with no specific skills',
            salary=40000,
            bonus=4000,
            country='UK',
            created_by=self.employer,
            created_at=timezone.now(),
            skills_needed='',
            skills_wanted='',
            job_type='FT'
        )
        
        matches = JobMatcher.match_job_to_employees(no_skills_job)
        # Should return moderate scores since no skills to match against
        self.assertEqual(len(matches), 3)  # All 3 employees
        self.assertGreater(matches[0]['score'], 40.0)  # Moderate base score