# Generated by Django 5.1.2 on 2025-02-11 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_alter_user_user_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('employer', 'Employer'), ('employee', 'Employee'), ('admin', 'Admin')], max_length=10),
        ),
    ]
