from django.contrib import admin
from .models import FAQ, ExchangeRule, KYCAMLCheck, CurrencyNews, Contact, Contest

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('title', 'language')
    search_fields = ('title', 'text')
    list_filter = ('language',)


@admin.register(ExchangeRule)
class ExchangeRuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'language')
    search_fields = ('title', 'text')
    list_filter = ('language',)


@admin.register(KYCAMLCheck)
class KYCAMLCheckAdmin(admin.ModelAdmin):
    list_display = ('title', 'language')
    search_fields = ('title', 'text')
    list_filter = ('language',)


@admin.register(CurrencyNews)
class CurrencyNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'date')
    search_fields = ('title', 'content')
    list_filter = ('language', 'date')
    date_hierarchy = 'date'


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('email', 'sender', 'timestamp')
    search_fields = ('email', 'sender', 'message')


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'participants', 'prize_amount', 'end_time', 'deadline', 'url')
    search_fields = ('title', 'participation_instructions')
    list_filter = ('language',)
