from django.db import models


class Document(models.Model):
    file = models.FileField(upload_to="uploads/")
    pdf_file = models.FileField(upload_to="pdf_files/", null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

# Create your models here.
