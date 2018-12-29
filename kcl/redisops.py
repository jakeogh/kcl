#!/usr/bin/env python

import redis
from .printops import ceprint

r = redis.StrictRedis(host='127.0.0.1')


def redis_add_iri_to_visited_ordered_set(key, iri, timestamp):
    r.zadd(key, timestamp, iri)


def check_for_value_in_set(key, value, timestamp=False):
    #ceprint("key:", key, "value:", value)
    if r.zscore(key, value):
        return True
    return False
