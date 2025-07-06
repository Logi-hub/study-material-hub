from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, CustomTokenObtainPairSerializer, StudyMaterialSerializer,UploaderProfileSerializer
from .models import CustomUser, StudyMaterial, UploaderProfile
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
import os
from django.http import FileResponse,Http404
from .models import StudyMaterial
from django.conf import settings
from rest_framework.parsers import MultiPartParser,FormParser
from twilio.rest import Client
from django.core.mail import send_mail
from django.conf import settings
from .models import EmailOTP
from django.shortcuts import get_object_or_404
from  .models import PendingUser
import random
User = get_user_model()


#  Signup
class SignupView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        print("📥 Signup incoming:", request.data)

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("❌ Serializer Errors:", serializer.errors)
            return Response(serializer.errors, status=400)

        email = request.data.get("email")
        if not PendingUser.objects.filter(email=email).exists():
            return Response({"error": "OTP not verified."}, status=400)

        # Delete OTP record
        PendingUser.objects.filter(email=email).delete()

        self.perform_create(serializer)
        return Response(serializer.data, status=201)




#  Login with custom token
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

from .serializers import UploadMaterialSerializer
# Upload Material (Only for verified uploader with valid code)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_material(request):

    print("upload_material view hit")
    data=request.data
    data['upload_by']=request.user.id
    serializer=UploadMaterialSerializer(data=data)
    if serializer.is_valid():
        serializer.save(uploaded_by=request.user)
        return Response(serializer.data,status=201)
    else:
        print("upload error:",serializer.errors)
        return Response(serializer.errors,status=400)


#  Register uploader details
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UploaderProfile

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_uploader(request):
    try:
        user = request.user
        data = request.data

       
        profile, created = UploaderProfile.objects.get_or_create(user=user)
        
        
        profile.phone = data.get('phone')
        profile.designation = data.get('designation')
        profile.institution = data.get('institution')
        profile.place = data.get('place')
        profile.save()

        
        user.is_authorized_uploader = True
        user.save()

        return Response({
            "msg": "✅ Verification successful",
            "code": profile.upload_code
        }, status=201)

    except Exception as e:
        return Response({"error": str(e)}, status=400)

  
@api_view(['GET'])
@permission_classes([AllowAny])
def list_materials(request):
    materials = StudyMaterial.objects.all().order_by('-uploaded_at')
    serializer = StudyMaterialSerializer(materials, many=True, context={'request': request})
    return Response(serializer.data)





@api_view(['GET'])
@permission_classes([AllowAny])
def preview_material(request, pk):
    try:
        material = StudyMaterial.objects.get(pk=pk)
        file_path = material.file.path
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
        raise Http404
    except StudyMaterial.DoesNotExist:
        raise Http404

#  Download Material
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_material(request, pk):
    try:
        material = StudyMaterial.objects.get(pk=pk)
        file_path = material.file.path
        file_name = material.file.name.split('/')[-1]

        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=file_name)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
