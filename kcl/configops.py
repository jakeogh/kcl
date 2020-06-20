#!/usr/bin/env python3

import os
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
    for section in parser.sections():
        rv[section] = {}
        for key, value in parser.items(section):
            rv[section][key] = value
    if verbose:
        ic.enable()
        ic(rv)
    return rv


def read_config_file(config_file):
    # race condition, CONFIG.read throws no error when it trys to read empty or non existing config file
    if os.path.isfile(config_file) and not empty_file(config_file):
        config_parser = configparser.ConfigParser()
        config_parser.read(config_file)
        return config_parser
    else:
        print("Problem reading config file, creating default CONFIG.")
        #write_default_config_file()
        #config_parser.read(config_file)
        #return config_parser


