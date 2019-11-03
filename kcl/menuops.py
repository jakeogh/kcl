import os
from icecream import ic

def prompt_tag_dmenu(file="/home/user/.iridb/.dmenu_tag_cache", verbose=False):
    command = '''dmenu -fn "-misc-fixed-*-*-*-*-20-*-*-*-*-*-*-*" -f -nb "#000000" -i <''' + file
    text = os.popen(command).read()
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
