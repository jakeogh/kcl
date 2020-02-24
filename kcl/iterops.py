#!/usr/bin/env python3

from itertools import zip_longest


# https://docs.python.org/3/library/itertools.html#itertools-recipes
def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

def compact(items):
    return [item for item in items if item]

