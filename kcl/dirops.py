#!/usr/bin/env python3
# tab-width:4
# pylint: disable=missing-docstring

# MIT License
# https://github.com/jakeogh/dnsgate/blob/master/LICENSE
#
# common dir functions
__version__ = "0.0.1"

import time
import os
import shutil
import pprint
import psutil
from shutil import copyfileobj
import subprocess
import stat
from .printops import cprint

def all_files(folder):
    #all_files = [os.path.join(path, filename) for path, dirs, files in os.walk(folder) for filename in files]
    all_files = []
    for path, dirs, files in os.walk(folder):
        for filename in files:
            all_files.append(os.path.join(path, filename))
        for d in dirs:
            all_files.append(os.path.join(path, d))
    return all_files

def count_files(folder):
    total = 0
    for root, dirs, files in os.walk(folder):
        total += len(files)
    return total

def list_files(folder):
    all_files = []
    total = 0
    for root, dirs, files in os.walk(folder):
        for file in files:
            relative_file_path = root + b'/' + file
            all_files.append(relative_file_path)
    return set(all_files)

def path_is_dir(path):
    if os.path.isdir(path): #could still be a symlink
        if os.path.islink(path):
            return False
        return True

def path_is_dir_or_symlink_to_dir(path):
    # unlike os.path.exists(False), os.path.isdir(False) returns False
    if os.path.isdir(path): # returns False if it's a symlink to a file
        return True
    return False

def check_or_create_dir(folder, confirm=True):
    if not os.path.isdir(folder):
        if confirm:
            make_folder_answer = \
                input(b"The folder " + folder + b" does not exist.
                 This is not normal. Type yes to create it and continue,
                 otherwise exiting here.: ")
            if make_folder_answer.lower() != "yes":
                cprint("Exiting before mkdir.")
                os._exit(1)
        create_dir(folder)
        return True

def create_dir(folder):
    os.makedirs(folder)


if __name__ == '__main__':
    quit(0)

