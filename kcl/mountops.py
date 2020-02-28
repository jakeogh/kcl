#!/usr/bin/env python3
# tab-width:4
# pylint: disable=missing-docstring

# MIT License
# https://github.com/jakeogh/dnsgate/blob/master/LICENSE
#
# common mount functions

# TODO: https://docs.python.org/3.7/library/pathlib.html#pathlib.Path.is_mount

import os
from pathlib import Path
from .pathops import path_is_block_special
from psutil import disk_partitions
from .printops import ceprint

def block_special_path_is_mounted(path):
    assert path
    path = Path(path)
    assert isinstance(path, Path)
    for mount in disk_partitions():
        #print(mount)
        if path.as_posix() in mount.device:
            return True
    return False


def path_is_mounted(path, verbose=False):  # todo test with angryfiles
    assert path
    path = Path(path)
    assert isinstance(path, Path)
    for mount in disk_partitions():
        if verbose: ceprint("mount:", mount)
        if mount.mountpoint == path.as_posix():
            return True
    if os.path.ismount(path):
        return True
    return False
