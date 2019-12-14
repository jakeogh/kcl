#!/usr/bin/env python3

import dmenu
from .printops import ceprint


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


def dmenu_tag(tag_cache_file):
    with open(tag_cache_file, 'r') as fh:
        tag_list = fh.readlines()
    font = "-Misc-Fixed-Medium-R-SemiCondensed--13-120-75-75-C-60-ISO10646-1"
    #answer = dmenu.show(tag_list, font="-misc-fixed-*-*-*-*-50-*-*-*-*-*-*-*", case_insensitive=True)
    answer = dmenu.show(tag_list, font=font, case_insensitive=True)
    return answer


def get_tag_dmenu(tag_cache_file):
    try:
        tag = dmenu_tag(tag_cache_file)
        return tag
    except Exception as e:
        ceprint(e)
        tag = input("enter a tag: ")
        return tag

