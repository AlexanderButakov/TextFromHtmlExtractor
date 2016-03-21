# -*- coding: utf-8 -*-

import codecs
import math
from collections import defaultdict, Counter

import numpy

from settings import Settings

from text_processor import TextProcessor


class ArticleExtractor(object):
    """
    Класс для подсчета частотностей сигнальных слов в элементах
    и вычисления элемента, содержащего новостную статью.
    """

    def __init__(self, languge):

        self.settings = Settings()

        self.language = languge
        self.text_processor = TextProcessor(self.language)
        self.signalwords = self.settings.signal_words_ru

    def count_freqs(self, stemmed_text):
        """
        Методы считает относительную частотность
        сигнальных слов в тексте.
        Возвращет список кортежей, первым элементов которого
        является слово, вторым его относительная частота.
        """

        stemfreqs = defaultdict(int)

        for stem in stemmed_text:
            stemfreqs[stem] += 1

        total_stems_in_text = float(len(stemmed_text))

        stems = [(word, freq / total_stems_in_text) for word, freq in stemfreqs.iteritems()]

        sorted_freqs = sorted(((term, round(frequency, 3)) for term, frequency in stems),
                              key=lambda w: w[1], reverse=True)

        return sorted_freqs

    def count_signalwords_in_html(self, texts):

        signalwords_to_text = {}

        for raw_element, stemmed_text in texts.iteritems():
            signalwords_count = self.count_freqs(stemmed_text)

            signalwords_to_text[raw_element] = Counter({term[0]: term[1] for term in signalwords_count})

        return signalwords_to_text

    def count_signalwords_in_file(self):

        signalwords = self.signalwords

        signalwords_terms = [term for term in self.text_processor.process_line(signalwords)]

        signalwords_freqs = self.count_freqs(signalwords_terms)

        return Counter({term[0]: term[1] for term in signalwords_freqs})

    @staticmethod
    def cosine_similarity(html_freqdict, signalwords_freqdict):
        """
        Вычисление косинусного коэффициента
        https://en.wikipedia.org/wiki/Cosine_similarity
        """

        terms = set(html_freqdict.keys()).union(set(signalwords_freqdict.keys()))

        doc_vector = [html_freqdict[k] for k in terms]
        signals_vector = [signalwords_freqdict[k] for k in terms]

        doc_vector = numpy.asanyarray(doc_vector, dtype=float)
        signals_vector = numpy.asanyarray(signals_vector, dtype=float)

        dot_product = 0.0
        for v1, v2 in zip(doc_vector, signals_vector):
            dot_product += v1*v2

        magnitude_v1 = math.sqrt(sum(i1**2 for i1 in doc_vector))
        magnitude_v2 = math.sqrt(sum(i2**2 for i2 in signals_vector))

        if magnitude_v2 != 0 and magnitude_v1 != 0:

            return dot_product / (magnitude_v1 * magnitude_v2)
        else:
            return 0.0

    def find_best_node(self, texts_stemmed):
        
        """
        Для каждого элемента вычисляется косинусный коэффициент.
        Элементы сортируются по убыванию значения коэффициента.
        Возвращается ранжированный список кортежей,
        первый элемент которых - текст, второй - его кос. коэфф.
        """

        result_dict = {}

        docs_index = self.count_signalwords_in_html(texts_stemmed)
        signals_freqdict = self.count_signalwords_in_file()

        for tag_element_text, element_terms_dict in docs_index.iteritems():

            cossim = self.cosine_similarity(element_terms_dict, signals_freqdict)
            result_dict[tag_element_text] = cossim

        # mean = sum(result_dict.values()) / len(result_dict)

        relevant_elements = sorted(((text, cos) for text, cos in result_dict.iteritems()),
                                   key=lambda w: w[1], reverse=True)

        return relevant_elements
