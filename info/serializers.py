from rest_framework import serializers
from .models import FAQ, ExchangeRule, KYCAMLCheck, CurrencyNews, Contact, Contest
from googletrans import Translator

translator = Translator()


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'


class ExchangeRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRule
        fields = '__all__'


class KYCAMLCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCAMLCheck
        fields = '__all__'


class CurrencyNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyNews
        fields = '__all__'


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'


class ContestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        fields = '__all__'

    def validate_participants(self, value):
        if value < 0:
            raise serializers.ValidationError("Participants must be a positive integer.")
        return value

    def validate_prize_amount(self, value):
        try:
            prize_amount = float(value)
        except ValueError:
            raise serializers.ValidationError("Prize amount must be a valid number.")
        return prize_amount
