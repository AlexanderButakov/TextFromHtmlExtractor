# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import sys
import re
import StringIO

from lxml import etree
from HTMLParser import HTMLParser


reload(sys)
sys.setdefaultencoding('utf-8')


class Formatter(object):

	HTML_TAG_REGEX = re.compile(r'<[^<]+>')

	ADD_EMPTY_LINE = re.compile(r'</p>|</h[1-6]>|<br/>|</br>')

	def find_hrefs(self, node):
		"""
		находим теги с ссылками.
		возвращаем словарь:
		ключ: первая часть тега <a> (без </a>)
		значение: содержимое href
		"""
		
		node_parser = etree.HTMLParser(encoding='utf-8')
		node_tree = etree.parse(StringIO.StringIO(node), node_parser)

		links = node_tree.xpath("//a")
		hrefs = {}
		for link in links:
			link_to_str = etree.tostring(link, encoding='utf8')
			a_without_closing_tag = link_to_str[:link_to_str.find('>')+1]
			hrefs[a_without_closing_tag] = link.get("href")

		return hrefs

	def convert_links(self, node, links):
		"""обрамляем ссылки [], удалем <a>"""

		links = self.find_hrefs(node)
		link_to_replace = "[{}] "

		if links:
			regexp_replace = re.compile('|'.join([re.escape(key) for key in links.keys()]))
		
			new_node = regexp_replace.sub(lambda l: link_to_replace.format(links[l.group(0)]), node)

			return new_node
		else:
			return node


	def convert_p(self, node):
		"""
		закрывающий тег </p> заменяем на 
		два знака переноса строки
		"""
		
		new_node = self.ADD_EMPTY_LINE.sub('\n\n', node)

		return new_node

	def delete_tags(self, node):
		"""
		удаляем все остальные теги
		"""

		return HTMLParser().unescape(self.HTML_TAG_REGEX.sub('', node))

	def adjust_string_width(self, text):

		""" разбиваем строки на длину 80 символов"""

		paragraphs = re.split(r'\n\n', text)

		text_80 = []
		for paragraph in paragraphs:

			splitted_text = paragraph.split(' ')

			lines_80 = []
			line = []
			
			for word in splitted_text:
				if len(word) > 0:
					if word != splitted_text[-1]:
						if len(' '.join(line))+len(word)+1 < 80:
							line.append(word)
						else:
							lines_80.append(' '.join(line).strip())
							line = [word]

					else:
						line.append(word)
						lines_80.append(' '.join(line).strip())

			text_80.append(lines_80)

		return text_80


	def format_article(self, node):
		"""
		Внешний метод.
		Реализует все методы выше
		и отдает отформатированный текст.
		"""

		links = self.find_hrefs(node)
		node_converted_links = self.convert_links(node, links)
		node_converted_p = self.convert_p(node_converted_links)
		clean_text = self.delete_tags(node_converted_p)
		# clean_from_empty = self.clear_empty_newlines_tabs(clean_text)
		text_80 = self.adjust_string_width(clean_text)

		return text_80
