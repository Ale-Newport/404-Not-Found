from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import RegexValidator
from project.constants import COUNTRIES
import random
from datetime import timedelta
from django.utils import timezone

# ------------------------------------------------------------------------------
# USER DELEGATION MIXIN
# ------------------------------------------------------------------------------
class UserDelegationMixin:
    @property
    def email(self):
        return self.user.email

    @email.setter
    def email(self, value):
        self.user.email = value
        self.user.save()

    @property
    def first_name(self):
        return self.user.first_name

    @first_name.setter
    def first_name(self, value):
        self.user.first_name = value
        self.user.save()

    @property
    def last_name(self):
        return self.user.last_name

    @last_name.setter
    def last_name(self, value):
        self.user.last_name = value
        self.user.save()

    @property
    def is_staff(self):
        return self.user.is_staff

    @is_staff.setter
    def is_staff(self, value):
        self.user.is_staff = value
        self.user.save()

    @property
    def is_superuser(self):
        return self.user.is_superuser

    @is_superuser.setter
    def is_superuser(self, value):
        self.user.is_superuser = value
        self.user.save()

    @property
    def is_active(self):
        return self.user.is_active

    @is_active.setter
    def is_active(self, value):
        self.user.is_active = value
        self.user.save()

# ------------------------------------------------------------------------------
# CUSTOM MANAGERS
# ------------------------------------------------------------------------------
from django.db.models import Manager, F

class AdminManager(Manager):
    def create(self, **kwargs):
        user_keys = {'username', 'email', 'first_name', 'last_name', 'password', 'is_staff', 'is_superuser'}
        if user_keys.intersection(kwargs.keys()):
            return self.create_user(**kwargs)
        return super().create(**kwargs)
        
    def create_user(self, **kwargs):
        user_fields = {}
        for field in ['username', 'email', 'first_name', 'last_name', 'password', 'is_staff', 'is_superuser']:
            if field in kwargs:
                user_fields[field] = kwargs.pop(field)
        if not user_fields.get('email'):
            raise ValueError("Users must have an email address")
        if not user_fields.get('username'):
            raise ValueError("Users must have a username")
        user_fields['user_type'] = 'admin'
        user_fields.setdefault('is_staff', True)
        user_fields.setdefault('is_superuser', True)
        # Use Django's built-in create_user for proper password handling.
        user = User.objects.create_user(**user_fields)
        return super().create(user=user, **kwargs)
    
    def create_superuser(self, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        return self.create_user(**kwargs)

class EmployeeManager(Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('user').annotate(email=F('user__email'))
    
    def create(self, **kwargs):
        user_keys = {'username', 'email', 'first_name', 'last_name', 'password'}
        if user_keys.intersection(kwargs.keys()):
            return self.create_user(**kwargs)
        return super().create(**kwargs)
        
    def create_user(self, **kwargs):
        user_fields = {}
        for field in ['username', 'email', 'first_name', 'last_name', 'password']:
            if field in kwargs:
                user_fields[field] = kwargs.pop(field)
        if not user_fields.get('email'):
            raise ValueError("Users must have an email address")
        if not user_fields.get('username'):
            raise ValueError("Users must have a username")
        user_fields['user_type'] = 'employee'
        user = User.objects.create_user(**user_fields)
        return super().create(user=user, **kwargs)

class EmployerManager(Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('user').annotate(email=F('user__email'))
    
    def create(self, **kwargs):
        user_keys = {'username', 'email', 'first_name', 'last_name', 'password'}
        if user_keys.intersection(kwargs.keys()):
            return self.create_user(**kwargs)
        return super().create(**kwargs)
        
    def create_user(self, **kwargs):
        user_fields = {}
        for field in ['username', 'email', 'first_name', 'last_name', 'password']:
            if field in kwargs:
                user_fields[field] = kwargs.pop(field)
        if not user_fields.get('email'):
            raise ValueError("Users must have an email address")
        if not user_fields.get('username'):
            raise ValueError("Users must have a username")
        user_fields['user_type'] = 'employer'
        user = User.objects.create_user(**user_fields)
        return super().create(user=user, **kwargs)

# ------------------------------------------------------------------------------
# MODELS
# ------------------------------------------------------------------------------
class User(AbstractUser):
    USER_TYPES = [
        ('admin', 'Admin'),
        ('employee', 'Employee'),
        ('employer', 'Employer')
    ]
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

class Admin(UserDelegationMixin, models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    
    objects = AdminManager()
    
    def clean(self):
        super().clean()
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

    def __str__(self):
        return f"{self.user.username} (Admin)"
    
    @classmethod
    def create_user(cls, username, email, password, first_name, last_name, **extra_fields):
        extra_fields.setdefault('user_type', 'admin')
        
        user = User.objects.create_user(
            username=username, 
            email=email, 
            password=password,
            first_name=first_name, 
            last_name=last_name, 
            **extra_fields
        )
        
        admin = cls.objects.create(user=user)
        admin.clean()
        return admin

class Employee(UserDelegationMixin, models.Model):
    """Job seeker user type."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    objects = EmployeeManager()

    country = models.CharField(max_length=100, choices=COUNTRIES, blank=True)
    skills = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    education = models.TextField(blank=True)
    languages = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    interests = models.TextField(blank=True)
    preferred_contract = models.CharField(
        max_length=2,
        choices=[('FT', 'Full Time'), ('PT', 'Part Time')],
        blank=True
    )
    cv_filename = models.CharField(max_length=255, blank=True)
    experience = models.TextField(default="")

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

class Employer(UserDelegationMixin, models.Model):
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
    country = models.CharField(max_length=100, choices=COUNTRIES, blank=True)

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
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])

    def is_valid(self):
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
    
    cover_letter = models.TextField(blank=True, default='')
    full_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, default='')
    country = models.CharField(max_length=100, choices=COUNTRIES, blank=True, null=True)
    current_position = models.CharField(max_length=100, blank=True, default='')
    skills = models.TextField(blank=True, default='')
    experience = models.TextField(blank=True, default='')
    education = models.TextField(blank=True, default='')
    portfolio_url = models.URLField(blank=True, default='')
    linkedin_url = models.URLField(blank=True, default='')
    custom_cv = models.FileField(upload_to='applications/cvs/', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('job', 'applicant')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name or self.applicant.user.get_full_name()} - {self.job.name}"
