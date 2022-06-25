import datetime

from django.core.exceptions import ValidationError


def validate_year(value):
    if value > datetime.datetime.now().year and value < 0:
        raise ValidationError(
            'Вы ввели некорректный год.'
            'Год создания произведения не может быть больше текущего'
            'и меньше начала нашей эры.'
        )
