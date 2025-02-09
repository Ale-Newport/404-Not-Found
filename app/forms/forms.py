from django import forms
from django.contrib.auth.forms import UserCreationForm
from app.models import User, Admin, Employee, Employer, Job
from django.contrib.auth import authenticate
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox

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
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'captcha':  # Don't add form-control to captcha
                field.widget.attrs.update({'class': 'form-control'})

class EmployerSignUpForm(UserCreationForm):
    country = forms.CharField(max_length=100)
    company_name = forms.CharField(max_length=255)
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields except captcha
        for field in self.fields:
            if field != 'captcha':
                self.fields[field].widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': f'Enter {field.replace("_", " ").title()}'
                })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'employer'
        if commit:
            user.save()
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