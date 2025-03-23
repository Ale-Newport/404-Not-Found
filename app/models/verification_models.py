from django.db import models
from datetime import timedelta
from django.utils import timezone
import random
from app.models import User

class VerificationCode(models.Model):
    CODE_TYPES = [
        ('password_reset', 'Password Reset'),
        ('email_verification', 'Email Verification'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    code_type = models.CharField(max_length=20, choices=CODE_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    @classmethod
    def generate_code(cls):
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])

    def is_valid(self):
        return not self.is_used and self.created_at >= timezone.now() - timedelta(minutes=15)

    class Meta:
        ordering = ['-created_at']
