#!/usr/bin/env python3

import os
import sys
import time
import inspect
from colorama import Fore
from colorama import Style
from pprint import pprint


def ceprint(*args, **kwargs):
    '''Simple debugging replacement for print()'''
    caller = sys._getframe(1).f_code.co_name
    stack = inspect.stack()
    frm = stack[1]
    depth = len(stack)
    mod = str(inspect.getmodule(frm[0]))
    source_file = mod.split()[-1].split('>')[0].split("'")[1].split('/')[-1]
    head = ' '.join([
        depth * ' ',
        str(depth).zfill(3),
        str("%.5f" % time.time()),
        str(os.getpid()),
        source_file,
        caller + '()'
        ])
    print('{0: <49}'.format(head), *args, file=sys.stderr, **kwargs)


def eeprint(*args, **kwargs):
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
    head_format = '{0: <46}'
    if "start" in kwargs.keys():
        head_format = kwargs["start"] + head_format
        kwargs.pop("start")
    print(head_format.format(head), *args, file=sys.stderr, **kwargs)
    #print('{0: <49}'.format(head), *args, file=sys.stderr, **kwargs)


def eprint(*args, **kwargs):
    print(Fore.GREEN, file=sys.stderr, end='')
    if 'end' in kwargs.keys():
        print(*args, file=sys.stderr, **kwargs)
        print(Style.RESET_ALL, file=sys.stderr, end='')
    else:
        print(*args, file=sys.stderr, **kwargs, end='')
        print(Style.RESET_ALL, file=sys.stderr)


def epprint(*args, **kwargs):
    pprint(*args, **kwargs)


def print_object_attrs(obj):
    eprint("type(obj):", type(obj))
    obj_attrs = vars(obj)
    eprint('\n'.join("%s: %s" % item for item in obj_attrs.items()))
