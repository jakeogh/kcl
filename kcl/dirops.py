#!/usr/bin/env python3
# tab-width:4
# pylint: disable=missing-docstring

# MIT License
# https://github.com/jakeogh/dnsgate/blob/master/LICENSE
#
# common dir functions

import time
import os
import shutil
import pprint
import psutil
from shutil import copyfileobj
import subprocess
import stat
from .printops import eprint

def all_files(folder, files_only=False): #todo add flags for recursive, follow symlinks etc, return a generator
    assert path_is_dir(folder)
    ##all_files = [os.path.join(path, filename) for path, dirs, files in os.walk(folder) for filename in files]
    all_files = []
    for path, dirs, files in os.walk(folder):
        for filename in files:
            all_files.append(os.path.join(path, filename))
        if not files_only:
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

def dir_exists(path):
    return path_is_dir(path)

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
    #assert isinstance(folder, bytes)
    if not os.path.isdir(folder):
        if confirm:
            print("The folder:")
            print(folder)
            print("does not exist. Type yes to create it and continue, otherwise exiting:")
            make_folder_answer = input(folder)
            if make_folder_answer.lower() != "yes":
                eprint("Exiting before mkdir.")
                os._exit(1)
        create_dir(folder)
        return True

def create_dir(folder):
    try:
        os.makedirs(folder)
    except FileExistsError:
        pass

def mkdir_or_exit(folder):
    try:
        os.makedirs(folder)
    except Exception as e:
        print("Exception:", e)
        os._exit(1)
    return True

def chdir_or_exit(targetdir):
    try:
        os.chdir(targetdir)
    except Exception as e:
        print("Exception:", e)
        print("Unable to os.chdir(%s). Exiting.", targetdir)
        os._exit(1)
    return True


if __name__ == '__main__':
    quit(0)

