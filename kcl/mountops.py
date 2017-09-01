#!/usr/bin/env python3
# tab-width:4
# pylint: disable=missing-docstring

# MIT License
# https://github.com/jakeogh/dnsgate/blob/master/LICENSE
#
# common mount functions

import subprocess
from .fileops import path_is_block_special
from psutil import disk_partitions


def block_special_path_is_mounted(path):
    for mount in disk_partitions():
        if mount.device == path:
            return True
    return False

def path_is_mounted(path):
    for mount in disk_partitions():
        if mount.mountpoint == path:
            return True
    return False


if __name__ == '__main__':
    quit(0)

