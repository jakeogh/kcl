#!/usr/bin/env python3
# tab-width:4
# pylint: disable=missing-docstring

# MIT License
# https://github.com/jakeogh/dnsgate/blob/master/LICENSE
#
# common file functions
__version__ = "0.0.1"

import time
import os
import shutil
import pprint
import psutil
from shutil import copyfileobj
import subprocess
import stat

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
    dest_file = file_to_backup.name + '.bak.' + timestamp
    try:
        with open(file_to_backup.name, 'r') as sf:
            with open(dest_file, 'x') as df:
                copyfileobj(sf, df)
    except FileNotFoundError:
        pass    # skip backup if file does not exist

def read_file_bytes(path):
    with open(path, 'rb') as fh:
        file_bytes = fh.read()
    return file_bytes

def read_file_bytes_or_exit(file):
    try:
        with open(file,'rb') as string_fh:
            string = string_fh.read()
            if len(string) == 0:
                logger.error("Error, read empty file: " + file)
            return string
    except Exception as e:
        logger.error("Got Exception: %s", e)
        logger.error("Unable to read file: %s Exiting.", file)

def path_exists(path):
    return os.path.lexists(path) #returns True for broken symlinks

def file_exists(file):
    if os.path.isfile(file): #unlike os.path.exists(False), os.path.isfile(False) returns False so no need to call path_exists() first.
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

def block_special_path_is_mounted(path):
    string_to_match = path + ' on'
    assert path_is_block_special(path)
    mount_output = subprocess.getoutput("mount")
    #print(mount_output)
    if string_to_match in mount_output:
        return True
    return False

def path_is_mounted(path):
    string_to_match = 'on ' + path + ' '
    #assert path_is_block_special(path)
    mount_output = subprocess.getoutput("mount")
    #print(mount_output)
    if string_to_match in mount_output:
        return True
    return False

def get_file_size(filename):
    fd = os.open(filename, os.O_RDONLY)
    try:
        return os.lseek(fd, 0, os.SEEK_END)
    finally:
        os.close(fd)

#def is_zero_length_file(fpath): # prob should be called "empty_file()"
def empty_file(fpath): # prob should be called "empty_file()"
    if os.path.isfile(fpath):
        if os.path.getsize(fpath) == 0:
            return True
    return False

def make_file_immutable(file):
    command = "sudo /usr/bin/chattr +i " + file
    os.system(command)
    result_command = "/usr/bin/lsattr " + file
    result = os.popen(result_command).read()
    if result[4] != 'i':
        cprint('make_file_immutable(%s) failed. Exiting')
        os._exit(1)
    else:
        return True


@log_prefix
def rename_or_exit(src, dest):
    try:
        os.rename(src, dest)
    except Exception as e:
        logger.error("Got Exception: %s", e)
        logger.error("Unable to rename src: %s to dest: %s Exiting.", src, dest)
        os._exit(1)

@log_prefix
def move_file_only_if_new_or_exit(source, dest):
    try:
        shutil.move(source, dest)   #todo: fix race condition beacuse shutil.move overwrites existing dest
    except Exception as e:
        logger.error("Exception: %s", e)
        logger.error("move_file_only_if_new_or_exit(): error. Exiting.")
        os._exit(1)




if __name__ == '__main__':
    quit(0)

