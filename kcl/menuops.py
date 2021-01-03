#!/usr/bin/env python3


import os
from subprocess import CalledProcessError

from icecream import ic

from .commandops import run_command
from .printops import eprint


def _prompt_tag_dmenu(*,
                      cache_file,
                      verbose: bool,
                      debug: bool,):
    command = '''dmenu -fn "-misc-fixed-*-*-*-*-20-*-*-*-*-*-*-*" -f -nb "#000000" -i <''' + cache_file
    text = run_command(command,
                       popen=True,
                       verbose=verbose,
                       str_output=True,
                       debug=debug,)
    text = text.strip()
    if verbose:
        ic(text)
    return text


def _prompt_tag_slmenu(*,
                       cache_file,
                       verbose: bool,
                       debug: bool,
                       msg: str = None,):
    command = "/usr/bin/slmenu -i <" + cache_file
    if msg:
        eprint("\n" + msg, end=None)
    text = os.popen(command).read()
    if verbose:
        ic(text)
    #tag_completer = WordCompleter(tags, ignore_case=True)
    #text = prompt('Tag: ', completer=tag_completer,
    #              complete_style=CompleteStyle.READLINE_LIKE, complete_while_typing=True)
    return text


def prompt_string(*,
                  cache_file,
                  verbose: bool,
                  debug: bool,
                  msg: str = None):
    try:
        tag = _prompt_tag_dmenu(cache_file=cache_file,
                                verbose=verbose,
                                debug=debug,)
    except CalledProcessError:
        tag = _prompt_tag_slmenu(cache_file=cache_file,
                                 verbose=verbose,
                                 debug=debug,
                                 msg=msg)
    if verbose:
        ic(tag)
    return tag
