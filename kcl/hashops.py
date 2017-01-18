#!/usr/bin/env python3
#from .sa_logging import log_prefix, logger, print_traceback

import hashlib
import os
import tempfile
import requests

def generate_hash(data):
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
    if isinstance(data, requests.models.Response):
        temp_file = tempfile.NamedTemporaryFile(mode='wb', suffix='.tmp', prefix='tmp-', dir='/var/tmp/iridb', delete=False) #todo make temp_folder configurable, make sure it exists
        for chunk in data.iter_content(chunk_size):
            sha1.update(chunk)
            temp_file.write(chunk)
        temp_file.close()
        #logger.debug('finished writing temp_file: %s', temp_file.name)
        if os.path.getsize(temp_file.name) == 0:
            #logger.error('content is zero bytes, returning False')        #this happens
            return False
        return_dict['hash'] = sha1.hexdigest()
        return_dict['temp_file'] = temp_file
        return return_dict
    if len(data) == 0:
        empty_hash = hashlib.sha1(data).hexdigest()
        #logger.error("hey! Error, you are attempting to hash a empty string. (not) Exiting on hash: " + empty_hash)
        raise FileNotFoundError
#       return False
#       os._exit(1)
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
