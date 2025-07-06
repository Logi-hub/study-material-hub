from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import StudyMaterial
from .models import UploaderProfile
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'confirm_password', 'role', 'is_authorized_uploader']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user




class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['is_authorized_uploader'] = user.is_authorized_uploader
        token['role']='Uploader' if user.is_authorized_uploader else 'Reader'
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        data['username'] = self.user.username
        data['role'] = 'Uploader' if self.user.is_authorized_uploader else 'Reader'
        data['id'] = self.user.id 
        return data


class StudyMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyMaterial
        fields = '__all__'
        read_only_fields=['uploaded_by','uploaded_at','verification_code','id']



class UploaderProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=False)
    email = serializers.EmailField(source='user.email', read_only=False)

    class Meta:
        model = UploaderProfile 
        fields = ['username', 'email', 'phone', 'designation', 'institution', 'place','upload_code']

    def update(self, instance, validated_data):
        
        user_data = validated_data.pop('user', {})
        
       
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)

        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

       
        instance.user.save()
        instance.save()
        return instance
    

from rest_framework import serializers
from .models import SavedMaterial, StudyMaterial

class StudyMaterialSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField()
    uploaded_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    is_saved=serializers.SerializerMethodField()

    class Meta:
        model = StudyMaterial
        fields = ['id', 'title', 'subject', 'uploaded_by', 'uploaded_at','is_saved']

    def get_is_saved(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        if user and user.is_authenticated:
            return obj.savedmaterial_set.filter(user=user).exists()
        return False

class SavedMaterialSerializer(serializers.ModelSerializer):
    material = StudyMaterialSerializer(read_only=True)

    class Meta:
        model = SavedMaterial
        fields = ['id', 'material', 'saved_at']



class UploadMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyMaterial
        fields = ['title', 'subject', 'file', 'verification_code']
