from django import forms
from django.contrib.auth.forms import UserCreationForm
from app.models import User, Admin, Employee, Employer, Job
from django.contrib.auth import authenticate


class LogInForm(forms.Form):
    """Form enabling registered users to log in."""
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticated user if possible."""
        user = None
        if self.is_valid():
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
        return user


class EmployeeSignUpForm(UserCreationForm):
    COUNTRIES = [
        ('', 'Select a country'),
        ('US', 'United States'),
        ('UK', 'United Kingdom'),
        ('CA', 'Canada'),
        ('AU', 'Australia'),
        ('FR', 'France'),
        ('DE', 'Germany'),
        ('IT', 'Italy'),
        ('ES', 'Spain'),
        ('PT', 'Portugal'),
        ('BR', 'Brazil'),
        ('JP', 'Japan'),
        ('CN', 'China'),
        ('IN', 'India'),
    ]
    
    country = forms.ChoiceField(choices=COUNTRIES)
    
    class Meta:
        model = User  # Changed from Employee to User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'employee'
        if commit:
            user.save()
        return user


class EmployerSignUpForm(UserCreationForm):
    country = forms.CharField(max_length=100)
    company_name = forms.CharField(max_length=255)

    class Meta:
        model = User  # Changed from Employer to User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': f'Enter {field.replace("_", " ").title()}'
            })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'employer'
        if commit:
            user.save()
            # Create the employer profile
            Employer.objects.create(
                user=user,
                country=self.cleaned_data['country'],
                company_name=self.cleaned_data['company_name']
            )
        return user

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['name', 'department', 'description', 'salary', 'job_type', 'bonus', 'skills_needed', 'skills_wanted']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'skills_needed': forms.Textarea(attrs={'rows': 3}),
            'skills_wanted': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': f'Enter {field.replace("_", " ").title()}'
            })
