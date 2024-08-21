# Открываем файл для чтения
curse_words = []
with open('ru_curse_words.txt', 'r', encoding='utf-8') as file:
    curse_words = [line.strip() for line in file]

BAD_WORDS = curse_words