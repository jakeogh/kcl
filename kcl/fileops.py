#!/usr/bin/env python3
# tab-width:4
# pylint: disable=missing-docstring

# MIT License
# https://github.com/jakeogh/dnsgate/blob/master/LICENSE
#
# common file functions

import time
import os
import shutil
import pprint
import psutil
from shutil import copyfileobj
import stat
from .printops import eprint

def all_files(folder):
    #all_files = [os.path.join(path, filename) for path, dirs, files in os.walk(folder) for filename in files]
    all_files = []
    for path, dirs, files in os.walk(folder):
        for filename in files:
            all_files.append(os.path.join(path, filename))
        for d in dirs:
            all_files.append(os.path.join(path, d))
    return all_files

def comment_out_line_in_file(file_path, line_to_match):
    '''
    add a # to the beginning of all instances of line_to_match
    iff there is not already a # preceding line_to_match and
        line_to_match is the only thing on the line
            except possibly a preceeding # and/or whitespace

    if line_to_match is found and all instances are commented return True
    if line_to_match is found and all instances already commented return True
    if line_to_match is not found return False
    '''
    with open(file_path, 'r') as rfh:
        lines = rfh.read().splitlines()
    newlines = []
    commented = False
    for line in lines:
        if line_to_match in line:
            line_stripped = line.strip()
            if line_stripped.startswith('#'):
                newlines.append(line)
                commented = True
                continue
            else:
                if line_stripped == line:
                    newlines.append('#' + line)
                    commented = True
                    continue
                else:
                    newlines.append(line)
                    continue
        else:
            newlines.append(line)
    if lines != newlines:
        with open(file_path, 'w') as rfh:
            rfh.write('\n'.join(newlines) + '\n')
        return True
    elif commented:
        return True
    return False

def uncomment_line_in_file(file_path, line_to_match):
    '''
    remove # from the beginning of all instances of line_to_match
    iff there is already a # preceding line_to_match and
        line_to_match is the only thing on the line
            except possibly a preceeding # and/or whitespace

    if line_to_match is found and all instances uncommented return True
    if line_to_match is found and all instances already uncommented return True
    if line_to_match is not found return False
    '''
    with open(file_path, 'r') as rfh:
        lines = rfh.read().splitlines()
    newlines = []
    uncommented = False
    for line in lines:
        if line_to_match in line:
            line_stripped = line.strip()
            if line_stripped.startswith('#'):
                newlines.append(line[1:])
                uncommented = True
                continue
            else:
                if line_stripped == line:
                    newlines.append(line)
                    uncommented = True
                    continue
                else:
                    newlines.append(line)
                    continue
        else:
            newlines.append(line)
    if lines != newlines:
        with open(file_path, 'w') as rfh:
            rfh.write('\n'.join(newlines) + '\n')
        return True
    if uncommented:
        return True
    return False

def write_unique_line_to_file(line, file_to_write):
    '''
    Write line to file_to_write iff line not in file_to_write.
    '''
    try:
        with open(file_to_write, 'r+') as fh:
            if line not in fh:
                fh.write(line)
    except FileNotFoundError:
        with open(file_to_write, 'a') as fh:
            fh.write(line)

def backup_file_if_exists(file_to_backup):
    timestamp = str(time.time())
    dest_file = file_to_backup + '.bak.' + timestamp
    try:
        with open(file_to_backup, 'r') as sf:
            with open(dest_file, 'x') as df:
                copyfileobj(sf, df)
    except FileNotFoundError:
        pass    # skip backup if file does not exist

def read_file_bytes(path):
    with open(path, 'rb') as fh:
        file_bytes = fh.read()
    return file_bytes

def read_file_bytes_or_exit(infile):
    try:
        with open(infile,'rb') as string_fh:
            string = string_fh.read()
            if len(string) == 0:
                eprint("Error, read empty file: " + infile)
            return string
    except Exception as e:
        eprint("Got Exception: %s", e)
        eprint("Unable to read file:", infile, "Exiting.")

def path_exists(path):
    return os.path.lexists(path) #returns True for broken symlinks

def file_exists(infile):
    if os.path.isfile(infile): #unlike os.path.exists(False), os.path.isfile(False) returns False so no need to call path_exists() first.
        return True
    return False

def file_exists_nonzero(infile):
    if file_exists(infile):
        if not empty_file(infile):
            return True
    return False

def path_is_block_special(path):
    if path_exists(path):
        mode = os.stat(path).st_mode
        if stat.S_ISBLK(mode):
            return True
        else:
            return False
    else:
        return False


def get_file_size(filename):
    fd = os.open(filename, os.O_RDONLY)
    try:
        return os.lseek(fd, 0, os.SEEK_END)
    finally:
        os.close(fd)

#def is_zero_length_file(fpath): # prob should be called "empty_file()"
def empty_file(fpath):
    if os.path.isfile(fpath):
        if os.path.getsize(fpath) == 0:
            return True
    return False

def make_file_immutable(infile):
    command = "sudo /usr/bin/chattr +i " + infile
    os.system(command)
    result_command = "/usr/bin/lsattr " + infile
    result = os.popen(result_command).read()
    if result[4] != 'i':
        eprint('make_file_immutable(%s) failed. Exiting')
        os._exit(1)
    else:
        return True

def rename_or_exit(src, dest):
    try:
        os.rename(src, dest)
    except Exception as e:
        eprint("Got Exception: %s", e)
        eprint("Unable to rename src: %s to dest: %s Exiting.", src, dest)
        os._exit(1)

def move_file_only_if_new_or_exit(source, dest):
    try:
        shutil.move(source, dest)   #todo: fix race condition beacuse shutil.move overwrites existing dest
    except Exception as e:
        eprint("Exception: %s", e)
        eprint("move_file_only_if_new_or_exit(): error. Exiting.")
        os._exit(1)

def make_file_only_if_new(infile, data):
    assert len(data) > 0
    if file_exists(infile):
        raise FileExistsError
    write_file(infile, data)
    return True

def make_file_only_if_new_or_exit(infile, data):
    try:
        make_file_only_if_new(infile, data)
        return True
    except Exception as e:
        #print_traceback()
        eprint("Got Exception: %s", e)
        eprint("Problem writing file: %s Exiting.", infile)
        os._exit(1)
    else:
        return False

def write_file(infile, data):
    #On Py3 we have one text type, str which holds Unicode data and two byte types; bytes and bytearray.
    if isinstance(data, str): #unicode in py3
        with open(infile, "x", encoding='utf-8') as fd:
            fd.write(data)
    elif isinstance(data, bytes):
        with open(infile, "bx") as fd:
            fd.write(data)
    else:
        eprint("Unknown type for data: %s. Could not create python file descriptor: %s Exiting.", type(data), infile)
        os._exit(1)


def is_regular_file(path):
    mode = os.stat(path)[ST_MODE]
    if S_ISREG(mode):
        return True
    else:
        return False


if __name__ == '__main__':
    quit(0)

# todo
# https://github.com/MostAwesomeDude/betterpath/blob/master/bp/filepath.py
# https://github.com/twisted/twisted/blob/trunk/twisted/python/filepath.py
