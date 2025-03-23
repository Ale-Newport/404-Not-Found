from django import forms
from app.models import Job, JobApplication, Employer

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

class JobForm(forms.ModelForm):
    """Form for administrators to create a new job listing."""
    
    skills_needed = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        help_text='Enter required skills, separated by commas.'
    )
    
    skills_wanted = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        required=False,
        help_text='Enter preferred skills, separated by commas.'
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}),
        help_text='Enter a detailed job description.'
    )
    
    # Add field to select the employer who posted the job
    created_by = forms.ModelChoiceField(
        queryset=Employer.objects.all(),
        label="Employer",
        help_text="Select the employer who is posting this job.",
        required=False
    )
    
    class Meta:
        model = Job
        fields = [
            'name', 'department', 'description', 'salary', 
            'job_type', 'bonus', 'skills_needed', 'skills_wanted', 'created_by'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Job title', 'class': 'form-control'}),
            'department': forms.TextInput(attrs={'placeholder': 'Department name', 'class': 'form-control'}),
            'salary': forms.NumberInput(attrs={'min': 0, 'step': '0.01', 'class': 'form-control'}),
            'job_type': forms.Select(attrs={'class': 'form-control'}),
            'bonus': forms.NumberInput(attrs={'min': 0, 'step': '0.01', 'placeholder': 'Optional', 'class': 'form-control'}),
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
