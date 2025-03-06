from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import RegexValidator
from project.constants import COUNTRIES
import random
from datetime import timedelta
from django.utils import timezone

# First define all manager classes
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('user_type', 'employee')  # Default to employee
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(username, email, password, **extra_fields)

class AdminManager(models.Manager):
    def create_user(self, username, email, password=None, **extra_fields):
        from django.apps import apps
        User = apps.get_model('app', 'User')
        
        user_type = extra_fields.pop('user_type', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        user = User.objects.create_user(
            username=username,
            email=email, 
            password=password,
            user_type=user_type,
            **extra_fields
        )
        admin = self.model(user=user)
        admin.save()
        return admin

class EmployeeManager(models.Manager):
    def create_user(self, username, email, password=None, **extra_fields):
        from django.apps import apps
        User = apps.get_model('app', 'User')
        
        country = extra_fields.pop('country', '')
        skills = extra_fields.pop('skills', '')
        interests = extra_fields.pop('interests', '')
        preferred_contract = extra_fields.pop('preferred_contract', '')
        cv_filename = extra_fields.pop('cv_filename', '')
        
        user_type = extra_fields.pop('user_type', 'employee')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            user_type=user_type,
            **extra_fields
        )
        
        employee = self.model(
            user=user,
            country=country,
            skills=skills,
            interests=interests,
            preferred_contract=preferred_contract,
            cv_filename=cv_filename
        )
        employee.save()
        return employee

class EmployerManager(models.Manager):
    def create_user(self, username, email, password=None, **extra_fields):
        from django.apps import apps
        User = apps.get_model('app', 'User')
        
        country = extra_fields.pop('country', '')
        company_name = extra_fields.pop('company_name', '')
        
        user_type = extra_fields.pop('user_type', 'employer')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            user_type=user_type,
            **extra_fields
        )
        
        employer = self.model(
            user=user,
            country=country,
            company_name=company_name
        )
        employer.save()
        return employer

# Now define the models
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
    
    # Connect the custom manager
    objects = CustomUserManager()

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    objects = AdminManager()

    def clean(self):
        """Ensure admin users have staff/superuser status"""
        super().clean()
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

    def __str__(self):
        return f"{self.user.username} (Admin)"
    
    @classmethod
    def create_user(cls, username, email, password, first_name, last_name, **extra_fields):
        extra_fields.setdefault('user_type', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        user = User.objects.create_user(
            username=username, 
            email=email, 
            password=password,
            first_name=first_name, 
            last_name=last_name, 
            **extra_fields
        )
        
        admin = cls.objects.create(user=user)
        return admin

class Employee(models.Model):
    """Job seeker user type."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    objects = EmployeeManager()

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
    
    @classmethod
    def create_user(cls, username, email, password, first_name, last_name, country="", **extra_fields):
        extra_fields.setdefault('user_type', 'employee')
        
        user = User.objects.create_user(
            username=username, 
            email=email, 
            password=password,
            first_name=first_name, 
            last_name=last_name, 
            **extra_fields
        )
        
        employee = cls.objects.create(user=user, country=country)
        return employee


class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    objects = EmployerManager()

    country = models.CharField(max_length=100, choices=COUNTRIES, blank=True)
    company_name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user.username} (Employer) - {self.company_name}"
    
    @classmethod
    def create_user(cls, username, email, password, first_name, last_name, company_name="", country="", **extra_fields):
        extra_fields.setdefault('user_type', 'employer')
        
        user = User.objects.create_user(
            username=username, 
            email=email, 
            password=password,
            first_name=first_name, 
            last_name=last_name, 
            **extra_fields
        )
        
        employer = cls.objects.create(user=user, company_name=company_name, country=country)
        return employer


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
    created_by = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name='jobs')

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

class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewing', 'Reviewing'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Application Details
    cover_letter = models.TextField()
    full_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True) 
    country = models.CharField(max_length=100, choices=COUNTRIES, blank=True, null=True)
    current_position = models.CharField(max_length=100, blank=True, null=True)
    skills = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    education = models.TextField(blank=True)
    portfolio_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    custom_cv = models.FileField(upload_to='applications/cvs/', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('job', 'applicant')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name or self.applicant.user.get_full_name()} - {self.job.name}"