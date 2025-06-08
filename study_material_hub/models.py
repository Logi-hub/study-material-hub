from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
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

