#!/usr/bin/env python3

# pylint: disable=C0111     # docstrings are always outdated and wrong
# pylint: disable=W0511     # todo is encouraged
# pylint: disable=C0301     # line too long
# pylint: disable=R0902     # too many instance attributes
# pylint: disable=C0302     # too many lines in module
# pylint: disable=C0103     # single letter var names, func name too descriptive
# pylint: disable=R0911     # too many return statements
# pylint: disable=R0912     # too many branches
# pylint: disable=R0915     # too many statements
# pylint: disable=R0913     # too many arguments
# pylint: disable=R1702     # too many nested blocks
# pylint: disable=R0914     # too many local variables
# pylint: disable=R0903     # too few public methods
# pylint: disable=E1101     # no member for base
# pylint: disable=W0201     # attribute defined outside __init__


import errno
import os
import signal
import time
from functools import wraps

import dateparser
from humanize import naturaldelta, naturaltime
from icecream import ic

from .assertops import verify
from .printops import eprint


class Delay():
    def __init__(self, start, multiplier, end):
        start = float(start)
        multiplier = float(multiplier)
        end = float(end)
        assert start >= 0
        assert end > 0
        assert multiplier > 0
        assert start <= end
        delay = start
        self.delay = delay
        self.multiplier = multiplier
        self.end = end

    def _sleep(self):
        ic(self.delay)
        time.sleep(self.delay)

    def _sleep_next(self):
        if self.delay < self.end:
            self.delay = max(self.delay + (self.delay * self.multiplier), self.end)

    def sleep(self):
        self._sleep()
        self._sleep_next()


def timestamp():
    stamp = str("%.22f" % time.time())
    return stamp


def timestamp_to_epoch(date_time):
    #date_time = '2016-03-14T18:54:56.1942132'.split('.')[0]
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


def update_mtime_if_older(*, path, mtime, verbose, debug):
    verify(isinstance(mtime, tuple))
    verify(isinstance(mtime[0], int))
    verify(isinstance(mtime[1], int))
    current_mtime = get_amtime(path)
    if current_mtime[1] > mtime[1]:
        if verbose:
            eprint("{} old: {} new: {}".format(path, current_mtime[1], mtime[1]))
        os.utime(path, ns=mtime, follow_symlinks=False)


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


def human_date_to_timestamp(date):
    dt = dateparser(date)
    return dt.timestamp()


def seconds_duration_to_human_readable(seconds, ago):
    seconds = float(seconds)
    if ago:
        result = naturaltime(seconds)
    else:
        result = naturaldelta(seconds)

    result = result.replace(" seconds", "s")
    result = result.replace("a second", "1s")
    result = result.replace(" minutes", "min")
    result = result.replace("a minute", "1min")
    result = result.replace(" hours", "hr")
    result = result.replace("a hour", "1hr")
    result = result.replace(" days", "days")
    result = result.replace("a day", "1day")
    result = result.replace(" years", "yrs")
    result = result.replace("a year", "1yr")
    result = result.replace(" ago", "_ago")
    return result
