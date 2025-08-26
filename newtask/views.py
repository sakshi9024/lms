from django.shortcuts import render
from .models import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from .serializers import EmployeeSerializer, ChangePasswordSerializer , ForgetPasswordSerializer, VerifyotpSerializer, AttendanceLoginSerializer, AttendanceLogoutSerializer
from django.contrib.auth.hashers import make_password , check_password
import jwt
from lms.settings import SECRET_KEY
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission
import random
from django.core.mail import send_mail
from datetime import date, datetime,timedelta
from geopy.geocoders import Nominatim
import geocoder
from geopy.distance import geodesic
from .authentication import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
# from django.views.decorators.csrf import csrf_exempt
# from django.utils.decorators import method_decorator


OFFICE_LATITUDE = 26.9124
OFFICE_LONGITUDE = 75.7873
OFFICE_RADIUS_METERS = 50 

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip or "8.8.8.8"
  
def generate_token(obj):
    access_token = jwt.encode({"id": obj["id"],     # use actual valsues from obj
                               "email": obj["email"]}, 
                               SECRET_KEY, 
                               algorithm="HS256")
    return access_token

def Secret_detail(obj):
    secret_token = jwt.encode({"id": obj["id"],     # use actual values from obj
                               "email": obj["email"],
                               "otp" : obj['hash_otp']}, 
                               SECRET_KEY, 
                               algorithm="HS256")
    return secret_token


class LoginView(APIView):
    throttle_classes = [UserRateThrottle]
    # @method_decorator(csrf_exempt, name='dispatch')
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        if email and not password:
            return Response({'msg': 'Password is required'}, status=status.HTTP_404_NOT_FOUND)
        if not latitude or not longitude:
            return Response({'msg': 'Latitude and Longitude required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            return Response({'msg': 'Invalid coordinates'}, status=status.HTTP_400_BAD_REQUEST)

        if password and not email:
            return Response({'msg': 'Email is required'}, status=status.HTTP_404_NOT_FOUND)

        if password and email:
            employee = Employee.objects.filter(email=email).first()
            if employee:
                check_pass = check_password(password, employee.password)
                if check_pass:
                    today = date.today()
                    check_in = datetime.now().time()
                    role_entry_datetime = datetime.combine(today, employee.role.entry_time)
                    late_entry = (role_entry_datetime + timedelta(minutes=10)).time()
                    is_late = check_in > late_entry 
                    too_late = (role_entry_datetime + timedelta(hours=6)).time()
                    too_early = (role_entry_datetime - timedelta(hours=2)).time()
                    
                    
                    if check_in < too_early or check_in > too_late:
                        return Response({
                        'access_token': generate_token({'id': employee.id, 'email': employee.email}),
                        'msg': 'Login Successfully'})
                        

                    user_location = (latitude, longitude)        
                    office_location = (OFFICE_LATITUDE, OFFICE_LONGITUDE)
                    distance = geodesic(user_location, office_location).meters
                    print(distance)
                    print(distance <= OFFICE_RADIUS_METERS)
                    

                    if distance <= OFFICE_RADIUS_METERS:
                        attendance_type = "office"
                    else:
                        attendance_type = "wfh"

                    # Create or update attendance record
                    attendance, created = Attendance.objects.get_or_create(
                        employee=employee,
                        date=today,
                        defaults={
                            "check_in": check_in,
                            "late_check_in": is_late,
                            "attendance_type": attendance_type
                        }
                    )

                    attendance_data = AttendanceLoginSerializer(attendance).data

                    return Response({
                        'access_token': generate_token({'id': employee.id, 'email': employee.email}),
                        'msg': 'Login Successfully',
                        'attendance': attendance_data,
                        'attendance_type': attendance.attendance_type
                    })

                else:
                    return Response({'msg': 'Invalid password'})
            else:
                return Response({'msg': 'No employee found'})

        return Response({'msg': 'Email and password are required'}, status=status.HTTP_404_NOT_FOUND)
 
 
class IsEmployee(BasePermission):
    def has_permission(self, request, view):
      
        token = request.headers.get('Authorization')
        if not token:
            raise PermissionDenied('Unauthorized: No token provided')
        if token.startswith("Bearer "):
            token_split = token.split(" ")
            if len(token_split) == 2:
                try:
                    decoded_data = jwt.decode(token_split[1], SECRET_KEY, algorithms=['HS256'])
                    employee = Employee.objects.filter(
                        email=decoded_data.get('email'),
                        id=decoded_data.get('id')
                    ).first()
                    if not employee:
                        raise PermissionDenied('Unauthorized: Employee not found')
                    request.employee = employee
                    return True

                except jwt.ExpiredSignatureError:
                    raise PermissionDenied('Unauthorized: Token expired')
                except jwt.DecodeError:
                    raise PermissionDenied('Unauthorized: Invalid token')
                except Exception:
                    raise PermissionDenied('Unauthorized: Token error')
        
        raise PermissionDenied('Unauthorized: Invalid Authorization header')

class EmployeeMe(ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [IsEmployee]
    http_method_names = ['get']
    
    def list(self, request, *args, **kwargs):
        query_set = Employee.objects.filter(id=request.employee.id).first()
        serializer = self.serializer_class(query_set)
        return Response(serializer.data)
    
class ChangePasswordView(ModelViewSet):
    serializer_class = ChangePasswordSerializer
    http_method_names = ['post']
    permission_classes = [IsEmployee]
    def create(self, request, *args, **kwrgs):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        employee = request.employee
        if not old_password or not new_password:
            return Response({'msg':'old_password and new_password are required'}, status=status.HTTP_404_NOT_FOUND)

        if not check_password(old_password, employee.password):
            return Response({'msg':'password is invalid'})
        employee.password = make_password(new_password)
        employee.save()
        return Response({'msg':'Password updated successfully'})


class ForgetPasswordView(APIView):

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'msg': 'Email is required'}, status=400)

        try:
            employee = Employee.objects.get(email=email)
        except Employee.DoesNotExist:
            return Response({'msg': 'Incorrect Email'}, status=status.HTTP_404_NOT_FOUND)

        otp = random.randint(111111, 999999)
        try:
          
            send_mail(
                subject="Password Reset OTP",
                message=f"Your OTP code is {otp}",
                from_email="sakshiverma9024@gmail.com",
                recipient_list=["vanditaquadsoft@gmail.com"],
                fail_silently=False,
            )
            hash_otp = make_password(str(otp))

            return Response({'secret_token': Secret_detail({'id':employee.id,'email':employee.email,'hash_otp':hash_otp})}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'msg': "Error sending OTP"}, status= status.HTTP_400_BAD_REQUEST)

                       
