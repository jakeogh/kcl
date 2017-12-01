#!/usr/bin/env python3

import hashlib
import os
import tempfile
#import requests
from requests.models import Response
from .printops import eprint


def generate_hash(data, verbose=False):
    sha1 = hashlib.sha1()
    chunk_size = 128 * sha1.block_size  #8MB
    return_dict = {}
    if isinstance(data, tempfile._TemporaryFileWrapper):
        filename = data.name
        with open(filename, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                sha1.update(chunk)
        return_dict['hash'] = sha1.hexdigest()
        return return_dict
    #if isinstance(data, requests.models.Response):
    if isinstance(data, Response):
        #todo make temp_folder configurable, make sure it exists
        temp_file = tempfile.NamedTemporaryFile(mode='wb', suffix='.tmp', prefix='tmp-', dir='/var/tmp/iridb', delete=False)
        if verbose:
            #import IPython; IPython.embed()
            #eprint(data.url)
            try:
                data_size = int(data.headers['Content-Length'])
            except KeyError:
                data_size = False
            #eprint("data_size:", data_size)
        for chunk in data.iter_content(chunk_size):
            sha1.update(chunk)
            temp_file.write(chunk)
            current_file_size = int(os.path.getsize(temp_file.name))
            if data_size:
                eprint(temp_file.name, str(int((current_file_size/data_size)*100))+'%', current_file_size, data.url, end='\r', flush=True)
            else:
                eprint(temp_file.name, current_file_size, data.url, end='\r', flush=True)
        temp_file.close()
        if verbose: eprint('\n', end='')
        #eprint('finished writing temp_file: %s', temp_file.name)
        if os.path.getsize(temp_file.name) == 0:
            #eprint('content is zero bytes, returning False')        #this happens
            return False
        return_dict['hash'] = sha1.hexdigest()
        return_dict['temp_file'] = temp_file
        return return_dict
    if len(data) == 0:
        empty_hash = hashlib.sha1(data).hexdigest()
        #eprint("Error: you are attempting to hash a empty string.")
        raise FileNotFoundError
    if type(data) is str:
        return_dict['hash'] = hashlib.sha1(data.encode('utf-8')).hexdigest()
    else:
        return_dict['hash'] = hashlib.sha1(data).hexdigest()
    return return_dict

def sha1_hash_file(path, block_size=256*128*2):
    sha1 = hashlib.sha1()
    with open(path,'rb') as f:
        for chunk in iter(lambda: f.read(block_size), b''):
            sha1.update(chunk)

    return sha1.hexdigest()

# Calculate (multiple) digest(s) for file(s)
# Author: Peter Wu <peter@lekensteyn.nl>
# Licensed under the MIT license <http://opensource.org/licenses/MIT>
# http://unix.stackexchange.com/questions/163747/simultaneously-calculate-multiple-digests-md5-sha256
# https://git.lekensteyn.nl/scripts/tree/digest.py

import hashlib
import sys
from threading import Thread
import subprocess
from queue import Queue
from kcl.printops import eprint

def get_openssl_hash_algs():
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
        '''
        Wait until all calculations are done and yield hexdigests in the meantime.
        '''
        for algo in self.algos:
            q = self._queues[algo]
            q.put(b'')  # Terminate
            self._threads[algo].join()
            assert q.empty()
        return super(MtHasher, self).hexdigests()

    def digests(self):
        '''
        Wait until all calculations are done and yield digests in the meantime.
        '''
        for algo in self.algos:
            q = self._queues[algo]
            q.put(b'')  # Terminate
            self._threads[algo].join()
            assert q.empty()
        return super(MtHasher, self).digests()

def hash_file(file):
    hasher = MtHasher()
    '''
    Read the file and update the hash states.
    '''
    try:
        for data in read_blocks(file):
            hasher.update(data)
    except OSError as e:
        eprint('digest: {0}: {1}'.format(file, e.strerror))
        quit(1)
    return hasher

def hash_bytes(byte_string):
    if isinstance(byte_string, str):
        byte_string = byte_string.encode('UTF-8')

    hasher = MtHasher()
    '''
    encode unicode to UTF-8, read bytes
    and update the hash states.
    '''
    try:
        hasher.update(byte_string)
    except Exception as e:
        eprint(e)
        quit(1)
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


if __name__ == '__main__':
    filename = sys.argv[1]

    hasher = hash_file(filename)
    for algo, digest in hasher.hexdigests():
        eprint('{0} {1}'.format(algo, digest))

#    bytes_dict = get_bytes_dict(filename)
#    print(bytes_dict)

    sys.exit(0)
