from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from project.constants import COUNTRIES
import random
from datetime import timedelta
from django.utils import timezone

class User(AbstractUser):
    USER_TYPES = {
        ('admin', 'Admin'),
        ('employee', 'Employee'),
        ('employer', 'Employer')
    }
    user_type = models.CharField(max_length=10, choices=USER_TYPES)

    username = models.CharField(max_length=50, unique=True,
            validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name="%(class)s_groups",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name="%(class)s_permissions",
        blank=True
    )

    USERNAME_FIELD = 'username'

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def clean(self):
        """Ensure admin users have staff/superuser status"""
        super().clean()
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

    def __str__(self):
        return f"{self.user.username} (Admin)"

class Employee(models.Model):
    """Job seeker user type."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    country = models.CharField(max_length=100, choices=COUNTRIES, blank=True)
    skills = models.TextField(blank=True)
    interests = models.TextField(blank=True)
    preferred_contract = models.CharField(
        max_length=2,
        choices=[('FT', 'Full Time'), ('PT', 'Part Time')],
        blank=True
    )
    cv_filename = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user.username} (Employee)"


class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    country = models.CharField(max_length=100, choices=COUNTRIES, blank=True)
    company_name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user.username} (Employer) - {self.company_name}"


class Job(models.Model):
    def __str__(self):
        return f"{self.name} - {self.department}"

    JOB_TYPE_CHOICES = [
        ('FT', 'Full Time'),
        ('PT', 'Part Time'),
    ]
    
    name = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    description = models.TextField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    job_type = models.CharField(max_length=2, choices=JOB_TYPE_CHOICES, default='FT')
    bonus = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    skills_needed = models.TextField(help_text='Comma separated skills required.')
    skills_wanted = models.TextField(help_text='Comma separated preferred skills.', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs')

class VerificationCode(models.Model):
    CODE_TYPES = [
        ('password_reset', 'Password Reset'),
        ('email_verification', 'Email Verification'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    code_type = models.CharField(max_length=20, choices=CODE_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    @classmethod
    def generate_code(cls):
        """Generate a random 6-digit code"""
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])

    def is_valid(self):
        """Check if code is valid (not expired and not used)"""
        return not self.is_used and self.created_at >= timezone.now() - timedelta(minutes=15)

    class Meta:
        ordering = ['-created_at']