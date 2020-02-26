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
from pathlib import Path
from shutil import copyfileobj
import stat
import fcntl
from .printops import eprint
from .assertops import verify
import magic  # sys-apps/file  #PIA


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


def write_unique_line_to_file(line, file_to_write, make_new=True):
    if isinstance(line, str):
        line = line.encode('UTF8')
    assert isinstance(line, bytes)
    assert line.count(b'\n') == 1
    assert line.endswith(b'\n')
    '''
    Write line to file_to_write iff line not in file_to_write.
    '''
    try:
        with open(file_to_write, 'rb+') as fh:
            if line not in fh:
                fh.write(line)
                return True
            return False
    except FileNotFoundError as e:
        if make_new:
            with open(file_to_write, 'xb') as fh:
                fh.write(line)
                return True
        else:
            raise e


def line_exists_in_file(line, file_to_check):
    if isinstance(line, str):
        line = line.encode('UTF8')
    assert isinstance(line, bytes)
    assert line.count(b'\n') == 1
    assert line.endswith(b'\n')
    with open(file_to_check, 'rb') as fh:
        if line in fh:
            return True
        return False


def backup_file_if_exists(file_to_backup):
    timestamp = str(time.time())
    dest_file = file_to_backup + '.bak.' + timestamp
    try:
        with open(file_to_backup, 'rb') as sf:
            with open(dest_file, 'xb') as df:
                copyfileobj(sf, df)
    except FileNotFoundError:
        pass    # skip backup if file does not exist


def read_file_bytes(path):
    with open(path, 'rb') as fh:
        file_bytes = fh.read()
    return file_bytes


def path_exists(path):
    #return os.lastat(path)  # faster?
    return os.path.lexists(path) #returns True for broken symlinks


def path_is_file(path: Path):
    verify(isinstance(path, Path))
    if path.is_symlink():
        return False
    if os.path.isfile(path): #unlike os.path.exists(False), os.path.isfile(False) returns False so no need to call path_exists() first.
        return True
    return False


def file_exists_nonzero(infile):
    if path_is_file(infile):
        if not empty_file(infile):
            return True
    return False


def path_is_block_special(path, follow_symlinks=False):
    if path_exists(path):
        mode = os.stat(path, follow_symlinks=follow_symlinks).st_mode
        if stat.S_ISBLK(mode):
            return True
    return False


def get_block_device_size(device):
    assert Path(device).is_block_device()
    fd = os.open(device, os.O_RDONLY)
    try:
        return os.lseek(fd, 0, os.SEEK_END)
    finally:
        os.close(fd)


def get_file_size(filename):
    filename = Path(filename)
    size = filename.lstat().st_size
    #size = os.path.getsize(filename)
    return size


def points_to_data(fpath, empty_ok=False):
    assert isinstance(fpath, (str, bytes, Path))
    try:
        size = os.path.getsize(fpath)  # annoyingly, os.stat(False) == os.stat(0) == os.stat('/dev/stdout')
    except FileNotFoundError:
        return False
    if empty_ok:
        return True
    if size > 0:
        return True
    return False


def empty_file(fpath):
    if not path_exists(fpath):
        #return True #hm
        raise FileNotFoundError
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


def write_file(infile, data):
    assert len(data) > 0
    #On Py3 we have one text type, str which holds Unicode data and two byte types; bytes and bytearray.
    if isinstance(data, str): #unicode in py3
        with open(infile, "x", encoding='utf-8') as fd:
            fd.write(data)
    elif isinstance(data, bytes):
        with open(infile, "xb") as fd:
            fd.write(data)
    else:
        eprint("Unknown type for data: %s. Could not create python file descriptor: %s Exiting.", type(data), infile)
        os._exit(1)


def is_regular_file(path):
    mode = os.stat(path, follow_symlinks=False)[stat.ST_MODE]
    if stat.S_ISREG(mode):
        return True
    return False


def get_file_type(path):
    line_id = magic.from_file(path)
    return line_id


def combine_files(source, destination, buffer=65535):
    verify(is_regular_file(source))
    verify(is_regular_file(destination))
    with open(source, "rb") as sfh:
        fcntl.flock(sfh, fcntl.LOCK_SH)
        with open(destination, "ab") as dfh:
            fcntl.flock(dfh, fcntl.LOCK_EX)
            while True:
                data = sfh.read(buffer)
                if data:
                    dfh.write(data)
                else:
                    break


# todo
# https://github.com/MostAwesomeDude/betterpath/blob/master/bp/filepath.py
# https://github.com/twisted/twisted/blob/trunk/twisted/python/filepath.py
