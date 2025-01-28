from django.core.management.base import BaseCommand
from app.models import Admin, Employee, Employer

class Command(BaseCommand):
    """Build automation command to unseed the database."""
    
    help = 'Seeds the database with sample data'

    def handle(self, *args, **options):
        """Unseed the database."""

        Admin.objects.all().delete()
        Employee.objects.all().delete()
        Employer.objects.all().delete()