#!/usr/bin/env python3

import time
import secrets
from kcl.printops import eprint
from itertools import zip_longest
from icecream import ic

# https://docs.python.org/3/library/itertools.html#itertools-recipes
def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def compact(items):
    return [item for item in items if item]


def append_to_set_for_time(*, iterator, the_set, max_wait, verbose=False, debug=False):
    start_time = time.time()

    loops = 0
    while (time.time() - start_time) < max_wait:
        loops += 1
        try:
            the_set.add(next(iterator))
        except StopIteration:
            pass

    assert loops > 0

    return the_set


# add time-like memory limit
# the longer the max_wait, the larger buffer_set will be,
# resulting in better mixing
def randomize_iterator(iterator, buffer_set=None, max_wait=0.1, verbose=False, debug=False):

    if not buffer_set:
        buffer_set = set()
        try:
            buffer_set.add(next(iterator))
        except StopIteration:
            pass

    buffer_set = append_to_set_for_time(iterator=iterator,
                                        the_set=buffer_set,
                                        max_wait=max_wait,
                                        verbose=verbose,
                                        debug=debug)

    while buffer_set:
        try:
            buffer_set.add(next(iterator))
        except StopIteration:
            pass

        random_index = secrets.randbelow(len(buffer_set))
        #[next_item] = itertools.islice(buffer_set, random_index, 1)
        next_item = list(buffer_set).pop(random_index)
        buffer_set.remove(next_item)

        if verbose:
            eprint("len(buffer_set):", len(buffer_set))

        yield next_item
