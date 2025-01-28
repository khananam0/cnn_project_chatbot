from django.contrib import admin
from .models import (
    CustomUser, 
    Roles, 
    ChatHistory,
    CourseDetail,
    UserStudentInfo,
    OTP, Ticket,
    Notification,
    )



"""Create course admin"""
@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username',)
    
admin.site.register(CourseDetail)
admin.site.register(UserStudentInfo)
admin.site.register(OTP)
admin.site.register(Ticket)
admin.site.register(Notification)
admin.site.register(Roles)
admin.site.register(ChatHistory)






