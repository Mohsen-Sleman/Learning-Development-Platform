from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from users.models import RoleChoices
from django.contrib.auth import get_user_model
from courses.serializers import EnrollmentSerializer,EnrollmenTracktSerializer,CourseListSerializer,TrackListSerializer
from courses.models import Enrollment,TrackEnrollment,Course,Track
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from django.core.mail import send_mail
import pyotp
from users.tasks import send_otp_email_task

User = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer) :

    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.is_verified :
            
            totp = pyotp.TOTP(self.user.otp_secret,interval=300)
            otp_code = totp.now()

            send_otp_email_task.delay(self.user.email,otp_code)
            raise AuthenticationFailed({
                "detail": "Account not verified. A verification code has been sent to your email.",
                "is_verified": False,
                "email": self.user.email
            })

        data['full_name'] = self.user.full_name

        if self.user.profile_picture:
            data['profile_picture'] = self.context['request'].build_absolute_uri(self.user.profile_picture.url)
        else:
            data['profile_picture'] = None

        return data

class RegisterSerializer(serializers.ModelSerializer) :
    password2 = serializers.CharField(write_only = True)
    role = serializers.CharField(required = False,default = RoleChoices.STUDENT)
    profile_picture = serializers.ImageField(required = False,allow_null = True)
    class Meta : 
        model = User
        fields = [
            'email',
            'full_name',
            'password',
            'password2',
            'role',
            'profile_picture'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if instance.profile_picture and request :
            data['profile_picture'] = request.build_absolute_uri(instance.profile_picture.url)
        else :
            data['profile_picture'] = None
        return data

    def validate(self, attrs):
        if attrs['password'] != attrs['password2'] :
            raise serializers.ValidationError('Passwords do not match')
        
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        profile_picture = validated_data.get('profile_picture',None)
        return User.objects.create_user(email=validated_data['email'],
                                        full_name=validated_data['full_name'],
                                        password=validated_data['password'],
                                        role=validated_data['role'],
                                        profile_picture = profile_picture)

class ProfileEnrollmentSerialier(serializers.ModelSerializer) :
    course_name = serializers.CharField(source='course.name',read_only = True)
    class Meta :
        model = Enrollment
        fields = [
            'id',
            'course',
            'course_name',
        ]

class ProfileEnrollmentTrackSerializer(serializers.ModelSerializer) :
    track_name = serializers.CharField(source='track.name',read_only = True)
    class Meta :
        model = TrackEnrollment
        fields = [
            'id',
            'track',
            'track_name',
            'score',
            'is_completed',
        ]

class ProfileCourseSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Course
        fields = [
            'id',
            'name'
        ]

class ProfileTrackSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Track
        fields = [
            'id',
            'name'
        ]

class ProfileSerializer(serializers.ModelSerializer) :
    class Meta :
        model = User
        fields = [
            'id',
            'email',
            'full_name',
            'role',
            'profile_picture',
        ]
        read_only_fields = ['email','role']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.role == RoleChoices.STUDENT:
            
            enrolled_courses = Enrollment.objects.filter(user = instance)
            enrolled_tracks = TrackEnrollment.objects.filter(user = instance)
            representation['enrolled_courses'] = ProfileEnrollmentSerialier(enrolled_courses, many=True).data
            representation['enrolled_tracks'] = ProfileEnrollmentTrackSerializer(enrolled_tracks, many=True).data
            
        elif instance.role == RoleChoices.INSTRUCTOR:
            teaching_courses = Course.objects.filter(instructor = instance)
            teaching_tracks = Track.objects.filter(instructor = instance)
            representation['teaching_courses'] = ProfileCourseSerializer(teaching_courses, many=True).data
            representation['teaching_tracks'] = ProfileTrackSerializer(teaching_tracks, many=True).data

        return representation


class CustomUserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'email', 'full_name', 'profile_picture',)