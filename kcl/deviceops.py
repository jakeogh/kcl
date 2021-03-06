#!/usr/bin/env python3

# pylint: disable=C0111  # docstrings are always outdated and wrong
# pylint: disable=W0511  # todo is encouraged
# pylint: disable=C0301  # line too long
# pylint: disable=R0902  # too many instance attributes
# pylint: disable=C0302  # too many lines in module
# pylint: disable=C0103  # single letter var names, func name too descriptive
# pylint: disable=R0911  # too many return statements
# pylint: disable=R0912  # too many branches
# pylint: disable=R0915  # too many statements
# pylint: disable=R0913  # too many arguments
# pylint: disable=R1702  # too many nested blocks
# pylint: disable=R0914  # too many local variables
# pylint: disable=R0903  # too few public methods
# pylint: disable=E1101  # no member for base
# pylint: disable=W0201  # attribute defined outside __init__
# pylint: disable=R0916  # Too many boolean expressions in if statement


import os
import time
import click
from pathlib import Path
from kcl.timeops import timestamp
from kcl.mountops import block_special_path_is_mounted
from kcl.pathops import path_is_block_special
from kcl.fileops import get_block_device_size
from kcl.fileops import path_exists
from kcl.printops import eprint
from kcl.commandops import run_command
from kcl.warnops import warn
from kcl.inputops import passphrase_prompt

deviceops = click.Group()


def wait_for_block_special_device_to_exist(path, timeout=5):
    eprint("waiting for block special path: {} to exist".format(path))
    start = time.time()
    if path_exists(path):
        assert path_is_block_special(path)
        return True

    while not path_exists(path):
        time.sleep(0.1)
        if time.time() - start > timeout:
            raise TimeoutError("timeout waiting for block special path: {} to exist".format(path))
        if path_is_block_special(path):
            break
    return True


def add_partition_number_to_device(device, partition_number, verbose=False):
    if Path(device).name.startswith('nvme'):
        devpath = device + 'p' + partition_number
    else:
        devpath = device + partition_number
    return devpath


@deviceops.command()
@click.argument('device', required=True, nargs=1)
@click.option('--force', is_flag=True, required=False)
@click.option('--skipdestroy', is_flag=True, required=False)
@click.option('--simulate', is_flag=True, required=False)
@click.pass_context
def luksformat(ctx, device, force, skipdestroy, simulate):
    assert path_is_block_special(device)
    assert not block_special_path_is_mounted(device)
    if not force:
        if not simulate:
            warn((device,))

    passphrase = passphrase_prompt("LUKS", verbose=False, debug=False,)
    assert passphrase
    read, write = os.pipe()
    os.write(write, passphrase)
    os.close(write)
    if not skipdestroy:
        if not simulate:
            ctx.invoke(destroy_block_device, device=device, force=True)
    luks_command = b"cryptsetup -q --debug --verbose --cipher aes-xts-essiv:sha256 --key-size 512 --hash sha512 --use-random --iter-time 15000 --timeout 24000 --key-file - luksFormat " + os.fsencode(device)
    if simulate:
        eprint(luks_command)
    else:
        run_command(luks_command, verbose=True, expected_exit_status=0, stdin=read)
    #  xts with essiv is redundant, but there is no downside to using it


