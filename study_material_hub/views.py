from django.shortcuts import render, redirect
from rest_framework import generics
from .models import CustomUser
from .serializers import UserSerializer,CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from django.contrib.auth.decorators import login_required,user_passes_test
from django.http import HttpResponseForbidden
from .models import StudyMaterial
from  .forms import StudyMaterialForm
from django.contrib.auth.models import User
from .models import UploaderProfile
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated



class SignupView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
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
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_material(request):
    code = request.data.get('verification_code')
    profile = UploaderProfile.objects.get(user=request.user)
    if profile.upload_code != code:
        return Response({"error": "Invalid verification code"}, status=403)

    return Response({"msg": "Material uploaded successfully"})

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

# views.py

@api_view(['POST'])
def register_uploader(request):
    data = request.data
    try:
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )
        profile = UploaderProfile.objects.get(user=user)
        profile.phone = data['phone']
        profile.designation = data['designation']
        profile.institution = data['institution']
        profile.address = data['address']
        profile.save()
        return Response({"msg": "Registration successful", "code": profile.upload_code}, status=201)
    except Exception as e:
        return Response({"error": str(e)}, status=400)

