#!/usr/bin/env python3

# /mnt/t420s_256GB_samsung_ssd_S2R5NX0J707260P/.iridb/database.local/data_index/8/9/6/89689beecc6ebf06cb1859b8085ec9154e7edb1b

#import nltk
from bs4 import BeautifulSoup

import lxml.html
from lxml.etree import ParserError
import re
from bs4 import BeautifulSoup
from kcl.printops import eprint
from kcl.printops import ceprint
from kcl.command import run_command


def soup(html):
    soup = BeautifulSoup(html, 'lxml')
    return soup


def soup_from_file(file_name):
    with open(file_name, 'r') as fh:
        file_soup = soup(fh.read())
    return file_soup


def get_title_from_dom_tree(dom_tree):
    return dom_tree.find(".//title").text


def parse_html_to_dom(html):
    dom_tree = lxml.html.fromstring(html)
    return dom_tree


#this one is used for internal links plugin
def extract_urls_lxml_with_link_text(html_file, url):
    with open(html_file, 'rb') as fh:
        html_bytes = fh.read()
    html = html_bytes.decode('utf8', 'ignore')
    url_list = []
    #try:
    dom = lxml.html.fromstring(html)
    #except ParserError:
    #    return set([])

    dom.make_links_absolute(url)
    links_a = dom.cssselect('a')
    for link in links_a:
        try:
            url_list.append((link.attrib['href'], link.text))
        except KeyError:
            pass
    links_img = dom.cssselect('img')
    for link in links_img:
        try:
            url_list.append((link.attrib['src'], link.text))
        except KeyError:
            pass
    filtered_url_list = []
    for url in url_list:
        #ceprint(url)
        if url[0].startswith("javascript:"):
            continue
        filtered_url_list.append(url)
    return set(filtered_url_list)


def extract_urls_lxml(html_file, url):
    #with open(html_file, 'rb') as fh:
    #    html_bytes = fh.read()
    #html = html_bytes.decode('utf8', 'ignore')
    url_only_list = []
    url_list = extract_urls_lxml_with_link_text(html_file=html_file, url=url)
    for item in url_list:
        url_only_list.append(item[0])
    return set(url_only_list)


def extract_urls_lxml_nofollow(html_file, url):
    with open(html_file, 'rb') as fh:
        html_bytes = fh.read()
    html = html_bytes.decode('utf8', 'ignore')
    url_list = []
    dom = lxml.html.fromstring(html)
    dom.make_links_absolute(url)
    links = dom.cssselect('a')
    for link in links:
        try:
            if link.attrib['href'].startswith("javascript"):
                pass
            else:
                try:
                    if link.attrib['rel'] == 'nofollow':
                        current_url = link.attrib['href']
                        if current_url != 'http://' and current_url != 'https://':
                            url_list.append(link.attrib['href'])
                except:
                    pass
        except:
            pass
    return url_list


# todo: https://raw.githubusercontent.com/oakkitten/scripts/url_hint/python/url_hint.py
def extract_iris_from_text(text):  # todo, buggy, already had to add the ~ below
    if isinstance(text, bytes):
        text = text.decode('utf8', 'ignore')
    assert isinstance(text, str)
    text_list = text.split("\n")
    clean_text = filter(None, text_list)
    url_list = []
    for line in clean_text:
        for word in line.split(' '):
            #urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[~$-_@.&+#]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', word)
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[~$\-/_@.&+#]|[!*,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', word)
            for url in urls:
                url_list.append(url)
    url_set = set(url_list)
    return url_set


def extract_iris_from_text_file(infile):
    with open(infile, 'r') as fh:
        text = fh.read()
    url_set = extract_iris_from_text(text)
    return url_set


def convert_html_file_to_text(html_file):
    with open(html_file, 'rb') as fh:
        html_bytes = fh.read()
    html = html_bytes.decode('utf8', 'ignore')
    soup = BeautifulSoup(html, 'lxml')
    text = soup.get_text()
    #text = nltk.clean_html(html)
    ceprint(len(text))
    ceprint(text)
    return text


def extract_iris_from_html_file(html_file):
    #text = run_command(b' '.join([b'/home/cfg/html/html2text', html_file]), verbose=True)
    text = convert_html_file_to_text(html_file)
    url_set = extract_iris_from_text(text)
    return url_set

