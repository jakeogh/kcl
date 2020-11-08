#!/usr/bin/env python3

import pyperclip
import subprocess
import os
from kcl.htmlops import extract_iris_from_text
from kcl.commandops import run_command
from icecream import ic


def put_clipboard(string, verbose=False):
    pyperclip.set_clipboard('xclip')
    if verbose:
        ic(string)
    pyperclip.copy(string, primary=True)


# bug putting snowman http://☃.net in the clipboard results in no iris
def get_clipboard(verbose=False):
    command = [b"xclip", b"-o", b"-selection", b"primary"]
    if verbose:
        ic(command)

    string = run_command(command, shell=True, verbose=True)
    #string = \
    #    subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).stdout.read()
    if verbose:
        ic(string)
    return string.decode("utf-8")


def prompt_tag_slmenu(cache_file="/home/user/.iridb/.dmenu_tag_cache"):
    #with open(file, 'r') as fh:
    #    tags = fh.readlines()

    command = "/usr/bin/slmenu -i <" + cache_file
    text = os.popen(command).read()

    return text


def get_clipboard_iri():
    clipboard_contents = get_clipboard()
    if clipboard_contents[0] == "'":
        if clipboard_contents[-1] == "'":
            clipboard_contents = clipboard_contents[1:-1]
    if clipboard_contents[0] == '"':
        if clipboard_contents[-1] == '"':
            clipboard_contents = clipboard_contents[1:-1]
    uri_list = extract_iris_from_text(clipboard_contents)
    #try:
    clean_uri = list(filter(None, uri_list))[0]
    #except IndexError:
    #    ceprint("Clipboard has no uris. Exiting.")
    #    #bug: looking for URLs when should be looking for URIs. /home/user/something should work
    #    os._exit(1)

    return clean_uri


def get_clipboard_iris(verbose=False):
    clipboard_contents = get_clipboard(verbose=verbose)
    iri_list = extract_iris_from_text(clipboard_contents, verbose=verbose)
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

    for iri in iri_list:
        yield iri


