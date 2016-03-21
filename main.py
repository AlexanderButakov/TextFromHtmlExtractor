# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import sys
import codecs

from text_processor import TextProcessor
from html_parser import Parser
from article_extractor import ArticleExtractor
from url_handler import UrlHandler
from output_formatter import Formatter

from settings import Settings

reload(sys)
sys.setdefaultencoding('utf-8')


class PageArticle(object):
    """

    """

    def __init__(self):

        self.config = Settings()
        self.language = self.config.language
    
    def get_article(self, url):

        # инициализируем UrlHandler
        urlhandler = UrlHandler()
        # получаем веб-страницу и её кодировку
        source_page, encoding = urlhandler.load_page(url)


        # инициализируем парсер, текстовый процессор, экстрактор
        html_parser = Parser(source_page, encoding)
        text_processor = TextProcessor(self.language)
        article_extractor = ArticleExtractor(self.language)
        formatter = Formatter()

        # получаем списки элементов, очищенных от тегов (raw_cleaned_elements) 
        # и нет (elements_as_string)
        raw_cleaned_elements, elements_as_string = html_parser.get_parsed_nodes()
        # заголовок
        title = html_parser.get_title()

        # получаем спосок лемматизированных текстов
        stemmed_tag_elements = text_processor.iterate_over_texts(raw_cleaned_elements)
        # получаем ранжированный список элементов
        best_nodes = article_extractor.find_best_node(stemmed_tag_elements)

        # для первого элемента из ранжированного списка
        # ищем в цикле нужный элемент с тегами (elements_as_string)
        # передаем найденный элемент в out_formatter
        for text, element in zip(raw_cleaned_elements, elements_as_string):
            if best_nodes[0][0] == text:
                node_to_format = element

        # out_formatter подготавливает текст для сохранения
        clean_text = formatter.format_article(node_to_format)

        # сохраняем в текстовый файл
        with codecs.open('output.txt', 'w', 'utf-8') as out:
            out.write(title+'\n\n')
            for paragraph in clean_text:
                for line in paragraph:
                    out.write(line)
                    out.write('\n')
                out.write('\n')


if __name__ == '__main__':

    url = sys.argv[1]
    
    article = PageArticle()
    article.get_article(url)
