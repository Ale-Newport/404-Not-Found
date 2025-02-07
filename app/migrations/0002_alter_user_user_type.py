# Generated by Django 5.1.2 on 2025-02-06 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('admin', 'Admin'), ('employee', 'Employee'), ('employer', 'Employer')], max_length=10),
        ),
    ]
