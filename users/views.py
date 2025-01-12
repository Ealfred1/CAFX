from rest_framework import generics, status
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
import uuid
from .models import User
from .serializers import InitialSignupSerializer, CompleteProfileSerializer

class EmailService:
    @staticmethod
    def send_verification_email(user):
        verification_link = f"{settings.FRONTEND_APP_URL}?token={user.verification_token}"
        
        html_message = render_to_string('verification_email.html', {
            'verification_link': verification_link,
            'user_email': user.email
        })
        
        send_mail(
            subject='Verify your email',
            message=f'Click this link to verify your email: {verification_link}',
            html_message=html_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )

@extend_schema(
    tags=['Authentication'],
    description='Initial signup endpoint for creating a new user account',
    responses={
        201: OpenApiResponse(
            description='User created successfully',
            examples=[
                OpenApiExample(
                    'Success',
                    value={'message': 'Please check your email to verify your account', 'email': 'user@example.com'}
                )
            ]
        ),
        400: OpenApiResponse(description='Invalid input')
    }
)
class InitialSignupView(generics.CreateAPIView):
    serializer_class = InitialSignupSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = User.objects.create_user(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            agreed_to_terms=serializer.validated_data['agreed_to_terms'],
            agreed_to_marketing=serializer.validated_data['agreed_to_marketing'],
            referral_code=serializer.validated_data.get('referral_code'),
            verification_token=uuid.uuid4()
        )

        EmailService.send_verification_email(user)
        
        return Response({
            'message': 'Please check your email to verify your account',
            'email': user.email
        }, status=status.HTTP_201_CREATED)

@extend_schema(
    tags=['Authentication'],
    description='Resend verification email to unverified users',
    request={'application/json': {'properties': {'email': {'type': 'string', 'format': 'email'}}}},
    responses={
        200: OpenApiResponse(
            description='Verification email resent successfully',
            examples=[
                OpenApiExample(
                    'Success',
                    value={'message': 'Verification email has been resent', 'email': 'user@example.com'}
                )
            ]
        ),
        404: OpenApiResponse(description='User not found'),
        400: OpenApiResponse(description='Invalid input')
    }
)
class ResendVerificationEmailView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        
        if not email:
            return Response(
                {'error': 'Email is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email, is_email_verified=False)
            user.verification_token = uuid.uuid4()
            user.save()
            
            EmailService.send_verification_email(user)
            
            return Response({
                'message': 'Verification email has been resent',
                'email': user.email
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'error': 'No unverified user found with this email'
            }, status=status.HTTP_404_NOT_FOUND)

@extend_schema(
    tags=['Authentication'],
    description='Verify email using the token from the verification email',
    parameters=[
        {
            'name': 'token',
            'in': 'query',
            'description': 'Verification token from email',
            'required': True,
            'type': 'string'
        }
    ],
    responses={
        200: OpenApiResponse(
            description='Email verified successfully',
            examples=[
                OpenApiExample(
                    'Success',
                    value={
                        'message': 'Email verified successfully',
                        'tokens': {
                            'access': 'access_token_here',
                            'refresh': 'refresh_token_here'
                        }
                    }
                )
            ]
        ),
        400: OpenApiResponse(description='Invalid token')
    }
)
class VerifyEmailView(generics.GenericAPIView):
    def get(self, request):
        token = request.query_params.get('token')
        
        if not token:
            return Response(
                {'error': 'Verification token is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(verification_token=token, is_email_verified=False)
            user.is_email_verified = True
            user.save()
            
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Email verified successfully',
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'error': 'Invalid or expired verification token'
            }, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=['Profile'],
    description='Complete user profile with additional information',
    responses={
        200: OpenApiResponse(description='Profile updated successfully'),
        400: OpenApiResponse(description='Invalid input')
    }
)
class CompleteProfileView(generics.UpdateAPIView):
    serializer_class = CompleteProfileSerializer
    permission_classes = []  # Add your permission classes here
    
    def get_object(self):
        return self.request.user