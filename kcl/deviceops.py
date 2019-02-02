#!/usr/bin/env python3

import click
import time
from kcl.mountops import block_special_path_is_mounted
from kcl.fileops import path_is_block_special
from kcl.printops import eprint
from kcl.command import run_command
from kcl.fileops import get_file_size


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


def destroy_block_device_head(device, size, no_backup, note):
    #eprint("destroy_black_device_head()")
    #eprint("no_backup:", no_backup)
    assert path_is_block_special(device)
    assert not block_special_path_is_mounted(device)
    zero_byte_range(device, 0, size, no_backup, note)


def destroy_block_device_tail(device, size, no_backup, note):
    #eprint("destroy_block_device_tail()")
    #eprint("no_backup:", no_backup)
    assert size > 0
    device_size = get_file_size(device)
    #eprint("device_size:", device_size)
    assert size <= device_size
    start = device_size - size
    #eprint("start:       ", start)
    assert start > 0
    #eprint("bytes to zero:", size)
    end = start + size
    zero_byte_range(device, start, end, no_backup, note)


def zero_byte_range(device, start, end, no_backup, note):
    #eprint("zero_byte_range()")
    #eprint("start:", start)
    #eprint("end:", end)
    #eprint("no_backup:", no_backup)
    assert start >= 0
    assert end > 0
    assert start < end
    if not no_backup:
        backup_byte_range(device, start, end, note)
    with open(device, 'wb') as dfh:
        bytes_to_zero = end - start
        assert bytes_to_zero > 0
        dfh.seek(start)
        dfh.write(bytearray(bytes_to_zero))


@click.command()
@click.option('--device', is_flag=False, required=True)
@click.option('--size', is_flag=False, required=False, type=int, default=(512))
@click.option('--note', is_flag=False, required=False)
@click.option('--force', is_flag=True, required=False)
@click.option('--no-backup', is_flag=True, required=False)
def destroy_block_device_head_and_tail(device, size, note, force, no_backup):
    #run_command("sgdisk --zap-all " + device) #alt method
    #eprint("destroy_block_device_head_and_tail()")
    #eprint("no_backup:", no_backup)
    assert isinstance(no_backup, bool)
    assert not device[-1].isdigit()
    eprint("destroying device:", device)
    assert path_is_block_special(device)
    assert not block_special_path_is_mounted(device)
    if not force:
        warn((device,))

    destroy_block_device_head(device=device, size=size, note=note, no_backup=no_backup)
    destroy_block_device_tail(device=device, size=size, note=note, no_backup=no_backup)


