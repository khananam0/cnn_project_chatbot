from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
                    RegisterView, LoginView, AdminCreateUserView, 
                    # CourseViewSet, 
                    CourseDetailViewSet, GenerateOTP, 
                    ValidateOTP, UserStudentInfoView,CreateTicketAPIView, 
                    TicketListAPIView, AssignedTicketListAPIView, 
                    ClosedTicketListAPIView, CloseTicketAPIView,
                    UpdateFCMTokenView, NotificationViewSet,
                    RoleInfoSet, DepartmentRoleView,
                    ChatHistoryAPIView, AskQuestionView,UpdateViewTicketAPIView,
                    # CustomAuthToken
                )


router = DefaultRouter()
router.register(r'course-details', CourseDetailViewSet)
router.register(r'notifications', NotificationViewSet)


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('users/', AdminCreateUserView.as_view(), name='create_user'),

    path('generate-otp/', GenerateOTP.as_view(), name='generate-otp'), 
    path('validate-otp/', ValidateOTP.as_view(), name='validate-otp'),
    path('user-student-info/', UserStudentInfoView.as_view(), name='user_student_info'),
    path('students/<int:studentId>/', UserStudentInfoView.as_view(), name='student_info_detail'),

    path('roles-user/', RoleInfoSet.as_view(), name='role'),
    path('get-department/<str:value>/', DepartmentRoleView.as_view(), name='role_detail'),

    path('askchatbot/', AskQuestionView.as_view(), name='ask_question'),
    path('allchatbotdata/<int:studentid>/', AskQuestionView.as_view(), name='chatbot_chat_history'),
    
    # path('chat-history/<int:sender_id>/<int:receiver_id>/', ChatHistoryAPIView.as_view(), name='chat_history'),
    path('create-ticket/', CreateTicketAPIView.as_view(), name='create_ticket'),
    path('tickets/', TicketListAPIView.as_view(), name='ticket_list'),
    path('tickets/assigned/', AssignedTicketListAPIView.as_view(), name='assigned_ticket_list'),
    path('tickets/update-view-ticket/<int:ticketid>/', UpdateViewTicketAPIView.as_view(), name='update_ticket_answer'),
    path('tickets/closed/', ClosedTicketListAPIView.as_view(), name='closed_ticket_list'),
    path('close-ticket/<int:pk>/', CloseTicketAPIView.as_view(), name='close_ticket'),

    path('update-fcm-token/', UpdateFCMTokenView.as_view(), name='update_fcm_token'),

    # path('api-token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),


    path('', include(router.urls)),
]



