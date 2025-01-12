# serializers.py
from rest_framework import serializers
from .models import User

class InitialSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    agreed_to_terms = serializers.BooleanField()
    agreed_to_marketing = serializers.BooleanField()
    referral_code = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'agreed_to_terms', 'agreed_to_marketing', 'referral_code']
        extra_kwargs = {
            'email': {'required': True},
            'password': {'write_only': True}
        }

    def validate_agreed_to_terms(self, value):
        if not value:
            raise serializers.ValidationError("You must agree to the terms and conditions.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ['email']

class CompleteProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'country']
        extra_kwargs = {
            'full_name': {'required': True},
            'country': {'required': True}
        }

class TokenVerificationSerializer(serializers.Serializer):
    token = serializers.UUIDField()

    class Meta:
        fields = ['token']