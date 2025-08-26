from django.contrib import admin
from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter

default_router =  DefaultRouter()

default_router.register(r'books',BooksView , basename='books')
default_router.register(r'author',AuthorView , basename='author')
default_router.register(r'category',CategoryView , basename='category')
default_router.register(r'bookuser',BookUserView , basename='bookuser')




urlpatterns = default_router.urls+[
    
    path('bookdetail/',BookDetail.as_view(), name='bookdetail'),
    path("booklist/", BookDetailView.as_view(), name="booklist"),

]
