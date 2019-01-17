#!/usr/bin/env python3

import os.path
import itertools


def components(path):
    '''
    Returns the individual components of the given file path
    string (for the local operating system).

    The returned components, when joined with os.path.join(), point to
    the same location as the original path.
    '''
    components = []
    # The loop guarantees that the returned components can be
    # os.path.joined with the path separator and point to the same
    # location:
    while True:
        (new_path, tail) = os.path.split(path)  # Works on any platform
        components.append(tail)
        if new_path == path:  # Root (including drive, on Windows) reached
            break
        path = new_path
    components.append(new_path)

    components.reverse()  # First component first
    return components


def longest_prefix(iter0, iter1):
    '''
    Returns the longest common prefix of the given two iterables.
    '''
    longest_prefix = []
    for (elmt0, elmt1) in itertools.izip(iter0, iter1):
        if elmt0 != elmt1:
            break
        longest_prefix.append(elmt0)
    return longest_prefix


def common_prefix_path(path0, path1):
    return os.path.join(*longest_prefix(components(path0), components(path1)))

# For Unix:
assert common_prefix_path('/', '/usr') == '/'
assert common_prefix_path('/usr/var1/log/', '/usr/var2/log/') == '/usr'
assert common_prefix_path('/usr/var/log1/', '/usr/var/log2/') == '/usr/var'
assert common_prefix_path('/usr/var/log', '/usr/var/log2') == '/usr/var'
assert common_prefix_path('/usr/var/log', '/usr/var/log') == '/usr/var/log'
# Only for Windows:
# assert common_prefix_path(r'C:\Programs\Me', r'C:\Programs') == r'C:\Programs'
