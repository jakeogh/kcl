#!/usr/bin/env python3

import time
import secrets
from kcl.printops import eprint
from itertools import zip_longest
from icecream import ic


def true_items_in_iterator(iterator, verbose=False):
    if verbose:
        ic(iterator)
    answer = sum(x for x in iterator if x is True)
    return answer


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
                  min_pool_size,  # the_set always has 1 item
                  verbose=False,
                  debug=False):

    assert max_wait_time > 0.01
    assert min_pool_size >= 2


    time_loops = 0
    eprint("\nWaiting for min_pool_size: {}\n".format(min_pool_size))
    while len(the_set) < min_pool_size:
        start_time = time.time()
        while (time.time() - start_time) < max_wait_time:
            time_loops += 1
            try:
                the_set.add(next(iterator))
            except StopIteration:
                pass

        if time_loops > 1:
            eprint("\nWarning: min_pool_size: {} was not reached in max_wait_time: {}s so actual wait time was: {}x {}s\n".format(min_pool_size, max_wait_time, time_loops, max_wait_time * time_loops))

        if len(the_set) < min_pool_size:
            eprint("\nlen(the_set) is {} waiting for min_pool_size: {}\n".format(len(the_set), min_pool_size))

    assert time_loops > 0

    return the_set


# add time-like memory limit
# the longer the max_wait, the larger buffer_set will be,
# resulting in better mixing
def randomize_iterator(iterator, *,
                       min_pool_size,
                       max_wait_time,
                       buffer_set=None,
                       verbose=False,
                       debug=False):

    assert max_wait_time
    assert min_pool_size

    if not buffer_set:
        buffer_set = set()
        try:
            buffer_set.add(next(iterator))
        except StopIteration:
            pass

    buffer_set = append_to_set(iterator=iterator,
                               the_set=buffer_set,
                               min_pool_size=min_pool_size,
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
        if debug:
            eprint("Chose 1 item out of", buffer_set_length)

        if debug:
            eprint("len(buffer_set):", buffer_set_length - 1)

        if verbose:
            ic(len(buffer_set), next_item)

        yield next_item
