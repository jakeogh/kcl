#!/usr/bin/env python3

import time
import os
from kcl.mountops import block_special_path_is_mounted
from kcl.fileops import path_is_block_special
from kcl.printops import eprint


def warn(devices):
    assert isinstance(devices, tuple)
    for device in devices:
        assert path_is_block_special(device)
        assert not block_special_path_is_mounted(device)
    eprint("THIS WILL DESTROY ALL DATA ON", ' '.join(devices), "_REMOVE_ ANY HARD DRIVES (and removable storage like USB sticks) WHICH YOU DO NOT WANT TO ACCIDENTLY DELETE THE DATA ON")
    os.system("fdisk --list " + device)
    answer = input("Do you want to delete all of your data? (type YES to proceed): ")
    if answer != 'YES':
        quit(1)
    eprint("Sleeping 5 seconds")
    time.sleep(5)
