from django.test import TestCase
from app.models import Job, Employer, Admin
from decimal import Decimal

class JobModelTest(TestCase):

    fixtures = ['app/tests/fixtures/users.json', 'app/tests/fixtures/employer_users.json', 'app/tests/fixtures/jobs.json']

    def setUp(self):
        super().setUp()
        self.job = Job.objects.get(pk=1)
        self.employer = Employer.objects.get(pk=1)

    def test_job_creation(self):
        self.assertEqual(self.job.name, "Software Developer")
        self.assertEqual(self.job.department, "Engineering")
        self.assertEqual(self.job.job_type, "FT")
        self.assertEqual(self.job.created_by, self.employer)

    def test_job_string_representation(self):
        expected_string = f"{self.job.name} - {self.job.department}"
        self.assertEqual(str(self.job), expected_string)

    def test_optional_fields(self):
        self.assertEqual(self.job.bonus, Decimal("0"))
        self.assertEqual(self.job.skills_wanted, "Machine Learning, Artificial Intelligence")

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