from django import forms
from .models import StudyMaterial # Use your actual model name here

class StudyMaterialForm(forms.ModelForm):
    class Meta:
        model = StudyMaterial
        fields = ['title', 'file'] # Add other fields if needed
