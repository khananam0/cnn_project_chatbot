from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status, permissions
from django.contrib.auth import authenticate
from .models import CustomUser
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from rest_framework.permissions import IsAuthenticated
from .serializers import AdminCreateUserSerializer
from rest_framework import viewsets
from .models import CourseDetail,  UserStudentInfo, OTP, Ticket, Notification
from .serializers import CourseDetailSerializer, RoleSerializer, UserStudentInfoSerializer, OTPSerializer, TicketSerializer, NotificationSerializer
from django.db.models import Q
# from rest_framework.exceptions import MethodNotAllowed
from .models import Roles
# from .gen_ai_chatbot import PDFQuestionAnswering # Import your GenAI model's extraction function
import random
from datetime import datetime, timedelta
# from twilio.rest import Client
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .utils import send_push_notification



#  add condition only admin
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            user_role = Roles.objects.get(id=request.data['role'])
        except Exception:
            return Response({'message':'Role does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        if user_role.role.lower() == 'admin':
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                user.is_staff = True # Set the user as staff/admin
                user.set_password(serializer.validated_data['password']) # Hash the password
                # user.role = (user_role)
                user.save()
                return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':'Admin can only register'}, status=status.HTTP_401_UNAUTHORIZED)



class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)

            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'role': str(user.role),
                    'user_id': str(user.id)
                }, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoleInfoSet(APIView):
    def post(self, request):
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        roles = Roles.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DepartmentRoleView(APIView):
    def get(self, request, value):
        if value.lower() == "new":
            department = Roles.objects.filter(role__icontains='admin')
        else:
            department = Roles.objects.filter(~Q(role__icontains='admin'))

        serializer = RoleSerializer(department, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminCreateUserView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access

    def post(self, request):
        if request.user.role.role.lower() == 'admin':
            serializer = AdminCreateUserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'User created successfully by admin'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'error': 'You do not have permission to perform this action, only admin can create users'}, status=status.HTTP_403_FORBIDDEN)
        

"""Create Course viewset"""
class CourseDetailViewSet(viewsets.ModelViewSet):
    queryset = CourseDetail.objects.all()
    serializer_class = CourseDetailSerializer


"""Sending sms otp validation"""

# Twilio credentials (replace with your actual credentials)
# TWILIO_ACCOUNT_SID = 'your_account_sid'
# TWILIO_AUTH_TOKEN = 'your_auth_token'
# TWILIO_PHONE_NUMBER = 'your_twilio_phone_number'

# Function to send SMS using Twilio
# def send_sms(mobile_no, otp):
#     client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
#     message = client.messages.create(
#         body=f"Your OTP is {otp}",
#         from_=TWILIO_PHONE_NUMBER,
#         to=mobile_no
#     )
#     print(f"Sent OTP {otp} to {mobile_no}")


import requests
import json
from myproject.settings import SMS_BASE_URL
def send_sms(mobile_no, otp):
    sms1 = SMS_BASE_URL.replace('{mobileno}', mobile_no)
    sms_url =sms1.replace('{message}', "This is the OTP for verification")

    sms_url = SMS_BASE_URL.replace('{mobile_no}', mobile_no).replace('{otp}', otp)
    message = requests.request("GET", sms_url)
    response = json.loads(message.text)
    return response


class GenerateOTP(APIView):
    def post(self, request):
        mobile_no = request.data.get('mobile_no')
        if not mobile_no:
            return Response({"error": "Mobile number is required"}, status=status.HTTP_400_BAD_REQUEST)
      
        # otp = random.randint(100000, 999999)
        # send_sms(str(mobile_no), str(otp))
        otp = 12345
        # Save OTP in database
        OTP.objects.update_or_create(
            mobile_no=mobile_no,
            defaults={'otp': otp, 'created_at': datetime.now(timezone.utc), 'is_validated': False}
        )
        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)


