#!/usr/bin/env python

import redis
from .printops import ceprint

r = redis.StrictRedis(host='127.0.0.1')


def add_to_ordered_set(key, value, timestamp):
    return r.zadd(key, timestamp, value)


def get_ordered_set(key, start=0, stop=-1, withscores=False):
    return r.zrange(key, start, stop, withscores)


def check_for_value_in_set(key, value, timestamp=False):
    #ceprint("key:", key, "value:", value)
    if r.zscore(key, value):
        return True
    return False

def get_keys(pattern=False):
    if pattern:
        return r.keys(pattern)
    return r.keys()

