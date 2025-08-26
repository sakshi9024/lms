from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from django.dispatch import receiver
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework import filters
from django.db.models import Min, Subquery

class BooksView(ModelViewSet):
    serializer_class = BookSerializer
    http_method_names = ['get', 'post']
    queryset = Books.objects.select_related('author', 'category').all().distinct()

    # Enable filtering, searching, and ordering
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # 1️⃣ Filtering (exact matches)
    filterset_fields = ['author', 'category', 'selling_price']

    # 2️⃣ Searching (partial matches)
    search_fields = ['name', 'author__name', 'category__title']

    # 3️⃣ Ordering (sorting)
    ordering_fields = ['selling_price', 'rent_price', 'quantity']
    ordering = ['selling_price']  # Default ordering
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        ids_per_name = queruset.values('name').annote(first_id=Min('id')).values('first_id')
        deduped_qs = queryset.filter(id__in=Subquery(ids_per_name)).order_by('name','id')
        page = self.paginate_queryset(deduped_qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(deduped_qs, many=True)
        return Response(serializer.data)
            
        
        
class AuthorView(ModelViewSet):
    serializer_class = AuthorSerializer
    http_method_names = ['get', 'post']
    queryset = Author.objects.all()  

class CategoryView(ModelViewSet):
    serializer_class = CategorySerializer
    http_method_names = ['get', 'post']
    queryset = BooksCategory.objects.all()  
    
class ProfileView(ModelViewSet):
    serializer_class = ProfileSerializer
    http_method_names = ['get', 'post']
    queryset = UserProfile.objects.all()

class BookUserView(ModelViewSet):
    queryset = UserBook.objects.all()
    serializer_class = UserBookSerializer
    http_method_names = ['get', 'post']
    
class BookDetail(APIView):
    def get(self, request):
        book = Books.objects.filter(id=2).first()
        serializer = BookSerializer(book)
        return Response(serializer.data)

from .serializers import BookDetailSerializer

class BookDetailView(ListAPIView):
    queryset = Books.objects.select_related('author', 'category').all().distinct()
    serializer_class = BookDetailSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ["author", "category"]   # Filtering
    search_fields = ["name", "author__name"]    # Searching
    ordering_fields = ["selling_price", "quantity"] 

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        ids_per_name = queruset.values('name').annote(first_id=Min('id')).values('first_id')
        deduped_qs = queryset.filter(id__in=Subquery(ids_per_name)).order_by('name','id')
        page = self.paginate_queryset(deduped_qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(deduped_qs, many=True)
        return Response(serializer.data)
            
    
        
        

    
    
