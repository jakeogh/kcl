#!/usr/bin/env python3

# /mnt/t420s_256GB_samsung_ssd_S2R5NX0J707260P/.iridb/database.local/data_index/8/9/6/89689beecc6ebf06cb1859b8085ec9154e7edb1b

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
def extract_urls_lxml_with_link_text(html, url):
    url_list = []
    try:
        dom = lxml.html.fromstring(html)
    except ParserError:
        return set([])

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
            pass
        filtered_url_list.append(url)
    return set(filtered_url_list)


def extract_urls_lxml(html_file, url):
    with open(html_file, 'r') as fh:
        html = fh.read()
    url_only_list = []
    url_list = extract_urls_lxml_with_link_text(html=html, url=url)
    for item in url_list:
        url_only_list.append(item[0])
    return set(url_only_list)


def extract_urls_lxml_nofollow(html_file, url):
    with open(html_file, 'r') as fh:
        html = fh.read()
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


def extract_iris_from_text(text):  # todo, buggy, already had to add the ~ below
    if isinstance(text, bytes):
        text = text.decode('utf8', 'ignore')
    text_list = text.split("\n")
    clean_text = filter(None, text_list)
    url_list = []
    for line in clean_text:
        for word in line.split(' '):
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[~$-_@.&+#]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', word)
            for url in urls:
                url_list.append(url)
    url_set = set(url_list)
    return url_set


#def extract_iris_from_html(html):
#    text = run_command(['/home/cfg/html/html2text', infile])
#    url_set = extract_iris_from_text(text)

def extract_iris_from_text_file(infile):   #todo, buggy, already had to add the ~ below
    with open(infile, 'r') as fh:
        text = fh.read()
    url_set = extract_iris_from_text(text)
    return url_set

def extract_iris_from_html_file(infile):   #todo, buggy, already had to add the ~ below
    text = run_command(' '.join(['/home/cfg/html/html2text', infile]), verbose=True)
    url_set = extract_iris_from_text(text)
    return url_set

#if __name__ == '__main__':
#    htmlops()
    #try:
    #    domain = sys.argv[1]
    #except:
    #    print("a domain is reqired. exiting.")
    #    os._exit(1)
    #with open('/dev/stdin', 'r') as f:
    #    html = f.read()
    #for url in  extract_urls_lxml(html, domain):
    #    eprint(url)

