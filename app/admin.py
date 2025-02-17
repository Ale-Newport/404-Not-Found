from django.contrib import admin
from app.models import User, Job

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type')
    list_filter = ('user_type',)
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

@admin.register(Job)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'salary', 'job_type', 'bonus', 'skills_needed', 'skills_wanted', 'created_at', 'created_by')
    list_filter = ('job_type',)
    search_fields = ('name', 'department', 'salary', 'skills_needed', 'skills_wanted', 'created_by')
    ordering = ('name',)
