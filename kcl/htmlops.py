#!/usr/bin/env python3

import sys
import os
from urllib.parse import urlparse
import urllib.request
import lxml.html
import re
from bs4 import BeautifulSoup
from kcl.fileops import read_file_bytes_or_exit
from kcl.printops import eprint
import click
import shutil

# https://github.com/mitsuhiko/click/issues/441
CONTEXT_SETTINGS = \
    dict(help_option_names=['--help'],
         terminal_width=shutil.get_terminal_size((80, 20)).columns)

# pylint: disable=C0326
# http://pylint-messages.wikidot.com/messages:c0326
@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--verbose', is_flag=True, callback=set_verbose, expose_value=False)
# pylint: enable=C0326
@click.pass_context
def htmlops(ctx):
    '''
       various html related functions
    '''
    pass


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

@htmlops.command()
@click.argument('text', required=False)
def extract_iris_from_text(text=False):   #todo, buggy, already had to add the ~ below
    if not text:
        with open('/dev/stdin', 'r') as fh:
            text = fh.read()
    text_list = text.split("\n")
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
    htmlops()
    #try:
    #    domain = sys.argv[1]
    #except:
    #    print("a domain is reqired. exiting.")
    #    os._exit(1)
    #with open('/dev/stdin', 'r') as f:
    #    html = f.read()
    #for url in  extract_urls_lxml(html, domain):
    #    eprint(url)

