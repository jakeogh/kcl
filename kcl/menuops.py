#!/usr/bin/env python3


import os
from icecream import ic
from .commandops import run_command


def _prompt_tag_dmenu(*, cache_file, verbose=False):
    command = '''dmenu -fn "-misc-fixed-*-*-*-*-20-*-*-*-*-*-*-*" -f -nb "#000000" -i <''' + cache_file
    text = run_command(command, popen=True, verbose=verbose, str_output=True)
    text = text.strip()
    if verbose:
        ic(text)
    return text


def _prompt_tag_slmenu(*, cache_file, verbose=False):
    command = "/usr/bin/slmenu -i <" + cache_file
    text = os.popen(command).read()
    #tag_completer = WordCompleter(tags, ignore_case=True)
    #text = prompt('Tag: ', completer=tag_completer,
    #              complete_style=CompleteStyle.READLINE_LIKE, complete_while_typing=True)
    return text


def prompt_tag(cache_file, verbose=False):
    tag = _prompt_tag_dmenu(cache_file=cache_file, verbose=verbose)
    if verbose:
        ic(tag)
