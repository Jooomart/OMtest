from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.db import IntegrityError
from rest_framework.generics import GenericAPIView
from django.conf import settings
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
import random
from .models import User
from .serializers import UserSerializer, UserLoginSerializer, ResetPasswordSerializer, ResetPasswordVerifySerializer


class RegistrationAPIView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            confirm_password = serializer.validated_data.get('confirm_password')

            if password != confirm_password:
                return Response({'error': 'Пароли не совпадают'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = serializer.save()

                # Добавлен код для отправки электронной почты только после успешного сохранения пользователя
                subject = 'Активация аккаунта'
                message = f'Здравствуйте, {email}!\n\nПоздравляем Вас с успешной регистрацией на сайте {settings.BASE_URL}\n\nВаш пароль: {password}\n\n  {settings.BASE_URL} Активация аккаунта \n\nС наилучшими пожеланиями,\nКоманда {settings.BASE_URL}\n\nДля активации вашего аккаунта перейдите по ссылке: {settings.BASE_URL}'
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [user.email]

                send_mail(subject, message, from_email, recipient_list)

                login(request, user)

                return Response({'response': True,
                                 'message': 'Пользователь успешно зарегистрирован. Проверьте вашу электронную почту для получения инструкций по активации.',
                                 'homepage_url': '/'}, status=status.HTTP_201_CREATED)

            except IntegrityError:
                return Response({'error': 'Произошла ошибка при регистрации пользователя'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # Обработка ошибки валидации сериализатора
            raise ValidationError(serializer.errors)


class UserLoginView(generics.CreateAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
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
                new_password = int(random.randint(1000, 9999))
                user.set_password(new_password)
                user.save()

                # Форматирование HTML-сообщения с ссылкой для сброса пароля
                message = _('''
                    <html>
                    <body>
                    <p>Здравствуйте, {}!</p>
                    <p>Для восстановления пароля перейдите по <a href="http://127.0.0.1:8000/auth/reset-password/verify/"> 
                    \nВосстановить пароль</a>.</p>
                    <p>Если у вас возникли вопросы, обратитесь в службу поддержки на нашем сайте или напишите на почту onemoment.cc@gmail.com</p>
                    </body>
                    </html>
                '''.format(email))

                send_mail(
                    _('Восстановление пароля'),
                    '',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=message,
                    fail_silently=False,
                )

                return Response({"response": True, "message": _(
                    "Пароль сброшен. Инструкции по восстановлению пароля отправлены на ваш email.")})
            except User.DoesNotExist:
                return Response({"response": False, "message": _("Пользователь с таким email не существует.")})
        return Response(
            {"response": False, "message": _("Пожалуйста, исправьте следующие ошибки валидации и попробуйте снова.")})


class ResetPasswordVerifyView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordVerifySerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            new_password = serializer.validated_data.get("new_password")

            try:
                user = User.objects.get(email=email)
                previous_password = user.password

                if previous_password == new_password:
                    return Response({'response': False, 'message': 'Новый пароль не должен совпадать с предыдущим.'},
                                    status=status.HTTP_400_BAD_REQUEST)

                user.set_password(new_password)
                user.save()

                return Response({'response': True, 'message': 'Пароль успешно изменен.'},
                                status=status.HTTP_200_OK)

            except User.DoesNotExist:
                return Response({'response': False, 'message': 'Пользователь с указанным email не найден.'},
                                status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                print(f"Ошибка при сбросе пароля: {e}")
                return Response({'response': False, 'message': f'Ошибка при сбросе пароля: {e}'},
                                status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'response': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
