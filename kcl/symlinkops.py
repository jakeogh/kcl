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

def calculate_relative_symlink_dest(target, link_name):
    assert '/mnt/t420s_256GB_samsung_ssd_S2R5NX0J707260P/' not in link_name
    ceprint("target:", target)
    assert not target.startswith('../')
    # got relative target, that's hard to deal with
    # pass in a fully qualified path, if it's also
    # an existing stmlink, detect that here and dont call realpath()
    # call something that gets the realpath but does not follow any links

    if is_unbroken_symlink(target):
        # the targt is also a symlink, dont resolve it, just get it's abspath
        target_realpath = os.path.abspath(target)
        # still a problem, since this was not fully resolved, it may still have symlinks embedded in it
        # get the folder, resolve that since it's guranteed not to be a symlink
        target_realpath_folder = '/'.join(target_realpath.split('/')[:-1])
        ceprint("target_realpath_folder:", target_realpath_folder)
        target_realpath_file = target_realpath.split('/')[-1]
        ceprint("target_realpath_file:", target_realpath_file)
        target_realpath_folder_realpath = os.path.realpath(target_realpath_folder)
        target_realpath = os.path.join(target_realpath_folder_realpath, target_realpath_file)
        # uug. ok now.
    elif path_exists(target):
        #target is prob a file or dir, could still be a broken symlink
        target_realpath = os.path.realpath(target)
    elif is_broken_symlink(link_name):
        assert False
    else:
        assert False

    #target_realpath = os.path.realpath(target) # realpath() does not require the file to exist will still resolve symlinks
    ceprint("target_realpath:", target_realpath)
    ceprint("link_name:", link_name)

    # if its a unbroken symlink, and this is being used to see if its the shortest dest
    # os.path.realpath() cant be called, because it resolves the existing link to the target
    if is_broken_symlink(link_name):
        link_name_realpath = os.path.realpath(link_name)
        ceprint("link_name_realpath:", link_name_realpath)
    elif not path_exists(link_name):
        link_name_realpath = os.path.realpath(link_name)
        ceprint("link_name_realpath:", link_name_realpath)

    elif is_unbroken_symlink(link_name):
        link_name_realpath = os.path.abspath(link_name)
        ceprint("link_name_realpath: (abspath)", link_name_realpath)
        # at this point, all is still not well.
        # link_name_realpath was actually constructed by abspath()
        # so if its really on a different filesystem, the link
        # might not reflect that.
        # the solution is to call realpath() on link_name_realpath_folder
        # since its not a symlink, this will work as expected
    else:
        assert False

    if not path_exists(target_realpath):
        ceprint('target_realpath:', target_realpath, 'does not exist. Refusing to make broken symlink. Exiting.')
        quit(1)


    if is_broken_symlink(link_name_realpath):
        ceprint('link_name_realpath:', link_name_realpath, 'exists as a broken symlink. ' +
            'Remove it before trying to make a new symlink. Exiting.')
        quit(1)

    #link_name_abspath_folder = '/'.join(link_name_abspath.split('/')[:-1])
    #ceprint("link_name_abspath_folder:", link_name_abspath_folder)

    link_name_realpath_folder = '/'.join(link_name_realpath.split('/')[:-1])
    ceprint("link_name_realpath_folder:", link_name_realpath_folder)
    link_name_realpath_folder_realpath = os.path.realpath(link_name_realpath_folder)
    ceprint("link_name_realpath_folder_realpath:", link_name_realpath_folder_realpath)
    if not os.path.isdir(link_name_realpath_folder_realpath):
        ceprint('link_name_realpath_folder_realpath:', link_name_realpath_folder_realpath, 'does not exist. Exiting.')
        quit(1)

    relative_target = os.path.relpath(target_realpath, link_name_realpath_folder_realpath) # relpath does not access the filesystem
    ceprint("relative_target:", relative_target)
    assert '/home/user/.iridb/database.local/' not in relative_target
    assert '/mnt/t420s_256GB_samsung_ssd_S2R5NX0J707260P/' not in relative_target
    return relative_target


def create_relative_symlink(target, link_name):
    relative_target = calculate_relative_symlink_dest(target, link_name)
    link_name_realpath = os.path.realpath(link_name)
    os.symlink(relative_target, link_name_realpath)


def symlink_destination(link): #broken for multi level symlinks
    return os.path.realpath(link)
    #ceprint("this function is unreliable. fix it. it can loop forever.")
    #ceprint(link)
    #"""
    #Return absolute path for the destination of a symlink. This prob should be split into "first dest" and "final dest"
    #"""
    ##assert (os.path.islink(link))
    #p = link
    #while os.path.islink(p):
    #    p = os.path.normpath(os.readlink(link))  # huah?
    #    if os.path.isabs(p):
    #        return p
    #    else:
    #        p = os.path.join(os.path.dirname(link), p)
    #dest = os.path.realpath(p)
    #return dest


def readlinkf(path): # ugly
        p = subprocess.Popen(['readlink', '-f', path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        readlink_output, errors = p.communicate()
        readlink_output_clean = readlink_output.strip()
        if errors:
            ceprint(errors)
        else:
            return readlink_output_clean


def get_abs_path_of_first_symlink_target(path):
    ceprint("path:", path)
    link_target = os.readlink(path)
    ceprint("link_target:", link_target)
    #assert link_target
    link_dir = os.path.dirname(path)
    link_first_target_abs = os.path.join(link_dir, link_target)
    #ceprint(link_first_target_abs)
    link_first_target_abs_normpath = os.path.normpath(link_first_target_abs)
    #ceprint(link_first_target_abs_normpath)
    link_first_target_abs_normpath_abspath = os.path.abspath(link_first_target_abs_normpath)
    ceprint("link_first_target_abs_normpath_abspath:", link_first_target_abs_normpath_abspath)
    return link_first_target_abs_normpath_abspath


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
