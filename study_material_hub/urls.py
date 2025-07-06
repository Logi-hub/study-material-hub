from django.urls import path
from .views import SignupView,CustomTokenObtainPairView
from .views import upload_material
from rest_framework_simplejwt.views import TokenRefreshView
from django.http import JsonResponse
from .views import register_uploader
from .views import list_materials,preview_material,download_material
from .views import send_email_otp, reset_password
from .views import uploader_profile
from .views import my_uploads
from .views import material_detail
from .views import send_otp
from .views import verify_otp
from .views import save_material,saved_materials,unsave_material



from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

def hello(request):
    return JsonResponse({"message":"hello guys, our Api is working"})

urlpatterns = [
    path('',hello,name='api_home'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('materials/upload/', upload_material, name='upload_material'),
    path('register-uploader/', register_uploader, name='register_uploader'),
    path('materials/list/', list_materials, name='list_materials'),
    path('materials/preview/<int:pk>/', preview_material),
    path('materials/download/<int:pk>/', download_material),
    path('forgot-password/email/', send_email_otp),
    path('reset-password/', reset_password),
    path('uploader-profile/', uploader_profile),
    path('materials/my-uploads/',my_uploads, name='my-uploads'),
    path('materials/<int:pk>/',material_detail, name='material-detail'),
    path('send-otp/',send_otp),
    path('verify-otp/',verify_otp),
    path('save-material/<int:material_id>/', save_material),
    path('unsave-material/<int:material_id>/', unsave_material),
    path('saved-materials/', saved_materials),

]
    



   
