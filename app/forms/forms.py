from django import forms
from django.contrib.auth.forms import UserCreationForm
from app.models import User, Admin, Employee, Employer, Job
from project.constants import COUNTRIES
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

class EmployeeAccountUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # make password fields optional
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        
        # update help texts for password fields
        self.fields['password1'].help_text = 'Leave blank to keep your current password'
        self.fields['password2'].help_text = 'Leave blank to keep your current password'

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and not password2:
            self.add_error('password2', 'Please confirm your new password')
        elif password2 and not password1:
            self.add_error('password1', 'Please enter your new password')
        
        return cleaned_data

class EmployerSignUpForm(UserCreationForm):
    country = forms.ChoiceField(choices=COUNTRIES)
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
