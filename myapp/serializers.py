from rest_framework import serializers
from .models import CustomUser
from .models import (
    CourseDetail, OTP, Ticket, UserStudentInfo, Notification, ChatHistory, Roles
)

class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    role = serializers.PrimaryKeyRelatedField(queryset=Roles.objects.all())
    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'email', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            role=validated_data['role']
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class AdminCreateUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    class Meta:
        model = CustomUser
        fields = ['id','username', 'password', 'email', 'role']
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'default': 'operations'}
        }

    def validate_role(self, value):
        if value == 'admin':
            raise serializers.ValidationError("Only users with the 'operations' role can be created.")
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            role=validated_data['role']
        )
        return user
    
class CourseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseDetail
        fields = ['id','coursename', 'duration', 'description', 'cost']


"""OTP validation and creation serializer"""
class UserStudentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStudentInfo
        fields = ['id','name','education_qualification', 'isworking','email', 'mobile_no']

class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ['mobile_no', 'otp', 'created_at', 'is_validated']

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'student_id', 'description', 'assigned_to', 'answer', 'status', 'closed_by', 'created_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'body', 'status', 'created_at']


class RoleSerializer(serializers.ModelSerializer):
    class  Meta:
        model = Roles
        fields = ['id', 'role']
        

class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory
        fields = '__all__'




