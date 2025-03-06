# Generated by Django 5.1.2 on 2025-03-06 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_alter_user_user_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobapplication',
            name='cover_letter',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='jobapplication',
            name='current_position',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('employee', 'Employee'), ('admin', 'Admin'), ('employer', 'Employer')], max_length=10),
        ),
    ]
