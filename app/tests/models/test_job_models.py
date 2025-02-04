from django.test import TestCase
from app.models import Job, Employer
from decimal import Decimal

class JobModelTest(TestCase):
    def setUp(self):
        self.employer = Employer.objects.create_user(
            username="employer",
            email="employer@test.com",
            password="testpass123",
            first_name="Test",
            last_name="Employer",
            company_name="Test Company"
        )
        
        self.job = Job.objects.create(
            name="Software Developer",
            department="Engineering",
            description="Test job description",
            salary=Decimal("75000.00"),
            job_type="FT",
            skills_needed="Python, Django",
            created_by=self.employer
        )

    def test_job_creation(self):
        self.assertEqual(self.job.name, "Software Developer")
        self.assertEqual(self.job.department, "Engineering")
        self.assertEqual(self.job.job_type, "FT")
        self.assertEqual(self.job.created_by, self.employer)

    def test_job_string_representation(self):
        expected_string = f"{self.job.name} - {self.job.department}"
        self.assertEqual(str(self.job), expected_string)

    def test_optional_fields(self):
        self.assertIsNone(self.job.bonus)
        self.assertIsNone(self.job.skills_wanted)

    def test_job_with_optional_fields(self):
        job_with_bonus = Job.objects.create(
            name="Senior Developer",
            department="Engineering",
            description="Senior role",
            salary=Decimal("100000.00"),
            job_type="FT",
            bonus=Decimal("10000.00"),
            skills_needed="Python, Django",
            skills_wanted="AWS, Docker",
            created_by=self.employer
        )
        self.assertEqual(job_with_bonus.bonus, Decimal("10000.00"))
        self.assertEqual(job_with_bonus.skills_wanted, "AWS, Docker")