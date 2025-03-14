from django.core.management.base import BaseCommand
from app.models import Admin, Employee, Employer, User, Job
from random import choices
from faker import Faker
from datetime import datetime, timedelta
import pytz

class Command(BaseCommand):
    help = "Seed the database with initial data"

    USER_COUNT = 100
    JOB_COUNT = 100
    DEFAULT_PASSWORD = 'Password123'

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_users()
        self.admins = Admin.objects.all()
        self.employees = Employee.objects.all()
        self.employers = Employer.objects.all()
        self.create_jobs()

    # User seeding
    def create_users(self):
        self.generate_fixtures_users()
        self.generate_random_users()

    def generate_fixtures_users(self):
        user_fixtures = [
            {'username': '@admin', 'email': 'admin@user.com', 'first_name': 'Admin', 'last_name': 'User', 'user_type': 'admin'},
            {'username': '@employee', 'email': 'employee@user.com', 'first_name': 'Employee', 'last_name': 'User', 'user_type': 'employee'},
            {'username': '@employer', 'email': 'employer@user.com', 'first_name': 'Employer', 'last_name': 'User', 'user_type': 'employer'},
        ]
        for data in user_fixtures:
            self.create_user(data)

    def generate_random_users(self):
        user_count = Admin.objects.count() + Employee.objects.count() + Employer.objects.count()
        while user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = Admin.objects.count() + Employee.objects.count() + Employer.objects.count()
        print("User seeding complete.      ")

    def generate_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        user_type = choices(['admin', 'employer', 'employee'], weights=[3, 12, 85], k=1)[0]
        self.create_user({'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name, 'user_type': user_type})

    def create_user(self, data):
        try:
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=Command.DEFAULT_PASSWORD,
                first_name=data['first_name'],
                last_name=data['last_name'],
                user_type=data['user_type']
            )
            if data['user_type'] == 'admin':
                Admin.objects.create(user=user)
                user.is_staff = True
                user.is_superuser = True
            elif data['user_type'] == 'employee':
                Employee.objects.create(user=user)
            elif data['user_type'] == 'employer':
                company_name = data.get('company_name', self.generate_company_name())
                Employer.objects.create(user=user, company_name = company_name,)
            user.save()
        except Exception as e: 
            print(f"Error creating user: {data} - {e}")
    

    
    def generate_company_name(self):
        """Generate a realistic company name using various patterns"""
        patterns = [
            lambda: f"{self.faker.last_name()} {self.get_company_suffix()}",
            lambda: f"{self.faker.word().capitalize()} {self.get_company_suffix()}",
            lambda: f"{self.faker.last_name()} & {self.faker.last_name()} {self.get_company_suffix()}",
            lambda: f"{self.faker.word().capitalize()}{self.faker.word().capitalize()}",
        ]
        return self.faker.random_element(patterns)()

    def get_company_suffix(self):
        """Return a random company suffix"""
        suffixes = [
            'Ltd', 'Limited', 'LLC', 'Inc', 'Industries',
            'Group', 'Technologies', 'Solutions', 'Associates',
            'Consulting', 'Services', 'Systems', 'Corporation'
        ]
        return self.faker.random_element(suffixes)

    # Job seeding
    def create_jobs(self):
        self.generate_fixtures_jobs()
        self.generate_random_jobs()
    
    def generate_fixtures_jobs(self):
        job_fixtures = [
            {'name': 'Software Developer', 'department': 'Engineering', 'description': '', 'salary': 50000, 'job_type': 'FT', 'bonus': 0, 'skills_needed': 'Python, Django', 'skills_wanted': 'AWS, Docker', 'created_at': datetime(2024, 8, 12, 10, 0, tzinfo=pytz.utc), 'created_by': Employer.objects.get(user__username='@employer')},
            {'name': 'Senior Developer', 'department': 'Engineering', 'description': '', 'salary': 100000, 'job_type': 'FT', 'bonus': 10000, 'skills_needed': 'Python, Django', 'skills_wanted': 'AWS, Docker', 'created_at': datetime(2024, 8, 12, 10, 0, tzinfo=pytz.utc), 'created_by': Employer.objects.get(user__username='@employer')},
        ]
        for data in job_fixtures:
            self.create_job(data)
    
    def generate_random_jobs(self):
        job_count = Job.objects.count()
        while job_count < self.JOB_COUNT:
            print(f"Seeding jobs {job_count}/{self.JOB_COUNT}", end='\r')
            self.generate_job()
            job_count = Job.objects.count()
        print("Job seeding complete.      ")

    def generate_job(self):
        # Dictionary of job roles and associated skills
        job_skills = {
            'Software Engineer': [
                'python', 'java', 'javascript', 'react', 'django', 'node.js', 'sql', 'nosql', 
                'docker', 'kubernetes', 'aws', 'git', 'ci/cd', 'microservices', 'rest api'
            ],
            'Data Scientist': [
                'python', 'r', 'sql', 'machine learning', 'deep learning', 'tensorflow', 
                'pytorch', 'pandas', 'numpy', 'data visualization', 'statistics', 'big data'
            ],
            'Web Developer': [
                'html', 'css', 'javascript', 'react', 'vue', 'angular', 'node.js', 'php',
                'wordpress', 'responsive design', 'ui/ux', 'bootstrap', 'sass'
            ],
            'Product Manager': [
                'agile', 'scrum', 'jira', 'product development', 'user research', 'roadmap planning',
                'stakeholder management', 'market analysis', 'a/b testing', 'analytics'
            ],
            'Marketing Specialist': [
                'seo', 'sem', 'social media', 'content marketing', 'analytics', 'email marketing',
                'google ads', 'copywriting', 'brand strategy', 'market research'
            ],
            'UX Designer': [
                'figma', 'sketch', 'adobe xd', 'user research', 'wireframing', 'prototyping',
                'usability testing', 'interaction design', 'information architecture'
            ],
            'DevOps Engineer': [
                'linux', 'aws', 'azure', 'gcp', 'terraform', 'docker', 'kubernetes', 
                'jenkins', 'gitlab ci', 'monitoring', 'automation', 'scripting'
            ],
            'Project Manager': [
                'agile', 'scrum', 'kanban', 'jira', 'ms project', 'risk management',
                'budgeting', 'stakeholder management', 'reporting', 'leadership'
            ],
            'Sales Representative': [
                'crm', 'salesforce', 'negotiation', 'prospecting', 'account management',
                'sales funnel', 'cold calling', 'relationship building', 'presentations'
            ],
            'Accountant': [
                'quickbooks', 'excel', 'financial reporting', 'tax preparation', 'gaap',
                'accounts payable', 'accounts receivable', 'auditing', 'bookkeeping'
            ]
        }

        job_category = self.faker.random_element(list(job_skills.keys()))
        name = f"{job_category} - {self.faker.job()}"

        department = self.faker.bs()
        description = self.faker.text()
        salary = self.faker.random_int(20000, 100000)
        job_type = choices(['FT', 'PT'], weights=[85, 15], k=1)[0]
        bonus = self.faker.random_int(0, 20000)
        all_skills = job_skills[job_category].copy()
        required_count = self.faker.random_int(3, 5)
        required_skills = self.faker.random_elements(all_skills, length=min(required_count, len(all_skills)), unique=True)
        
        for skill in required_skills:
            if skill in all_skills:
                all_skills.remove(skill)
        
        preferred_count = self.faker.random_int(2, 4)
        preferred_skills = self.faker.random_elements(all_skills, length=min(preferred_count, len(all_skills)), unique=True)
        
        skills_needed = ', '.join(required_skills)
        skills_wanted = ', '.join(preferred_skills)
        created_at = self.faker.date_time_this_year()
        created_by = choices(Employer.objects.all(), k=1)[0]
        self.create_job({'name': name, 'department': department, 'description': description, 'salary': salary, 'job_type': job_type, 'bonus': bonus, 'skills_needed': skills_needed, 'skills_wanted': skills_wanted, 'created_at': created_at, 'created_by': created_by})

    def create_job(self, data):
        try:
            job = Job.objects.create(
                name=data['name'],
                department=data['department'],
                description=data['description'],
                salary=data['salary'],
                job_type=data['job_type'],
                bonus=data['bonus'],
                skills_needed=data['skills_needed'],
                skills_wanted=data['skills_wanted'],
                created_at=data['created_at'],
                created_by=data['created_by']
            )
        except Exception as e:
            print(f"Error creating job: {data} - {e}")

    def printAll(self):
        print("Admins:")
        for admin in self.admins:
            print(f"  {admin}")
        print("Employees:")
        for employee in self.employees:
            print(f"  {employee}")
        print("Employers:")
        for employer in self.employers:
            print(f"  {employer}")


def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return first_name + '.' + last_name + '@example.com'
