#!/usr/bin/env python3

# /mnt/t420s_256GB_samsung_ssd_S2R5NX0J707260P/.iridb/database.local/data_index/8/9/6/89689beecc6ebf06cb1859b8085ec9154e7edb1b

from icecream import ic
from bs4 import BeautifulSoup
import lxml.html
from lxml.etree import ParserError
from lxml import etree
import re
from urllib.parse import urldefrag
from kcl.printops import ceprint
from kcl.printops import eprint
from kcl.fileops import read_file_bytes
from lxml import html
from lxml.etree import tostring
from lxml.etree import HTMLParser
from lxml.etree import ParserError
#import html5_parser


def soup(html):
    soup = BeautifulSoup(html, 'lxml')
    return soup


def soup_from_file(file_name):
    with open(file_name, 'r') as fh:
        file_soup = soup(fh.read())
    return file_soup


def get_title_from_dom_tree(dom_tree):
    return dom_tree.find(".//title").text


def extract_title_from_file(data_file, verbose=False):
    content = read_file_bytes(data_file)
    try:
        dom_tree = parse_html_to_dom(content)
    except ParserError:
        return None
    try:
        title = ' '.join(get_title_from_dom_tree(dom_tree).split())
    except (UnicodeDecodeError, AttributeError):
        return None
    title = title.replace('\r', ' ').replace('\n', ' ')
    if title == 'YouTube':
        if verbose: ic(data_file)
        try:
            split_marker = b'''\\",\\"title\\":\\"'''  # \",\"title\":\"
            title = content.split(split_marker)[1].split(b'''\\",\\"''')[0]
            title = title.decode('utf8')
        except IndexError:
            try:
                split_marker = b'''","title":"'''
                title = content.split(split_marker)[1].split(b'''","''')[0]
                title = title.decode('utf8')
            except:  # todo
                pass
    return title


def parse_html_to_dom(html):
    dom_tree = lxml.html.fromstring(html)
    return dom_tree


def extract_urls_from_html_dom(page_html, url, strip_fragments, verbose=False, debug=False):
    # METHOD 0: UNTRIED, might be faster
    #root = html5_parser.parse(page)
    #print(type(root))  # <class 'lxml.etree._Element'>
    #print(tostring(root))

    # METHOD 1: returns a 'lxml.html.HtmlElement' with .make_links_absolute(), but fails on malformed html
    # fails on 'https://www.noao.edu/noao/staff/plymate/fts/labguide.html'
    #dom = html.fromstring(page)  # <class 'lxml.html.HtmlElement'>
    ##print(type(dom))  # <class 'lxml.html.HtmlElement'>
    #print(len(dom))  # > 0 if it worked
    #dom.make_links_absolute(url)  # this needs lxml.html.HtmlElement
    #dom.cssselect()

    # METHOD 2, works but the # lxml.etree._Element has no .make_links_absolute()
    #domroot = html.fromstring(page, parser=parser, base_url=url)  # lxml.etree._Element
    #print(type(domroot))  # <class 'lxml.etree._Element'>
    ##if 'lab' in url: import IPython; IPython.embed()
    #dom = domroot.getroottree()
    #dom = dom.getroot()  # lxml.etree._Element
    #dom.cssselect()

    #assert verbose
    link_cache = set([])
    links = set([])
    parser = HTMLParser(recover=True)

    try:
        dom = html.fromstring(page_html)
    except ParserError as e:
        if verbose:
            #ceprint("ParserError")
            ic(e)
        pass
    except ValueError as e:
        if verbose:
            ic(e)
        pass

    else:
        #ic(len(dom))
        #ic(dom)
        if len(dom) > 0:
            try:
                dom.make_links_absolute(url)
            except ValueError as e:  #Invalid IPv6 URL for example
                if verbose:
                    ic(e)
                    ceprint("WARNING dom.make_links_absolute(url) failed due to ValueError")
                pass
        else:
            if verbose: ceprint("len(dom) == 0, parsing malformed html")
            root = html.fromstring(page_html, parser=parser, base_url=url).getroottree()  # lxml.etree._Element
            clean_html = tostring(root)
            dom = html.fromstring(clean_html)
            dom.make_links_absolute(url)

        #import IPython; IPython.embed()

        for link in dom.iterlinks():
            link_url = link[2]
            link_text = link[0].text
            if strip_fragments:
                link_url, _ = urldefrag(link_url)

            if link_url.startswith('javascript:'):
                continue

            if debug:
                ic(link_url)

            if link_url not in link_cache:
                try:
                    text = link_text.strip()
                except AttributeError:
                    text = link_text
                links.add((link_url, text))
                link_cache.add(link_url)

        for link in dom.cssselect('a'):
            #if verbose:
            #    ic(link)
            try:
                link_url = link.attrib['href']
                if link_url.startswith('javascript:'):
                    continue
                if strip_fragments:
                    link_url, _ = urldefrag(link_url)
                if debug:
                    ic(link_url)

                if link_url not in link_cache:
                    try:
                        text = link.text.strip()
                    except AttributeError:
                        text = link.text
                    links.add((link_url, text))
                    link_cache.add(link_url)
            except KeyError as e:
                if verbose:
                    ic(e)
                pass

        for link in dom.cssselect('img'):
            #if verbose:
            #    ic(link)  # <Element img at 0x7f993acd6630>
            try:
                link_url = link.attrib['src']
                if link_url.startswith('javascript:'):
                    continue
                if strip_fragments:
                    link_url, _ = urldefrag(link_url)
                if debug:
                    ic(link_url)
                if link_url not in link_cache:
                    try:
                        text = link.text.strip()
                    except AttributeError:
                        text = link.text
                    links.add((link_url, text))
                    link_cache.add(link_url)
            except KeyError as e:
                if verbose:
                    ic(e)
                pass

        #for link in dom.cssselect('div'):
        #    import IPython; IPython.embed()

    if verbose:
        ic(len(link_cache))

    return links, link_cache


