#!/usr/bin/env python3

import os
import click
import time
from kcl.timeops import timestamp
from kcl.mountops import block_special_path_is_mounted
from kcl.fileops import path_is_block_special
from kcl.printops import eprint
from kcl.command import run_command
from kcl.fileops import get_file_size
from kcl.filesystemops import create_filesystem
from kcl.warnops import warn


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


@click.command()
@click.argument('devices', required=True, nargs=-1)
@click.option('--size', is_flag=False, required=False, type=int, default=(1024*1024*128))
@click.option('--note', is_flag=False, required=False)
@click.option('--force', is_flag=True, required=False)
@click.option('--no-backup', is_flag=True, required=False)
def destroy_block_devices_head_and_tail(devices, size, note, force, no_backup):
    for device in devices:
        assert isinstance(no_backup, bool)
        assert not device[-1].isdigit()
        eprint("destroying device:", device)
        assert path_is_block_special(device)
        assert not block_special_path_is_mounted(device)

    if not force:
        warn(devices)

    for device in devices:
        destroy_block_device_head_and_tail(device, size, note, force, no_backup)


@click.command()
@click.option('--device', is_flag=False, required=True)
@click.option('--start', is_flag=False, required=True, type=int)
@click.option('--end', is_flag=False, required=True, type=int)
@click.option('--note', is_flag=False, required=False, type=str)
def backup_byte_range(device, start, end, note):
    with open(device, 'rb') as dfh:
        bytes_to_read = end - start
        assert bytes_to_read > 0
        dfh.seek(start)
        bytes_read = dfh.read(bytes_to_read)
        assert len(bytes_read) == bytes_to_read

    time_stamp = str(timestamp())
    running_on_hostname = os.uname()[1]
    device_string = device.replace('/', '_')
    backup_file_tail = '_.' \
        + device_string + '.' \
        + time_stamp + '.' \
        + running_on_hostname \
        + '_start_' + str(start) + '_end_' + str(end) + '.bak'
    if note:
        backup_file = '_backup_' + note + backup_file_tail
    else:
        backup_file = '_backup__.' + backup_file_tail
    with open(backup_file, 'xb') as bfh:
        bfh.write(bytes_read)
    print(backup_file)


@click.command()
@click.option('--device', is_flag=False, required=True)
@click.option('--backup-file', is_flag=False, required=True)
@click.option('--start', is_flag=False, required=False, type=int)
@click.option('--end', is_flag=False, required=False, type=int)
def compare_byte_range(device, backup_file, start, end):
    #eprint("backup_byte_range()")
    if not start:
        start = int(backup_file.split('start_')[1].split('_')[0])
    #eprint("start:", start)
    if not end:
        end = int(backup_file.split('end_')[1].split('_')[0].split('.')[0])
    #eprint("end:", end)
    assert isinstance(start, int)
    assert isinstance(end, int)
    current_copy = backup_byte_range(device, start, end, note='current')
    #eprint("current_copy:", current_copy)
    #eprint("bakckup_file:", backup_file)
    vbindiff_command = "vbindiff " + current_copy + ' ' + backup_file
    eprint(vbindiff_command)
    os.system(vbindiff_command)


@click.command()
@click.option('--device', is_flag=False, required=True)
@click.option('--force', is_flag=True, required=False)
@click.option('--no-wipe', is_flag=True, required=False)
@click.option('--no-backup', is_flag=True, required=False)
def write_gpt(device, force, no_wipe, no_backup):
    eprint("writing GPT to:", device)
    assert not device[-1].isdigit()
    assert path_is_block_special(device)
    assert not block_special_path_is_mounted(device)
    if not force:
        warn((device,))
    if not no_wipe:
        destroy_block_device_head_and_tail(device=device, force=force, no_backup=no_backup)
        #run_command("sgdisk --zap-all " + boot_device)
    else:
        eprint("skipping wipe")

    run_command("parted " + device + " --script -- mklabel gpt")
    #run_command("sgdisk --clear " + device) #alt way to greate gpt label


