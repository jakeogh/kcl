#!/usr/bin/env python3

import os
import subprocess

import pyperclip
from icecream import ic

from kcl.commandops import run_command
from kcl.htmlops import extract_iris_from_text


def put_clipboard(string, verbose=False):
    pyperclip.set_clipboard('xclip')
    if verbose:
        ic(string)
    pyperclip.copy(string, primary=True)


# bug putting snowman http://☃.net in the clipboard results in no iris
def get_clipboard(verbose=False, one_line=False, dont_decode=False):
    command = [b"xclip", b"-o", b"-selection", b"primary"]
    if verbose:
        ic(command)

    string = run_command(command, shell=True, verbose=True)
    #string = \
    #    subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).stdout.read()
    if verbose:
        ic(string)
    if not dont_decode:
        string = string.decode("utf-8")

    if one_line:
        string = string.split()
        return string[0]

    return string


def prompt_tag_slmenu(cache_file="/home/user/.iridb/.dmenu_tag_cache"):
    #with open(file, 'r') as fh:
    #    tags = fh.readlines()

    command = "/usr/bin/slmenu -i <" + cache_file
    text = os.popen(command).read()

    return text


def get_clipboard_iri(verbose: bool = False,
                      debug: bool = False,):

    iris = get_clipboard_iris(verbose=verbose,
                              debug=debug,)

    #clipboard_contents = get_clipboard()
    #if clipboard_contents[0] == "'":
    #    if clipboard_contents[-1] == "'":
    #        clipboard_contents = clipboard_contents[1:-1]
    #if clipboard_contents[0] == '"':
    #    if clipboard_contents[-1] == '"':
    #        clipboard_contents = clipboard_contents[1:-1]
    #if verbose:
    #    ic(clipboard_contents)
    #uri_list = extract_iris_from_text(clipboard_contents,
    #                                  strip_fragments=False,
    #                                  verbose=verbose,
    #                                  debug=debug,)
    ##try:
    #clean_uri = list(filter(None, uri_list))[0]
    ##except IndexError:
    ##    ceprint("Clipboard has no uris. Exiting.")
    ##    #bug: looking for URLs when should be looking for URIs. /home/user/something should work
    ##    os._exit(1)

    #return clean_uri
    return iris[0]


def get_clipboard_iris(verbose=False, debug=False):
    clipboard_contents = get_clipboard(verbose=verbose)
    iri_list = extract_iris_from_text(clipboard_contents,
                                      strip_fragments=False,
                                      verbose=verbose,
                                      debug=debug,)
    for iri in iri_list:
        iri = iri.strip()
        if iri.startswith("'"):
            if iri.endswith("'"):
                iri = iri[1:-1]
                ic(iri)
        if iri.startswith('"'):
            if iri.endswith('"'):
                iri = iri[1:-1]
                ic(iri)
        if verbose:
            ic(iri)

        yield iri

