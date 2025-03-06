# Generated by Django 5.1.2 on 2025-02-25 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_user_user_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('admin', 'Admin'), ('employee', 'Employee'), ('employer', 'Employer')], max_length=10),
        ),
    ]
