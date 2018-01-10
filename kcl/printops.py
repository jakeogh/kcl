#!/usr/bin/env python3

import os
import sys
import time
import inspect
from pprint import pprint

def ceprint(*args, **kwargs):
    '''Simple debugging replacement for print()'''
    caller = sys._getframe(1).f_code.co_name
    frm = inspect.stack()[1]
    mod = str(inspect.getmodule(frm[0]))
    source_file = mod.split()[-1].split('>')[0].split("'")[1].split('/')[-1]
    head = ' '.join([str("%.5f" % time.time()), str(os.getpid()), source_file])
    print(head,
          '{0: <29}'.format(caller+'()'),
          *args,
          file=sys.stderr,
          **kwargs)

    #print(str("%.5f" % time.time()),
    #      os.getpid(),
    #      source_file,
    #      '{0: <29}'.format(caller+'()'),
    #      *args,
    #      file=sys.stderr,
    #      **kwargs)
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def epprint(*args, **kwargs):
    pprint(*args, stream=sys.stderr, **kwargs)

def print_object_attrs(obj):
    eprint("type(obj):", type(obj))
    obj_attrs = vars(obj)
    eprint('\n'.join("%s: %s" % item for item in obj_attrs.items()))

