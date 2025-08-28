from django.contrib import admin
from .models import *

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'file', 'pdf_file','uploaded_at']


# Register your models here.
