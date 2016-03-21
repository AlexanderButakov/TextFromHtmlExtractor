# -*- coding: utf-8 -*-

__title__ = 'TextFromHTMLExtractor'
__author__ = 'Alexander Butakov'

import codecs

class Settings(object):
    """
    Настройки для программы.
    Можно задать язык, указать пути до файлов стоп-слов 
    и сигнальных слов.
    """

    language = 'ru'

    @property
    def stop_words_ru(self):

        with codecs.open(r".\resources\stopwords_ru.txt", 'r', 'utf-8') as stopwords_file:
            return set(stopwords_file.read().split('\n'))

    @property
    def signal_words_ru(self):

        with codecs.open(r".\resources\signalwords.txt", 'r', 'utf-8') as infile:
            return infile.read()