#!/usr/bin/env python3

import os
import sys
from pathlib import Path
import configparser
from kcl.fileops import empty_file
from icecream import ic


def click_read_config(click_instance, app_name, verbose=False):
    cfg = Path(os.path.join(click_instance.get_app_dir(app_name), 'config.ini'))
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
    return rv


def click_write_config_entry(click_instance, app_name, section, key, value):
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

