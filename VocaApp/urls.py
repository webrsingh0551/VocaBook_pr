from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = "index"),
    path('index', views.index, name = "index"),
    path('upload', views.upload_files, name = "upload"),
    path('vocabook/<CSV_File_Name>/<CSV_File_path>/', views.vocabook, name = "vocabook"),
    path('vocabooks_list', views.vocabooks_list, name = "vocabooks_list")

]
