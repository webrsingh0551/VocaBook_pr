from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class User_Details(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField( max_length=50)
    
    def __str__(self):
        return self.name


class VocaBooks(models.Model): 
    BookName    = models.CharField(("bookname"), max_length=50)
    FileName    = models.CharField(("filename"), max_length=50)
    Uploaded_By = models.CharField(("Uploaded_by"), max_length=50)

    def __str__(self):
        return self.BookName