def send_email_otp(request):
    email = request.data.get('email')
    print("email is checked")
    if not email:
        return Response({"error": "Email is required"}, status=400)

    if not User.objects.filter(email=email).exists():
        return Response({"error": "No user with this email"}, status=404)

    otp = str(random.randint(100000, 999999))
    EmailOTP.objects.create(email=email, otp=otp)

    try:
        send_mail(
            subject="🔐 Your OTP for Password Reset",
            message=f"Your OTP is: {otp}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return Response({"message": "OTP sent to email"})
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
def reset_password(request):
    email = request.data.get('email')
    otp = request.data.get('otp')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    print("email",email)
    print("otp",otp)
    print("new password",new_password)
    print("confirm password",confirm_password)

    if not all([email, otp, new_password, confirm_password]):
        return Response({"error": "All fields are required"}, status=400)

    if new_password != confirm_password:
        return Response({"error": "Passwords do not match"}, status=400)

    try:
        valid_otp = EmailOTP.objects.filter(email=email, otp=otp).latest('created_at')
    except EmailOTP.DoesNotExist:
        return Response({"error": "Invalid or expired OTP"}, status=400)

    try:
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error":"user not found"},status=404)
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password reset successful!"})
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_uploads(request):
    user = request.user
    materials = StudyMaterial.objects.filter(uploaded_by=user)
    serializer = StudyMaterialSerializer(materials, many=True)
    return Response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def material_detail(request, pk):
    try:
        material = StudyMaterial.objects.get(pk=pk)
    except StudyMaterial.DoesNotExist:
        return Response({'error': 'Material not found'}, status=status.HTTP_404_NOT_FOUND)

    if material.uploaded_by != request.user:
        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
    

    if request.method == 'GET':
        serializer = StudyMaterialSerializer(material)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = StudyMaterialSerializer(material, data=request.data, partial=True)
        print("incoming data for put:",request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        material.delete()
        return Response({'message': 'Deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UploaderProfile
from .serializers import UploaderProfileSerializer

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def uploader_profile(request):
    user = request.user

    if user.is_authorized_uploader:
        try:
            uploader = UploaderProfile.objects.get(user=user)
        except UploaderProfile.DoesNotExist:
            return Response({'error': 'Uploader profile not found'}, status=404)

        if request.method == 'GET':
            serializer = UploaderProfileSerializer(uploader, context={'request': request})
            return Response(serializer.data) 

        elif request.method == 'PUT':
            serializer = UploaderProfileSerializer(
                uploader,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data) 
            return Response(serializer.errors, status=400)

   
    elif request.method == 'GET':
        return Response({
            'username': user.username,
            'email': user.email,
            'upload_code': '',
            'phone': '',
            'designation': '',
            'institution': '',
            'place': '',
        })

    else:
        return Response({'error': 'Only uploaders can update profile'}, status=403)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def become_uploader(request):
    user = request.user

    if user.role == 'Uploader':
        return Response({'error': 'Already an uploader'}, status=400)

    
    phone = request.data.get('phone')
    designation = request.data.get('designation')
    institution = request.data.get('institution')
    place = request.data.get('place')

    
    user.role = 'Uploader'
    user.is_authorized_uploader = True
    user.save()

   
    from .models import UploaderProfile
    if not hasattr(user, 'uploaderprofile'):
        UploaderProfile.objects.create(
            user=user,
            phone=phone,
            designation=designation,
            institution=institution,
            place=place
        )

    return Response({'message': 'You are now an authorized uploader'})




@api_view(['POST'])
def send_otp(request):
    email = request.data.get('email')
    username = request.data.get('username')

    if not email or not username:
        return Response({"error": "Email and username required"}, status=400)

    if CustomUser.objects.filter(email=email).exists():
        return Response({"error": "Email already registered"}, status=400)

    otp = str(random.randint(100000, 999999))
    PendingUser.objects.update_or_create(
        email=email,
        defaults={"username": username, "otp": otp}
    )

    send_mail(
        subject="Your OTP for StudyHub Signup",
        message=f"Use this OTP to complete your signup: {otp}",
        from_email="studyhub@example.com",
        recipient_list=[email]
    )

    return Response({"msg": "OTP sent to email!"}, status=200)



@api_view(['POST'])
def verify_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')

    try:
        user = PendingUser.objects.get(email=email)
    except PendingUser.DoesNotExist:
        return Response({"error": "No pending user"}, status=404)

    if user.otp != otp:
        return Response({"error": "Invalid OTP"}, status=400)

    return Response({"msg": "OTP Verified!"}, status=200)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import SavedMaterial,StudyMaterial
from .serializers import SavedMaterialSerializer
from django.shortcuts import get_object_or_404

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_material(request, material_id):
    material = get_object_or_404(StudyMaterial, id=material_id)
    saved, created = SavedMaterial.objects.get_or_create(user=request.user, material=material)
   
    if created:
        return Response({"message": "Material saved ✅"})
    return Response({"message": "Already saved"})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unsave_material(request, material_id):
    try:
        saved = SavedMaterial.objects.get(user=request.user, material_id=material_id)
        saved.delete()
        return Response({"message": "Unsave successful"})
    except SavedMaterial.DoesNotExist:
        return Response({"message": "Material not found in saved list"}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def saved_materials(request):
    saved = SavedMaterial.objects.filter(user=request.user).order_by('-saved_at')
    serializer = SavedMaterialSerializer(saved, many=True)
    return Response(serializer.data)

