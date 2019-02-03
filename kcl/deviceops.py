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

deviceops = click.Group()

@deviceops.command()
@click.argument('device', required=True, nargs=1)
@click.option('--force', is_flag=True, required=False)
@click.pass_context
def luksformat_device(ctx, device, force):
    assert path_is_block_special(device)
    assert not block_special_path_is_mounted(device)
    if not force:
        warn((device,))

    ctx.invoke(destroy_block_device, device=device, source='zero', force=True) # change to urandom
    luks_command = "cryptsetup -q --debug --verbose --cipher twofish-xts-essiv:sha256 --key-size 512 --hash sha512 --use-random --verify-passphrase --iter-time 10000 --timeout 24000 luksFormat " + device
    run_command(luks_command, verbose=True, expected_exit_code=0)


@deviceops.command()
@click.argument('device', required=True, nargs=1)
@click.option('--force', is_flag=True, required=False)
@click.option('--source', is_flag=False, required=True, type=click.Choice(['urandom', 'zero']))
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


@deviceops.command()
@click.argument('device', required=True, nargs=1, type=str)
@click.option('--size', is_flag=False, required=True, type=int)
@click.option('--source', is_flag=False, required=True, type=click.Choice(['urandom', 'zero']))
@click.option('--no-backup', is_flag=True, required=False)
@click.option('--note', is_flag=False, required=False, type=str)
@click.pass_context
def destroy_block_device_head(ctx, device, size, source, no_backup, note):
    assert path_is_block_special(device)
    assert not block_special_path_is_mounted(device)
    ctx.invoke(destroy_byte_range, device=device, start=0, end=size, source=source, no_backup=no_backup, note=note)


@deviceops.command()
@click.argument('device', required=True, nargs=1, type=str)
@click.option('--size', is_flag=False, required=True, type=int)
@click.option('--source', is_flag=False, required=True, type=click.Choice(['urandom', 'zero']))
@click.option('--no-backup', is_flag=True, required=False)
@click.option('--note', is_flag=False, required=False, type=str)
@click.pass_context
def destroy_block_device_tail(ctx, device, size, source, no_backup, note):
    assert size > 0
    device_size = get_file_size(device)
    assert size <= device_size
    start = device_size - size
    assert start > 0
    end = start + size
    ctx.invoke(destroy_byte_range, device=device, start=start, end=end, source=source, no_backup=no_backup, note=note)


@deviceops.command()
@click.argument('device', required=True, nargs=1, type=str)
@click.option('--start', is_flag=False, required=True, type=int)
@click.option('--end', is_flag=False, required=True, type=int)
@click.option('--source', is_flag=False, required=True, type=click.Choice(['urandom', 'zero']))
@click.option('--no-backup', is_flag=True, required=False)
@click.option('--note', is_flag=False, required=False, type=str)
@click.pass_context
def destroy_byte_range(ctx, device, start, end, source, no_backup, note):
    assert start >= 0
    assert end > 0
    assert start < end
    eprint("source:", source)
    if not no_backup:
        ctx.invoke(backup_byte_range, device=device, start=start, end=end, note=note)
    bytes_to_zero = end - start
    assert bytes_to_zero > 0
    with open(device, 'wb') as dfh:
        dfh.seek(start)
        if source == 'zero':
            dfh.write(bytearray(bytes_to_zero))
        if source == 'urandom':
            urandom_bytes = os.urandom(bytes_to_zero)
            assert len(urandom_bytes) == bytes_to_zero
            dfh.write(urandom_bytes)


@deviceops.command()
@click.argument('device', required=True, nargs=1)
@click.option('--size', is_flag=False, required=False, type=int, default=(512))
@click.option('--source', is_flag=False, required=True, type=click.Choice(['urandom', 'zero']))
@click.option('--note', is_flag=False, required=False, type=str)
@click.option('--force', is_flag=True, required=False)
@click.option('--no-backup', is_flag=True, required=False)
@click.pass_context
def destroy_block_device_head_and_tail(ctx, device, size, source, note, force, no_backup):
    #run_command("sgdisk --zap-all " + device) #alt method
    assert not device[-1].isdigit()
    eprint("destroying device:", device)
    assert path_is_block_special(device)
    assert not block_special_path_is_mounted(device)
    if not force:
        warn((device,))
    if not note:
        note = str(time.time()) + '_' + device.replace('/', '_')
        eprint("note:", note)

    ctx.invoke(destroy_block_device_head, device=device, size=size, source=source, note=note, no_backup=no_backup)
    ctx.invoke(destroy_block_device_tail, device=device, size=size, source=source, note=note, no_backup=no_backup)


