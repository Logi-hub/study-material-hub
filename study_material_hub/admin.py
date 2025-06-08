from django.contrib import admin
from .models import StudyMaterial,CustomUser
from django.contrib.auth.admin import UserAdmin


admin.site.register(CustomUser,UserAdmin)
admin.site.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display=('title','subject','year','uploaded_by')
    search_fields=('title','subject')
