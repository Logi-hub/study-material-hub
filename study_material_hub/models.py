from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
import string, random




class CustomUser(AbstractUser):
    is_authorized_uploader=models.BooleanField(default=False)
    USER_ROLES = (
        ('student', 'Student'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=USER_ROLES, default='student')

    def __str__(self):
        return f"{self.username} ({self.role})"

class StudyMaterial(models.Model):
    title = models.CharField(max_length=100)
    subject = models.CharField(max_length=50)
    file = models.FileField(upload_to='materials/')
    uploaded_by = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

      

def generate_upload_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class UploaderProfile(models.Model):
    user = models.OneToOneField('study_material_hub.CustomUser', on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    designation = models.CharField(max_length=100)
    institution = models.CharField(max_length=100)
    address = models.TextField()
    upload_code = models.CharField(max_length=191, unique=True, default=generate_upload_code)
    is_verified = models.BooleanField(default=True)  # Set True for now
      
    def __str__(self):
        return self.username

      