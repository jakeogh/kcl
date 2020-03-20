import os
from icecream import ic
from .commandops import run_command


def prompt_tag_dmenu(tag_cache_file="/home/user/.iridb/.dmenu_tag_cache", verbose=False):
    command = '''dmenu -fn "-misc-fixed-*-*-*-*-20-*-*-*-*-*-*-*" -f -nb "#000000" -i <''' + tag_cache_file
    #text = os.popen(command).read()
    text = run_command(command, popen=True, verbose=verbose)
    text = text.strip()
    if verbose:
        ic(text)
    return text


def prompt_tag_slmenu(file="/home/user/.iridb/.dmenu_tag_cache"):
    command = "/usr/bin/slmenu -i <" + file
    text = os.popen(command).read()

    #tag_completer = WordCompleter(tags, ignore_case=True)
    #text = prompt('Tag: ', completer=tag_completer,
    #              complete_style=CompleteStyle.READLINE_LIKE, complete_while_typing=True)
    return text
