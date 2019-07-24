#!/usr/bin/env python

import redis
from .printops import ceprint

r = redis.StrictRedis(host='127.0.0.1')


def get_size_of_key(key, key_type=False, p=None):
    global r
    if p: r = p
    if not key_type:
        key_type = r.type(key)
    if key_type == b'zset':
        return r.zcard(key)
    elif key_type == b'set':
        return r.scard(key)
    elif key_type == b'list':
        return r.llen(key)
    elif key_type == b'hash':
        return r.hlen(key)
    else:
        raise FileNotFoundError


def add_to_set(key, value, p=None):
    global r
    if p: r = p
    return r.sadd(key, value)


def get_set(key, p=None):
    global r
    if p: r = p
    return r.smembers(key)


def add_to_ordered_set(key, value, timestamp, p=None, verbose=False):
    global r
    if p: r = p
    if verbose: ceprint('r.zadd("{0}", "{1}", "{2}")'.format(key, timestamp, value))
    result = r.zadd(name=key, mapping={value:timestamp})
    if verbose: ceprint("result:", result)
    return result

def get_ordered_set(key, start=0, stop=-1, withscores=False, p=None):
    global r
    if p: r = p
    return r.zrange(key, start, stop, withscores)


def check_for_value_in_ordered_set(key, value, p=None):
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


def delete_key(key, p=None):
    global r
    if p: r = p
    return r.delete(key)


def add_to_hash(key, mapping, p=None):
    global r
    if p: r = p
    return r.hmset(name=key, mapping=mapping)

