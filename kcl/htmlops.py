#!/usr/bin/env python3

import sys
import os
from urllib.parse import urlparse
import urllib.request
import lxml.html
import re
from bs4 import BeautifulSoup
from kcl.fileops import read_file_bytes_or_exit
from kcl.printops import cprint

def soup(content):
    soup = BeautifulSoup(content, 'lxml')
    return soup

def get_title_from_dom_tree(dom_tree):
    return dom_tree.find(".//title").text

def parse_html_to_dom(html):
    dom_tree = lxml.html.fromstring(html)
    return dom_tree

def extract_urls_lxml(html, url):
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
                    current_url = link.attrib['href']
                    if current_url != 'http://' and current_url != 'https://':
                        url_list.append(link.attrib['href'])
                except:
                    pass
        except:
            pass
    return set(url_list)

def extract_urls_lxml_nofollow(html, url):
    url_list=[]
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

def extract_iris_from_text(text):   #todo, buggy, already had to add the ~ below
    text_list=text.split("\n")
    clean_text = filter(None, text_list)
    url_list=[]
    for line in clean_text:
        for word in line.split(' '):
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[~$-_@.&+#]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', word)
            for url in urls:
                url_list.append(url)
    url_set=set(url_list)
    return url_set

if __name__ == '__main__':
    try:
        domain = sys.argv[1]
    except:
        print("a domain is reqired. exiting.")
        os._exit(1)
    with open('/dev/stdin', 'r') as f:
        html = f.read()
    for url in  extract_urls_lxml(html, domain):
        cprint(url)