@deviceops.command()
@click.argument('device', required=True, nargs=1)
@click.option('--force', is_flag=True, required=False)
#@click.option('--source', is_flag=False, required=True, type=click.Choice(['urandom', 'zero']))
@click.pass_context
def destroy_block_device(ctx, device, force):
    assert isinstance(force, bool)
    #assert source in ['urandom', 'zero']
    if not Path(device).name.startswith('nvme'):
        assert not device[-1].isdigit()
    assert device.startswith('/dev/')
    assert not device.endswith('/')
    eprint("destroying device:", device)
    assert path_is_block_special(device)
    assert not block_special_path_is_mounted(device)
    if not force:
        warn((device,))
    device_name = device.split('/')[-1]
    assert len(device_name) >= 3
    assert '/' not in device_name
    assert device.endswith(device_name)
    luks_mapper = "/dev/mapper/" + device_name
    print(luks_mapper)
    assert not path_is_block_special(luks_mapper, follow_symlinks=True)
    ctx.invoke(destroy_block_device_head, device=device, source='zero', size=4092)
    luks_command = "cryptsetup open --type plain -d /dev/urandom " + device + " " + device_name
    print(luks_command)
    run_command(luks_command, verbose=True, expected_exit_status=0)
    assert path_is_block_special(luks_mapper, follow_symlinks=True)
    assert not block_special_path_is_mounted(luks_mapper)
    wipe_command = "dd_rescue --color=1 --abort_we /dev/zero " + luks_mapper
    #wipe_command = "dd if=/dev/" + source + " of=" + device
    print(wipe_command)
    #run_command(wipe_command, verbose=True, expected_exit_status=0)
    os.system(wipe_command)
    time.sleep(1) # so "cryptsetup close" doesnt throw an error
    #run_command(wipe_command, verbose=True, expected_exit_status=1)  # dd returns 1 when it hits the end of the device
    close_command = "cryptsetup close " + device_name
    print(close_command)
    run_command(close_command, verbose=True, expected_exit_status=0)


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
    device_size = get_block_device_size(device)
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
@click.option('--size', is_flag=False, required=False, type=int, default=(1024))
@click.option('--source', is_flag=False, required=True, type=click.Choice(['urandom', 'zero']))
@click.option('--note', is_flag=False, required=False, type=str)
@click.option('--force', is_flag=True, required=False)
@click.option('--no-backup', is_flag=True, required=False)
@click.pass_context
def destroy_block_device_head_and_tail(ctx, device, size, source, note, force, no_backup):
    #run_command("sgdisk --zap-all " + device) #alt method
    if not Path(device).name.startswith('nvme'):
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
        if not Path(device).name.startswith('nvme'):
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
    if not Path(device).name.startswith('nvme'):
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
@click.option('--force',      is_flag=True, required=False)
@click.option('--no-wipe',    is_flag=True, required=False)
@click.option('--no-backup',  is_flag=True, required=False)
@click.pass_context
def write_mbr(ctx, device, force, no_wipe, no_backup):
    eprint("writing MBR to:", device)
    if not Path(device).name.startswith('nvme'):
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
@click.option('--partition-number', is_flag=False, required=True, type=str)
@click.option('--force',  is_flag=True, required=False)
@click.pass_context
def write_efi_partition(ctx, device, start, end, partition_number, force):
    eprint("creating efi partition on device:", device, "partition_number:", partition_number, "start:", start, "end:", end)
    if not Path(device).name.startswith('nvme'):
        assert not device[-1].isdigit()
    assert not device.endswith('/')
    assert path_is_block_special(device)
    assert not block_special_path_is_mounted(device)
    assert int(partition_number)

    if not force:
        warn((device,))

    #output = run_command("parted " + device + " --align optimal --script -- mkpart primary " + start + ' ' + end)
    run_command("parted --align minimal " + device + " --script -- mkpart primary " + start + ' ' + end, verbose=True)
    run_command("parted " + device + " --script -- name " + partition_number + " EFI")
    run_command("parted " + device + " --script -- set " + partition_number + " boot on")

    fat16_partition_device = add_partition_number_to_device(device=device, partition_number=partition_number)
    wait_for_block_special_device_to_exist(fat16_partition_device)
    #while not path_is_block_special(fat16_partition_device):
    #    eprint("fat16_partition_device", fat16_partition_device, "is not block special yet, waiting a second.")
    #    time.sleep(1)

    ctx.invoke(create_filesystem, device=fat16_partition_device, filesystem='fat16', force=True)

    # 127488 /mnt/sdb2/EFI/BOOT/BOOTX64.EFI


@deviceops.command()
@click.option('--device', is_flag=False, required=True)
@click.option('--start', is_flag=False, required=True, type=str)
@click.option('--end', is_flag=False, required=True, type=str)
@click.option('--partition_number', is_flag=False, required=True, type=str)
@click.option('--force', is_flag=True, required=False)
def write_grub_bios_partition(device, start, end, force, partition_number):
    eprint("creating grub_bios partition on device:", device, "partition_number:", partition_number, "start:", start, "end:", end)
    if not Path(device).name.startswith('nvme'):
        assert not device[-1].isdigit()
    assert path_is_block_special(device)
    assert not block_special_path_is_mounted(device)
    assert int(partition_number)

    if not force:
        warn((device,))

    #run_command("parted " + device + " --align optimal --script -- mkpart primary " + start + ' ' + end)
    run_command("parted " + device + " --align minimal --script -- mkpart primary " + start + ' ' + end)
    run_command("parted " + device + " --script -- name " + partition_number + " BIOSGRUB")
    run_command("parted " + device + " --script -- set " + partition_number + " bios_grub on")
    grub_bios_partition_device = add_partition_number_to_device(device=device, partition_number=partition_number)
    wait_for_block_special_device_to_exist(grub_bios_partition_device)

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
    wait_for_block_special_device_to_exist(path=device)
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

