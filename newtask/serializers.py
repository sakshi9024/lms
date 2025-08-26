from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import *

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id','email']
        
class ChangePasswordSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Employee
        old_password = serializers.CharField(required= True)
        new_password = serializers.CharField(required =  True)
        
class ForgetPasswordSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  Employee
        email = serializers.CharField(required = True)

class VerifyotpSerializer(serializers.ModelSerializer):
    
    email = serializers.CharField(required=True)
    otp = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = Employee
        fields = ['email', 'otp', 'new_password']
        
class AttendanceLoginSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Attendance
        fields = ['employee','date','check_in' ]
        
class AttendanceLogoutSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Attendance
        fields = ['employee','date','check_out' ]
