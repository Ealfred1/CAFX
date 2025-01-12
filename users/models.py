from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    agreed_to_terms = models.BooleanField(default=False)
    agreed_to_marketing = models.BooleanField(default=False)
    referral_code = models.CharField(max_length=20, blank=True, null=True)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    country = models.CharField(max_length=100, blank=True, null=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['']