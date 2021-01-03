#!/usr/bin/env python3

import configparser
import os
import sys
from pathlib import Path

from icecream import ic

#from kcl.fileops import empty_file
from kcl.timeops import get_mtime


class ConfigUnchangedError(ValueError):
    pass


def click_read_config(*,
                      click_instance,
                      app_name,
                      verbose: bool,
                      debug: bool,
                      last_mtime=None,
                      keep_case=True,):
    cfg = Path(os.path.join(click_instance.get_app_dir(app_name), 'config.ini'))
    try:
        config_mtime = get_mtime(cfg)
    except FileNotFoundError:
        config_mtime = None

    if config_mtime:
        if config_mtime == last_mtime:
            raise ConfigUnchangedError

    cfg.parent.mkdir(exist_ok=True)
    if verbose:
        ic(cfg)
    parser = configparser.RawConfigParser()
    if keep_case:
        parser.optionxform = str
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


def click_write_config_entry(*,
                             click_instance,
                             app_name,
                             section,
                             key,
                             value,
                             verbose: bool,
                             debug: bool,
                             keep_case=True):
    if verbose:
        ic(app_name, section, key, value)
    cfg = Path(os.path.join(click_instance.get_app_dir(app_name), 'config.ini'))
    cfg.parent.mkdir(exist_ok=True)
    parser = configparser.RawConfigParser()
    if keep_case:
        parser.optionxform = str
    parser.read([cfg])
    try:
        parser[section][key] = value
    except KeyError:
        parser[section] = {}
        parser[section][key] = value

    with open(cfg, 'w') as configfile:
        parser.write(configfile)

    config, config_mtime = click_read_config(click_instance=click_instance,
                                             app_name=app_name,
                                             verbose=verbose,
                                             debug=debug,)
    return config, config_mtime


def _click_remove_config_entry(*,
                               click_instance,
                               app_name,
                               section,
                               key,
                               value,
                               verbose: bool,
                               debug: bool,
                               keep_case=True,):
    cfg = Path(os.path.join(click_instance.get_app_dir(app_name), 'config.ini'))
    parser = configparser.RawConfigParser()
    parser.read([cfg])
    if keep_case:
        parser.optionxform = str
    try:
        parser[section][key] = value
    except KeyError:
        parser[section] = {}
        parser[section][key] = value

    with open(cfg, 'w') as configfile:
        parser.write(configfile)

    config, config_mtime = click_read_config(click_instance=click_instance,
                                             app_name=app_name,
                                             verbose=verbose,
                                             debug=debug,)
    return config, config_mtime
