from django.contrib import admin
from .models import *
from django.contrib.auth.hashers import make_password 

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name','description']
    
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['title','level_type']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [id,'first_name','email','password']
    
    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date','status']

# Register your models here.
