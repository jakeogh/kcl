#!/usr/bin/env python3

import inspect
import os
import sys
import time
from pprint import pprint

import attr
from colorama import Fore, Style
from icecream import ic


def render_line(*, line, end):
    line = [str(thing) for thing in line]   # angryfiles...
    if len(line) == 1:
        print(line[0], end='')
    else:
        line = ' '.join(line)
        print(line, end='')

    print(end, end='')


def ceprint(*args, **kwargs):
    '''Simple debugging replacement for print()'''
    caller = sys._getframe(1).f_code.co_name
    stack = inspect.stack()
    frm = stack[1]
    depth = len(stack)
    mod = str(inspect.getmodule(frm[0]))
    try:
        source_file = mod.split()[-1].split('>')[0].split("'")[1].split('/')[-1]
    except IndexError:
        source_file = "(none)"
    head = ' '.join([
        depth * ' ',
        str(depth).zfill(3),
        str("%.5f" % time.time()),
        str(os.getpid()),
        source_file,
        caller + '()'
        ])
    print('{0: <49}'.format(head), *args, file=sys.stderr, **kwargs)


def eeprint(*args, **kwargs): # todo merge with ceprint
    '''Simple debugging replacement for print()'''
    caller = sys._getframe(1).f_code.co_name
    stack = inspect.stack()
    frm = stack[1]
    depth = len(stack)
    mod = str(inspect.getmodule(frm[0]))
    source_file = mod.split()[-1].split('>')[0].split("'")[1].split('/')[-1]
    head = ' '.join([
        str(depth).zfill(3),
        source_file,
        caller + '()'
        ])
    head_format = '{0: <40}'
    if "start" in kwargs.keys():
        head_format = kwargs["start"] + head_format
        kwargs.pop("start")
    print(head_format.format(head), *args, file=sys.stderr, **kwargs)
    #print('{0: <49}'.format(head), *args, file=sys.stderr, **kwargs)


def eprint(*args, **kwargs):
    if 'file' in kwargs.keys():
        kwargs.pop('file')
    print(*args, file=sys.stderr, **kwargs)


def eprint_green(*args, **kwargs):
    print(Fore.GREEN, file=sys.stderr, end='')
    if 'end' in kwargs.keys():
        print(*args, file=sys.stderr, **kwargs)
        print(Style.RESET_ALL, file=sys.stderr, end='')
    else:
        print(*args, file=sys.stderr, **kwargs, end='')
        print(Style.RESET_ALL, file=sys.stderr)


def autoprint(tuple_list, *args, **kwargs):
    assert isinstance(tuple_list, list)
    for item in tuple_list:
        assert isinstance(item, tuple)
        assert len(item) == 3
        value = item[0]
        if item[1] == 'stdout':
            out = sys.stderr
        elif item[1] == 'stdderr':
            out = sys.stdout
        else:
            raise ValueError("unknown output file {}".format(item[1]))
        end = item[2]
        print(value, file=out, end=end)


def epprint(*args, **kwargs):
    pprint(*args, **kwargs)


def print_object_attrs(obj):
    eprint("type(obj):", type(obj))
    obj_attrs = vars(obj)
    eprint('\n'.join("%s: %s" % item for item in obj_attrs.items()))
