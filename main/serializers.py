from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        confirm_password = validated_data.pop('confirm_password', None)
        if confirm_password != validated_data['password']:
            raise serializers.ValidationError("Пароли не совпадают")

        return User.objects.create_user(email=validated_data['email'], password=validated_data['password'])


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        error_messages={"required": "Это поле обязательно."}
    )


class ResetPasswordVerifySerializer(serializers.Serializer):
    new_password = serializers.CharField(
        required=True,
        min_length=8,
        error_messages={
            "required": "Это поле обязательно.",
            "min_length": "Пароль должен содержать минимум 8 символов."
        }
    )
    confirm_password = serializers.CharField(
        required=True,
        error_messages={"required": "Это поле обязательно."}
    )

    def validate(self, data):
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if new_password != confirm_password:
            raise serializers.ValidationError("Пароли не совпадают.")

        return data


class LogoutSerializer(serializers.Serializer):
    pass
