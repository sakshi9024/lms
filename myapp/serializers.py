from rest_framework.serializers import Serializer
from rest_framework import serializers
from .models import *


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BooksCategory
        fields = '__all__'
        


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'
        
class BookDetail(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = '__all__'
        
class BookDetailSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()   

    class Meta:
        model = Books
        fields = ["id", "name", "selling_price","rent_price","category","author"]

class BookName(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = ['name']

class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    category = CategorySerializer()
    # similar_books = serializers.SerializerMethodField(method_name='get_similar_books')
    rent_books = serializers.SerializerMethodField(method_name='get_rent_books')
    sold_books = serializers.SerializerMethodField(method_name='get_sold_books')

    class Meta:
        model = Books
        fields = ['id', 'name','quantity','author','rent_books','category','sold_books']
    
    # def get_similar_books(self,obj):
    #     books = Books.objects.filter(category_id = obj.category.id).exclude(id=obj.id)
    #     serializer = BookDetail(books, many=True)
    #     return serializer.data
    
    def get_rent_books(self, obj):
        books = UserBook.objects.filter(type= 'R',book_id = obj.id).count()
        return books

    def get_sold_books(self, obj):
        books = UserBook.objects.filter(type= 'S',book_id = obj.id).count()
        return books
                        
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model =UserProfile
        fields = '__all__'

class UserBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBook
        fields = '__all__'
        
    def validate(self, data):
        book = data['book']
        if book.quantity < 1:
            raise serializers.ValidationError("This book is out of stock!")
        return data
        




    
