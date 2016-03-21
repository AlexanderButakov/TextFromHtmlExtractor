# -*- coding: utf-8 -*-

import urllib2


class UrlHandler(object):

    """
    Класс для обработки url.

    Метод load_page загружает веб-страницу
    и возвращает её как строку + её кодировку,
    которая нужна для парсера.
    """

    def check_url(self):
        pass

    def load_page(self, url):

        page = urllib2.urlopen(url)
        encoding = page.headers.getparam('charset')

        return page.read(), encoding
