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
            raise serializers.ValidationError("Пароли не совпадают!")

        return User.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        error_messages={"required": "Это поле обязательно."}
    )

    def validate(self, attrs):
        return super().validate(attrs)


class ResetPasswordVerifySerializer(serializers.Serializer):
    new_password = serializers.CharField(
        required=True,
        error_messages={"required": "Это поле обязательно."}  # Обновлено сообщение об ошибке на русский
    )
    email = serializers.CharField(
        required=True,
        error_messages={"required": "Это поле обязательно."}  # Обновлено сообщение об ошибке на русский
    )
