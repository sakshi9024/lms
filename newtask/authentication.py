from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed ,  NotAuthenticated
import jwt
from rest_framework.response import Response
from .models import *
from .serializers import *
from lms.settings import SECRET_KEY
from django.contrib.auth.hashers import check_password
from rest_framework import status



def encode_token(email, password, model):
    if not email or not password:
        return Response({"message": "Please provide both email and password"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        employee=model.objects.get(email=email)
    except Exception:
        return Response({"message": "email not found"}, status=status.HTTP_404_NOT_FOUND)
    if check_password(password, employee.password):
        token = jwt.encode({"email":email, "id":employee.id}, SECRET_KEY, algorithm='HS256')
        return Response({"token":token}, status=status.HTTP_201_CREATED)
    return Response({"message": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED)


def decode_token(request, model, serializer_class):
    headers = request.headers.get("Authorization")
    if not headers:
        return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

    if not headers.startswith('Bearer '):
        return Response({"detail": "Invalid token format."}, status=status.HTTP_401_UNAUTHORIZED)

    split_header = headers.split(' ')
    if len(split_header) != 2:
        return Response({"detail": "Invalid token format."}, status=status.HTTP_401_UNAUTHORIZED)

    token = split_header[1]  
    print(token)

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        print(decoded)
        queryset = model.objects.filter(id=decoded.get("id")).first()
        
        if queryset is None:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = serializer_class(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except jwt.ExpiredSignatureError:
        return Response({"detail": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as error:
        return Response({"detail": str(error)}, status=status.HTTP_401_UNAUTHORIZED)


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        response = decode_token(request, Employee, EmployeeSerializer)
        print(response)
        if response.status_code == 200:
            employee_data = response.data
            request.id = employee_data['id']
            request.user = employee_data
            return True
        else:
            raise NotAuthenticated(detail=response.data)
    