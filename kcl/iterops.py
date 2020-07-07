#!/usr/bin/env python3

import time
import secrets
from itertools import zip_longest
from icecream import ic

# https://docs.python.org/3/library/itertools.html#itertools-recipes
def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def compact(items):
    return [item for item in items if item]


# todo add memory limit
def randomize_iterator(iterator, max_wait=0.01, verbose=False):
    buffer_set = set()
    buffer_set.add(next(iterator))

    start_time = time.time()
    if verbose:
        ic(start_time)
    while ((time.time() - start_time) > max_wait):
        buffer_set.add(next(iterator))

    random_index = secrets.randbelow(len(buffer_set))
    next_item = list(buffer_set).pop(random_index)
    buffer_set.remove(next_item)

    if verbose:
        ic(len(buffer_set))

    yield next_item

