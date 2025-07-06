from django.contrib import admin
from .models import StudyMaterial,CustomUser
from django.contrib.auth.admin import UserAdmin
from .models import UploaderProfile

admin.site.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display=('title','subject','year','uploaded_by')
    search_fields=('title','subject')

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display= ["username", 'role','is_authorized_uploader']


@admin.register(UploaderProfile)
class UploaderProfileAdmin(admin.ModelAdmin):
    list_display= ["user", "phone", "designation", "institution", "place", "upload_code", "is_verified"]

    
