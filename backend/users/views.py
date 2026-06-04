from rest_framework.generics import CreateAPIView,RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser,FormParser
from users.serializers import RegisterSerializer,ProfileSerializer,MyTokenObtainPairSerializer
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
import pyotp
from users.tasks import send_otp_email_task

User = get_user_model()
# Create your views here.

class MyTokenObtainPairView(TokenObtainPairView) :
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(CreateAPIView) :
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    parser_classes = [MultiPartParser,FormParser]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data,context={'request' : request})
        
        serializer.is_valid(raise_exception = True)
        user = serializer.save()

        totp = pyotp.TOTP(user.otp_secret,interval=300)
        otp_code = totp.now()

        send_otp_email_task.delay(user.email,otp_code)

        profile = None
        if user.profile_picture :
            profile = user.profile_picture.url
        return Response({
            "message" : "Registration successful. Please check your email for the verification code.",
            "id" : user.id,
            "email" : user.email,
            "full_name" : user.full_name,
            "role" : user.role,
            "profile_picture" : profile
        },status = status.HTTP_201_CREATED)


class ProfileView(RetrieveUpdateAPIView) :
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user

class LogoutView(APIView) :
    permission_classes = [AllowAny]

    def post(self,request) :
        try :
            refresh_token = request.data.get('refresh')
            if not refresh_token :
                return Response({"detail" : "Refresh token is required"},status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"detail": "Successfully logged out."}, status=status.HTTP_204_NO_CONTENT)
        
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        
class GoogleLogin(SocialLoginView) :
    permission_classes = [AllowAny]
    authentication_classes = []
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:3000"
    client_class = OAuth2Client

class GitHubLogin(SocialLoginView):
    permission_classes = [AllowAny]
    authentication_classes = []
    adapter_class = GitHubOAuth2Adapter
    callback_url = "http://localhost:3000"
    client_class = OAuth2Client

class VerifyOTPView(APIView) :
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self,request) :
        email = request.data.get('email')
        otp_code = request.data.get('otp')

        if not email or not otp_code :
            return Response({'error' : 'Email and OTP code are required.'},status=status.HTTP_400_BAD_REQUEST)
        
        try :
            user = User.objects.get(email=email)
        except User.DoesNotExist :
            return Response({'error' : 'User not found'},status=status.HTTP_404_NOT_FOUND)
        
        totp = pyotp.TOTP(user.otp_secret,interval=300)
        if totp.verify(otp_code) :
            user.is_verified = True
            user.save()

            return Response({
                'message': 'Account verified successfully. You can now log in.'
            }, status=status.HTTP_200_OK)
        
        return Response({'error': 'Invalid or expired OTP code.'}, status=status.HTTP_400_BAD_REQUEST)
    

class ResendOTPView(APIView) :
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self,request) :
        email = request.data.get('email')

        if not email :
            return Response({'error' : 'Email field is Required .'},status=status.HTTP_400_BAD_REQUEST)
        
        try :
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error' : 'User with this email does not exist'},status=status.HTTP_404_NOT_FOUND)
        
        if user.is_verified :
            return Response({'message' : 'Account is already verified. You can log in.'}, status=status.HTTP_400_BAD_REQUEST)
        
        totp = pyotp.TOTP(user.otp_secret,interval=300)
        user.otp_secret = pyotp.random_base32()
        user.save()

        totp = pyotp.TOTP(user.otp_secret,interval=300)
        otp_code = totp.now()

        send_otp_email_task.delay(user.email,otp_code)

        return Response({
            'message': 'A new verification code has been sent to your email.'
        }, status=status.HTTP_200_OK)
