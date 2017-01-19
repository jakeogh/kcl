#!/usr/bin/env python3
# tab-width:4
# pylint: disable=missing-docstring

# MIT License
# https://github.com/jakeogh/dnsgate/blob/master/LICENSE
#
# common symlink functions
__version__ = "0.0.1"

from kcl.printops import LOG
from kcl.printops import eprint
from kcl.fileops import path_exists
import os

def symlink_or_exit(target, link_name):
    try:
        os.symlink(target, link_name)
    except Exception as e:
        print("Got Exception: %s", e)
        print("Unable to symlink link_name: %s to target: %s Exiting." % (link_name, target))
        os._exit(1)

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
    target = os.path.abspath(target)
    link_name = os.path.abspath(link_name)
    if not path_exists(target):
        eprint('target: %s does not exist. Refusing to make broken symlink. Exiting.',
            target, level=LOG['ERROR'])
        quit(1)

    if is_broken_symlink(link_name):
        eprint('ERROR: %s exists as a broken symlink. ' +
            'Remove it before trying to make a new symlink. Exiting.',
            link_name, level=LOG['ERROR'])
        quit(1)

    link_name_folder = '/'.join(link_name.split('/')[:-1])
    if not os.path.isdir(link_name_folder):
        eprint('link_name_folder: %s does not exist. Exiting.',
            link_name_folder, level=LOG['ERROR'])
        quit(1)

    relative_target = os.path.relpath(target, link_name_folder)
    os.symlink(relative_target, link_name)

def symlink_destination(link):
    """
    Return absolute path for the destination of a symlink. This prob should be split into "first dest" and "final dest"
    """
    assert (os.path.islink(link))
    p = link
    while os.path.islink(p):
        p = os.path.normpath(os.readlink(link))
        #cprint("p:", p)
        if os.path.isabs(p):
            #cprint("returning p:", p)
            return p
        else:
            #cprint("in else p:", p)
            p = os.path.join(os.path.dirname(link), p)
            #cprint("in else p:", p)
            #cprint("looping again")
    #return os.path.join(os.path.dirname(link), p)
    #dest = os.path.normpath(p) #prepends extra /home/user
    dest = os.path.realpath(p)
    #cprint("dest:", dest)
    return dest

@log_prefix(log_level='DEBUG')
def readlinkf(path):
        p = subprocess.Popen(['readlink', '-f', path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        readlink_output, errors = p.communicate()
        readlink_output_clean = readlink_output.strip()
        if errors:
                cprint(errors)
        else:
                return readlink_output_clean

@log_prefix(log_level='DEBUG')
def get_symlink_target(symlink_file):
        #print(symlink_file)
        assert isinstance(symlink_file, str)
        if os.path.islink(symlink_file):
                target = os.readlink(symlink_file)
                target_joined = os.path.join(os.path.dirname(symlink_file), target)
                target_file = readlinkf(target_joined).decode('UTF-8')
        else:
                target_file = readlinkf(symlink_file).decode('UTF-8')
        #print("target_file:", target_file)
        return target_file

@log_prefix(log_level='DEBUG')
def symlink_or_exit(target, link_name, hash_folder=''):
    if hash_folder != '':
        os.chdir(hash_folder)
    try:
        os.symlink(target, link_name)
    except Exception as e:
        logger.error("Got Exception: %s", e)
        logger.error("Unable to symlink link_name: %s to target: %s Exiting.", link_name, target)
        if len(error_msg) > 0:
            logger.error("PRINTING ERROR MESSAGE...")
            logger.error(error_msg)
        os._exit(1)




if __name__ == '__main__':
    quit(0)
