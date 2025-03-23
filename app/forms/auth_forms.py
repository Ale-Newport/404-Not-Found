from django import forms
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
