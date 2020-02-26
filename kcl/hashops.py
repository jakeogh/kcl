#!/usr/bin/env python3

# pylint: disable=C0111     # docstrings are always outdated and wrong
# pylint: disable=W0511     # todo
# pylint: disable=R0902     # too many instance attributes
# pylint: disable=C0302     # too many lines in module
# pylint: disable=C0103     # single letter var names
# pylint: disable=R0911     # too many return statements
# pylint: disable=R0912     # too many branches
# pylint: disable=R0915     # too many statements
# pylint: disable=R0913     # too many arguments
# pylint: disable=R1702     # too many nested blocks
# pylint: disable=R0914     # too many local variables
# pylint: disable=R0903     # too few public methods
# pylint: disable=E1101     # no uhashfs member for base
# pylint: disable=W0201     # attribute defined outside __init__
# pylint: disable=W0703     # catching too general exception
from itertools import product
import attr
import os
import sys
import hashlib
import tempfile
import subprocess
from icecream import ic
from pathlib import Path
from requests.models import Response
from threading import Thread
from queue import Queue
from getdents import paths
from .printops import ceprint
from .printops import eprint
from .assertops import verify
from .pathops import path_is_file
from .iterops import compact


@attr.s(auto_attribs=True)
class WDgen():
    width: int
    depth: int

    def __attrs_post_init__(self):
        self.gen = product(range(self.width), range(self.depth))

    def go(self):
        for w, d in self.gen:
            if w == 0:
                continue
            if d == 0:
                continue
            else:
                yield (w, d)


def generate_hash(data, verbose=False):
    if not data:
        raise ValueError
    sha1 = hashlib.sha1()
    chunk_size = 128 * sha1.block_size  # 8MB
    return_dict = {}
    if isinstance(data, tempfile._TemporaryFileWrapper):
        filename = data.name
        with open(filename, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                sha1.update(chunk)
        return_dict['hash'] = sha1.hexdigest()
        return return_dict
    elif isinstance(data, Response):
        # todo make temp_folder configurable, make sure it exists
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.tmp', prefix='tmp-', dir='/var/tmp/iridb', delete=False) as temp_file:
            if verbose:
                #import IPython; IPython.embed()
                ceprint("data.url:", data.url)
            try:
                data_size_from_headers = int(data.headers['Content-Length'])
                #ceprint("data_size_from_headers:", data_size_from_headers)
            except KeyError:
                data_size_from_headers = False
            for chunk in data.iter_content(chunk_size):
                sha1.update(chunk)
                temp_file.write(chunk)
                current_file_size = int(os.path.getsize(temp_file.name))
                if data_size_from_headers:
                    eprint(temp_file.name,
                           str(int((current_file_size / data_size_from_headers) * 100)) + '%', current_file_size, data.url, end='\r', flush=True)
                else:
                    eprint(temp_file.name, current_file_size, data.url, end='\r', flush=True)

        current_file_size = int(os.path.getsize(temp_file.name))
        # update final size
        if data_size_from_headers:
            eprint(temp_file.name,
                   str(int((current_file_size / data_size_from_headers) * 100)) + '%', current_file_size, data.url, end='\r', flush=True)
        else:
            eprint(temp_file.name, current_file_size, data.url, end='\r', flush=True)

        if verbose: eprint('\n', end='')
        #eprint('finished writing temp_file:', temp_file.name)
        if os.path.getsize(temp_file.name) == 0:
            ceprint('content is zero bytes, raising FileNotFoundError')  # this happens
            raise FileNotFoundError
        return_dict['hash'] = sha1.hexdigest()
        assert return_dict['hash']
        return_dict['temp_file'] = temp_file
        return return_dict
    else:
        try:
            if len(data) == 0:
                # empty_hash = hashlib.sha1(data).hexdigest()
                ceprint("Error: you are attempting to hash a empty string.")
                raise FileNotFoundError
        except TypeError:
            raise FileNotFoundError

        if isinstance(data, str):
            return_dict['hash'] = hashlib.sha1(data.encode('utf-8')).hexdigest()
        else:
            return_dict['hash'] = hashlib.sha1(data).hexdigest()
        return return_dict


def sha1_hash_file(path, block_size=256*128*2, binary=False):
    sha1 = hashlib.sha1()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(block_size), b''):
            sha1.update(chunk)
    if binary:
        return sha1.digest()
    return sha1.hexdigest()


