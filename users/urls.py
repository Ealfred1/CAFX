from django.urls import path
from .views import (
    InitialSignupView,
    ResendVerificationView,
    VerifyEmailView,
    CompleteProfileView,
)

urlpatterns = [
    path('signup/', InitialSignupView.as_view(), name='signup'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend-verification'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('complete-profile/', CompleteProfileView.as_view(), name='complete-profile'),
]