@deviceops.command()
@click.argument('devices', required=True, nargs=-1)
@click.option('--size', is_flag=False, required=False, type=int, default=(1024*1024*128))
@click.option('--note', is_flag=False, required=False, type=str)
@click.option('--force', is_flag=True, required=False)
@click.option('--no-backup', is_flag=True, required=False)
@click.pass_context
def destroy_block_devices_head_and_tail(ctx, devices, size, note, force, no_backup):
    for device in devices:
        assert not device[-1].isdigit()
        eprint("destroying device:", device)
        assert path_is_block_special(device)
        assert not block_special_path_is_mounted(device)

    if not force:
        warn(devices)

    for device in devices:
        ctx.invoke(destroy_block_device_head_and_tail, device=device, size=size, note=note, force=force, no_backup=no_backup)


@deviceops.command()
@click.argument('device', required=True, nargs=1)
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


@deviceops.command()
@click.option('--device', is_flag=False, required=True)
@click.option('--backup-file', is_flag=False, required=True)
@click.option('--start', is_flag=False, required=False, type=int)
@click.option('--end', is_flag=False, required=False, type=int)
def compare_byte_range(device, backup_file, start, end):
    if not start:
        start = int(backup_file.split('start_')[1].split('_')[0])
    if not end:
        end = int(backup_file.split('end_')[1].split('_')[0].split('.')[0])
    assert isinstance(start, int)
    assert isinstance(end, int)
    current_copy = backup_byte_range(device, start=start, end=end, note='current')
    vbindiff_command = "vbindiff " + current_copy + ' ' + backup_file
    eprint(vbindiff_command)
    os.system(vbindiff_command)


@deviceops.command()
@click.option('--device', is_flag=False, required=True)
@click.option('--force', is_flag=True, required=False)
@click.option('--no-wipe', is_flag=True, required=False)
@click.option('--no-backup', is_flag=True, required=False)
@click.pass_context
def write_gpt(ctx, device, force, no_wipe, no_backup):
    eprint("writing GPT to:", device)
    assert not device[-1].isdigit()
    assert path_is_block_special(device)
    assert not block_special_path_is_mounted(device)
    if not force:
        warn((device,))
    if not no_wipe:
        ctx.invoke(destroy_block_device_head_and_tail, device=device, force=force, no_backup=no_backup)
        #run_command("sgdisk --zap-all " + boot_device)
    else:
        eprint("skipping wipe")

    run_command("parted " + device + " --script -- mklabel gpt")
    #run_command("sgdisk --clear " + device) #alt way to greate gpt label


@deviceops.command()
@click.option('--device',     is_flag=False, required=True)
#@click.option('--device-partition-table', is_flag=False, required=True, type=click.Choice(['gpt']))
@click.option('--force',      is_flag=True, required=False)
@click.option('--no-wipe',    is_flag=True, required=False)
@click.option('--no-backup',  is_flag=True, required=False)
@click.pass_context
def write_mbr(ctx, device, force, no_wipe, no_backup):
    eprint("writing MBR to:", device)
    assert not device[-1].isdigit()
    assert path_is_block_special(device)
    assert not block_special_path_is_mounted(device)
    if not force:
        warn((device,))
    if not no_wipe:
        ctx.invoke(destroy_block_device_head_and_tail, device=device, force=force, no_backup=no_backup)
        #run_command("sgdisk --zap-all " + boot_device)

    run_command("parted " + device + " --script -- mklabel msdos")
    #run_command("parted " + device + " --script -- mklabel gpt")
    #run_command("sgdisk --clear " + device) #alt way to greate gpt label


@deviceops.command()
@click.option('--device', is_flag=False, required=True)
@click.option('--start',  is_flag=False, required=True, type=str)
@click.option('--end',    is_flag=False, required=True, type=str)
@click.option('--partition-number',    is_flag=False, required=True, type=str)
@click.option('--force',  is_flag=True,  required=False)
@click.pass_context
def write_efi(ctx, device, start, end, partition_number, force):
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

    ctx.invoke(create_filesystem, device=fat16_partition_device, partition_type='fat16', force=True)

    # 127488 /mnt/sdb2/EFI/BOOT/BOOTX64.EFI


@deviceops.command()
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
