#!/usr/bin/env python

import redis
from .printops import ceprint

r = redis.StrictRedis(host='127.0.0.1')

def redis_add_iri_to_visited_ordered_set(key, iri, timestamp):
    r.zadd(name=key, timestamp, iri)
