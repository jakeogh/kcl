#!/usr/bin/env python3
import os
import time


def timestamp():
    timestamp = str("%.22f" % time.time())
    return timestamp


def timestamp_to_epoch(date_time):
#   date_time = '2016-03-14T18:54:56.1942132'.split('.')[0]
    date_time = date_time.split('.')[0]
    pattern = '%Y-%m-%dT%H:%M:%S'
    epoch = int(time.mktime(time.strptime(date_time, pattern)))
    return epoch


def timeit(f):
    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        print('func:%r args:[%r, %r] took: %2.4f sec' % (f.__name__, args, kw, te-ts))
        return result
    return timed


def get_mtime(infile):
    mtime = os.lstat(file).st_mtime #does not follow symlinks
    return mtime