def extract_urls_from_file(html_file, url, strip_fragments, text_extract=True, dom_extract=True, verbose=False, debug=False):
    #page_html = requests.get(url).text
    if verbose:
        ic(html_file)
        ic(text_extract)
        ic(dom_extract)
    with open(html_file, 'rb') as fh:
        html_bytes = fh.read()
    page_html = html_bytes.decode('utf8', 'ignore')

    if verbose:
        ic(len(page_html))

    if dom_extract:
        links, link_cache = extract_urls_from_html_dom(page_html, url, strip_fragments, verbose=verbose, debug=debug)
    else:
        links = set([])
        link_cache = set([])

    if text_extract:
        for link in extract_iris_from_text(page_html, verbose=verbose, debug=debug):
            if link not in link_cache:
                links.add((link, None))

    links = set(links)  #pointless...
    if verbose:
        ic(len(links))

    return links


    #parser = etree.HTMLParser(recover=True)
    #with open(html_file, 'rb') as fh:
    #    html_bytes = fh.read()
    #html = html_bytes.decode('utf8', 'ignore')
    #if verbose: ceprint("len(html):", len(html))
    #url_list = []
    #try:
    #    #dom = lxml.html.fromstring(html, base_url=url, parser=parser)
    #    #dom = lxml.html.fromstring(html)
    #    #e_tree = etree.parse(html_file, base_url=url, parser=parser)
    #    #dom = etree.parse(html_file, base_url=url, parser=parser).getroot()
    #    dom = etree.parse(html_file, base_url=url).getroot()
    #    #dom = lxml.html.parse(html_file, base_url=url, parser=parser)
    ##except ValueError:
    ##    if verbose: ceprint("ValueError")
    ##    dom = lxml.html.fromstring(html_bytes, recover=True)
    #except ParserError: # images etc
    #    if verbose: ceprint("ParseError")
    #    return set([])

    #if verbose: ceprint("len(dom):", len(dom))


    ##if verbose: ceprint("type(e_tree):", type(e_tree))
    ##if verbose: pprint(e_tree)


    #try:
    #    dom.make_links_absolute(url)
    #except ValueError:  # ValueError: Invalid IPv6 URL
    #    if verbose: ceprint("ValueError while trying dom.make_links_absolute(url)")
    #    return set([])

    #links_a = dom.cssselect('a')
    #if verbose: ceprint("len(links_a):", len(links_a))
    #for link in links_a:
    #    try:
    #        url_list.append((link.attrib['href'], link.text))
    #    except KeyError:
    #        pass
    #links_img = dom.cssselect('img')
    #for link in links_img:
    #    try:
    #        url_list.append((link.attrib['src'], link.text))
    #    except KeyError:
    #        pass
    #return set(url_list)


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
def extract_iris_from_text(text, verbose=False, debug=False):  # todo, buggy, already had to add the ~ below
    if verbose:
        ic(len(text))
    #if debug:
    #    ic(text)
    if isinstance(text, bytes):
        text = text.decode('utf8', 'ignore')
    assert isinstance(text, str)
    text = text.replace("<em>//</em>", "//")
    text = text.replace("<wbr>", "")

    text_list = text.split("\n")
    clean_text = filter(None, text_list)

    url_list = []
    for line in clean_text:
        if debug:
            ic(line)
        for word in line.split():
           #urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[~$-_@.&+#]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', word)
           #urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[~$\-/_@.&+#]|[!*,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', word)
           #urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[~$\-/_@.&+#;()]|[!*,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', word)
           #urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[~$\-/_@.&+#;()?]|[!*,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', word)
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[~$\-/_@.&+#;()?i=]|[!*,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', word)
            for url in urls:
                if debug:
                    ic(word)
                    ic(url)

                url = url.strip()

                if url.endswith(';'):
                    url = url[:-1]
                if url.endswith(')'):
                    if '(' not in url:
                        if verbose:
                            eprint("removing trailing ) from url:", url)
                        url = url[:-1]
                if url.endswith('..'):
                    continue
                if '&quot' in url:
                    url = url.split('&quot')[0]
                if url.endswith('&'):
                    if verbose:
                        eprint("removing trailing % from url:", url)
                    url = url[:-1]

                url_list.append(url)

    url_set = set(url_list)
    if verbose:
        ic(url_set)
    return url_set


def extract_iris_from_text_file(text_file):
    with open(text_file, 'rb') as fh:
        text_bytes = fh.read()
    text = text_bytes.decode('utf8', 'ignore')
    url_set = extract_iris_from_text(text)
    return url_set


# note this removes all links, produces a text version of a page printout
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


#def extract_iris_from_html_file(html_file):
#    #text = run_command(b' '.join([b'/home/cfg/html/html2text', html_file]), verbose=True)
#    text = convert_html_file_to_text(html_file)
#    url_set = extract_iris_from_text(text)
#    return url_set

#
#
