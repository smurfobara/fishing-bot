import re
from words  import BAD_WORDS
from itertools import product
def check_text(text, BAD_WORDS = BAD_WORDS, user = '0'):
    char_map = {
        'а': ['а', 'a', '@'],
        'б': ['б', '6', 'b'],
        'в': ['в', 'b', 'v'],
        'г': ['г', 'r', 'g'],
        'д': ['д', 'd', 'g'],
        'е': ['е', 'e'],
        'ё': ['ё', 'e'],
        'ж': ['ж', 'zh', '*'],
        'з': ['з', '3', 'z'],
        'и': ['и', 'u', 'i'],
        'й': ['й', 'u', 'i'],
        'к': ['к', 'k', 'i{', '|{'],
        'л': ['л', 'l', 'ji'],
        'м': ['м', 'm'],
        'н': ['н', 'h', 'n'],
        'о': ['о', 'o', '0'],
        'п': ['п', 'n', 'p'],
        'р': ['р', 'r', 'p'],
        'с': ['с', 'c', 's'],
        'т': ['т', 'm', 't'],
        'у': ['у', 'y', 'u'],
        'ф': ['ф', 'f'],
        'х': ['х', 'x', 'h', '}{'],
        'ц': ['ц', 'c', 'u,'],
        'ч': ['ч', 'ch'],
        'ш': ['ш', 'sh'],
        'щ': ['щ', 'sch'],
        'ь': ['ь', 'b'],
        'ы': ['ы', 'bi'],
        'ъ': ['ъ'],
        'э': ['э', 'e'],
        'ю': ['ю', 'io'],
        'я': ['я', 'ya']
    }

    # Проверка на наличие запрещенных слов
    def contains_bad_word(text, bad_words, char_map):
        for word in bad_words:
            translated_texts = [''.join(variant) for variant in product(*(char_map.get(char, [char]) for char in word))]
            for translated_text in translated_texts:
                if translated_text in text:
                    return True
        return False

    # Проверка на наличие URL
    def contains_url(user):
        url_pattern = re.compile(r'(https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+|\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}\b)')
        urls = re.findall(url_pattern, text)
        return bool(urls)

    # Приведение текста к нижнему регистру для проверки
    text_lower = text.lower()

    has_bad_words = contains_bad_word(text_lower, BAD_WORDS, char_map)
    has_url = contains_url(text_lower)

    # Возвращение результата в зависимости от найденных данных
    if has_bad_words and has_url:
        return 3  # Есть и запрещенные слова, и ссылки
    elif has_bad_words:
        return 1  # Есть запрещенные слова
    elif has_url:
        return 2  # Есть ссылки
    else:
        return 0  # Нет ни запрещенных слов, ни ссылок



