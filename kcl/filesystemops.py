#!/usr/bin/env python3

import click
from kcl.fileops import path_is_block_special
from kcl.mountops import block_special_path_is_mounted
from kcl.command import run_command
from kcl.printops import eprint
from kcl.warnops import warn


@click.command()
@click.option('--device', is_flag=False, required=True)
@click.option('--filesystem', "filesystem", is_flag=False, required=True, type=click.Choice(['fat16', 'fat32']))
@click.option('--force', is_flag=True, required=False)
def create_filesystem(device, filesystem, force):
    eprint("creating", filesystem, "filesystem on:", device)
    assert device[-1].isdigit()
    # oddly, this failed on '/dev/sda2', maybe the kernel was not done
    # digesting the previous table change? (using fat16)
    assert path_is_block_special(device)
    assert not block_special_path_is_mounted(device)

    if not force:
        warn((device,))

    if filesystem == 'fat16':
        run_command("mkfs.fat -F16 -s2 " + device)
    elif filesystem == 'fat32':
        run_command("mkfs.fat -F32 -s2 " + device)
    else:
        assert False