from datetime import datetime, timedelta, timezone
class ValidateOTP(APIView):
    def post(self, request):
        otp = request.data.get('otp')
        mobile_no = request.data.get('mobile_no')

        if not otp or not mobile_no:
            return Response({"error": "OTP and mobile number are required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            otp_record = OTP.objects.get(mobile_no=mobile_no, otp=otp)
            now = datetime.now(timezone.utc)
            if otp_record.created_at < now - timedelta(minutes=10):
                return Response({"error": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST)
            elif otp_record.otp != otp:
                return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
            otp_record.is_validated = True
            otp_record.save()

            """Add users details along if user exit"""
            if UserStudentInfo.objects.filter(mobile_no=mobile_no).exists():
                user_detail = UserStudentInfo.objects.get(mobile_no=mobile_no)
                user_info = UserStudentInfoSerializer(user_detail)
                return Response({"message": "User already exists and is verified",
                                 "user_info": user_info.data}, status=status.HTTP_200_OK)
            
            return Response({"message": "OTP validated successfully"}, status=status.HTTP_200_OK)
        except OTP.DoesNotExist:
            return Response({"error": "Invalid OTP or mobile number"}, status=status.HTTP_400_BAD_REQUEST)

class UserStudentInfoView(APIView):
    def post(self, request):
        mobile_no = request.data.get('mobile_no')
        try:
            OTP.objects.filter(mobile_no=mobile_no, is_validated=True)
        except OTP.DoesNotExist:
            return Response({"error": "Mobile number not verified"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = UserStudentInfoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, studentId):
        try:
            student_info = UserStudentInfo.objects.get(id=studentId)
            serializer = UserStudentInfoSerializer(student_info)
            return Response(serializer.data)
        except UserStudentInfo.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)


class TicketListAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        tickets = Ticket.objects.all()
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AssignedTicketListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        tickets = Ticket.objects.filter(assigned_to=request.user.role)
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ClosedTicketListAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        tickets = Ticket.objects.filter(status='closed')
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CloseTicketAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]
    def post(self, request, pk):
        try:
            ticket = Ticket.objects.get(pk=pk)
            if ticket.status == 'closed':
                return Response({"error": "Ticket is already closed"}, status=status.HTTP_400_BAD_REQUEST)
            ticket.status = 'closed'
            ticket.closed_by = request.data.get('closed_by')
            ticket.save()
            return Response({"message": "Ticket closed successfully"}, status=status.HTTP_200_OK)
        except Ticket.DoesNotExist:
            return Response({"error": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)


class CreateTicketAPIView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            try:
                assigned_user = CustomUser.objects.get(role=serializer.validated_data.get('assigned_to'))  # Assuming Ticket model has an 'assigned_to' field
            except CustomUser.DoesNotExist:
                return Response({"error": "Assigned user not found"}, status=status.HTTP_400_BAD_REQUEST)
            ticket = serializer.save(status='assigned')

            # if assigned_user and assigned_user.fcm_token:
            if assigned_user and assigned_user.fcm_token:
                # Send push notification
                try:
                    send_push_notification(assigned_user.fcm_token, ticket)
                except Exception as e:
                    print(f"Error sending notification: {e}")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateViewTicketAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, ticketid):
        try:
            ticket = Ticket.objects.get(pk=ticketid)
        except Ticket.DoesNotExist:
            return Response({"error": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TicketSerializer(ticket, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, ticketid):
        try:
            ticket = Ticket.objects.get(pk=ticketid)
            serializer = TicketSerializer(ticket)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Ticket.DoesNotExist:
            return Response({"error": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)
        

class UpdateFCMTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        fcm_token = request.data.get('fcm_token')
        if not fcm_token:
            return Response({"error": "FCM token is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update the user's FCM token
        user = request.user
        user.fcm_token = fcm_token
        user.save()
        return Response({"message": "FCM token updated successfully"}, status=status.HTTP_200_OK)


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({'token': token.key, 'user_id': token.user_id, 'email': token.user.email})


"""Chat implementation"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Message
from django.contrib.auth.models import User

class ChatHistoryAPIView(APIView):
    def get(self, request, sender_id, receiver_id):
        try:
            sender = User.objects.get(id=sender_id)
            receiver = User.objects.get(id=receiver_id)

            messages = Message.objects.filter(
                sender=sender, receiver=receiver
            ) | Message.objects.filter(
                sender=receiver, receiver=sender
            )
            messages = messages.order_by('timestamp')

            return Response(
                [
                    {
                        "sender": msg.sender.username,
                        "receiver": msg.receiver.username,
                        "content": msg.content,
                        "timestamp": msg.timestamp,
                    }
                    for msg in messages
                ],
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


# chatapp/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ChatHistory
from .serializers import ChatHistorySerializer
from .gen_ai_chatbot import PDFQuestionAnswering
import os

class AskQuestionView(APIView):
    def post(self, request, *args, **kwargs):
        student_id = request.data.get('student_id')
        question = request.data.get('question')
        print(request.data, "=======request.data==========")

        """commenting for now yerniapis"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print("=====base_dir======",base_dir)
        courses_info_folder = os.path.join(base_dir, 'Courses info2')
        model_path = os.path.join(base_dir, 'chat_model')
        print("=====courses_info_folder======",courses_info_folder, "====model_path====",model_path)
        # C:\Anam - learn\Freelancing\CNC\Project API\myproject\jsadjbasno

        pdf_qa_system = PDFQuestionAnswering(folder_path=courses_info_folder, model_path=model_path)
        result = pdf_qa_system.ask_question(question)
        if 'error' in result:
            return Response({'error': result['error']}, status=status.HTTP_400_BAD_REQUEST)
        answer = result['answer']
        """end of commenting"""

        # answer = "I am happy to assist you with your query. Please wait while I fetch the answer for you."
        # print("=====question======",question)

        student_info_instance = UserStudentInfo.objects.get(id=student_id)
        print("=====student_info_instance======",student_info_instance)
        # Save the chat history
        # chat_history_instance = ChatHistory.objects.create(student_id=student_info_instance, question=question, answer=answer)
        chat_entry = ChatHistory(student_id=student_info_instance, question=question, answer=answer)
        chat_entry.save()
        
        serializer = ChatHistorySerializer(chat_entry)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get(self, request, studentid):
        print("=======request.data==========")
        chat_history = ChatHistory.objects.filter(student_id=studentid)
        print("=======chat_history==========",chat_history)
        serializer = ChatHistorySerializer(chat_history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



