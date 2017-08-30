#!/usr/bin/env python3
# tab-width:4
# pylint: disable=missing-docstring

# MIT License
# https://github.com/jakeogh/dnsgate/blob/master/LICENSE
#
# common functions acting on bytes

import requests
from kcl.logops import leprint
from kcl.logops import LOG

def get_random_bytes(count):
    with open('/dev/urandom', "rb") as python_fd:
        return python_fd.read(count)

def get_random_non_null_bytes(count):
    by = bytearray(get_random_bytes(100)).replace(b'\x00', b'')
    while len(by) != count:
        bytes_needed = count - len(by)
        print("bytes_needed:", bytes_needed)
        new_bytes = bytearray(get_random_bytes(bytes_needed)).replace(b'\x00', b'')
        by = by + new_bytes
    return(bytes(by))



def remove_comments_from_bytes(line): #todo check for (assert <=1 line break) multiple linebreaks?
    assert isinstance(line, bytes)
    uncommented_line = b''
    for char in line:
        char = bytes([char])
        if char != b'#':
            uncommented_line += char
        else:
            break
    return uncommented_line

def read_url_bytes(url):
    leprint("GET: %s", url, level=LOG['DEBUG'])
    user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0'
    try:
        raw_url_bytes = requests.get(url, headers={'User-Agent': user_agent},
            allow_redirects=True, stream=False, timeout=15.500).content
    except Exception as e:
        leprint(e, level=LOG['WARNING'])
        return False
    return raw_url_bytes

def read_url_bytes_and_cache(url, cache=True):
    raw_url_bytes = read_url_bytes(url)
    if cache:
        cache_index_file = CACHE_DIRECTORY + '/sha1_index'
        cache_file = generate_cache_file_name(url)
        with open(cache_file, 'xb') as fh:
            fh.write(raw_url_bytes)
        line_to_write = cache_file + ' ' + url + '\n'
        write_unique_line(line_to_write, cache_index_file)

    if raw_url_bytes:
        leprint("Returning %d bytes from %s", len(raw_url_bytes), url, level=LOG['DEBUG'])
        return raw_url_bytes
    else:
        return False


if __name__ == '__main__':
    quit(0)
