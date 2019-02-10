#!/usr/bin/env python3

import urllib
from requests.exceptions import InvalidURL
from http.client import parse_headers
import io
import re
import sys
import traceback
import requests
from kcl.printops import eprint
import struct
import socket


def int2ip(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))


def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]


def validate_ipv4(addr):
    try:
        socket.inet_aton(addr)
        return True
    except socket.error as e:
#       raise e
        return False


def normalize_ipv4(addr):
    if validate_ipv4(addr):
        return int2ip(ip2int(addr))



def print_traceback():
    ex_type, ex, tb = sys.exc_info()
    traceback.print_tb(tb)
    del tb


def punycode_netloc(parserresult):
    assert isinstance(parserresult, urllib.parse.ParseResult)
    punycoded_hostname = parserresult.hostname.encode('idna').decode('ascii')
    if parserresult.username or parserresult.password:
        netloc = ':'.join([parserresult.username, parserresult.password]) + '@' + punycoded_hostname
    else:
        netloc = punycoded_hostname
    if parserresult.port:
        netloc = netloc + ':' + str(parserresult.port)
    return netloc


##IDNA2003
## http://stackoverflow.com/questions/4389572/how-to-fetch-a-non-ascii-url-with-python-urlopen/42309027
## https://docs.python.org/3/library/codecs.html#module-encodings.idna
## RFC 3490 Internationalized Domain Names in Applications
## RFC 3492 Nameprep: A Stringprep Profile for Internationalized Domain Names (IDN)
## idna.encode('☃.net') -> "idna.core.InvalidCodepoint: Codepoint U+2603 at position 1 of '☃' not allowed"
## '☃.net'.encode('idna') -> b'xn--n3h.net'
#todo look at urldefragauth: https://github.com/kennethreitz/requests/blob/master/requests/utils.py (line 695)
# idna lib: https://github.com/kjd/idna is IDNA2008 only
# therefore idna.encode('☃') does not return 'xn--n3h'
# need to fallback on IDAN2003 https://github.com/kjd/idna/issues/25
# IDNA2008 raises idna.core.InvalidCodepoint
# dont use bytes, just make sure the str can decode('ascii')
# https://gist.github.com/hangtwenty/8aaab82e6ba23806f8dc

def normalize_to_request_uri(iri):
    #eprint("iri:", iri)
    #assert isinstance(iri, Locator_String)

    req = requests.Request('HEAD', iri)
    try:
        r = req.prepare()
    except InvalidURL:
        ipar = requests.utils.urlparse(str(iri))
        try:
            netloc_punycoded = punycode_netloc(ipar)
        except AttributeError:
            raise InvalidURL #prob empty netloc

        iri_parsed_punycoded = \
            urllib.parse.ParseResult(ipar.scheme,
                                     netloc_punycoded,
                                     ipar.path,
                                     ipar.params,
                                     ipar.query,
                                     ipar.fragment)
        iri = requests.utils.urlunparse(iri_parsed_punycoded)
        req = requests.Request('HEAD', iri)
        r = req.prepare()

    uri = r.url
    assert uri.encode('ascii')
    return uri



def extract_user_pass_from_netloc(orig_netloc):
    assert(isinstance(orig_netloc, str))
    # must strip the user:pass otherwise uppercase unicode in the pass gets
    # converted to lowercase (todo check pass with unicode)
    # (todo check normal user without unicode with caps)
    if '@' in orig_netloc:
        user_pass, netloc = orig_netloc.split('@')
    else:
        user_pass = None
        netloc = orig_netloc
    return user_pass, netloc

def normalize_percent_encoded_case(iri):
    # upper case any % encoded chars
    # literal % is invalid anywhere in a URI unless it's followed by 2 hex digits.
    # unquote_unreserved fails above if that happens
    if '%' in iri:
        two_hex_digits = re.compile('[A-Fa-f0-9]{2,2}')
        percent_split_iri = iri.split('%')
        for index, part in enumerate(percent_split_iri):
            if two_hex_digits.match(part[:2]):
                new_part = part[:2].upper() + part[2:]
                percent_split_iri[index] = new_part
        iri = '%'.join(percent_split_iri)
    return iri


