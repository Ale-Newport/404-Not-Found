# Generated by Django 5.1.2 on 2025-02-05 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_alter_admin_username_alter_employee_username_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='cv_filename',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='employee',
            name='interests',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='preferred_contract',
            field=models.CharField(blank=True, choices=[('FT', 'Full Time'), ('PT', 'Part Time')], max_length=2),
        ),
        migrations.AddField(
            model_name='employee',
            name='skills',
            field=models.TextField(blank=True),
        ),
    ]
