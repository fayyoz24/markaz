from django.contrib import admin

# Register your models here.
from .models import User, Group, StudentProfile, Payment, Attendance, Grade
admin.site.register(User)
admin.site.register(Group)
admin.site.register(StudentProfile)
admin.site.register(Payment)
admin.site.register(Attendance)
admin.site.register(Grade)
