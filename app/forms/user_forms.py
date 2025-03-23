from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import password_validation
from app.models import User, Employer
from project.constants import COUNTRIES
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox

class EmployeeSignUpForm(UserCreationForm):
    country = forms.ChoiceField(choices=COUNTRIES)
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'captcha':
                field.widget.attrs.update({'class': 'form-control'})

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            existing_user = User.objects.filter(email=email).first()
            if existing_user:
                if not existing_user.is_active:
                    #delete the inactive user
                    existing_user.delete()
                else:
                    raise forms.ValidationError("A user with this email already exists.")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            existing_user = User.objects.filter(username=username).first()
            if existing_user:
                if not existing_user.is_active:
                    #delete the inactive user
                    existing_user.delete()
                else:
                    raise forms.ValidationError("A user with this username already exists.")
        return username
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

class EmployeeAccountUpdateForm(forms.ModelForm):
    password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="Leave blank to keep your current password"
    )
    password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="Enter the same password as above to confirm"
    )

    country = forms.ChoiceField(
        choices=COUNTRIES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    email = forms.EmailField(
        max_length=255,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields =['first_name', 'last_name', 'email']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 or password2:
            if not password1:
                self.add_error('password1', 'Please enter your new password')
            if not password2:
                self.add_error('password2', 'Please confirm your new password')
            elif password1 != password2:
                self.add_error('password2', 'Passwords do not match')
            else:
                try:
                    password_validation.validate_password(password1, self.instance)
                except forms.ValidationError as error:
                    self.add_error('password1', error)

        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)

        if self.cleaned_data.get('password1'):
            user.set_password(self.cleaned_data['password1'])
        
        if commit:
            user.save()
        return user

class EmployerSignUpForm(UserCreationForm):
    country = forms.ChoiceField(choices=COUNTRIES)
    company_name = forms.CharField(max_length=255)
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            existing_user = User.objects.filter(email=email).first()
            if existing_user:
                if not existing_user.is_active:
                    #delete the inactive user
                    existing_user.delete()
                else:
                    raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            existing_user = User.objects.filter(username=username).first()
            if existing_user:
                if not existing_user.is_active:
                    #delete the inactive user
                    existing_user.delete()
                else:
                    raise forms.ValidationError("A user with this username already exists.")
        return username
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
    