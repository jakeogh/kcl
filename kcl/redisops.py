#!/usr/bin/env python

# pylint: disable=C0111  # docstrings are always outdated and wrong
# pylint: disable=W0511  # todo is encouraged
# pylint: disable=C0301  # line too long
# pylint: disable=R0902  # too many instance attributes
# pylint: disable=C0302  # too many lines in module
# pylint: disable=C0103  # single letter var names, func name too descriptive
# pylint: disable=R0911  # too many return statements
# pylint: disable=R0912  # too many branches
# pylint: disable=R0915  # too many statements
# pylint: disable=R0913  # too many arguments
# pylint: disable=R1702  # too many nested blocks
# pylint: disable=R0914  # too many local variables
# pylint: disable=R0903  # too few public methods
# pylint: disable=E1101  # no member for base
# pylint: disable=W0201  # attribute defined outside __init__
# pylint: disable=R0916  # Too many boolean expressions in if statement


from icecream import ic

#r = redis.StrictRedis(host='127.0.0.1')


class RedisKeyTypeNotFoundError(ValueError):
    pass


def get_size_of_key(r, *,
                    key,
                    key_type=False,):
    if not key_type:
        key_type = r.type(key)
    if key_type == b'zset':
        return r.zcard(key)
    if key_type == b'set':
        return r.scard(key)
    if key_type == b'list':
        return r.llen(key)
    if key_type == b'hash':
        return r.hlen(key)
    raise RedisKeyTypeNotFoundError(key_type)


def add_to_set(r, *,
               key,
               value,):
    return r.sadd(key, value)


def get_set(r, *,
            key,):
    return r.smembers(key)


def add_to_ordered_set(r, *,
                       key,
                       value,
                       timestamp,
                       verbose=False):
    if verbose:
        ic('r.zadd("{0}", "{1}", "{2}")'.format(key, timestamp, value))
    result = r.zadd(name=key, mapping={value: timestamp})
    if verbose:
        ic("result:", result)
    return result


def get_ordered_set(r, *,
                    key,
                    start: int = 0,
                    stop: int = -1,
                    withscores: bool = False,):
    return r.zrange(key, start, stop, withscores)


def check_for_value_in_ordered_set(r, *,
                                   key,
                                   value,):
    #ic("key:", key, "value:", value)
    return r.zscore(key, value)


def check_for_value_in_set(r, *,
                           key,
                           value,):
    #ic("key:", key, "value:", value)
    return r.sismember(key, value)


def get_keys(r,
             pattern=False,):
    if pattern:
        return r.keys(pattern)
    return r.keys()


def delete_key(r, *,
               key,):
    return r.delete(key)


def add_to_hash(r, *,
                key,
                mapping,):
    return r.hmset(name=key, mapping=mapping)

