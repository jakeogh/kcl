#!/usr/bin/env python3

import click
import time
from kcl.mountops import block_special_path_is_mounted
from kcl.fileops import path_is_block_special
from kcl.printops import eprint
from kcl.command import run_command


def warn(devices):
    assert isinstance(devices, tuple)
    for device in devices:
        assert path_is_block_special(device)
        assert not block_special_path_is_mounted(device)
    eprint("THIS WILL DESTROY ALL DATA ON", ' '.join(devices), "_REMOVE_ ANY HARD DRIVES (and removable storage like USB sticks) WHICH YOU DO NOT WANT TO ACCIDENTLY DELETE THE DATA ON")
    answer = input("Do you want to proceed with deleting all of your data? (type YES to proceed)")
    if answer != 'YES':
        quit(1)
    eprint("Sleeping 5 seconds")
    time.sleep(5)


@click.command()
@click.argument('device', required=True, nargs=1)
@click.option('--force', is_flag=True, required=False)
@click.option('--source', is_flag=False, required=False, type=click.Choice(['urandom', 'zero']), default="urandom")
def destroy_block_device(device, force, source):
    assert isinstance(force, bool)
    assert source in ['urandom', 'zero']
    assert not device[-1].isdigit()
    eprint("destroying device:", device)
    assert path_is_block_special(device)
    assert not block_special_path_is_mounted(device)
    if not force:
        warn((device,))
    wipe_command = "dd if=/dev/" + source + " of=" + device
    print(wipe_command)
    run_command(wipe_command, verbose=True, expected_exit_code=1)  # dd returns 1 when it hits the end of the device
