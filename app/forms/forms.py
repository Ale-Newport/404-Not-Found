from django import forms
from django.contrib.auth.forms import UserCreationForm

from app.models import Employee, Employer

class EmployeeSignUpForm(UserCreationForm):
    class Meta:
        model = Employee
        fields = [
            'first_name',
            'last_name',
            'email',
            'country',
            'password1',
            'password2',
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class EmployerSignUpForm(UserCreationForm):
    class Meta:
        model = Employer
        fields = ['first_name', 'last_name', 'email', 'country', 'company_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': f'Enter {field.replace("_", " ").title()}'
            })
