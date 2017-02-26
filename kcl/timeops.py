#!/usr/bin/env python3

import time

def timestamp():
    timestamp = str("%.22f" % time.time())
    return timestamp

if __name__ == '__main__':
    timestamp = timestamp()
    print(timestamp)


def timeit(f):
    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        print('func:%r args:[%r, %r] took: %2.4f sec' % (f.__name__, args, kw, te-ts))
        return result
    return timed