@click.command()
@click.option('--device',     is_flag=False, required=True)
#@click.option('--device-partition-table', is_flag=False, required=True, type=click.Choice(['gpt']))
@click.option('--force',      is_flag=True, required=False)
@click.option('--no-wipe',    is_flag=True, required=False)
@click.option('--no-backup',  is_flag=True, required=False)
def write_mbr(device, force, no_wipe, no_backup):
    eprint("writing MBR to:", device)
    assert not device[-1].isdigit()
    assert path_is_block_special(device)
    assert not block_special_path_is_mounted(device)
    if not force:
        warn((device,))
    if not no_wipe:
        destroy_block_device_head_and_tail(device=device, force=force, no_backup=no_backup)
        #run_command("sgdisk --zap-all " + boot_device)

    run_command("parted " + device + " --script -- mklabel msdos")
    #run_command("parted " + device + " --script -- mklabel gpt")
    #run_command("sgdisk --clear " + device) #alt way to greate gpt label


@click.command()
@click.option('--device', is_flag=False, required=True)
@click.option('--start',  is_flag=False, required=True, type=str)
@click.option('--end',    is_flag=False, required=True, type=str)
@click.option('--partition-number',    is_flag=False, required=True, type=str)
@click.option('--force',  is_flag=True,  required=False)
def write_efi(device, start, end, partition_number, force):
    eprint("creating efi partition on device:", device, "partition_number:", partition_number, "start:", start, "end:", end)
    assert not device[-1].isdigit()
    assert path_is_block_special(device)
    assert not block_special_path_is_mounted(device)

    if not force:
        warn((device,))

    #output = run_command("parted " + device + " --align optimal --script -- mkpart primary " + start + ' ' + end)
    run_command("parted --align minimal " + device + " --script -- mkpart primary " + start + ' ' + end, verbose=True)
    run_command("parted " + device + " --script -- name " + partition_number + " EFI")
    run_command("parted " + device + " --script -- set " + partition_number + " boot on")

    fat16_partition_device = device + partition_number
    while not path_is_block_special(fat16_partition_device):
        eprint("fat16_partition_device", fat16_partition_device, "is not block special yet, waiting a second.")
        time.sleep(1)

    create_filesystem(device=fat16_partition_device, partition_type='fat16', force=True)

    # 127488 /mnt/sdb2/EFI/BOOT/BOOTX64.EFI



@click.command()
@click.option('--device', is_flag=False, required=True)
@click.option('--start', is_flag=False, required=True, type=str)
@click.option('--end', is_flag=False, required=True, type=str)
@click.option('--partition_number', is_flag=False, required=True, type=str)
@click.option('--force', is_flag=True, required=False)
def write_grub_bios_partition(device, start, end, force, partition_number):
    eprint("creating grub_bios partition on device:", device, "partition_number:", partition_number, "start:", start, "end:", end)
    assert not device[-1].isdigit()
    assert path_is_block_special(device)
    assert not block_special_path_is_mounted(device)

    if not force:
        warn((device,))

    #run_command("parted " + device + " --align optimal --script -- mkpart primary " + start + ' ' + end)
    run_command("parted " + device + " --align minimal --script -- mkpart primary " + start + ' ' + end)
    run_command("parted " + device + " --script -- name " + partition_number + " BIOSGRUB")
    run_command("parted " + device + " --script -- set " + partition_number + " bios_grub on")

#    parted size prefixes
#    "s" (sectors)
#    "B" (bytes)
#    "kB"
#    "MB"
#    "MiB"
#    "GB"
#    "GiB"
#    "TB"
#    "TiB"
#    "%" (percentage of device size)
#    "cyl" (cylinders)

    # sgdisk -a1 -n2:48:2047 -t2:EF02 -c2:"BIOS boot partition " + device # numbers in 512B sectors
