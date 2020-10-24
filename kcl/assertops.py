#!/usr/bin/env python3


def one(thing):
    count = 0
    for x in thing:
        #eprint("x:", x, bool(x))
        if bool(x):
            count += 1
    #count = sum(1 for x in thing if bool(x))
    if count == 1:
        return True
    raise ValueError(thing)


def maxone(thing):
    count = 0
    for x in thing:
        if bool(x):
            count += 1
    if count in [0, 1]:
        return True
    raise ValueError(thing)


def minone(thing):
    count = 0
    for x in thing:
        if bool(x):
            count += 1
    if count >= 1:
        return True
    raise ValueError(thing)


import sys
def old_verify(exception, thing, verbose=False):
    if not issubclass(exception, Exception):
    #if not isinstance(exception, Exception):  # cant pass class instances and thn call them later
        raise TypeError(exception)
    try:
        #thing  # nope, want thing=False to raise
        assert thing
    except Exception as e:
        e_type = type(e)
        if verbose:
            print(e_type, file=sys.stderr)
        raise exception(e_type)


def verify(exc_type, thing):
    if not thing:
        raise exc_type('something failed')
