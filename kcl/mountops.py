#!/usr/bin/env python3
# tab-width:4
# pylint: disable=missing-docstring

# MIT License
# https://github.com/jakeogh/dnsgate/blob/master/LICENSE
#
# common mount functions

import os
from .fileops import path_is_block_special
from psutil import disk_partitions
from .printops import ceprint

def block_special_path_is_mounted(path):
    for mount in disk_partitions():
        #print(mount)
        if path in mount.device:
            return True
    return False


def path_is_mounted(path, verbose=False):  # todo test with angryfiles
    path = path.strip()
    assert path
    assert isinstance(path, str)  # fixme
    for mount in disk_partitions():
        if verbose: ceprint("mount:", mount)
        if mount.mountpoint == path:
            return True
    if os.path.ismount(path):
        return True
    return False
