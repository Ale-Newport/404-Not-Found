from django import forms
from django.contrib.auth.forms import UserCreationForm
from app.models import JobApplication, User, Admin, Employee, Employer, Job
from project.constants import COUNTRIES
from django.contrib.auth import authenticate, password_validation
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator

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



class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        max_length=255,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

class SetNewPasswordForm(forms.Form):
    password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Password must be at least 8 characters long."
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("The two passwords must match.")
        return cleaned_data
    

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = [
            'cover_letter', 'full_name', 'email', 'phone', 'country',
            'current_position', 'skills', 'experience', 'education',
            'portfolio_url', 'linkedin_url', 'custom_cv'
        ]
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 6}),
            'skills': forms.Textarea(attrs={'rows': 4}),
            'experience': forms.Textarea(attrs={'rows': 4}),
            'education': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, employee=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if employee:
            self.fields['full_name'].initial = f"{employee.user.first_name} {employee.user.last_name}"
            self.fields['email'].initial = employee.user.email
            self.fields['country'].initial = employee.country
            self.fields['skills'].initial = employee.skills


class UserForm(UserCreationForm):
    user_type = forms.ChoiceField(
        choices=[('admin', 'Admin'), ('employee', 'Employee'), ('employer', 'Employer')],
        initial='employee'
    )
    
    # Common fields for all user types
    username = forms.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                regex=r'^@\w{3,}$',
                message='Username must consist of @ followed by at least three alphanumericals'
            )
        ],
        help_text='Required. Format: @username'
    )
    email = forms.EmailField(max_length=255)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    
    # Fields specific to Employee
    country = forms.ChoiceField(choices=COUNTRIES, required=False)
    skills = forms.CharField(widget=forms.Textarea, required=False)
    experience = forms.CharField(widget=forms.Textarea, required=False)
    education = forms.CharField(widget=forms.Textarea, required=False)
    languages = forms.CharField(widget=forms.Textarea, required=False)
    phone = forms.CharField(max_length=20, required=False)
    interests = forms.CharField(widget=forms.Textarea, required=False)
    preferred_contract = forms.ChoiceField(
        choices=[('FT', 'Full Time'), ('PT', 'Part Time')],
        required=False
    )
    
    # Fields specific to Employer
    company_name = forms.CharField(max_length=255, required=False)
    
    # Fields specific to Admin
    is_staff = forms.ChoiceField(
        choices=[(True, 'True'), (False, 'False')],
        initial=False
    )
    is_superuser = forms.ChoiceField(
        choices=[(True, 'True'), (False, 'False')],
        initial=False
    )

    class Meta:
        model = User
        fields = [
            'user_type', 'username', 'email', 'first_name', 'last_name', 
            'password1', 'password2', 'is_staff', 'is_superuser', 'country',
            'skills', 'experience', 'education', 'languages', 'phone',
            'interests', 'preferred_contract', 'company_name'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = 'Your password must contain at least 8 characters.'
        self.fields['password2'].help_text = 'Enter the same password as before, for verification.'
    
    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        
        # Handle required fields based on user_type
        if user_type == 'employer' and not cleaned_data.get('company_name'):
            self.add_error('company_name', 'Company name is required for Employer accounts')
        
        if user_type == 'admin':
            cleaned_data['is_staff'] = True
            cleaned_data['is_superuser'] = True
        
        return cleaned_data
    
    def save(self, commit=True):
        # Don't save the user yet
        user = super().save(commit=False)
        user_type = self.cleaned_data.get('user_type')
        user.user_type = user_type
        
        if user_type == 'admin':
            user.is_staff = True
            user.is_superuser = True
        
        if commit:
            user.save()
            
            # Create the appropriate profile based on user_type
            if user_type == 'admin':
                Admin.objects.create(user=user)
            elif user_type == 'employee':
                Employee.objects.create(
                    user=user,
                    country=self.cleaned_data.get('country', ''),
                    skills=self.cleaned_data.get('skills', ''),
                    experience=self.cleaned_data.get('experience', ''),
                    education=self.cleaned_data.get('education', ''),
                    languages=self.cleaned_data.get('languages', ''),
                    phone=self.cleaned_data.get('phone', ''),
                    interests=self.cleaned_data.get('interests', ''),
                    preferred_contract=self.cleaned_data.get('preferred_contract', '')
                )
            elif user_type == 'employer':
                Employer.objects.create(
                    user=user,
                    company_name=self.cleaned_data.get('company_name', ''),
                    country=self.cleaned_data.get('country', '')
                )
        
        return user

class JobForm(forms.ModelForm):
    """Form for administrators to create a new job listing."""
    
    skills_needed = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        help_text='Enter required skills, separated by commas.'
    )
    
    skills_wanted = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        help_text='Enter preferred skills, separated by commas.'
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6}),
        help_text='Enter a detailed job description.'
    )
    
    # Add field to select the employer who posted the job
    created_by = forms.ModelChoiceField(
        queryset=Employer.objects.all(),
        label="Employer",
        help_text="Select the employer who is posting this job."
    )
    
    class Meta:
        model = Job
        fields = [
            'name', 'department', 'description', 'salary', 
            'job_type', 'bonus', 'skills_needed', 'skills_wanted', 'created_by'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Job title'}),
            'department': forms.TextInput(attrs={'placeholder': 'Department name'}),
            'salary': forms.NumberInput(attrs={'min': 0, 'step': '0.01'}),
            'bonus': forms.NumberInput(attrs={'min': 0, 'step': '0.01', 'placeholder': 'Optional'}),
        }
        help_texts = {
            'job_type': 'Select the type of employment.',
            'salary': 'Annual salary in $',
            'bonus': 'Annual bonus in $ (if applicable)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Format employer choices to show more information
        self.fields['created_by'].label_from_instance = lambda obj: f"{obj.company_name} ({obj.user.get_full_name()} - {obj.user.email})"
    
    def clean_salary(self):
        """Validate salary is a positive number."""
        salary = self.cleaned_data.get('salary')
        if salary <= 0:
            raise forms.ValidationError("Salary must be a positive number.")
        return salary
    
    def clean_bonus(self):
        """Validate bonus is a positive number if provided."""
        bonus = self.cleaned_data.get('bonus')
        if bonus is not None and bonus < 0:
            raise forms.ValidationError("Bonus cannot be negative.")
        return bonus