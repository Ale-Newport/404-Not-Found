from django.core.management.base import BaseCommand
from app.models import Admin, Employee, Employer

class Command(BaseCommand):
    help = "Seed the database with initial data"

    def handle(self, *args, **kwargs):
        # Create an Admin user
        if not Admin.objects.filter(email="admin@example.com").exists():
            Admin.objects.create_superuser(
                email="admin@example.com",
                password="Password123",
                first_name="Super",
                last_name="Admin",
            )
            self.stdout.write(self.style.SUCCESS('Successfully seeded Admin user'))

        # Create Employee users
        if not Employee.objects.filter(email="employee1@example.com").exists():
            Employee.objects.create_user(
                email="employee1@example.com",
                password="Password123",
                first_name="John",
                last_name="Doe",
            )
            self.stdout.write(self.style.SUCCESS('Successfully seeded Employee user 1'))

        if not Employee.objects.filter(email="employee2@example.com").exists():
            Employee.objects.create_user(
                email="employee2@example.com",
                password="Password123",
                first_name="Jane",
                last_name="Smith",
            )
            self.stdout.write(self.style.SUCCESS('Successfully seeded Employee user 2'))

        # Create Employer users
        if not Employer.objects.filter(email="employer1@example.com").exists():
            Employer.objects.create_user(
                email="employer1@example.com",
                password="Password123",
                first_name="Alice",
                last_name="Johnson",
                company_name="Company1",
            )
            self.stdout.write(self.style.SUCCESS('Successfully seeded Employer user 1'))

        if not Employer.objects.filter(email="employer2@example.com").exists():
            Employer.objects.create_user(
                email="employer2@example.com",
                password="Password123",
                first_name="Bob",
                last_name="Brown",
                company_name="company1",
            )
            self.stdout.write(self.style.SUCCESS('Successfully seeded Employer user 2'))
