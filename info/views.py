from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import FAQ, ExchangeRule, KYCAMLCheck, CurrencyNews, Contact, Contest
from .serializers import FAQSerializer, ExchangeRuleSerializer, KYCAMLCheckSerializer, CurrencyNewsSerializer, \
    ContactSerializer, ContestSerializer


class CombinedView(APIView):

    def get(self, request, *args, **kwargs):
        lang = self.kwargs.get('lang', 'en')
        response_data = {}

        try:
            # Получение данных FAQ
            faq_queryset = FAQ.objects.filter(language=lang)
            faq_serializer = FAQSerializer(faq_queryset, many=True)
            response_data['faqs'] = faq_serializer.data

            # Получение данных ExchangeRule
            exchange_rule_queryset = ExchangeRule.objects.filter(language=lang)
            exchange_rule_serializer = ExchangeRuleSerializer(exchange_rule_queryset, many=True)
            response_data['exchange_rules'] = exchange_rule_serializer.data

            # Получение данных KYCAMLCheck
            kycaml_check_queryset = KYCAMLCheck.objects.filter(language=lang)
            kycaml_check_serializer = KYCAMLCheckSerializer(kycaml_check_queryset, many=True)
            response_data['kyc_aml_checks'] = kycaml_check_serializer.data

            # Получение данных CurrencyNews
            currency_news_queryset = CurrencyNews.objects.filter(language=lang)
            currency_news_serializer = CurrencyNewsSerializer(currency_news_queryset, many=True)
            response_data['currency_news'] = currency_news_serializer.data

            # Получение данных Contact
            contact_queryset = Contact.objects.all()
            contact_serializer = ContactSerializer(contact_queryset, many=True)
            response_data['contacts'] = contact_serializer.data

            # Получение данных Contest
            contest_queryset = Contest.objects.filter(language=lang)
            contest_serializer = ContestSerializer(contest_queryset, many=True)
            response_data['contests'] = contest_serializer.data

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