class VerifyOtp(ModelViewSet):
    serializer_class = VerifyotpSerializer
    http_method_names = ['post']
    
    def create(self, request, *args, **kwargs):
        secret = request.data.get('secret')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')
        if not secret and not otp and not new_password:
            return Response({'msg':'secret, otp and newpassword is required'}, status= status.HTTP_404_NOT_FOUND)
        try:
            decoded_data = jwt.decode(secret, SECRET_KEY, algorithms=['HS256'])
            employee = Employee.objects.filter(email= decoded_data.get('email')).first()
            if not employee:
                return Response({'msg':'email not found'}, status= status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'msg':'Error getting email'}, status= status.HTTP_404_NOT_FOUND)
        check_pass = check_password(otp, decoded_data.get('otp'))
        if check_pass:
            employee.password = make_password(new_password)
            employee.otp = None
            employee.save()
            return Response({'msg':"Password updated successfully"}, status=status.HTTP_201_CREATED)
        return Response({'msg':"OTP is invalid"}, status= status.HTTP_404_NOT_FOUND)  
    
# class AttendanceAPI(ModelViewSet):
#     serializer_class = AttendanceSerializer
#     http_method_names = ['post']
#     permission_classes = [IsEmployee]
#     def create(self, request, *args, **kwargs):
#         employee = request.employee
#         today = date.today()
#         attendance = Attendance.objects.filter(employee=employee, date=today).first()
#         if attendance:
#             return Response({'msg': 'Already checked in today'}, status=status.HTTP_400_BAD_REQUEST)
#         # Create new attendance record
#         attendance = Attendance.objects.create(employee=employee,date=today, check_in=datetime.now().time())
#         return Response({'msg': 'Checked in successfully','attendance': AttendanceSerializer(attendance).data}, status=status.HTTP_201_CREATED)
        
    
class AttendanceView(APIView):
    def post(self, request):
        ip = get_client_ip(request)
        g = geocoder.ip(ip)
        print(g)
        if g.ok and g.latlng:
            user_lat, user_lon = g.latlng
        else:
            return Response({"msg": "Location could not be determined"}, status=400)

        # Your office location (e.g., Delhi)
        office_lat, office_lon = 28.6139, 77.2090

        distance = geodesic((user_lat, user_lon), (office_lat, office_lon)).meters

        if distance <= 100:
            location_status = "At office"
        else:
            location_status = "Outside office"

        return Response({
            "ip": ip,
            "user_location": (user_lat, user_lon),
            "office_location": (office_lat, office_lon),
            "location_status": location_status,
            "distance_meters": distance
        }, status=200)
        
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  

    def post(self, request):
        # Get the employee from the logged-in user's email
        employee = Employee.objects.filter(id=request.id).first()
        print(f"{employee} employee")
        if not employee:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

        today = date.today()

        try:
            attendance = Attendance.objects.get(employee=employee, date=today)
        except Attendance.DoesNotExist:
            return Response({'error': 'No login record found for today'}, status=status.HTTP_404_NOT_FOUND)

        check_out = datetime.now()

        # Role exit time check
        role_exit_datetime = datetime.combine(today, employee.role.exit_time)
        early_exit_time = role_exit_datetime - timedelta(minutes=10)
        is_early_exit = check_out < early_exit_time

        # Calculate total working hours
        check_in_datetime = datetime.combine(today, attendance.check_in)
        total_work_hours = (check_out - check_in_datetime).total_seconds() / 3600

        # Determine attendance status
        if total_work_hours < 3:
            status_type = "absent"
        elif total_work_hours < 7:
            status_type = "half_day"
        else:
            status_type = "present"

        attendance.check_out = check_out.time()
        attendance.early_check_out = is_early_exit
        attendance.status = status_type
        attendance.save(update_fields=['check_out', 'early_check_out', 'status'])

        return Response({
            'msg': 'Logout Successfully',
            'attendance': AttendanceLogoutSerializer(attendance).data
        }, status=status.HTTP_200_OK)


