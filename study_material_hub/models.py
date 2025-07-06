from django.db import models
from django.contrib.auth.models import AbstractUser
import string, random
from django.conf import settings


#  Custom User Model
class CustomUser(AbstractUser):
    is_authorized_uploader = models.BooleanField(default=False)

    USER_ROLES = (
        ('Reader', 'Reader'),
        ('Uploader', 'Uploader'),
    )
    role = models.CharField(max_length=10, choices=USER_ROLES, default='Reader')

    def __str__(self):
        return f"{self.username} ({self.role})"


#  Study Material Model
from django.db import models

class StudyMaterial(models.Model):
    title = models.CharField(max_length=100)
    subject = models.CharField(max_length=50)
    file = models.FileField(upload_to='materials/')
    uploaded_by = models.ForeignKey(CustomUser,
        on_delete=models.CASCADE,
    )
    verification_code = models.CharField(max_length=100)  
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



# Random Upload Code Generator
def generate_upload_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


# Uploader Profile for Authorized Users
class UploaderProfile(models.Model):
    user = models.OneToOneField('study_material_hub.CustomUser', on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    designation = models.CharField(max_length=100)
    institution = models.CharField(max_length=100)
    place = models.CharField(max_length=100,blank=True,null=True)
    upload_code = models.CharField(max_length=191, unique=True, default=generate_upload_code)
    is_verified = models.BooleanField(default=True)  

    def __str__(self):
        return self.user.username
    
from django.db import models

class EmailOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.otp}"



from django.db import models

class PendingUser(models.Model):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=20, default='Reader')
    is_authorized_uploader = models.BooleanField(default=False)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email



class SavedMaterial(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    material = models.ForeignKey(StudyMaterial, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'material')

    def __str__(self):
        return f"{self.user.username} saved {self.material.title}"

