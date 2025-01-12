from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import InitialSignupSerializer, CompleteProfileSerializer
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
import uuid


class initialSignupView(generics.CreateAPIView):
    serializer_class = InitialSignupSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = User.objects.create_user(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            agreed_to_terms=serializer.validated_data['agreed_to_terms'],
            agreed_to_marketing=serializer.validated_data['agreed_to_marketing'],
            referral_code=serializer.validated_data.get('referral_code', None)
            verification_token=uuid.uuid4()
        )
        
        # Send verification email
        self.send_verification_email(user)
        
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)

    def send_verification_email(self, user):
        verification_link = f"{settings.FRONTEND_URL}?token={user.verification_token}"
        
        html_message = render_to_string('verification_email.html', {'verification_link': verification_link})
        
        send_mail(
            subject='Verify Your Email',
            message=f'Click ths link to verify your email: {verification_link}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message
        )


class VerifyEmailView(generics.GenericAPIView):
    def get(self, request):
        token = request.query_params.get('token')
        
        try:
            user = User.objects.get(verification_token=token, is_email_verified=False)
            user.is_email_verified = True
            user.save()
            
            refresh = RefreshToken.for_user(user)
            return Response({'refresh': str(refresh), 'access': str(refresh.access_token)}, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({'error': 'Invalid or expired verification token'}, status=status.HTTP_400_BAD_REQUEST)


class CompleteProfileView(generics.UpdateAPIView):
    serializer_class = CompleteProfileSerializer
    
    def get_objecct(self):
        return self.request.user
    
