from django.shortcuts import render, redirect
from rest_framework import generics
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework.permissions import AllowAny
from django.contrib.auth.decorators import login_required,user_passes_test
from django.http import HttpResponseForbidden
from .models import StudyMaterial
from  .forms import StudyMaterialForm


class SignupView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

@login_required
def study_material_page(request):
    materials = StudyMaterial.objects.all()

    if request.method == "POST":
        # Allow only Uploader group to upload
        if not request.user.groups.filter(name='Uploader').exists():
            return HttpResponseForbidden("You are not authorized to upload materials.")
        
        form = StudyMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('study_material_page') # refresh the page
    else:
        form = StudyMaterialForm()

    context = {
        'form': form,
        'materials': materials,
        'can_upload': request.user.groups.filter(name='Uploader').exists()
    }
    return render(request, 'study_materials.html', context)


def is_uploader(user):
    return user.groups.filter(name='Uploader').exists()

@login_required
@user_passes_test(is_uploader)
def upload_material(request):
    if request.method == 'POST':
        form = StudyMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.uploaded_by = request.user
            material.save()
            return redirect('material_list') # change this to your list page
    else:
        form = StudyMaterialForm()
    return render(request, 'upload_material.html', {'form': form})
