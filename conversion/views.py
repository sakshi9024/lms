import os
from django.shortcuts import render, redirect
from django.core.files import File
from django.conf import settings
from .models import Document
from .utils import convert_to_pdf


def upload_file(request):
    if request.method == "POST":
        uploaded = request.FILES.get("file")
        if not uploaded:
            return render(request, "conversion/upload.html", {"error": "No file selected!"})

        obj = Document.objects.create(file=uploaded)

        input_path = obj.file.path
        output_dir = os.path.join(settings.MEDIA_ROOT, "pdfs")
        os.makedirs(output_dir, exist_ok=True)

        filename_wo_ext = os.path.splitext(os.path.basename(input_path))[0]
        output_filename = filename_wo_ext + ".pdf"
        output_path = os.path.join(output_dir, output_filename)

        try:
            convert_to_pdf(input_path, output_path)
            with open(output_path, "rb") as f:
                obj.pdf_file.save(output_filename, File(f), save=True)
        except Exception as e:
            return render(request, "conversion/upload.html", {"error": f"Conversion failed: {str(e)}"})

        return redirect("success", doc_id=obj.id)

    return render(request, "conversion/upload.html")


def success(request, doc_id):
    try:
        document = Document.objects.get(id=doc_id)
        pdf_url = document.pdf_file.url
        return render(request, "conversion/success.html", {"pdf_url": pdf_url})
    except Document.DoesNotExist:
        return render(request, "conversion/success.html", {"error": "Document not found!"})



# using LibreOffice 


# import os
# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from django.conf import settings
# from .models import Document
# from .serializers import DocumentSerializer
# from .utils import convert_to_pdf, image_to_pdf


# class DocumentViewSet(viewsets.ModelViewSet):
#     queryset = Document.objects.all()
#     serializer_class = DocumentSerializer

#     def create(self, request, *args, **kwargs):
#         uploaded_file = request.FILES.get("file")

#         if not uploaded_file:
#             return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

#         # Save original uploaded file
#         document = Document.objects.create(file=uploaded_file)
#         input_file = document.file.path
#         filename, ext = os.path.splitext(uploaded_file.name)
#         ext = ext.lower()

#         try:
#             output_file = None

#             if ext == ".pdf":
#                 output_file = input_file

#             elif ext in [".doc", ".docx", ".csv"]:
#                 output_file = convert_to_pdf(input_file, settings.MEDIA_ROOT)

#             elif ext in [".jpg", ".jpeg", ".png"]:
#                 output_file = os.path.join(settings.MEDIA_ROOT, f"{filename}.pdf")
#                 image_to_pdf(input_file, output_file)

#             else:
#                 return Response(
#                     {"error": f"Unsupported file type: {ext}"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             # Update DB with PDF path
#             document.pdf_file.name = os.path.relpath(output_file, settings.MEDIA_ROOT)
#             document.save()

#             serializer = self.get_serializer(document)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
