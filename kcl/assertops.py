#!/usr/bin/env python3


def one(thing):
    #eeprint("thing:", thing)
    count = 0
    for x in thing:
        #eprint("x:", x, bool(x))
        if bool(x):
            count += 1
    #count = sum(1 for x in thing if bool(x))
    #eprint("count", count)
    if count == 1:
        return True
    return False
    #return count == 1


def verify(thing):
    if not thing:
        #eeprint("thing:", thing)
        raise ValueError(thing)


