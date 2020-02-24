#!/usr/bin/env python3

from icecream import ic
import os
import stat
import itertools
from pathlib import Path
from .assertops import verify
from .hashops import sha3_256_hash_file


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


def paths_are_identical(path1, path2, time=False, perms=False, verbose=False):
    verify(isinstance(path1, Path))
    verify(isinstance(path2, Path))
    if time or perms:
        raise NotImplementedError

    path1_lstat = os.lstat(path1)
    path2_lstat = os.lstat(path2)

    path1_type = stat.S_IFMT(path1_lstat.mode)
    path2_type = stat.S_IFMT(path2_lstat.mode)
    if verbose:
        ic(path1_type)
        ic(path2_type)
    if path1_type != path2_type:
        return False

    return False


#def common_prefix_path(path0, path1):
#    return os.path.join(*longest_prefix(components(path0), components(path1)))

# For Unix:
#assert common_prefix_path('/', '/usr') == '/'
#assert common_prefix_path('/usr/var1/log/', '/usr/var2/log/') == '/usr'
#assert common_prefix_path('/usr/var/log1/', '/usr/var/log2/') == '/usr/var'
#assert common_prefix_path('/usr/var/log', '/usr/var/log2') == '/usr/var'
#assert common_prefix_path('/usr/var/log', '/usr/var/log') == '/usr/var/log'
# Only for Windows:
# assert common_prefix_path(r'C:\Programs\Me', r'C:\Programs') == r'C:\Programs'
