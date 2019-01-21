#!/usr/bin/env python3
# tab-width:4
# pylint: disable=missing-docstring

# MIT License
# https://github.com/jakeogh/dnsgate/blob/master/LICENSE
#
# common symlink functions
__version__ = "0.0.1"

from kcl.printops import ceprint
from kcl.fileops import path_exists
import os
import subprocess


def is_symlink(infile):
    if os.path.islink(infile):
        return True
    return False


def is_symlink_to_dir(link):
    if os.path.islink(link):
        return os.path.isdir(link)


def is_broken_symlink(path):
    if os.path.islink(path): # path is a symlink
        return not os.path.exists(path) # returns False for broken symlinks
    return False # path isnt a symlink


def is_unbroken_symlink(path):
    if os.path.islink(path): # path is a symlink
        return os.path.exists(path) # returns False for broken symlinks
    return False # path isnt a symlink


def get_symlink_abs_target(link): # assumes link is unbroken
    target = os.readlink(link)
    target_joined = os.path.join(os.path.dirname(link), target)
    target_file = os.path.realpath(target_joined)
    return target_file


def is_unbroken_symlink_to_target(target, link):    #bug, should not assume unicode paths
    if is_unbroken_symlink(link):
        link_target = get_symlink_abs_target(link)
        if link_target == target:
            return True
    return False


def create_relative_symlink(target, link_name):
    assert '/mnt/t420s_256GB_samsung_ssd_S2R5NX0J707260P/' not in link_name
    ceprint("(b4 abspath) target:", target)
    ceprint("os.path.realpath(target):", os.path.realpath(target))
    ceprint("(b4 abspath) link_name:", link_name)
    target_abspath = os.path.abspath(target)
    target_realpath = os.path.realpath(target)
    link_name = os.path.abspath(link_name) # by expectation, this does not exist yet
                                           # it depends on cwd if its a relative path
    ceprint("target_abspath:", target_abspath)
    ceprint("target_realpath:", target_realpath)
    ceprint("link_name:", link_name)
    #assert '/mnt/t420s_256GB_samsung_ssd_S2R5NX0J707260P/' not in link_name

    #redunt check left in after switching from abspath to realpath on the target
    if not path_exists(target_abspath):
        ceprint('target_abspath:', target_abspath, 'does not exist. Refusing to make broken symlink. Exiting.')
        quit(1)

    if not path_exists(target_realpath):
        ceprint('target_realpath:', target_realpath, 'does not exist. Refusing to make broken symlink. Exiting.')
        quit(1)

    if is_broken_symlink(link_name):
        ceprint('ERROR:', link_name, 'exists as a broken symlink. ' +
            'Remove it before trying to make a new symlink. Exiting.')
        quit(1)

    link_name_folder = '/'.join(link_name.split('/')[:-1])
    if not os.path.isdir(link_name_folder):
        ceprint('link_name_folder:', link_name_folder, 'does not exist. Exiting.')
        quit(1)

    relative_target = os.path.relpath(target_realpath, link_name_folder) # relpath does not access the filesystem
    ceprint("relative_target:", relative_target)
    assert '/home/user/.iridb/database.local/' not in relative_target
    raw_input("Press Enter to continue ...")
    os.symlink(relative_target, link_name)


def symlink_destination(link): #broken for multi level symlinks
    #ceprint(link)
    """
    Return absolute path for the destination of a symlink. This prob should be split into "first dest" and "final dest"
    """
    #assert (os.path.islink(link))
    p = link
    while os.path.islink(p):
        p = os.path.normpath(os.readlink(link))  # huah?
        if os.path.isabs(p):
            return p
        else:
            p = os.path.join(os.path.dirname(link), p)
    dest = os.path.realpath(p)
    return dest


def readlinkf(path): # ugly
        p = subprocess.Popen(['readlink', '-f', path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        readlink_output, errors = p.communicate()
        readlink_output_clean = readlink_output.strip()
        if errors:
            ceprint(errors)
        else:
            return readlink_output_clean


def get_symlink_target_next(path):
        assert os.path.islink(path)
        target = os.readlink(path)
        return target


def get_symlink_target_final(path): #broken for bytes
        if os.path.islink(path):
            target = os.readlink(path)
            target_joined = os.path.join(os.path.dirname(path), target)
            target_file = readlinkf(target_joined).decode('UTF-8')
        else:
            target_file = readlinkf(path).decode('UTF-8')
        #print("target_file:", target_file)
        return target_file


def symlink_or_exit(target, link_name):
    try:
        os.symlink(target, link_name)
    except Exception as e:
        print("Got Exception: %s", e)
        print("Unable to symlink link_name: %s to target: %s Exiting." % (link_name, target))
        os._exit(1)


#def symlink_or_exit(target, link_name, hash_folder=''):
#    if hash_folder != '':
#        os.chdir(hash_folder)
#    try:
#        os.symlink(target, link_name)
#    except Exception as e:
#        ceprint("Got Exception:", e)
#        ceprint("Unable to symlink link_name:", link_name, "to target:", target, "Exiting.")
#        os._exit(1)
