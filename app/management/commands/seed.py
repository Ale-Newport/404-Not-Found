from django.core.management.base import BaseCommand
from app.models import Admin, Employee, Employer, Job
from random import randint, choices, random
from faker import Faker

class Command(BaseCommand):
    help = "Seed the database with initial data"

    USER_COUNT = 100
    DEFAULT_PASSWORD = 'Password123'

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_users()
        self.admins = Admin.objects.all()
        self.employees = Employee.objects.all()
        self.emplyers = Employer.objects.all()
        self.printAll()

    # User seeding
    def create_users(self):
        self.generate_fixtures_users()
        self.generate_random_users()

    def generate_fixtures_users(self):
        user_fixtures = [
            {'username': '@admin', 'email': 'admin@user.com', 'first_name': 'Admin', 'last_name': 'User', 'user_type': Admin},
            {'username': '@employee', 'email': 'employee@user.com', 'first_name': 'Employee', 'last_name': 'User', 'user_type': Employee},
            {'username': '@employer', 'email': 'employer@user.com', 'first_name': 'Employer', 'last_name': 'User', 'user_type': Employer},
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
        user_type = choices([Admin, Employer, Employee], weights=[3, 12, 85], k=1)[0]
        self.create_user({'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name, 'user_type': user_type})

    def create_user(self, data):
        try:
            user = data['user_type'].objects.create_user(
                username=data['username'],
                email=data['email'],
                password=Command.DEFAULT_PASSWORD,
                first_name=data['first_name'],
                last_name=data['last_name'],
            )
            if data['user_type'] == Admin:
                user.is_staff = True
                user.is_superuser = True
            user.save()
        except:
            print(f"Error creating user: {data}")


    def printAll(self):
        print("Admins:")
        for admin in self.admins:
            print(f"  {admin}")
        print("Employees:")
        for employee in self.employees:
            print(f"  {employee}")
        print("Employers:")
        for employer in self.emplyers:
            print(f"  {employer}")


def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return first_name + '.' + last_name + '@example.com'