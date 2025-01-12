from rest_framework import serializers
from .models import User


class InitialSignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    agreed_to_terms = serializers.BooleanField()
    agreed_to_marketing = serializers.BooleanField()
    referral_code = serializers.CharField(required=False, allow_blank=True)


class CompleteProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'country']


