#!/usr/bin/env python

import redis
from .printops import ceprint

r = redis.StrictRedis(host='127.0.0.1')


def add_to_ordered_set(key, value, timestamp):
    r.zadd(key, timestamp, value)


def check_for_value_in_set(key, value, timestamp=False):
    #ceprint("key:", key, "value:", value)
    if r.zscore(key, value):
        return True
    return False
