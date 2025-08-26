from django.db import models


class BooksCategory(models.Model):
    title = models.CharField(max_length=200, unique=True)
    
    def __str__(self):
        return self.title
    
class Author(models.Model):
    name = models.CharField(max_length=200, unique= True)
    # books = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name

class Books(models.Model):
    name = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, db_index=True, related_name='book_author')
    selling_price = models.IntegerField()
    quantity = models.IntegerField(default=50)
    rent_price = models.IntegerField(help_text='per day')
    category = models.ForeignKey(BooksCategory, on_delete=models.CASCADE, db_index=True , related_name='book_category') 
   
    

    def __str__(self):
        return self.name
    
class UserProfile(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    password = models.CharField(max_length=200, blank=True, null=True)
    phone_no = models.CharField(max_length=200)
    address = models.TextField()
    
    def __str__(self):
        return self.name
    
class UserBook(models.Model):
    user = models.ForeignKey(UserProfile, related_name='user', on_delete=models.CASCADE, db_index=True)
    book = models.ForeignKey(Books,related_name='book', on_delete=models.CASCADE, db_index=True)
    no_of_days = models.IntegerField(blank=True, null=True)
    renting_date = models.DateTimeField(blank=True, null=True)
    type = models.CharField(max_length=200,choices=[
        ('S', 'Sale'),
        ('R', 'Rent')
    ])


