# -*- coding: utf-8 -8_

from __future__ import print_function
from __future__ import unicode_literals

import sys
import re
import pymorphy2

from settings import Settings

reload(sys)
sys.setdefaultencoding('utf-8')

class TextProcessor(object):
    """
    Класс для обработки текста.

    """

    def __init__(self, language):

        self.language = language
        self.settings = Settings()

        # знаки, которые будут удаляться в начале и конце токена
        self.punctuation = "∙!‼¡\"#£€$¥%&'()*+±×÷·,-./:;<=>?¿@[\]^ˆ¨_`—–­{|}~≈≠→↓¬’“”«" \
                           "»≫‘…¦›🌼′″¹§¼⅜½¾⅘©✒•►●★❤➡➜➚➘➔✔➓➒➑➐➏➎➍➌➋➊❸❷■†✝✌￼️³‎²‚„ ​"

        # для разбивки на токены по пробелам и прочим символам
        self.splitchars = re.compile(r'[\s\\\/\(\)\[\]\<\>\;\:\,\‚\—\?\!\|\"…#=]|\.\.\.+|\-\-|\.[\'\"’“”‘′″„-]')

        if self.language == 'ru':
            # self.stopwords = resource_loader.load_stop_words_ru()
            self.stopwords = self.settings.stop_words_ru
            self.lemmatizer_ru = pymorphy2.MorphAnalyzer()

    @staticmethod
    def normalize_e(word):

        """ Преобразуем русскую 'ё' --> 'е' """

        if 'ё' in word:
            word = word.replace('ё', 'е')

        return word

    def process_line(self, line):
        """
        Метод обрабатывает строку текста,
        разбивает её на слова по регулярному выражению,
        слова лемматизирует.
        Возвращает генератор лемматизированных слов
        """

        if self.language == 'ru':
            tokens = (self.normalize_e(token.strip(self.punctuation).lower()) for token in self.splitchars.split(line))

            rslt_list = (self.lemmatizer_ru.parse(term)[0].normal_form for term in tokens if term in self.stopwords and len(term) > 0)

        return rslt_list

    def process_text(self, text):
        """
        Принимает на вход целый текст,
        отдает построчно на обработку process_line
        """

        terms_list = []

        for term in self.process_line(text):
            terms_list.append(term)

        return terms_list

    def iterate_over_texts(self, texts_set):
        """
        Метод проходит по всем текстам 
        и вызывает для каждого process_text.
        Возвращает словарь, в котором
        ключ - это текст,
        значение - список его лемматизированных слов
        """

        texts_stemmed = {}

        for text in texts_set:

            text_stemmed = self.process_text(text)

            if len(text_stemmed) > 0:

                texts_stemmed[text] = text_stemmed

        return texts_stemmed
