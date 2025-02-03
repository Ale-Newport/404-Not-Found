from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, AbstractUser

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class AbstractUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='%(class)s_groups',
        blank=True,
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='%(class)s_permissions',
        blank=True,
        help_text='Specific permissions for this user.'
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        abstract = True

    def __str__(self):
        return self.email

class Admin(AbstractUser):
    # add custom fields here

    def save(self, *args, **kwargs):
        """Ensure admin users have staff/superuser status"""
        self.is_staff = True
        self.is_superuser = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'

class Employee(AbstractUser):
    """Job seeker user type."""
    country = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.email} (Employee)"


class Employer(AbstractUser):
    country = models.CharField(max_length=100, blank=True)
    company_name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.email} (Employer) - {self.company_name}"

    class Meta:
        verbose_name = 'Employer'
        verbose_name_plural = 'Employers'

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
    created_by = models.ForeignKey('Employer', on_delete=models.CASCADE, related_name='jobs')