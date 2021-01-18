#!/usr/bin/env python3
# tab-width:4
# pylint: disable=missing-docstring

# MIT License
# https://github.com/jakeogh/dnsgate/blob/master/LICENSE
#
# common file functions

# pylint: disable=C0111  # docstrings are always outdated and wrong
# pylint: disable=W0511  # todo is encouraged
# pylint: disable=C0301  # line too long
# pylint: disable=R0902  # too many instance attributes
# pylint: disable=C0302  # too many lines in module
# pylint: disable=C0103  # single letter var names, func name too descriptive
# pylint: disable=R0911  # too many return statements
# pylint: disable=R0912  # too many branches
# pylint: disable=R0915  # too many statements
# pylint: disable=R0913  # too many arguments
# pylint: disable=R1702  # too many nested blocks
# pylint: disable=R0914  # too many local variables
# pylint: disable=R0903  # too few public methods
# pylint: disable=E1101  # no member for base
# pylint: disable=W0201  # attribute defined outside __init__


import errno
import fcntl
import os
import shutil
import stat
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from shutil import copyfileobj

import magic  # sys-apps/file  #PIA
from icecream import ic
from retry_on_exception import retry_on_exception

from .assertops import verify
from .pathops import path_exists, path_is_file
from .printops import eprint


def comment_out_line_in_file(*,
                             file_path,
                             line_to_match,
                             verbose: bool,
                             debug: bool,):
    '''
    add a # to the beginning of all instances of line_to_match
    iff there is not already a # preceding line_to_match and
        line_to_match is the only thing on the line
            except possibly a preceeding # and/or whitespace

    if line_to_match is found and all instances are commented return True
    if line_to_match is found and all instances already commented return True
    if line_to_match is not found return False
    '''
    with open(file_path, 'r') as rfh:  # bug should hold the fh
        lines = rfh.read().splitlines()
    newlines = []
    #commented = False
    for line in lines:
        if line_to_match in line:
            line_stripped = line.strip()
            if line_stripped.startswith('#'):
                newlines.append(line)
                #commented = True
                continue
            if line_stripped == line:
                newlines.append('#' + line)
                #commented = True
                continue
            newlines.append(line)
            continue
        newlines.append(line)
    if lines != newlines:
        with open(file_path, 'w') as rfh:
            rfh.write('\n'.join(newlines) + '\n')
        return True
    return True


def uncomment_line_in_file(*,
                           file_path,
                           line_to_match,
                           verbose: bool,
                           debug: bool,):
    '''
    remove # from the beginning of all instances of line_to_match
    iff there is already a # preceding line_to_match and
        line_to_match is the only thing on the line
            except possibly a preceeding # and/or whitespace

    if line_to_match is found and all instances uncommented return True
    if line_to_match is found and all instances already uncommented return True
    if line_to_match is not found return False
    '''
    with open(file_path, 'r') as rfh:  # bug should hold the fh
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
            if line_stripped == line:
                newlines.append(line)
                uncommented = True
                continue
            newlines.append(line)
            continue
        newlines.append(line)
    if lines != newlines:
        with open(file_path, 'w') as rfh:
            rfh.write('\n'.join(newlines) + '\n')
        return True
    if uncommented:
        return True
    return False


@retry_on_exception(exception=OSError,
                    errno=errno.ENOSPC,)
def write_line_to_file(*,
                       line,
                       file_to_write,
                       verbose: bool,
                       debug: bool,
                       unique: bool = False,
                       make_new: bool = True,):
    '''
    Write line to file_to_write
    if unique_line == True, write line iff line not in file_to_write.
    '''
    if isinstance(line, str):
        line = line.encode('UTF8')
    assert isinstance(line, bytes)
    assert line.count(b'\n') == 1
    assert line.endswith(b'\n')

    try:
        with open(file_to_write, 'rb+') as fh:
            if not unique:
                fh.write(line)
                return True

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


#def write_unique_line_to_file(line, file_to_write, make_new=True):
#    if isinstance(line, str):
#        line = line.encode('UTF8')
#    assert isinstance(line, bytes)
#    assert line.count(b'\n') == 1
#    assert line.endswith(b'\n')
#    '''
#    Write line to file_to_write iff line not in file_to_write.
#    '''
#    try:
#        with open(file_to_write, 'rb+') as fh:
#            if line not in fh:
#                fh.write(line)
#                return True
#            return False
#    except FileNotFoundError as e:
#        if make_new:
#            with open(file_to_write, 'xb') as fh:
#                fh.write(line)
#                return True
#        else:
#            raise e


def line_exists_in_file(*,
                        line,
                        file_to_check,
                        verbose: bool,
                        debug: bool,):
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


def file_exists_nonzero(infile):
    if path_is_file(infile):
        if not empty_file(infile):
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
# https://stackoverflow.com/questions/1430446/create-a-temporary-fifo-named-pipe-in-python
@contextmanager
def temp_fifo(verbose=False):
    """Context Manager for creating named pipes with temporary names."""
    tmpdir = tempfile.mkdtemp()
    filename = os.path.join(tmpdir, 'fifo')  # Temporary filename
    if verbose:
        ic(filename)
    os.mkfifo(filename)  # Create FIFO
    try:
        yield filename
    finally:
        os.unlink(filename)  # Remove file
        os.rmdir(tmpdir)  # Remove directory

