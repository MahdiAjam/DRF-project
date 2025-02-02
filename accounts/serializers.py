from rest_framework import serializers
from .models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        del validated_data['password2']
        return User.objects.create_user(**validated_data)

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'default': 'password must be match'})
        return data

    def validate_email(self, value):
        if 'admin' in value:
            raise serializers.ValidationError('admin can not be in email')
        return value

    def validate_username(self, value):
        if 'admin' in value:
            raise serializers.ValidationError('admin can not be in username')
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