def sha3_256_hash_file(path, block_size=256*128*2, binary=False):
    sha3 = hashlib.sha3_256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(block_size), b''):
            sha3.update(chunk)
    if binary:
        return sha3.digest()
    return sha3.hexdigest()



def get_openssl_hash_algs_real():
    blacklist = set(['SHA', 'MD4', 'ecdsa-with-SHA1', 'DSA', 'DSA-SHA', 'MDC2'])
    results = []
    command = ' '.join(['openssl', 'list-message-digest-algorithms'])
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for index, line in enumerate(p.stdout.readlines()):
        if b'=>' not in line:
            line = line.strip()
#           line = line.lower()
            line = line[:]
            line = line.decode('ascii')
            results.append(line)
    return set(results) - blacklist


def get_openssl_hash_algs():
    return set(['SHA1', 'MD5', 'RIPEMD160', 'SHA256', 'SHA384', 'SHA512', 'whirlpool', 'SHA224'])


def read_blocks(filename):
    if filename == '-':
        f = sys.stdin
        # Python 3 compat: read binary instead of unicode
        if hasattr(f, 'buffer'):
            f = f.buffer
    else:
        f = open(filename, 'rb')
    try:
        megabyte = 2 ** 20
        while True:
            data = f.read(megabyte)
            if not data:
                break
            yield data
    finally:
        f.close()


# Calculate (multiple) digest(s) for file(s)
# Author: Peter Wu <peter@lekensteyn.nl>
# Licensed under the MIT license <http://opensource.org/licenses/MIT>
# http://unix.stackexchange.com/questions/163747/simultaneously-calculate-multiple-digests-md5-sha256
# https://git.lekensteyn.nl/scripts/tree/digest.py

class Hasher(object):
    '''Calculate multiple hash digests for a piece of data.'''
    def __init__(self, algos):
        self.algos = algos
        self._hashes = {}
        for algo in self.algos:
            self._hashes[algo] = getattr(hashlib, 'new')(algo)

    def update(self, data):
        for h in self._hashes:
            eprint(h)
            h.update(data)

    def hexdigests(self):
        '''Yields the algorithm and the calculated hex digest.'''
        for algo in self.algos:
            digest = self._hashes[algo].hexdigest()
            yield algo.lower(), digest

    def digests(self):
        '''Yields the algorithm and the calculated bytes digest.'''
        for algo in self.algos:
            digest = self._hashes[algo].digest()
            yield algo.lower(), digest


class MtHasher(Hasher):
    # Queue size. Memory usage is this times block size (1M)
    QUEUE_SIZE = 10

    def __init__(self):
        algos = get_openssl_hash_algs()
        #eprint("algos:", algos)
        super(MtHasher, self).__init__(algos)
        self._queues = {}
        self._threads = {}
        for algo in algos:
            t = Thread(target=self._queue_updater, args=(algo,), name=algo)
            self._queues[algo] = Queue(MtHasher.QUEUE_SIZE)
            self._threads[algo] = t
            t.start()

    def _queue_updater(self, algo):
        q = self._queues[algo]
        h = self._hashes[algo]
        while True:
            data = q.get()
            # Treat an empty value as terminator
            if not data:
                break
            h.update(data)

    def update(self, data):
        if data:
            for q in self._queues.values():
                q.put(data)

    def hexdigests(self):
        '''Wait until all calculations are done and yield hexdigests in the meantime.'''
        for algo in self.algos:
            q = self._queues[algo]
            q.put(b'')  # Terminate
            self._threads[algo].join()
            assert q.empty()
        return super(MtHasher, self).hexdigests()

    def digests(self):
        '''Wait until all calculations are done and yield digests in the meantime.'''
        for algo in self.algos:
            q = self._queues[algo]
            q.put(b'')  # Terminate
            self._threads[algo].join()
            assert q.empty()
        return super(MtHasher, self).digests()


