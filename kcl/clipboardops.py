import subprocess
import os
from kcl.htmlops import extract_iris_from_text
from icecream import ic


# bug putting snowman http://☃.net in the clipboard results in no iris
def get_clipboard(verbose=False):
    ic()
    command = "xclip -o -selection primary".split()
    string = \
        subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).stdout.read()
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
    uri_list = extract_iris_from_text(get_clipboard())
    #try:
    clean_uri = list(filter(None, uri_list))[0]
    #except IndexError:
    #    ceprint("Clipboard has no uris. Exiting.")
    #    #bug: looking for URLs when should be looking for URIs. /home/user/something should work
    #    os._exit(1)

    return clean_uri


def get_clipboard_iris(verbose=False):
    iri_list = extract_iris_from_text(get_clipboard(verbose=verbose))
    return iri_list


