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
                Employer.objects.create(user=user)
            user.save()
        except Exception as e:
            print(f"Error creating user: {data} - {e}")

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
        name = self.faker.job()
        department = self.faker.bs()
        description = self.faker.text()
        salary = self.faker.random_int(20000, 100000)
        job_type = choices(['FT', 'PT'], weights=[85, 15], k=1)[0]
        bonus = self.faker.random_int(0, 20000)
        skills_needed = ', '.join(self.faker.words(3))
        skills_wanted = ', '.join(self.faker.words(3))
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