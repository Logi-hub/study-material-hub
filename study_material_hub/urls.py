from django.urls import path
from .views import SignupView,CustomTokenObtainPairView
from .views import study_material_page
from .views import upload_material
from rest_framework_simplejwt.views import TokenRefreshView
from django.http import JsonResponse


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('materials/', study_material_page, name='study_material_page'),
    path('upload/', upload_material, name='upload_material'),
]

def hello(request):
    return JsonResponse({"message":"hello guys, our Api is working"})
urlpatterns=[path('',hello),]
   
