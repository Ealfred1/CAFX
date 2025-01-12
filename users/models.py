# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    agreed_to_terms = models.BooleanField(default=False)
    agreed_to_marketing = models.BooleanField(default=False)
    referral_code = models.CharField(max_length=20, blank=True, null=True)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    country = models.CharField(max_length=100, blank=True)
    full_name = models.CharField(max_length=255, blank=True)

    # Add related_name to resolve conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',  # Changed from user_set
        related_query_name='custom_user'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',  # Changed from user_set
        related_query_name='custom_user'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []