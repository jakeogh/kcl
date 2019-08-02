#!/usr/bin/env python3

import click
import builtins
CONFIG = builtins.config
from kcl.printops import print_object_attrs
from kcl.printops import eprint

@click.command()
def config():
    print_object_attrs(CONFIG)
    try:
        print_object_attrs(CONFIG.sa_config)
    except AttributeError:
        pass #temp for iridb fixme

