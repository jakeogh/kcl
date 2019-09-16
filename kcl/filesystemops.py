#!/usr/bin/env python3

import click
from kcl.fileops import path_is_block_special
from kcl.mountops import block_special_path_is_mounted
from kcl.commandops import run_command
from kcl.printops import eprint
from kcl.warnops import warn


@click.command()
@click.argument('device', required=True, nargs=1, type=str)
@click.option('--filesystem', "filesystem", is_flag=False, required=True, type=click.Choice(['fat16', 'fat32', 'ext4']))
@click.option('--force', is_flag=True, required=False)
@click.option('--raw-device', is_flag=True, required=False)
def create_filesystem(device, filesystem, force, raw_device):
    eprint("creating", filesystem, "filesystem on:", device)
    if not raw_device:
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
    elif filesystem == 'ext4':
        run_command("mkfs.ext4 " + device)
    else:
        assert False

