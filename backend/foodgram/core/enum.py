from enum import IntEnum, Enum


class Regex(Enum):
    """Regex для проверки имени."""
    RU_REGEX = r'^[А-ЯЁ][а-яё]+$'


class Message(Enum):
    """Сообщения для ошибки в валидации."""
    TAG_NAME_MESSAGE = ('Название должно начинаться с заглавной буквы '
                        'и только буквы русского алфавита')
    MIN_COOKING_TIME_MESSAGE = 'Время приготовление должно быть >= 1'
    MIN_AMOUNT_MESSAGE = 'Количество ингридиента должно быть >= 1'


class MinLimit(IntEnum):
    """Минимальные значения."""
    MIN_COOKING_TIME = 1
    MIN_AMOUNT = 1
