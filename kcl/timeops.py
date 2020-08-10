#!/usr/bin/env python3
import os
import time
import errno
import signal
from functools import wraps
from .assertops import verify
from .printops import eprint
from icecream import ic


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
    mtime = os.lstat(infile).st_mtime #does not follow symlinks
    return mtime


def get_amtime(infile):
    try:
        infile_stat = os.lstat(infile)
    except TypeError:
        infile_stat = os.lstat(infile.fileno())
    amtime = (infile_stat.st_atime_ns, infile_stat.st_mtime_ns)
    return amtime


def update_mtime_if_older(path, mtime, verbose=False):
    verify(isinstance(mtime, tuple))
    verify(isinstance(mtime[0], int))
    verify(isinstance(mtime[1], int))
    current_mtime = get_amtime(path)
    if current_mtime[1] > mtime[1]:
        if verbose:
            eprint("{} old: {} new: {}".format(path, current_mtime[1], mtime[1]))
        os.utime(path, ns=mtime, follow_symlinks=False)


#class TimeoutError(Exception):
#    pass


def timeout(seconds, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator
