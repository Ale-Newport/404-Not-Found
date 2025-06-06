# Generated by Django 5.1.2 on 2025-03-11 13:02

import app.models
import django.contrib.auth.models
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('user_type', models.CharField(choices=[('employer', 'Employer'), ('admin', 'Admin'), ('employee', 'Employee')], max_length=10)),
                ('username', models.CharField(max_length=50, unique=True, validators=[django.core.validators.RegexValidator(message='Username must consist of @ followed by at least three alphanumericals', regex='^@\\w{3,}$')])),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('groups', models.ManyToManyField(blank=True, related_name='%(class)s_groups', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='%(class)s_permissions', to='auth.permission')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            bases=(app.models.UserDelegationMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('country', models.CharField(blank=True, choices=[('', 'Select a country'), ('US', 'United States'), ('UK', 'United Kingdom'), ('CA', 'Canada'), ('AU', 'Australia'), ('FR', 'France'), ('DE', 'Germany'), ('IT', 'Italy'), ('ES', 'Spain'), ('PT', 'Portugal'), ('BR', 'Brazil'), ('JP', 'Japan'), ('CN', 'China'), ('IN', 'India')], max_length=100)),
                ('skills', models.TextField(blank=True)),
                ('education', models.TextField(blank=True)),
                ('languages', models.TextField(blank=True)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('interests', models.TextField(blank=True)),
                ('preferred_contract', models.CharField(blank=True, choices=[('FT', 'Full Time'), ('PT', 'Part Time')], max_length=2)),
                ('cv_filename', models.CharField(blank=True, max_length=255)),
                ('experience', models.TextField(blank=True, null=True)),
            ],
            bases=(app.models.UserDelegationMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Employer',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('country', models.CharField(blank=True, choices=[('', 'Select a country'), ('US', 'United States'), ('UK', 'United Kingdom'), ('CA', 'Canada'), ('AU', 'Australia'), ('FR', 'France'), ('DE', 'Germany'), ('IT', 'Italy'), ('ES', 'Spain'), ('PT', 'Portugal'), ('BR', 'Brazil'), ('JP', 'Japan'), ('CN', 'China'), ('IN', 'India')], max_length=100)),
                ('company_name', models.CharField(blank=True, max_length=255)),
            ],
            bases=(app.models.UserDelegationMixin, models.Model),
        ),
        migrations.CreateModel(
            name='VerificationCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=6)),
                ('code_type', models.CharField(choices=[('password_reset', 'Password Reset'), ('email_verification', 'Email Verification')], max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_used', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('department', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('salary', models.DecimalField(decimal_places=2, max_digits=10)),
                ('job_type', models.CharField(choices=[('FT', 'Full Time'), ('PT', 'Part Time')], default='FT', max_length=2)),
                ('bonus', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('skills_needed', models.TextField(help_text='Comma separated skills required.')),
                ('skills_wanted', models.TextField(blank=True, help_text='Comma separated preferred skills.', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to='app.employer')),
            ],
        ),
        migrations.CreateModel(
            name='JobApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('reviewing', 'Reviewing'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('cover_letter', models.TextField(blank=True, default='')),
                ('full_name', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone', models.CharField(blank=True, default='', max_length=20)),
                ('country', models.CharField(blank=True, choices=[('', 'Select a country'), ('US', 'United States'), ('UK', 'United Kingdom'), ('CA', 'Canada'), ('AU', 'Australia'), ('FR', 'France'), ('DE', 'Germany'), ('IT', 'Italy'), ('ES', 'Spain'), ('PT', 'Portugal'), ('BR', 'Brazil'), ('JP', 'Japan'), ('CN', 'China'), ('IN', 'India')], max_length=100, null=True)),
                ('current_position', models.CharField(blank=True, default='', max_length=100)),
                ('skills', models.TextField(blank=True, default='')),
                ('experience', models.TextField(blank=True, default='')),
                ('education', models.TextField(blank=True, default='')),
                ('portfolio_url', models.URLField(blank=True, default='')),
                ('linkedin_url', models.URLField(blank=True, default='')),
                ('custom_cv', models.FileField(blank=True, upload_to='applications/cvs/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='app.job')),
                ('applicant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='app.employee')),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('job', 'applicant')},
            },
        ),
    ]
