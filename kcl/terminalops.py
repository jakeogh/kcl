#!/usr/bin/env python3

import shutil
from icecream import ic
from .commandops import run_command


def get_current_virtural_terminal():
    output = run_command('fgconsole')
    return int(output)


# find out if this is executing in a xorg session
# note the xorg sesion is started under the user, but we could be root, or any user
# assumes a single X session is running
def in_xorg(verbose=False):
    vt = get_current_virtural_terminal()
    tty = 'tty' + str(vt)
    if verbose:
        ic(vt)
    output = run_command(['w', '--no-header']).decode('utf8').splitlines()
    if verbose:
        ic(output)
    assert len(output) == 0
    if 'xinit' in output[0]:
        if verbose:
            ic('xinit in output')
        output = output[0].split()
        if verbose:
            ic(output[1])
        if output[1] == tty:
            return True
    return False


def get_terminal_width(default=80):
    width, height = shutil.get_terminal_size((default, 20))
    return width

