from django.core.management.base import BaseCommand
from app.models import Admin, Employee, Employer, User, Job, JobApplication
from random import choices, randint, sample
from faker import Faker
from datetime import datetime, timedelta
import pytz
from project.constants import COUNTRIES
from app.services.job_matcher import JobMatcher
 
class Command(BaseCommand):
    help = "Seed the database with initial data"

    USER_COUNT = 100
    JOB_COUNT = 100
    APPLICATION_COUNT = 200
    DEFAULT_PASSWORD = 'Password123'

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_users()
        self.admins = Admin.objects.all()
        self.employees = Employee.objects.all()
        self.employers = Employer.objects.all()
        self.create_jobs()
        self.create_applications()

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
                skills = self.generate_employee_skills()
                experience = self.generate_employee_experience()
                education = self.generate_employee_education()
                Employee.objects.create(user=user, skills=skills, education=education, experience=experience)
            elif data['user_type'] == 'employer':
                company_name = data.get('company_name', self.generate_company_name())
                Employer.objects.create(user=user, company_name = company_name,)
            user.save()
        except Exception as e: 
            print(f"Error creating user: {data} - {e}")
    
    #Employees
    def generate_employee_skills(self):
        technical_skills = [
            'Python', 'JavaScript', 'Java', 'C#', 'C++', 'Ruby', 'PHP', 'Swift', 'Kotlin', 'Go',
            'React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Flask', 'Laravel', 'Spring Boot',
            'Express.js', 'ASP.NET', 'REST API', 'GraphQL', 'SQL', 'NoSQL', 'MongoDB', 'PostgreSQL',
            'MySQL', 'Redis', 'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform', 'Jenkins',
            'Git', 'CI/CD', 'Machine Learning', 'Data Analysis', 'TensorFlow', 'PyTorch', 'Pandas'
        ]
        
        soft_skills = [
            'Communication', 'Teamwork', 'Problem Solving', 'Critical Thinking', 'Time Management',
            'Leadership', 'Adaptability', 'Creativity', 'Attention to Detail', 'Project Management',
            'Collaboration', 'Presentation Skills', 'Analytical Skills', 'Customer Service'
        ]
        
        skill_count = randint(4, 10)
        technical_count = randint(2, min(skill_count - 1, len(technical_skills)))
        soft_count = min(skill_count - technical_count, len(soft_skills))
        
        selected_skills = sample(technical_skills, technical_count) + sample(soft_skills, soft_count)
        return ', '.join(selected_skills)
    
    def generate_employee_experience(self):
        experience_count = randint(1, 3)
        experiences = []
        
        current_year = datetime.now().year
        end_year = current_year
        
        for i in range(experience_count):
            duration = randint(1, 4)
            start_year = end_year - duration
            
            job_title = self.faker.job()
            company = self.generate_company_name()
            
            responsibilities = []
            for _ in range(randint(2, 4)):
                responsibility_type = self.faker.random_element([
                    f"Developed {self.faker.bs()}",
                    f"Led a team of {randint(2, 10)} in {self.faker.bs()}",
                    f"Improved {self.faker.bs()} by {randint(10, 50)}%",
                    f"Managed {self.faker.bs()} with a budget of £{randint(10, 100)}k",
                    f"Created {self.faker.bs()} resulting in {self.faker.bs()}"
                ])
                responsibilities.append(f"• {responsibility_type}")
            
            experience = f"{job_title} at {company} ({start_year} - {end_year if i == 0 else 'Present' if i == 0 else end_year})\n"
            experience += "\n".join(responsibilities)
            experiences.append(experience)
            
            end_year = start_year - 1 
        
        return "\n\n".join(experiences)
    
    def generate_employee_education(self):
        education_count = randint(1, 2)
        educations = []
        
        degree_types = [
            'BSc', 'BA', 'BEng', 'MSc', 'MA', 'MEng', 'PhD', 
            'Diploma', 'Certificate', 'Associate Degree'
        ]
        
        fields = [
            'Computer Science', 'Information Technology', 'Software Engineering', 
            'Data Science', 'Business Administration', 'Marketing', 'Economics',
            'Mathematics', 'Statistics', 'Engineering', 'Physics', 'Design',
            'Communications', 'Psychology', 'Finance', 'Accounting'
        ]
        
        current_year = datetime.now().year
        end_year = current_year - randint(0, 5)
        
        for i in range(education_count):
            degree = self.faker.random_element(degree_types)
            field = self.faker.random_element(fields)
            university = f"{self.faker.city()} University" if self.faker.boolean(70) else f"University of {self.faker.city()}"
            
            duration = 3 if degree in ['BSc', 'BA', 'BEng'] else 2 if degree in ['MSc', 'MA', 'MEng'] else 4 if degree == 'PhD' else 1
            start_year = end_year - duration
            
            highlights = []
            for _ in range(randint(1, 3)):
                highlight_type = self.faker.random_element([
                    f"Graduated with {self.faker.random_element(['First Class Honours', 'Upper Second Class Honours', 'Distinction', 'Merit'])}",
                    f"Specialized in {self.faker.bs()}",
                    f"Completed dissertation on {self.faker.bs()}",
                    f"Received scholarship for {self.faker.bs()}",
                    f"Participated in {self.faker.bs()}"
                ])
                highlights.append(f"• {highlight_type}")
            
            education = f"{degree} in {field} from {university} ({start_year} - {end_year})\n"
            education += "\n".join(highlights)
            educations.append(education)
            
            end_year = start_year - randint(1, 3)
        
        return "\n\n".join(educations)
    
    #Employers
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
            {'name': 'Software Developer', 'department': 'Engineering', 'description': '', 'salary': 50000, 'job_type': 'FT', 'bonus': 0, 'skills_needed': 'Python, Django', 'skills_wanted': 'AWS, Docker', 'created_at': datetime(2024, 8, 12, 10, 0, tzinfo=pytz.utc), 'created_by': Employer.objects.get(user__username='@employer'), 'country': 'UK'},
            {'name': 'Senior Developer', 'department': 'Engineering', 'description': '', 'salary': 100000, 'job_type': 'FT', 'bonus': 10000, 'skills_needed': 'Python, Django', 'skills_wanted': 'AWS, Docker', 'created_at': datetime(2024, 8, 12, 10, 0, tzinfo=pytz.utc), 'created_by': Employer.objects.get(user__username='@employer'), 'country': 'US'},
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
        country = self.faker.random_element([c[0] for c in COUNTRIES])
        self.create_job({'name': name, 'department': department, 'description': description, 'salary': salary, 'job_type': job_type, 'bonus': bonus, 'skills_needed': skills_needed, 'skills_wanted': skills_wanted, 'created_at': created_at, 'created_by': created_by, 'country': country})

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
                created_by=data['created_by'],
                country=data['country']
            )
        except Exception as e:
            print(f"Error creating job: {data} - {e}")

    #Application seeding

    def create_applications(self):
        self.generate_fixture_application()
        self.generate_random_applications()

    def create_application(self, data):
        try:
            #check if an application already exists for this job-applicant pair
            if JobApplication.objects.filter(job=data['job'], applicant=data['applicant']).exists():
                return
                
            application = JobApplication.objects.create(
                job=data['job'],
                applicant=data['applicant'],
                status=data['status'],
                cover_letter=data['cover_letter'],
                full_name=data['full_name'],
                email=data['email'],
                phone=data['phone'],
                country=data['country'],
                current_position=data['current_position'],
                skills=data['skills'],
                experience=data['experience'],
                education=data['education'],
                portfolio_url=data['portfolio_url'],
                linkedin_url=data['linkedin_url']
            )
            return application
        except Exception as e:
            print(f"Error creating application: {e}")

    def generate_fixture_application(self):
        employer_jobs = Job.objects.filter(created_by__user__username='@employer')
        employer_job = employer_jobs.first() if employer_jobs.exists() else Job.objects.first()
        
        application_fixtures = [
            {
                'job': employer_job,
                'applicant': Employee.objects.get(user__username='@employee'),
                'status': 'pending',
                'cover_letter': 'I am very interested in this position and believe my skills match your requirements.',
                'full_name': 'Employee User',
                'email': 'employee@user.com',
                'phone': '+44 1234 567890',
                'country': 'GB',
                'current_position': 'Junior Developer',
                'skills': 'Python, Django, JavaScript',
                'experience': '2 years of web development experience',
                'education': 'BSc Computer Science from King\'s College London',
                'portfolio_url': 'https://portfolio.employeeuser.com',
                'linkedin_url': 'https://linkedin.com/in/employeeuser'
            }
        ]

        for data in application_fixtures:
            self.create_application(data)

    def generate_random_applications(self):
        application_count = JobApplication.objects.count()
        jobs = list(Job.objects.all())
        employees = list(Employee.objects.all())
        
        possible_combinations = min(len(jobs) * len(employees), self.APPLICATION_COUNT)
        
        while application_count < possible_combinations:
            print(f"Seeding application {application_count}/{possible_combinations}", end='\r')
            self.generate_applications()
            application_count = JobApplication.objects.count()
        print("Application seeding complete.      ")
        
    def generate_applications(self):
        existing_applications = set(JobApplication.objects.values_list('job_id', 'applicant_id'))
        
        available_jobs = Job.objects.all()
        available_employees = Employee.objects.all()

        #try a few times to find a unique job-applicant pair
        for _ in range(10):
            job = self.faker.random_element(available_jobs)
            employee = self.faker.random_element(available_employees)
            
            if (job.id, employee.user_id) not in existing_applications:
                break
        else:
            #if we couldn't find a unique pair after 10 tries, just return
            return

        status = choices(['pending', 'reviewing', 'rejected'], 
                        weights=[60, 20, 10], k=1)[0]
        
        original_skills = employee.skills or ""
    
        job_required_skills = JobMatcher._parse_skills(job.skills_needed)
        job_preferred_skills = JobMatcher._parse_skills(job.skills_wanted)
        all_job_skills = job_required_skills + job_preferred_skills
        
        enhance_skills = self.faker.boolean(chance_of_getting_true=70)

        if enhance_skills and all_job_skills:
            max_skills_to_add = max(1, int(len(all_job_skills) * 0.7))
            num_skills_to_add = self.faker.random_int(min=1, max=max_skills_to_add)
            
            skills_to_add = self.faker.random_elements(
                elements=all_job_skills,
                length=min(num_skills_to_add, len(all_job_skills)),
                unique=True
            )
            
            employee_skills_list = JobMatcher._parse_skills(original_skills)
            
            for skill in skills_to_add:
                if skill not in employee_skills_list:
                    employee_skills_list.append(skill)
            
            enhanced_skills = ", ".join(employee_skills_list)
        else:
            enhanced_skills = original_skills

        application_data = {
            'job': job,
            'applicant': employee,
            'status': status,
            'cover_letter': self.faker.paragraph(nb_sentences=3),
            'full_name': f"{employee.first_name} {employee.last_name}",
            'email': employee.email,
            'phone': self.faker.phone_number(),
            'country': self.faker.random_element([c[0] for c in COUNTRIES]),
            'current_position': self.faker.job(),
            'skills': enhanced_skills,
            'experience': employee.experience,
            'education': employee.education,
            'portfolio_url': self.faker.boolean(chance_of_getting_true=30) and f"https://{self.faker.domain_name()}/portfolio" or "",
            'linkedin_url': self.faker.boolean(chance_of_getting_true=70) and f"https://linkedin.com/in/{employee.user.username.replace('@', '')}" or ""
        }

        self.create_application(application_data)

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
