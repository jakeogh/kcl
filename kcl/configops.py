#!/usr/bin/env python3

import os
import sys
from pathlib import Path
import configparser
#from kcl.fileops import empty_file
from kcl.timeops import get_mtime
from icecream import ic


class ConfigUnchangedError(ValueError):
    pass


def click_read_config(*, click_instance, app_name, verbose=False, last_mtime=None):
    cfg = Path(os.path.join(click_instance.get_app_dir(app_name), 'config.ini'))
    config_mtime = get_mtime(cfg)
    if config_mtime == last_mtime:
        raise ConfigUnchangedError

    cfg.parent.mkdir(exist_ok=True)
    if verbose:
        ic(cfg)
    parser = configparser.RawConfigParser()
    parser.read([cfg])
    rv = {}
    if verbose:
        ic(parser.sections())
    for section in parser.sections():
        rv[section] = {}
        for key, value in parser.items(section):
            rv[section][key] = value
    if verbose:
        ic(rv)

    return rv, config_mtime


def click_write_config_entry(*, click_instance, app_name, section, key, value, verbose=False):
    cfg = Path(os.path.join(click_instance.get_app_dir(app_name), 'config.ini'))
    parser = configparser.RawConfigParser()
    parser.read([cfg])
    try:
        parser[section][key] = value
    except KeyError:
        parser[section] = {}
        parser[section][key] = value

    with open(cfg, 'w') as configfile:
        parser.write(configfile)

    config, config_mtime = click_read_config(click_instance=click_instance, app_name=app_name, verbose=verbose)
    return config, config_mtime
