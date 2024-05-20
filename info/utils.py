from django.utils import timezone
from transliterate import translit


def time_remaining(contest):
    if contest.end_time:
        remaining = contest.end_time - timezone.now()
        days = remaining.days
        hours, remainder = divmod(remaining.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return days, hours, minutes, seconds
    else:
        return 0, 0, 0, 0


def transliterate_text(title, text, from_lang, to_lang):
    translated_title = translit(title, from_lang, reversed=(to_lang == 'en'))
    translated_text = translit(text, from_lang, reversed=(to_lang == 'en'))
    return translated_title, translated_text
