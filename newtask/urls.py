
from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter

default_router =  DefaultRouter()

default_router.register(r'me',EmployeeMe , basename='me')
default_router.register(r'changepassword',ChangePasswordView , basename='changepassword')
default_router.register(r'verifyotp',VerifyOtp , basename='verifyotp')

urlpatterns = default_router.urls+[

    path('login/', LoginView.as_view(), name='login'),
    path('forgetpassword/', ForgetPasswordView.as_view(), name='forgetpassword'),
    path('attendance/', AttendanceView.as_view(), name='attendance'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    
]
