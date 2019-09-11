#!/usr/bin/env python3

import os
import configparser
from kcl.fileops import empty_file


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

