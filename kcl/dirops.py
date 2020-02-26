#!/usr/bin/env python3
# tab-width:4
# pylint: disable=missing-docstring

# MIT License
# https://github.com/jakeogh/dnsgate/blob/master/LICENSE
#
# common dir functions

#from math import inf
import os
#import attr
import shutil
from psutil import disk_usage
from icecream import ic
from .printops import eprint
from .fileops import path_exists
from .pathops import path_is_dir
#from .printops import ceprint
#from pathlib import Path


def target_generator(target_list, min_free_space, verbose=True):
    if verbose: ic(min_free_space)
    for target in target_list:
        if verbose: ic(target)
        if path_exists(target):
            assert path_is_dir(target)
            free_space = disk_usage(target).free
            ic(free_space)
            if disk_usage(target).free >= min_free_space:
                yield target
            else:
                eprint("skipped:", target, "<", min_free_space)
    raise FileNotFoundError


#@attr.s(auto_attribs=True, kw_only=True)
#class Path_Iterator_Old():  # todo port features to python-getdents
#    path: str = attr.ib(converter=Path)
#    min_depth: int = 1
#    max_depth: object = inf
#    follow_symlinks: bool = False
#    return_dirs: bool = True
#    return_files: bool = True
#    return_symlinks: bool = True
#
#    def __attrs_post_init__(self):
#        self.root = self.path
#        if self.follow_symlinks:
#            assert not self.return_symlinks  # todo broken symlinks
#
#    def go(s):
#        depth = len(s.path.parts) - len(s.root.parts)  # len('/') == 1                                      # no fs syscalls
#        if depth >= s.min_depth:
#            if s.return_dirs and s.path.is_dir():                                                           # single stat()
#                if depth <= s.max_depth:
#                    yield s.path.absolute()                                                                 # no syscalls just looks to see if it starts with /
#            if s.return_files and not s.path.is_dir():  # dir/fifo/file/symlink/socket/reserved/char/block  # single stat()
#                if depth <= s.max_depth:
#                    yield s.path.absolute()
#
#        if depth > s.max_depth:
#            return
#        for sub in s.path.iterdir():                                                                        # 1 openat() 1 fstat() n getdents64() depending on dir size
#            depth = len(sub.parts) - len(s.root.parts)  # bug s.root is always '/'
#            if depth > s.max_depth:
#                return
#            if sub.is_symlink():  # must be before is_dir() # bug didnt check follow_symlinks
#                if s.return_files:
#                    yield sub.absolute()
#            elif sub.is_dir():
#                #print("could yield dir:", sub)
#                s.path = sub
#                yield from s.go()
#            else:
#                if s.return_files:
#                    yield sub.absolute()
#
#
#def all_files_iter(p):
#    if isinstance(p, str):
#        p = Path(p)
#    elif isinstance(p, bytes):
#        p = Path(p.decode())
#    assert isinstance(p, Path)
#    #print("yeilding p.absolute():", p.absolute())
#    yield bytes(p.absolute())
#    for sub in p.iterdir():
#        # eprint("sub:", sub)  # todo: read by terminal, so bell etc happens.... eprint bug?
#        if sub.is_symlink():  # must be before is_dir()
#            yield bytes(sub.absolute())
#        elif sub.is_dir():
#            yield from all_files_iter(sub)
#        else:
#            yield bytes(sub.absolute())
#
#
#def all_files(folder, files_only=False): # todo add flags for recursive, follow symlinks etc, return a generator
#    assert path_is_dir(folder)
#    all_files = []
#    for path, dirs, files in os.walk(folder):
#        for filename in files:
#            all_files.append(os.path.join(path, filename))
#        if not files_only:
#            for d in dirs:
#                all_files.append(os.path.join(path, d))
#    return all_files
#
#
#def count_entries(folder):  # fast, returns all types of objects in a folder
#    return len(os.listdir(folder))
#
#


def count_files(folder):  # calls lstat on every entry to see if its a file
    total = 0
    for root, dirs, files in os.walk(folder):
        total += len(files)
    return total
#
#
#def list_files(folder):
#    all_files = []
#    for root, dirs, files in os.walk(folder):
#        for ifile in files:
#            relative_file_path = root + b'/' + ifile
#            all_files.append(relative_file_path)
#    return set(all_files)


#def path_is_dir(path):
#    if os.path.isdir(path): #could still be a symlink
#        if os.path.islink(path):
#            return False
#        return True
#
#
#def path_is_dir_or_symlink_to_dir(path):
#    # unlike os.path.exists(False), os.path.isdir(False) returns False
#    if os.path.isdir(path): # returns False if it's a symlink to a file
#        return True
#    return False


def check_or_create_dir(folder, confirm=True):
    #assert isinstance(folder, bytes)
    if not os.path.isdir(folder):
        if confirm:
            eprint("The folder:")
            eprint(folder)
            eprint("does not exist. Type yes to create it and continue, otherwise exiting:")
            eprint("make dir:")
            eprint(folder, end=None)
            make_folder_answer = input(": ")
            if make_folder_answer.lower() != "yes":
                eprint("Exiting before mkdir.")
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
        eprint("Exception:", e)
        eprint("Unable to os.chdir(%s). Enxiting.", targetdir)
        os._exit(1)
    return True


def remove_empty_folders(path, remove_root=True, verbose=False):
    if not os.path.isdir(path):
        return

    # remove empty subfolders
    files = os.listdir(path)
    if len(files):
        for f in files:
            fullpath = os.path.join(path, f)
            if os.path.isdir(fullpath):
                if not os.path.islink(fullpath):
                    remove_empty_folders(fullpath)

    # if folder empty, delete it
    files = os.listdir(path)
    if len(files) == 0 and remove_root:
        if verbose:
            eprint("removing empty folder:", path)
        os.rmdir(path)

