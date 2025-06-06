from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from project.constants import COUNTRIES

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

class UserProfileMixin:
    @classmethod
    def create_base_user(cls, username, email, password, first_name, last_name, user_type, **extra_fields):
        profile_fields = {}
        for field in cls._meta.fields:
            field_name = field.name
            if field_name != 'user' and field_name in extra_fields:
                profile_fields[field_name] = extra_fields.pop(field_name)
        
        user_fields = {
            'username': username, 
            'email': email, 
            'password': password,
            'first_name': first_name, 
            'last_name': last_name, 
            'user_type': user_type
        }
        
        for key, value in extra_fields.items():
            if hasattr(User, key):
                user_fields[key] = value
        
        user = User.objects.create_user(**user_fields)
        
        profile = cls.objects.create(user=user, **profile_fields)
        return profile


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
        User.validate_user_fields(user_fields.get('email'), user_fields.get('username'))
        user_fields['user_type'] = 'admin'
        user_fields.setdefault('is_staff', True)
        user_fields.setdefault('is_superuser', True)
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
        User.validate_user_fields(user_fields.get('email'), user_fields.get('username'))
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
        User.validate_user_fields(user_fields.get('email'), user_fields.get('username'))
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

    @staticmethod
    def validate_user_fields(email, username):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have a username")

class Admin(UserDelegationMixin, UserProfileMixin, models.Model):
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
        profile = cls.create_base_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        user_type='admin',
        **extra_fields
        )
    
        if hasattr(profile, 'clean'):
            profile.clean()
        
        return profile

class Employee(UserDelegationMixin, UserProfileMixin, models.Model):
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
    def __str__(self):
        return f"{self.user.username} (Employee)"
    
    @classmethod
    def create_user(cls, username, email, password, first_name, last_name, country="", **extra_fields):
        extra_fields['country'] = country

        return cls.create_base_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            user_type='employee',
            **extra_fields
        )


class Employer(UserDelegationMixin, UserProfileMixin, models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    objects = EmployerManager()

    country = models.CharField(max_length=100, choices=COUNTRIES, blank=True)
    company_name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user.username} (Employer) - {self.company_name}"
    
    @classmethod
    def create_user(cls, username, email, password, first_name, last_name, company_name="", country="", **extra_fields):
        extra_fields['company_name'] = company_name
        extra_fields['country'] = country

        return cls.create_base_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            user_type='employer',
            **extra_fields
        )
