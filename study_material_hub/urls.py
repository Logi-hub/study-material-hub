from django.urls import path
from .views import SignupView
from .views import study_material_page
from .views import upload_material


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('materials/', study_material_page, name='study_material_page'),
    path('upload/', upload_material, name='upload_material'),
]


   
