#!/usr/bin/env python3
from decimal import Decimal
from decimal import getcontext
import collections
import binascii
import os

#try:
#    unicode = unicode
#except NameError:
#    # 'unicode' is undefined, must be Python 3
#    str = str
#    unicode = str
#    bytes = bytes
#    basestring = (str,bytes)
#else:
#    # 'unicode' exists, must be Python 2
#    str = str
#    unicode = unicode
#    bytes = str
#    basestring = basestring

def is_digits(string):
    for char in string:
        if not char.isdigit():
            return False
    return True


def get_values_from_dict(dict):
    all_uris = list(dict.values())
    return all_uris


def make_flatten_generator(l):
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, (str, bytes)):
            for sub in make_flatten_generator(el):
                yield sub
        else:
            yield el


def flatten_list(list):
    return [item for item in make_flatten_generator(list)]


def list_of_lists_to_list_of_sets(list):
    list_of_sets = []
    for item in list:
        list_of_sets.append(set(item))
    return list_of_sets


#def tag_union(tags):
#    tag_dict = return_tag_dict(tags)
#    all_valuess = get_values_from_dict(tag_dict)
#    union_set = set(flatten_list(all_values))
#    return(union_set)
#
#
#def tag_intersection(tags):
#    tag_dict = return_tag_dict(tags)
#    all_values = get_values_from_dict(tag_dict)
#    all_values_list_of_sets = list_of_lists_to_list_of_sets(all_values)
#    intersection_set = set.intersection(*all_values_list_of_sets)
#    return intersection_set


def dollar_string_to_float(string):
    negative = False
    if string[0] == '(':
        string = string[1:]
        negative = True
        if string[-1] != ')':
            print("ERROR: expected:", string, "to end with )")
            quit(1)
        string = string[0:-1]
    if string[0] != '$':
        print("ERROR:, no $ in:", string)
        quit(1)
    string = float(string[1:])
    if negative:
        string = -string
    return string


def dollar_string_to_decimal(string):
    string = string.replace(',', '')
    #print(string)
    getcontext().prec = 16
    negative = False
    if string[0] == '(':
        string = string[1:]
        negative = True
        if string[-1] != ')':
            print("ERROR: expected:", string, "to end with )")
            quit(1)
        string = string[0:-1]
    if string[0] != '$':
        print("ERROR:, no $ in:", string)
        quit(1)
    number = Decimal(string[1:])
    if negative:
        number = -number
    return number


def get_random_hex_bytes(count):
    assert isinstance(count, int)
    return binascii.hexlify(os.urandom(count))


def get_random_hex_digits(count):
    assert isinstance(count, int)
    bytes_needed = count
    if count % 2 != 0:
        bytes_needed = int((count + 1) / 2)
    else:
        bytes_needed = int(count / 2)
    ans = get_random_hex_bytes(bytes_needed)[0:count]
    assert len(ans) == count
    return ans.decode('UTF8')



