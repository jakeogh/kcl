#!/usr/bin/env python3

import dmenu
import pint
import sys
from icecream import ic
from .printops import ceprint
from .byteops import read_by_byte
from .iterops import randomize_iterator


def passphrase_prompt(note):
    note = note.strip()
    assert len(note) > 0
    prompt = "Enter {} passphrase: ".format(note)
    passphrase = input(prompt)
    passphrase = passphrase.encode('ascii')
    passphrase_v = input(prompt)
    passphrase_v = passphrase_v.encode('ascii')
    assert passphrase == passphrase_v
    assert len(passphrase) > 12
    return passphrase


#def dmenu_tag(tag_cache_file):
#    with open(tag_cache_file, 'r') as fh:
#        tag_list = fh.readlines()
#    font = "-Misc-Fixed-Medium-R-SemiCondensed--13-120-75-75-C-60-ISO10646-1"
#    #font = "-misc-fixed-*-*-*-*-50-*-*-*-*-*-*-*"
#    answer = dmenu.show(tag_list, font=font, case_insensitive=True)
#    return answer


#def get_thing_dmenu(cache_file, msg):
#    try:
#        thing = dmenu_tag(cache_file)
#        return thing
#    except Exception as e:
#        ceprint(e)
#        if not msg.endswith(' '):
#            msg += ' '
#        thing = input(msg)
#        return thing


def human_filesize_to_int(size,
        verbose=False,
                          debug=False):
    u = pint.UnitRegistry()
    i = u.parse_expression(size)
    result = i.to('bytes').magnitude
    #result = int(result)
    if verbose:
        ic(result)
    if debug:
        assert isinstance(result, int)
    return result


def input_iterator(null=False,
                   strings=None,
                   random=False,
                   verbose=False,
                   debug=False,
                   head=None):

    byte = b'\n'
    if null:
        byte = b'\x00'

    if strings:
        iterator = strings
    else:
        iterator = read_by_byte(sys.stdin.buffer, byte=byte)

    if random:
        iterator = randomize_iterator(iterator, min_pool_size=1, max_wait_time=1)

    lines_output = 0
    for index, string in enumerate(iterator):
        if debug:
            ic(index, string)

        if isinstance(string, bytes):
            string = string.decode('utf8')

        yield string
        lines_output += 1

        if head:
            if lines_output >= head:
                return


def enumerate_input(*,
                    iterator,
                    null,
                    verbose=False,
                    debug=False,
                    head=None):
    for index, thing in enumerate(input_iterator(strings=iterator,
                                                 null=null,
                                                 head=head,
                                                 debug=debug,
                                                 verbose=verbose)):
        yield index, thing
