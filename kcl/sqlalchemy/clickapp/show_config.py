#!/usr/bin/env python3

import click
import builtins
CONFIG = builtins.config
from kcl.printops import print_object_attrs
from kcl.printops import eprint

@click.command()
def show_config():
    print_object_attrs(CONFIG)
    print_object_attrs(CONFIG.sa_config)

