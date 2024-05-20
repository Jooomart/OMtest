from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .utils import transliterate_text

LANG_CHOICES = (
    ("en", "English"),
    ("ru", "Русский язык")
)

class FAQ(models.Model):
    language = models.CharField(_('Язык'), choices=LANG_CHOICES, default='en', max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, verbose_name=_('Заголовок'))
    text = models.TextField(verbose_name=_('Текст'))

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        target_language = kwargs.pop('target_language', None)
        if target_language and self.language != target_language:
            self.title, self.text = transliterate_text(self.title, self.text, self.language, target_language)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('FAQ')
        verbose_name_plural = _('FAQ')


class ExchangeRule(models.Model):
    language = models.CharField(_('Язык'), choices=LANG_CHOICES, default='en', max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, verbose_name=_('Заголовок'))
    text = models.TextField(verbose_name=_('Текст'))

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        target_language = kwargs.pop('target_language', None)
        if target_language and self.language != target_language:
            self.title, self.text = transliterate_text(self.title, self.text, self.language, target_language)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Правило обмена")
        verbose_name_plural = _("Правила обмена")


class KYCAMLCheck(models.Model):
    language = models.CharField(_('Язык'), choices=LANG_CHOICES, default='en', max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, verbose_name=_('Заголовок'))
    text = models.TextField(verbose_name=_('Текст'))

    def save(self, *args, **kwargs):
        target_language = kwargs.pop('target_language', None)
        if target_language and self.language != target_language:
            self.title, self.text = transliterate_text(self.title, self.text, self.language, target_language)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('KYC/AML Запись')
        verbose_name_plural = _('KYC/AML Записи')


class CurrencyNews(models.Model):
    language = models.CharField(_('Язык'), choices=LANG_CHOICES, default='en', max_length=255, null=True, blank=True)
    title = models.CharField(max_length=100, verbose_name=_('Заголовок'))
    content = models.TextField(verbose_name=_('Содержание'))
    date = models.DateField(auto_now_add=True, verbose_name=_('Дата создания'))
    image = models.ImageField(upload_to='currency_news/', verbose_name=_('Изображение'), blank=True, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        target_language = kwargs.pop('target_language', None)
        if target_language and self.language != target_language:
            self.title, self.content = transliterate_text(self.title, self.content, self.language, target_language)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Новость о валюте')
        verbose_name_plural = _('Новости о валютах')


class Contact(models.Model):
    email = models.EmailField(verbose_name=_('Адрес электронной почты'))
    website = models.URLField(verbose_name=_('Веб-сайт'), blank=True, null=True)
    sender = models.EmailField(verbose_name=_('Отправитель'))
    message = models.TextField(verbose_name=_('Сообщение'))
    timestamp = models.DateTimeField(default=timezone.now, verbose_name=_('Временная метка'))

    class Meta:
        verbose_name = _('Контакт')
        verbose_name_plural = _('Контакты')


class Contest(models.Model):
    language = models.CharField(_('Язык'), choices=LANG_CHOICES, default='en', max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, verbose_name=_('Заголовок'))
    participants = models.IntegerField(default=15, verbose_name=_("Количество участников"))
    prize_amount = models.DecimalField(max_digits=10, decimal_places=2, default=1300, verbose_name=_("Банк конкурса"))
    end_time = models.DateTimeField(verbose_name=_("Время окончания"))
    deadline = models.DateTimeField(verbose_name=_("Срок завершения"), null=True, blank=True)
    participation_instructions = models.TextField(
        default=_("\n1. Совершить обмен на нашем сервисе onemoment.cc\n2. Подписаться на телеграмм канал @onemomentinfo\n3. Написать отзыв на bestchange.ru в день совершения обмена\n4. Убедиться в том, что номер обмена и email в отзыве совпадают с email, который указывался в заявке на обмен\n5. Проверить результаты розыгрыша в пятницу 18:00 в нашем телеграм канале @onemomentinfo"),
        verbose_name=_("Инструкции по участию")
    )
    url = models.URLField(verbose_name=_("URL"), null=True, blank=True)

    def save(self, *args, **kwargs):
        self.participants += 1
        self.prize_amount = self.participants * 100

        if not self.deadline:
            self.deadline = self.end_time

        target_language = kwargs.pop('target_language', None)
        if target_language and self.language != target_language:
            self.title, self.participation_instructions = transliterate_text(self.title, self.participation_instructions, self.language, target_language)

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Конкурс")
        verbose_name_plural = _("Конкурсы")