def hash_file(file):
    hasher = MtHasher()
    '''Read the file and update the hash states.'''
    for data in read_blocks(file):
        hasher.update(data)
    return hasher


def hash_bytes(byte_string):
    if isinstance(byte_string, str):
        byte_string = byte_string.encode('UTF-8')
    hasher = MtHasher()
    '''encode unicode to UTF-8, read bytes and update the hash states. '''
    hasher.update(byte_string)
    return hasher


def bytes_dict_file(file):
    bytes_dict = {}
    hasher = hash_file(file)
    for algo, digest in hasher.digests():
        bytes_dict[algo] = digest
    return bytes_dict


def bytes_dict_bytes(byte_string):
    bytes_dict = {}
    hasher = hash_bytes(byte_string)
    for algo, digest in hasher.digests():
        bytes_dict[algo] = digest
    return bytes_dict


def hex_dict_file(file):
    bytes_dict = {}
    hasher = hash_file(file)
    for algo, digest in hasher.hexdigests():
        bytes_dict[algo] = digest
    return bytes_dict


def generate_algorithm_set():
    alg_set = set()
    algs = list(hashlib.algorithms_available)
    for alg in algs:
        if alg.startswith('sha3'):
            alg = alg.replace('-', '_')
        alg_set.add(alg)
    return list(alg_set)


def emptyhash(alg):
    emptydigest = getattr(hashlib, alg)(b'').digest()
    emptyhexdigest = emptydigest.hex()
    return emptyhexdigest


def shard(hexdigest, width, depth):
    return compact([hexdigest[i * width:width * (i + 1)]
                    for i in range(depth)] + [hexdigest])


def hexdigest_str_path(root: Path, hexdigest: str, width: int, depth: int) -> Path:
    paths = shard(hexdigest, width=width, depth=depth)
    rel_path = Path(os.path.join(*paths))
    path = root / rel_path
    return path



def detect_hash_tree_width_and_depth(root, alg, max_width=5, max_depth=5, verbose=False):
    verify(isinstance(root, Path))
    empty_hexdigest = emptyhash(alg)
    empty_hexdigest_length = len(empty_hexdigest)
    #empty_hexdigest_path = None
    width = 0
    depth = 0
    verify(alg == root.name)

    current_path = root
    while width < max_width:
        width += 1
        while depth < max_depth:
            depth += 1
            items = list(paths(path=current_path,
                               names_only=True,
                               return_dirs=True,
                               return_files=True,
                               return_symlinks=False,
                               min_depth=1, max_depth=0))
            if len(items[0]) != width:
                if len(items[0]) == empty_hexdigest_length:
                    return width, depth - 1
                break   # move to next width
            current_path = current_path / Path(os.fsdecode(items[0]))

    message = "Unable to detect width/depth."
    raise ValueError(message)

    #wdgen = WDgen(width=max_width, depth=max_depth).go()
    #while not empty_hexdigest_path:
    #    try:
    #        width, depth = next(wdgen)
    #    except StopIteration:
    #        message = "Unable to autodetect width/depth. Specify --width and --depth to create a new root."
    #        raise ValueError(message)

    #    path = hexdigest_str_path(root, empty_hexdigest, width=width, depth=depth)
    #    if path_is_file(path):
    #        empty_hexdigest_path = path

    #    verify(width > 0)
    #    verify(depth > 0)  # depth in theory could be zero, but then why use this?
    #    verify(width <= max_width)
    #    verify(depth <= max_depth)
    #    if verbose:
    #        eprint("width:", width)
    #        eprint("depth:", depth)

    #return width, depth

