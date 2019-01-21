#!/usr/bin/env python3
# tab-width:4
# pylint: disable=missing-docstring

# MIT License
# https://github.com/jakeogh/dnsgate/blob/master/LICENSE
#
# common dir functions

import os
import shutil
from .printops import eprint
from .printops import ceprint
from pathlib import Path


def all_files_iter(p):
    if isinstance(p, str) or isinstance(p, bytes):
        p = Path(p)
    assert isinstance(p, Path)
    print("yeilding p:", p)
    yield p
    for sub in p.iterdir():
        # eprint("sub:", sub)  # todo: read by terminal, so bell etc happens.... eprint bug?
        if sub.is_symlink():  # must be before is_dir()
            yield sub
        elif sub.is_dir():
            yield from all_files_iter(sub)
        else:
            yield sub


def all_files(folder, files_only=False): # todo add flags for recursive, follow symlinks etc, return a generator
    assert path_is_dir(folder)
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
    for root, dirs, files in os.walk(folder):
        for ifile in files:
            relative_file_path = root + b'/' + ifile
            all_files.append(relative_file_path)
    return set(all_files)


def dir_exists(path):
    return path_is_dir(path)


def is_directory(path):
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
            ceprint("The folder:")
            ceprint(folder)
            ceprint("does not exist. Type yes to create it and continue, otherwise exiting:")
            ceprint("make dir:")
            ceprint(folder, end=None)
            make_folder_answer = input(": ")
            if make_folder_answer.lower() != "yes":
                ceprint("Exiting before mkdir.")
                os._exit(1)
        create_dir(folder)
        return True


def create_dir(folder):
    try:
        os.makedirs(folder, exist_ok=True)
    except FileExistsError:
        pass


def mkdir_or_exit(folder, user=None, exists_ok=False):
    #ceprint("calling os.makedirs on:", folder)
    try:
        os.makedirs(folder)
    except FileExistsError:
        assert path_is_dir(folder)
    if user:
        shutil.chown(folder, user=user, group=user)


def chdir_or_exit(targetdir):
    try:
        os.chdir(targetdir)
    except Exception as e:
        print("Exception:", e)
        print("Unable to os.chdir(%s). Exiting.", targetdir)
        os._exit(1)
    return True


