#!/usr/bin/env python3

import dmenu
import pint
from icecream import ic
from .printops import ceprint


def passphrase_prompt(note):
    note = note.strip()
    assert len(note) > 0
    prompt = "Enter {} passphrase: ".format(note)
    passphrase = input(prompt)
    passphrase = passphrase.encode('ascii')
    passphrase_v = input(prompt)
    passphrase_v = passphrase_v.encode('ascii')
    assert passphrase == passphrase_v
    assert len(passphrase) > 12
    return passphrase


def dmenu_tag(tag_cache_file):
    with open(tag_cache_file, 'r') as fh:
        tag_list = fh.readlines()
    font = "-Misc-Fixed-Medium-R-SemiCondensed--13-120-75-75-C-60-ISO10646-1"
    #answer = dmenu.show(tag_list, font="-misc-fixed-*-*-*-*-50-*-*-*-*-*-*-*", case_insensitive=True)
    answer = dmenu.show(tag_list, font=font, case_insensitive=True)
    return answer


def get_thing_dmenu(cache_file, msg):
    try:
        thing = dmenu_tag(cache_file)
        return thing
    except Exception as e:
        ceprint(e)
        if not msg.endswith(' '):
            msg += ' '
        thing = input(msg)
        return thing


def human_filesize_to_int(size, verbose=False):
    u = pint.UnitRegistry()
    i = u.parse_expression(size)
    result = i.to('bytes').magnitude
    if verbose:
        ic(result)

    return result


@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True)
@click.option('--head', type=int)
@click.option("--null", is_flag=True)
def cli(strings, add, group, verbose, debug, head, null):

    byte = b'\n'
    if null:
        byte = b'\x00'

    if not group:
        group = "BANS"

    config, config_mtime = click_read_config(click_instance=click,
                                             app_name=APP_NAME,
                                             verbose=verbose)
    if verbose:
        ic(config)

    if strings:
        iterator = strings
    else:
        iterator = read_by_byte(sys.stdin.buffer, byte=byte)

    lines_output = 0
    for index, string in enumerate(iterator):
        if verbose:
            ic(index, string)

        if isinstance(string, bytes):
            string = string.decode('utf8')

        if add:
            section = "BANS"
            key = string
            value = ""
            config, config_mtime = click_write_config_entry(click_instance=click,
                                                            app_name=APP_NAME,
                                                            section=section,
                                                            key=key,
                                                            value=value,
                                                            verbose=verbose)
        else:
            banned = stringfilter(string=string,
                                  group=None,
                                  config=config,
                                  config_mtime=config_mtime,
                                  verbose=verbose,
                                  debug=debug)
            if banned:
                print("banned:", string, file=sys.stderr)
                continue
            else:
                print(string, end=byte.decode('utf8'))
                lines_output += 1

                if head:
                    if lines_output >= head:
                        break

