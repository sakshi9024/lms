# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import DocumentViewSet

# router = DefaultRouter()
# router.register(r"documents", DocumentViewSet, basename="document")

# urlpatterns = [
#     path("", include(router.urls)),
# ]


from django.urls import path
from . import views
from django.shortcuts import render 


urlpatterns = [
    path("upload/", views.upload_file, name="upload"),
    path("success/<int:doc_id>/", views.success, name="success"),
]
