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


def append_to_set(*,
                  iterator,
                  the_set,
                  max_wait_time,
                  min_pool_size=1,
                  verbose=False,
                  debug=False):

    start_time = time.time()

    time_loops = 0
    eprint("\nWaiting for min_pool_size: {}\n".format(min_pool_size))
    while len(the_set) < min_pool_size:
        while (time.time() - start_time) < max_wait_time:
            time_loops += 1
            try:
                the_set.add(next(iterator))
            except StopIteration:
                pass
        if time_loops > 1:
            eprint("\nWarning: min_pool_size: {} was not attained in max_wait_time: {} so actual wait time was: {}\n".format(min_pool_size, max_wait_time, max_wait_time*time_loops))


    assert time_loops > 0

    return the_set


# add time-like memory limit
# the longer the max_wait, the larger buffer_set will be,
# resulting in better mixing
def randomize_iterator(iterator, *,
                       buffer_set=None,
                       max_wait_time=1.6,
                       min_pool_size=1,
                       verbose=False,
                       debug=False):

    if not buffer_set:
        buffer_set = set()
        try:
            buffer_set.add(next(iterator))
        except StopIteration:
            pass

    buffer_set = append_to_set(iterator=iterator,
                               the_set=buffer_set,
                               max_wait_time=max_wait_time,
                               verbose=verbose,
                               debug=debug)

    while buffer_set:
        try:
            buffer_set.add(next(iterator))
        except StopIteration:
            pass

        buffer_set_length = len(buffer_set)
        random_index = secrets.randbelow(buffer_set_length)
        #[next_item] = itertools.islice(buffer_set, random_index, 1)
        next_item = list(buffer_set).pop(random_index)
        buffer_set.remove(next_item)
        if verbose:
            eprint("Chose 1 item out of", buffer_set_length)

        if debug:
            eprint("len(buffer_set):", buffer_set_length - 1)

        yield next_item
