from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.db import IntegrityError
from rest_framework.generics import GenericAPIView
from django.conf import settings
from rest_framework import generics, status
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import User
from .serializers import UserSerializer, UserLoginSerializer, ResetPasswordSerializer, ResetPasswordVerifySerializer, \
    UserProfileSerializer, LogoutSerializer
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str


class RegistrationAPIView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')

        if not all([email, password, confirm_password]):
            return Response({'message': 'Заполните все поля'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            User.objects.get(email=email)
            return Response({'message': 'Пользователь с таким email уже существует'},
                            status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            pass

        if password != confirm_password:
            return Response({'message': 'Пароли не совпадают'}, status=status.HTTP_400_BAD_REQUEST)

        if len(password) < 8:
            return Response({'message': 'Пароль должен содержать не менее 8 символов'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as err:
            return Response({'message': err.detail}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = serializer.save()
            subject = 'Активация аккаунта'
            message = f'Здравствуйте, {user.email}!\n\nПоздравляем Вас с успешной регистрацией на сайте {settings.BASE_URL}\n\nВаш пароль: {user.password}\n\n{settings.BASE_URL}\n\nС наилучшими пожеланиями,\nКоманда {settings.BASE_URL}\n\nДля активации вашего аккаунта перейдите по ссылке: {settings.BASE_URL}'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user.email]

            send_mail(subject, message, from_email, recipient_list)
            login(request, user)

            return Response({'response': True,
                             'message': 'Пользователь успешно зарегистрирован. Проверьте вашу электронную почту для получения инструкций по активации.',
                             'homepage_url': '/'}, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response({'message': 'Произошла ошибка при регистрации пользователя'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if request.user.is_authenticated:
            token, created = Token.objects.get_or_create(user=request.user)
            return Response({'token': token.key, "response": True}, status=status.HTTP_200_OK)
        else:
            serializer = UserLoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)

            if user:
                token, created = Token.objects.get_or_create(user=user)
                return Response({'token': token.key, "response": True}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Неверные учетные данные', "response": False},
                                status=status.HTTP_401_UNAUTHORIZED)



class ResetPasswordView(GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_link = f"http://127.0.0.1:8000/reset-password/verify/{uid}/{token}/"

                message = render_to_string('password_reset_email.html', {
                    'user': user,
                    'reset_link': reset_link,
                })

                send_mail(
                    _('Восстановление пароля'),
                    '',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=message,
                    fail_silently=False,
                )

                return Response({"response": True, "message": _("Инструкции по восстановлению пароля отправлены на ваш email.")})
            except User.DoesNotExist:
                return Response({"response": False, "message": _("Пользователь с таким email не существует.")})
        return Response(
            {"response": False, "message": _("Пожалуйста, исправьте следующие ошибки валидации и попробуйте снова.")}
        )


class ResetPasswordVerifyView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordVerifySerializer

    def post(self, request, uid, token):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            new_password = serializer.validated_data.get("new_password")

            try:
                uid = force_str(urlsafe_base64_decode(uid))
                user = User.objects.get(pk=uid)
                if not default_token_generator.check_token(user, token):
                    return Response({'response': False, 'message': 'Неверный или истекший токен.'},
                                    status=status.HTTP_400_BAD_REQUEST)

                user.set_password(new_password)
                user.save()

                return Response({'response': True, 'message': 'Пароль успешно изменен.'}, status=status.HTTP_200_OK)

            except User.DoesNotExist:
                return Response({'response': False, 'message': 'Пользователь не найден.'},
                                status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'response': False, 'message': f'Ошибка при сбросе пароля: {e}'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'response': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response_data = {
            'email': serializer.data['email']
        }
        return Response(response_data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    serializer_class = LogoutSerializer

    def post(self, request):
        logout(request)
        return Response({'message': 'Вы успешно вышли из системы.'})
