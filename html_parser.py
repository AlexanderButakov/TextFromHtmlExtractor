# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import re
import sys
import StringIO

from lxml import etree
from HTMLParser import HTMLParser


reload(sys)
sys.setdefaultencoding('utf-8')


class Parser(object):

    # регулярка для удаления тегов
    HTML_TAG_REGEX = re.compile(r'<[^<]+>')

    # регулярка для удаления узлов дерева, у которых классы или id называются следующими смловами
    NAMES_TO_DELETE = (
            "-feed|newsfeed|topics|topic-addition|headlines|similar|topic-addition|read_more"
            "|[Pp]opular|slick-track|^side$|combx|retweet|menucontainer|navbar|storytopbar-bucket|utility-bar"
            "|inline-share-tools|legende|breadcrumb|timestamp|js_replies|read-more|contact|foot|footer|Footer"
            "|footnote|links|meta$|other-materials|shoutbox|sponsor|top-news|tags|socialnetworking|socialNetworking"
            "|^inset$|pagetools|tabloid|socials|social-|post-attributes|communitypromo|runaroundLeft|subscribe"
            "|vcard|articleheadings|print$|popup|author-dropdown|tools|socialtools|byline|read_also|incut|bottom"
            "|^sidebar$|stream-news|widget|-prev|-next|slidenote|notification|baner|banner|aside|slick-slider|wgt"
            "|[Dd]igest|external|news-grid|latest|related|navigation|anchor|newsline|anonse|^warn|disclaim|^respond"
        )

    # регулярка для удаления узлов
    TAG_TO_REMOVE = '//script | //style | //nav | //footer | //noindex | //aside | //noscript'
    CLASSES_TO_REMOVE = "//*[re:test(@class, '%s', 'i')]" % NAMES_TO_DELETE
    IDS_TO_REMOVE = "//*[re:test(@id, '%s', 'i')]" % NAMES_TO_DELETE

    TAGS_TO_REMOVE = TAG_TO_REMOVE + ' | ' + CLASSES_TO_REMOVE + ' | ' + IDS_TO_REMOVE

    def __init__(self, page_source, encoding):

        self.page_source = page_source
        self.encoding = encoding

        # инициализируем парсер с опцией "удалять комментарии"
        hparser = etree.HTMLParser(remove_comments=True, encoding=self.encoding)
        self.htree = etree.parse(StringIO.StringIO(self.page_source), hparser)

    def get_body(self):
        """получаем узел body"""

        root = self.htree.getroot()
        body = root.find('body')

        return body

    def remove_unrelated(self, body):
        """удаляем ненужные узлы"""

        for s in body.xpath(self.TAGS_TO_REMOVE, namespaces={"re": "http://exslt.org/regular-expressions"}):
            s.getparent().remove(s)

        return body

    def get_paragraphs(self, body):
        
        """
        составляем список параграфов, 
        в которых содержится текст.
        Возвращается список.
        """

        text_nodes = []
        for tag in ['p', 'pre', 'blockquote', 'q', 'code', 'cite', 'dfn']:
            tag_name = 'descendant-or-self::%s' % (tag or '*')
            elements = body.xpath(tag_name, namespaces={"re": "http://exslt.org/regular-expressions"})
            text_nodes += elements

        return text_nodes

    def get_parents(self, paragraphs):
        
        """
        Находим родителей для параграфов.
        Возвращается список.
        """

        # находим родителей этих параграфов
        parents = []
        for paragraph in paragraphs:
            paragraph_parent = paragraph.getparent()
            if paragraph_parent not in parents and paragraph_parent not in paragraphs:
                parents.append(paragraph_parent)

        return parents

    def convert_to_string(self, elements):
        """
        Переводим родителей в строку.
        Возвращается список юникодных строк.
        """
        
        elements_to_string = []
        for node in elements:
            elements_to_string.append(etree.tostring(node, encoding='utf8'))

        return elements_to_string

    def get_title(self):
        """Находим заголовок"""

        title = self.htree.find(".//title").text.strip()

        return title

    def get_parsed_nodes(self):
        """
        Метод для внешнего вызова.
        Исполняет все вышезаданные методы
        и возвращает узлы с параграфами в двух версиях:
        
        raw_cleaned_elements - список грубо очищенных от тегов строк (для обработки)
        
        elements_as_string - список строк с html-тегами 
        для отправки на форматирование в out_formatter
        """

        body = self.get_body()
        cleaned_body = self.remove_unrelated(body)
        paragraphs = self.get_paragraphs(cleaned_body)
        parents = self.get_parents(paragraphs)

        elements_as_string = self.convert_to_string(parents)

        raw_cleaned_elements = [HTMLParser().unescape(self.HTML_TAG_REGEX.sub(' ', elem)) for elem in elements_as_string]

        return raw_cleaned_elements, elements_as_string
