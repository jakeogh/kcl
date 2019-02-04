#!/usr/bin/env python

import redis
from .printops import ceprint

r = redis.StrictRedis(host='127.0.0.1')


def add_to_set(key, value, p=None):
    global r
    if p: r = p
    return r.sadd(key, value)


def get_set(key, p=None):
    global r
    if p: r = p
    return r.smembers(key)


def add_to_ordered_set(key, value, timestamp, p=None):
    global r
    if p: r = p
    return r.zadd(key, timestamp, value)


def get_ordered_set(key, start=0, stop=-1, withscores=False, p=None):
    global r
    if p: r = p
    return r.zrange(key, start, stop, withscores)


def check_for_value_in_set(key, value, p=None):
    global r
    if p: r = p
    #ceprint("key:", key, "value:", value)
    return r.zscore(key, value)


def get_keys(pattern=False, p=None):
    global r
    if p: r = p
    if pattern:
        return r.keys(pattern)
    return r.keys()

def add_to_hash(key, mapping, p=None):
    global r
    if p: r = p
    return r.hmset(key=key, mapping=mapping)

