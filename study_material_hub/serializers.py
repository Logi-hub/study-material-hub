from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        role = validated_data.pop('role', 'student') # default role if not provided
        user = User(**validated_data)
        user.set_password(password)
        user.role = role
        user.save()
        return user
