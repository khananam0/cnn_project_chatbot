from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.db import models
from django.core.validators import RegexValidator


class Roles(models.Model):
    role = models.CharField(max_length=100)

    def __str__(self):
        return self.role
    
class CustomUser(AbstractUser):
    role = models.ForeignKey(Roles, on_delete=models.CASCADE, related_name='role_list', null=True, blank=True)
    fcm_token = models.TextField(null=True, blank=True)

    def __str__(self): 
        return self.username

"""Course Model"""
class CourseDetail(models.Model):
    coursename = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.description

"""Save student user information"""
class UserStudentInfo(models.Model):
    name = models.CharField(max_length=100)
    education_qualification = models.CharField(max_length=100)
    isworking = models.BooleanField(default=False)
    mobile_no = models.CharField(max_length=10,unique=True, blank=True, null=True, validators=[RegexValidator(
    regex=r"^\d{10}", message="Phone number must be 10 digits only.")])
    email = models.EmailField(unique=True)
    # is_verified = models.BooleanField(default=False)

    def __str__(self): 
        return self.name


"""OTP Validation and Creation"""
class OTP(models.Model):
    mobile_no = models.CharField(max_length=10,unique=True, blank=True, null=True, validators=[RegexValidator(
    regex=r"^\d{10}", message="Phone number must be 10 digits only.")])
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_validated = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP for {self.mobile_no}"


class Ticket(models.Model):
    STATUS_CHOICES = ( 
        ('open', 'Open'), 
        ('assigned', 'Assigned'), 
        ('closed', 'Closed'), 
    )
    student_id = models.ForeignKey(UserStudentInfo, on_delete=models.CASCADE, related_name='student_tickets') 
    description = models.TextField()
    assigned_to = models.ForeignKey(Roles,on_delete=models.CASCADE, related_name='department') # e.g., admin, technical manager, reception
    answer = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=10, null=True, blank=True,choices=STATUS_CHOICES, default='open') 
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)
    # closed_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='closed_tickets', null=True, blank=True)
    closed_by = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self): 
        return self.description

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = models.TextField()
    ticket_id = models.IntegerField()
    status = models.CharField(max_length=10)
    # is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Message(models.Model):
    sender = models.ForeignKey('myapp.UserStudentInfo', on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"


class ChatHistory(models.Model):
    student_id = models.ForeignKey(UserStudentInfo, on_delete=models.CASCADE, related_name='student_chat_history')
    question = models.TextField()
    answer = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)








