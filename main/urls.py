from django.urls import path
from .views import ResetPasswordView, ResetPasswordVerifyView, RegistrationAPIView, UserLoginView, LogoutView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegistrationAPIView.as_view(), name='reg'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('token/', TokenObtainPairView.as_view(), name='token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('reset-password/verify/<str:uid>/<str:token>/', ResetPasswordVerifyView.as_view(), name='reset_password_verify'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
