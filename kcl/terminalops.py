#!/usr/bin/env python3

import shutil
from .commandops import run_command


def get_current_virtural_terminal():
    output = run_command('fgconsole')
    return int(output)


def in_xorg():
    vt = get_current_virtural_terminal()
    output = run_command('w').decode('utf8').splitlines()
    for line in output:
        if '/usr/bin/X' in line:
            if line.endswith('vt' + str(vt)):
                return True
    return False


def get_terminal_width(default=80):
    width, height = shutil.get_terminal_size((default, 20))
    return width

